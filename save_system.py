import json
from pathlib import Path

from player import Player

SAVE_DIR = Path(__file__).resolve().parent / "saves"

# Latest normal progress. Used by "Continue saved climb".
SAVE_FILE = SAVE_DIR / "savegame.json"

# Protected death rollback snapshot. Updated only every 20 floors.
CHECKPOINT_FILE = SAVE_DIR / "safe_haven.json"


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
    """Autosave the latest active climb."""
    SAVE_DIR.mkdir(parents=True, exist_ok=True)

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
    return Player.from_dict(data["player"]), data["tower_seed"]


def load_checkpoint():
    """Load the protected Safe Haven snapshot used only after death."""
    if not has_checkpoint():
        return None, None

    data = _read_json(CHECKPOINT_FILE)
    return Player.from_dict(data["player"]), data["tower_seed"]


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
    """
    player, tower_seed = load_checkpoint()
    if player is None:
        return None, None

    save_game(player, tower_seed)
    return player, tower_seed


def delete_current_save():
    if SAVE_FILE.exists():
        SAVE_FILE.unlink()


def delete_checkpoint():
    if CHECKPOINT_FILE.exists():
        CHECKPOINT_FILE.unlink()


def delete_save():
    """Delete the entire run."""
    delete_current_save()
    delete_checkpoint()
