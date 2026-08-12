import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

from player import Player


def _game_data_root():
    """
    Source build: keep saves inside the project folder.
    PyInstaller build: keep saves beside WitchTower.exe so they persist
    between launches instead of living in PyInstaller's temporary directory.
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


SAVE_DIR = _game_data_root() / "saves"

# Latest normal progress. Used by "Continue saved climb".
SAVE_FILE = SAVE_DIR / "savegame.json"

# Protected death rollback snapshot. Updated only every 20 floors.
CHECKPOINT_FILE = SAVE_DIR / "safe_haven.json"

# Run-wide metadata that must NEVER rewind with a Safe Haven snapshot.
# Deaths, highest floor, difficulty, kills, and score live here.
META_FILE = SAVE_DIR / "run_meta.json"

# Permanent history. This file is NEVER deleted by permadeath or New Run.
RECORDS_FILE = SAVE_DIR / "tower_records.json"

MAX_RUN_DEATHS = 5


def _read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        return None


def has_save():
    """Return True when a normal progress save exists."""
    if not SAVE_FILE.exists():
        return False

    data = _read_json(SAVE_FILE)
    if not data:
        return False

    try:
        floor = int(data.get("player", {}).get("floor", 0))
    except (ValueError, TypeError):
        return False

    return (
        isinstance(data.get("player"), dict)
        and data.get("tower_seed") is not None
        and floor >= 1
    )


def has_checkpoint():
    """Return True when a valid 20-floor death checkpoint exists."""
    if not CHECKPOINT_FILE.exists():
        return False

    data = _read_json(CHECKPOINT_FILE)
    if not data:
        return False

    try:
        safe_floor = int(data.get("safe_haven_floor", 0))
        resume_floor = int(data.get("resume_floor", 0))
        player_floor = int(data.get("player", {}).get("floor", 0))
    except (ValueError, TypeError):
        return False

    return (
        safe_floor > 0
        and safe_floor % 20 == 0
        and resume_floor == safe_floor + 1
        and player_floor == resume_floor
    )


def save_game(player, tower_seed):
    """Autosave the latest active climb and refresh its permanent record."""
    SAVE_DIR.mkdir(parents=True, exist_ok=True)
    update_run_progress(player)

    data = {
        "version": 3,
        "tower_seed": tower_seed,
        "player": player.to_dict(),
    }
    SAVE_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def save_checkpoint(player, tower_seed, safe_haven_floor):
    """
    Save the protected death rollback point after Floors 20, 40, 60...

    A Safe Haven after Floor 20 resumes the climb on Floor 21.

    The permanent Tower Record is intentionally NOT stored here. Records and
    run-wide stats live outside the checkpoint so rewinding cannot erase them.
    """
    if safe_haven_floor <= 0 or safe_haven_floor % 20 != 0:
        raise ValueError("Death checkpoints only exist every 20 floors.")

    expected_resume = safe_haven_floor + 1
    if player.floor != expected_resume:
        raise ValueError(
            f"Checkpoint after Floor {safe_haven_floor} must resume at "
            f"Floor {expected_resume}."
        )

    SAVE_DIR.mkdir(parents=True, exist_ok=True)
    update_run_progress(player)

    data = {
        "version": 3,
        "safe_haven_floor": safe_haven_floor,
        "resume_floor": player.floor,
        "tower_seed": tower_seed,
        "player": player.to_dict(),
    }
    CHECKPOINT_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def load_game():
    """Load the newest normal autosave."""
    if not has_save():
        return None, None

    data = _read_json(SAVE_FILE)
    player = Player.from_dict(data["player"])

    # Migrates older saves into the Tower Records system automatically.
    update_run_progress(player)

    return player, data["tower_seed"]


def load_checkpoint():
    """Load the protected Safe Haven snapshot used only after death."""
    if not has_checkpoint():
        return None, None

    data = _read_json(CHECKPOINT_FILE)
    player = Player.from_dict(data["player"])

    # This never lowers record values because update_run_progress uses max().
    update_run_progress(player)

    return player, data["tower_seed"]


def checkpoint_floor():
    if not has_checkpoint():
        return None
    return int(_read_json(CHECKPOINT_FILE)["safe_haven_floor"])


def checkpoint_resume_floor():
    if not has_checkpoint():
        return None
    return int(_read_json(CHECKPOINT_FILE)["resume_floor"])


def current_floor():
    if not has_save():
        return None
    return int(_read_json(SAVE_FILE)["player"]["floor"])


def restore_checkpoint_to_current():
    """
    Rewind the active climb to the last 20-floor Safe Haven.

    savegame.json is overwritten with the checkpoint snapshot so reopening
    the game after death cannot restore progress that should have been lost.

    run_meta.json and tower_records.json are NOT rewound.
    """
    player, tower_seed = load_checkpoint()
    if player is None:
        return None, None

    save_game(player, tower_seed)
    return player, tower_seed


# ---------------------------------------------------------------------
# RUN-WIDE STATS + PERMANENT TOWER RECORDS
# ---------------------------------------------------------------------

def _now_text():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _new_run_id():
    return uuid.uuid4().hex


def _default_meta(player=None):
    """
    Stats for one climb.

    These values are deliberately separate from Player / Safe Haven snapshots.
    A checkpoint rewind must not erase deaths, kills, or the highest point
    already reached during the run.
    """
    name = player.name if player is not None else "Unknown Hunter"
    class_name = player.class_name if player is not None else "Unknown"
    floor = max(1, int(player.floor)) if player is not None else 1
    difficulty = (
        max(1, int(player.difficulty_multiplier))
        if player is not None
        else 1
    )

    return {
        "version": 2,
        "run_id": _new_run_id(),
        "character_name": name,
        "class_name": class_name,
        "status": "ACTIVE",
        "death_count": 0,
        "highest_floor": floor,
        "highest_difficulty": difficulty,
        "enemies_killed": 0,
        "best_score": 0,
        "started_at": _now_text(),
        "updated_at": _now_text(),
    }


def _normalize_meta(data, player=None):
    """Upgrade older run_meta.json files without destroying old death counts."""
    if not isinstance(data, dict):
        return _default_meta(player)

    default = _default_meta(player)

    try:
        deaths = max(0, int(data.get("death_count", 0)))
    except (TypeError, ValueError):
        deaths = 0

    try:
        highest_floor = max(1, int(data.get("highest_floor", default["highest_floor"])))
    except (TypeError, ValueError):
        highest_floor = default["highest_floor"]

    try:
        highest_difficulty = max(
            1,
            int(data.get("highest_difficulty", default["highest_difficulty"])),
        )
    except (TypeError, ValueError):
        highest_difficulty = default["highest_difficulty"]

    try:
        enemies_killed = max(0, int(data.get("enemies_killed", 0)))
    except (TypeError, ValueError):
        enemies_killed = 0

    try:
        best_score = max(0, int(data.get("best_score", 0)))
    except (TypeError, ValueError):
        best_score = 0

    character_name = str(data.get("character_name") or default["character_name"])
    class_name = str(data.get("class_name") or default["class_name"])
    status = str(data.get("status") or "ACTIVE").upper()
    if status not in {"ACTIVE", "FALLEN", "ABANDONED"}:
        status = "ACTIVE"

    # If a Player was supplied, use it to fill/migrate identifying data and
    # current progression, but never LOWER record values.
    if player is not None:
        character_name = player.name
        class_name = player.class_name
        highest_floor = max(highest_floor, int(player.floor))
        highest_difficulty = max(
            highest_difficulty,
            int(player.difficulty_multiplier),
        )

    return {
        "version": 2,
        "run_id": str(data.get("run_id") or default["run_id"]),
        "character_name": character_name,
        "class_name": class_name,
        "status": status,
        "death_count": deaths,
        "highest_floor": highest_floor,
        "highest_difficulty": highest_difficulty,
        "enemies_killed": enemies_killed,
        "best_score": best_score,
        "started_at": str(data.get("started_at") or default["started_at"]),
        "updated_at": str(data.get("updated_at") or _now_text()),
    }


def _read_meta(player=None):
    if not META_FILE.exists():
        return _default_meta(player)

    return _normalize_meta(_read_json(META_FILE), player)


def _write_meta(data):
    SAVE_DIR.mkdir(parents=True, exist_ok=True)
    META_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _difficulty_steps(multiplier):
    """
    BLUE/RED difficulty uses powers of two:
        x1, x2, x4, x8, x16...

    Return how many RED-door increases are represented by the multiplier.
    """
    value = max(1, int(multiplier))
    steps = 0
    while value >= 2:
        value //= 2
        steps += 1
    return steps


def calculate_score(meta):
    """
    Score emphasizes progress and risk.

    - 100 points per floor beyond Floor 1
    - 25 points per enemy killed
    - 750 points per RED-door difficulty step
    - 200 point penalty per death

    best_score stores the highest score the run ever reached, so a later death
    cannot erase the player's previous best performance.
    """
    floor_points = max(0, int(meta["highest_floor"]) - 1) * 100
    kill_points = max(0, int(meta["enemies_killed"])) * 25
    difficulty_points = _difficulty_steps(meta["highest_difficulty"]) * 750
    death_penalty = max(0, int(meta["death_count"])) * 200

    return max(
        0,
        floor_points + kill_points + difficulty_points - death_penalty,
    )


def _record_from_meta(meta):
    return {
        "run_id": meta["run_id"],
        "character_name": meta["character_name"],
        "class_name": meta["class_name"],
        "status": meta["status"],
        "highest_floor": int(meta["highest_floor"]),
        "deaths": int(meta["death_count"]),
        "highest_difficulty": int(meta["highest_difficulty"]),
        "enemies_killed": int(meta["enemies_killed"]),
        "best_score": int(meta["best_score"]),
        "started_at": meta.get("started_at", ""),
        "updated_at": meta.get("updated_at", ""),
    }


def _read_records_data():
    data = _read_json(RECORDS_FILE)
    if not isinstance(data, dict):
        return {"version": 1, "records": []}

    records = data.get("records")
    if not isinstance(records, list):
        records = []

    return {
        "version": 1,
        "records": [record for record in records if isinstance(record, dict)],
    }


def _write_records_data(data):
    SAVE_DIR.mkdir(parents=True, exist_ok=True)
    RECORDS_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _upsert_record(meta):
    """
    Insert/update this run in tower_records.json.

    The file is permanent and is not touched by delete_save().
    """
    data = _read_records_data()
    record = _record_from_meta(meta)
    run_id = record["run_id"]

    replaced = False
    for index, existing in enumerate(data["records"]):
        if existing.get("run_id") == run_id:
            data["records"][index] = record
            replaced = True
            break

    if not replaced:
        # Newest runs are stored first. Sorting for display happens separately.
        data["records"].insert(0, record)

    _write_records_data(data)
    return record


def ensure_run_meta(player=None):
    """
    Create or migrate metadata for the active run.

    Supplying Player is recommended because it lets old saves acquire the
    character name, class, floor, and difficulty automatically.
    """
    meta = _read_meta(player)
    meta["updated_at"] = _now_text()
    meta["best_score"] = max(meta["best_score"], calculate_score(meta))
    _write_meta(meta)
    _upsert_record(meta)
    return meta


def start_new_run(player):
    """Create fresh run-wide stats and a new permanent ACTIVE record."""
    meta = _default_meta(player)
    meta["best_score"] = calculate_score(meta)
    _write_meta(meta)
    _upsert_record(meta)
    return _record_from_meta(meta)


def update_run_progress(player):
    """
    Refresh highest floor/difficulty without allowing checkpoint rewinds
    to reduce the record.
    """
    meta = _read_meta(player)

    meta["character_name"] = player.name
    meta["class_name"] = player.class_name
    meta["highest_floor"] = max(meta["highest_floor"], int(player.floor))
    meta["highest_difficulty"] = max(
        meta["highest_difficulty"],
        int(player.difficulty_multiplier),
    )
    meta["updated_at"] = _now_text()

    score = calculate_score(meta)
    meta["best_score"] = max(meta["best_score"], score)

    _write_meta(meta)
    return _upsert_record(meta)


def record_enemy_kill(player=None):
    """
    Count one defeated enemy.

    This includes regular enemies and bosses, but there is intentionally no
    separate Bosses Defeated statistic.
    """
    meta = _read_meta(player)

    if player is not None:
        meta["character_name"] = player.name
        meta["class_name"] = player.class_name
        meta["highest_floor"] = max(meta["highest_floor"], int(player.floor))
        meta["highest_difficulty"] = max(
            meta["highest_difficulty"],
            int(player.difficulty_multiplier),
        )

    meta["enemies_killed"] += 1
    meta["updated_at"] = _now_text()
    meta["best_score"] = max(meta["best_score"], calculate_score(meta))

    _write_meta(meta)
    return _upsert_record(meta)


def death_count():
    return _read_meta()["death_count"]


def remaining_deaths():
    return max(0, MAX_RUN_DEATHS - death_count())


def record_death(player=None):
    """
    Add one irreversible death to the current run.

    Returns:
        (death_number, permadeath_reached)
    """
    meta = _read_meta(player)

    if player is not None:
        meta["character_name"] = player.name
        meta["class_name"] = player.class_name
        meta["highest_floor"] = max(meta["highest_floor"], int(player.floor))
        meta["highest_difficulty"] = max(
            meta["highest_difficulty"],
            int(player.difficulty_multiplier),
        )

    meta["death_count"] += 1
    meta["updated_at"] = _now_text()
    meta["best_score"] = max(meta["best_score"], calculate_score(meta))

    _write_meta(meta)
    _upsert_record(meta)

    count = meta["death_count"]
    return count, count >= MAX_RUN_DEATHS


def finalize_run(status, player=None):
    """
    Permanently mark a run.

    FALLEN:
        The hunter died permanently.

    ABANDONED:
        The player deliberately replaced an existing save with New Run.

    ACTIVE:
        Reserved for a living run.
    """
    status = str(status).upper()
    if status not in {"ACTIVE", "FALLEN", "ABANDONED"}:
        raise ValueError("Unknown Tower Record status.")

    meta = _read_meta(player)

    if player is not None:
        meta["character_name"] = player.name
        meta["class_name"] = player.class_name
        meta["highest_floor"] = max(meta["highest_floor"], int(player.floor))
        meta["highest_difficulty"] = max(
            meta["highest_difficulty"],
            int(player.difficulty_multiplier),
        )

    meta["status"] = status
    meta["updated_at"] = _now_text()
    meta["best_score"] = max(meta["best_score"], calculate_score(meta))

    _write_meta(meta)
    return _upsert_record(meta)


def current_run_record():
    """Return the active run's record, or None if run metadata does not exist."""
    if not META_FILE.exists():
        return None
    meta = _read_meta()
    meta["best_score"] = max(meta["best_score"], calculate_score(meta))
    return _record_from_meta(meta)


def tower_records():
    """
    Return all permanent runs ranked primarily by highest floor.

    No Attempts counter is stored. Each history entry IS one run.
    """
    records = _read_records_data()["records"]

    def value(record, key, default=0):
        try:
            return int(record.get(key, default))
        except (TypeError, ValueError):
            return default

    return sorted(
        records,
        key=lambda record: (
            value(record, "highest_floor", 1),
            value(record, "best_score", 0),
            value(record, "highest_difficulty", 1),
            value(record, "enemies_killed", 0),
        ),
        reverse=True,
    )


def reset_death_count():
    """
    Backward-compatible helper.

    New games should call start_new_run(player), which resets every run stat.
    """
    meta = _default_meta()
    _write_meta(meta)
    _upsert_record(meta)


def delete_current_save():
    if SAVE_FILE.exists():
        SAVE_FILE.unlink()


def delete_checkpoint():
    if CHECKPOINT_FILE.exists():
        CHECKPOINT_FILE.unlink()


def delete_meta():
    if META_FILE.exists():
        META_FILE.unlink()


def delete_save():
    """
    Delete the playable run and run-wide metadata.

    IMPORTANT:
    tower_records.json is intentionally preserved forever.
    """
    delete_current_save()
    delete_checkpoint()
    delete_meta()
