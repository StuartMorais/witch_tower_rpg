from game import Game
import ui


def main():
    ui.title_screen()
    ui.pause()
    Game().run()


if __name__ == "__main__":
    main()
