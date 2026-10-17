"""TikTok Fight Arena — MVP 0.4 (personagens, ícones e cenários)."""
from pathlib import Path

import pygame

from characters import Roster
from event_queue import EventQueue
from game import H, W, Game
from tiktok_adapter import KeyboardSource, RuleBook

EVENTS_PER_FRAME = 3
HERE = Path(__file__).parent


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("TikTok Fight Arena — MVP 0.4")
    clock = pygame.time.Clock()

    rulebook = RuleBook.load(HERE / "gift_rules.json")
    roster = Roster.load(HERE / "characters.json", HERE / "assets")
    queue = EventQueue(maxsize=200)
    game = Game(rulebook.moves, roster)
    keyboard = KeyboardSource(rulebook, queue)
    keyboard.start()

    running = True
    while running:
        dt = clock.tick(60) / 1000
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    running = False
                elif e.key == pygame.K_r:
                    game.reset()
                    queue.clear()
                elif e.key == pygame.K_TAB:
                    game.toggle_bio()
                elif e.key == pygame.K_F1:
                    game.cycle_character("A")
                    queue.clear()
                elif e.key == pygame.K_F2:
                    game.cycle_character("B")
                    queue.clear()
                elif e.key == pygame.K_F3:
                    game.cycle_stage()
                else:
                    keyboard.handle_key(pygame.key.name(e.key))

        for ev in queue.drain(EVENTS_PER_FRAME):
            game.apply_move(ev.side, ev.move, ev.user)

        game.update(dt)
        game.draw(screen)
        pygame.display.flip()

    keyboard.stop()
    pygame.quit()


if __name__ == "__main__":
    main()
