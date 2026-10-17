"""Regras de combate e renderização."""
from __future__ import annotations

from dataclasses import dataclass

import pygame

from characters import Character, Roster

W, H = 960, 540
MAX_HP = 100
GROUND_Y = 400

BG = (24, 26, 38)
FLOOR = (44, 48, 66)
TEXT = (235, 235, 245)
ICON_BAR = 64


@dataclass
class Fighter:
    side: str
    char: Character
    hp: int = MAX_HP
    attack_t: float = 0.0
    hit_t: float = 0.0

    def reset(self) -> None:
        self.hp = MAX_HP
        self.attack_t = 0.0
        self.hit_t = 0.0


def wrap(text: str, font: pygame.font.Font, width: int) -> list[str]:
    lines, cur = [], ""
    for word in text.split():
        test = f"{cur} {word}".strip()
        if font.size(test)[0] <= width:
            cur = test
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


class Game:
    ATTACK_TIME = 0.25
    HIT_TIME = 0.25

    def __init__(self, moves: dict, roster: Roster,
                 start_ids: tuple[str, str] | None = None) -> None:
        self.moves = moves
        self.roster = roster
        a, b = start_ids or (roster.ids[0], roster.ids[1])
        self.fighters = {"A": Fighter("A", roster.characters[a]),
                         "B": Fighter("B", roster.characters[b])}
        self.stage_override: str | None = None  # None = cenário do lutador A
        self.show_bio = False
        self.winner: str | None = None
        self.last_text = ""
        self.floaters: list[dict] = []
        self._fonts_ready = False

    # ---------- escolha de personagem / cenário ----------
    @property
    def stage_id(self) -> str:
        return self.stage_override or self.fighters["A"].char.stage

    def cycle_character(self, side: str) -> None:
        f = self.fighters[side]
        other = self.fighters["B" if side == "A" else "A"].char.id
        nxt = self.roster.cycle(f.char.id)
        if nxt == other:  # não deixa os dois serem o mesmo personagem
            nxt = self.roster.cycle(nxt)
        f.char = self.roster.characters[nxt]
        self.reset()

    def cycle_stage(self) -> None:
        self.stage_override = self.roster.cycle_stage(self.stage_id)

    def toggle_bio(self) -> None:
        self.show_bio = not self.show_bio

    # ---------- regras ----------
    def reset(self) -> None:
        for f in self.fighters.values():
            f.reset()
        self.winner = None
        self.last_text = ""
        self.floaters.clear()

    def apply_move(self, side: str, move_key: str, user: str | None = None) -> None:
        if self.winner or move_key not in self.moves or side not in self.fighters:
            return
        move = self.moves[move_key]
        attacker = self.fighters[side]
        target = self.fighters["B" if side == "A" else "A"]
        damage = int(move["damage"])
        target.hp = max(0, target.hp - damage)
        attacker.attack_t = self.ATTACK_TIME
        target.hit_t = self.HIT_TIME
        label = attacker.char.move_names.get(move_key, move["label"])
        who = f"{user}: " if user else ""
        self.last_text = f"{who}{attacker.char.nickname} — {label} (-{damage})"
        x = 240 if target.side == "A" else W - 240
        self.floaters.append({"text": f"-{damage}", "x": x, "y": GROUND_Y - 190, "t": 0.8})
        if target.hp == 0:
            self.winner = side

    def update(self, dt: float) -> None:
        for f in self.fighters.values():
            f.attack_t = max(0.0, f.attack_t - dt)
            f.hit_t = max(0.0, f.hit_t - dt)
        for fl in self.floaters:
            fl["t"] -= dt
            fl["y"] -= 60 * dt
        self.floaters = [fl for fl in self.floaters if fl["t"] > 0]

    # ---------- desenho ----------
    def _fonts(self) -> None:
        if not self._fonts_ready:
            self._font = pygame.font.Font(None, 28)
            self._small = pygame.font.Font(None, 22)
            self._mid = pygame.font.Font(None, 36)
            self._big = pygame.font.Font(None, 72)
            self._fonts_ready = True

    def draw(self, screen: pygame.Surface) -> None:
        self._fonts()
        stage = self.roster.stage_image(self.stage_id)
        if stage:
            screen.blit(stage, (0, 0))
        else:
            screen.fill(BG)
            pygame.draw.rect(screen, FLOOR, (0, GROUND_Y, W, H - GROUND_Y))

        self._draw_bar(screen, self.fighters["A"], 30, left=True)
        self._draw_bar(screen, self.fighters["B"], W - 30, left=False)

        for f in self.fighters.values():
            self._draw_fighter(screen, f)

        for fl in self.floaters:
            surf = self._big.render(fl["text"], True, (255, 220, 90))
            screen.blit(surf, surf.get_rect(center=(fl["x"], fl["y"])))

        if self.last_text:
            self._text_shadow(screen, self._font, self.last_text, (W // 2, 112))

        hint = "TAB: história  |  F1/F2: trocar lutador  |  F3: cenário"
        self._text_shadow(screen, self._small, hint, (W // 2, H - 16))

        if self.winner:
            c = self.fighters[self.winner].char
            self._text_shadow(screen, self._big, f"{c.nickname} venceu!", (W // 2, 220))
            self._text_shadow(screen, self._font, "R: reiniciar", (W // 2, 270))

        if self.show_bio:
            self._draw_bio(screen)

    def _text_shadow(self, screen, font, text, center) -> None:
        shadow = font.render(text, True, (0, 0, 0))
        surf = font.render(text, True, TEXT)
        r = surf.get_rect(center=center)
        screen.blit(shadow, r.move(2, 2))
        screen.blit(surf, r)

    def _draw_bar(self, screen, f: Fighter, anchor_x: int, left: bool) -> None:
        c = f.char
        icon = self.roster.icon(c.id, ICON_BAR)
        bar_w, bar_h = 300, 26
        icon_x = anchor_x if left else anchor_x - ICON_BAR
        bar_x = anchor_x + ICON_BAR + 12 if left else anchor_x - ICON_BAR - 12 - bar_w
        if icon:
            screen.blit(icon, (icon_x, 24))
        else:
            pygame.draw.circle(screen, c.color, (icon_x + ICON_BAR // 2, 24 + ICON_BAR // 2), ICON_BAR // 2)
        pygame.draw.rect(screen, (20, 20, 30), (bar_x - 2, 28, bar_w + 4, bar_h + 4), border_radius=8)
        pygame.draw.rect(screen, (60, 60, 75), (bar_x, 30, bar_w, bar_h), border_radius=6)
        fill = int(bar_w * f.hp / MAX_HP)
        fx = bar_x if left else bar_x + bar_w - fill
        if fill:
            pygame.draw.rect(screen, c.color, (fx, 30, fill, bar_h), border_radius=6)
        label = self._font.render(f"{c.nickname}  {f.hp}", True, TEXT)
        shadow = self._font.render(f"{c.nickname}  {f.hp}", True, (0, 0, 0))
        pos = (bar_x, 62) if left else label.get_rect(topright=(bar_x + bar_w, 62)).topleft
        screen.blit(shadow, (pos[0] + 2, pos[1] + 2))
        screen.blit(label, pos)

    def _draw_fighter(self, screen, f: Fighter) -> None:
        c = f.char
        direction = 1 if f.side == "A" else -1
        base_x = 240 if f.side == "A" else W - 240
        offset = 70 * direction * (f.attack_t / self.ATTACK_TIME) if f.attack_t else 0
        shake = int(((f.hit_t * 60) % 2) * 8 - 4) if f.hit_t else 0
        x = base_x + offset + shake
        body = (255, 255, 255) if f.hit_t else c.color
        if f.hp == 0:
            pygame.draw.rect(screen, body, (x - 70, GROUND_Y - 40, 140, 40), border_radius=10)
            return
        pygame.draw.ellipse(screen, (15, 15, 22), (x - 45, GROUND_Y - 6, 90, 14))  # sombra
        pygame.draw.rect(screen, body, (x - 35, GROUND_Y - 150, 70, 110), border_radius=10)
        pygame.draw.rect(screen, c.accent, (x - 35, GROUND_Y - 72, 70, 12))           # cinto
        pygame.draw.circle(screen, body, (int(x), GROUND_Y - 180), 30)                 # cabeça
        pygame.draw.rect(screen, c.accent, (x - 30, GROUND_Y - 192, 60, 10), border_radius=4)  # faixa
        icon = self.roster.icon(c.id, 44)
        if icon and not f.hit_t:
            screen.blit(icon, icon.get_rect(center=(int(x), GROUND_Y - 112)))
        if f.attack_t:
            arm_x = x + 25 if direction > 0 else x - 85
            pygame.draw.rect(screen, body, (arm_x, GROUND_Y - 130, 60, 18), border_radius=8)

    def _draw_bio(self, screen) -> None:
        panel = pygame.Surface((W - 80, 300), pygame.SRCALPHA)
        panel.fill((10, 10, 20, 225))
        screen.blit(panel, (40, 130))
        col_w = (W - 80) // 2
        for i, side in enumerate(("A", "B")):
            c = self.fighters[side].char
            x0 = 40 + i * col_w + 20
            y0 = 146
            icon = self.roster.icon(c.id, 88)
            if icon:
                screen.blit(icon, (x0, y0))
            screen.blit(self._mid.render(c.nickname, True, c.color), (x0 + 100, y0 + 2))
            screen.blit(self._font.render(f"{c.name}, {c.age} anos", True, TEXT), (x0 + 100, y0 + 38))
            screen.blit(self._small.render(c.origin, True, (170, 175, 200)), (x0 + 100, y0 + 64))
            y = y0 + 104
            screen.blit(self._small.render(f"Estilo: {c.style}", True, c.accent if sum(c.accent) > 200 else c.color), (x0, y))
            y += 28
            for line in wrap(c.backstory, self._small, col_w - 40):
                screen.blit(self._small.render(line, True, TEXT), (x0, y))
                y += 22
