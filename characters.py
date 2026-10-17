"""Elenco de personagens, ícones e cenários (dados em characters.json)."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

import pygame


def _rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


@dataclass(frozen=True)
class Character:
    id: str
    name: str
    nickname: str
    age: int
    origin: str
    style: str
    backstory: str
    color: tuple[int, int, int]
    accent: tuple[int, int, int]
    stage: str
    icon: str
    move_names: dict = field(default_factory=dict)


class Roster:
    def __init__(self, data: dict, assets_dir: Path) -> None:
        self.assets_dir = Path(assets_dir)
        self.stages: dict[str, dict] = data["stages"]
        self.characters: dict[str, Character] = {}
        for c in data["characters"]:
            self.characters[c["id"]] = Character(
                id=c["id"], name=c["name"], nickname=c["nickname"], age=c["age"],
                origin=c["origin"], style=c["style"], backstory=c["backstory"],
                color=_rgb(c["color"]), accent=_rgb(c["accent"]), stage=c["stage"],
                icon=c["icon"], move_names=c.get("move_names", {}),
            )
        self.ids = list(self.characters)
        self.stage_ids = list(self.stages)
        self._icons: dict[tuple[str, int], pygame.Surface | None] = {}
        self._stages: dict[str, pygame.Surface | None] = {}

    @classmethod
    def load(cls, json_path: str | Path, assets_dir: str | Path) -> "Roster":
        with open(json_path, encoding="utf-8") as f:
            return cls(json.load(f), Path(assets_dir))

    def cycle(self, current: str, step: int = 1) -> str:
        return self.ids[(self.ids.index(current) + step) % len(self.ids)]

    def cycle_stage(self, current: str, step: int = 1) -> str:
        return self.stage_ids[(self.stage_ids.index(current) + step) % len(self.stage_ids)]

    # As imagens são carregadas sob demanda; se o arquivo faltar, devolve
    # None e o jogo desenha uma versão simples no lugar.
    def icon(self, char_id: str, size: int) -> pygame.Surface | None:
        key = (char_id, size)
        if key not in self._icons:
            self._icons[key] = self._load(self.characters[char_id].icon, size=size)
        return self._icons[key]

    def stage_image(self, stage_id: str) -> pygame.Surface | None:
        if stage_id not in self._stages:
            self._stages[stage_id] = self._load(self.stages[stage_id]["file"])
        return self._stages[stage_id]

    def _load(self, rel: str, size: int | None = None) -> pygame.Surface | None:
        path = self.assets_dir / rel
        if not path.exists():
            return None
        try:
            img = pygame.image.load(str(path)).convert_alpha()
        except pygame.error:
            return None
        if size:
            img = pygame.transform.smoothscale(img, (size, size))
        return img
