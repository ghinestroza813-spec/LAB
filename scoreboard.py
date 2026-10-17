"""Placar de vitórias do TikTok Fight Arena.

Módulo independente: guarda as vitórias do Lado A e do Lado B, desenha o
placar no topo da tela e salva em score.json para não perder a contagem
ao fechar o jogo no meio da live.
"""
import json
import os

import pygame

SCORE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "score.json")


class Scoreboard:
    def __init__(self, path=SCORE_FILE):
        self.path = path
        self.wins = {"A": 0, "B": 0}
        self._font = None
        self._small = None
        self.load()

    # --- regras -----------------------------------------------------------
    def add_win(self, side):
        """Soma uma vitória. side = 'A' ou 'B'."""
        if side in self.wins:
            self.wins[side] += 1
            self.save()

    def reset(self):
        """Zera o placar (não mexe na rodada em andamento)."""
        self.wins = {"A": 0, "B": 0}
        self.save()

    # --- persistência -----------------------------------------------------
    def load(self):
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.wins["A"] = int(data.get("A", 0))
            self.wins["B"] = int(data.get("B", 0))
        except (OSError, ValueError):
            pass

    def save(self):
        try:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self.wins, f)
        except OSError:
            pass

    # --- desenho ----------------------------------------------------------
    def draw(self, surface, name_a="Lado A", name_b="Lado B",
             color_a=(220, 60, 60), color_b=(60, 120, 230)):
        if self._font is None:
            self._font = pygame.font.SysFont("arial", 34, bold=True)
            self._small = pygame.font.SysFont("arial", 16, bold=True)

        w = surface.get_width()
        box_w, box_h = 220, 52
        box = pygame.Rect((w - box_w) // 2, 8, box_w, box_h)

        panel = pygame.Surface(box.size, pygame.SRCALPHA)
        pygame.draw.rect(panel, (0, 0, 0, 170), panel.get_rect(), border_radius=10)
        surface.blit(panel, box.topleft)

        sa = self._font.render(str(self.wins["A"]), True, color_a)
        sb = self._font.render(str(self.wins["B"]), True, color_b)
        dash = self._font.render("x", True, (230, 230, 230))
        cy = box.centery
        surface.blit(dash, dash.get_rect(center=(box.centerx, cy)))
        surface.blit(sa, sa.get_rect(center=(box.centerx - 55, cy)))
        surface.blit(sb, sb.get_rect(center=(box.centerx + 55, cy)))

        la = self._small.render(name_a, True, color_a)
        lb = self._small.render(name_b, True, color_b)
        surface.blit(la, la.get_rect(midright=(box.left - 10, cy)))
        surface.blit(lb, lb.get_rect(midleft=(box.right + 10, cy)))
