"""Traduz eventos de entrada (teclado hoje, TikTok depois) em golpes.

`RuleBook` lê o gift_rules.json. As fontes de evento só precisam criar
`Event`s e chamar `queue.push()`.
"""
from __future__ import annotations

import itertools
import json
from abc import ABC, abstractmethod
from pathlib import Path

from event_queue import Event, EventQueue


class RuleBook:
    def __init__(self, data: dict) -> None:
        self.moves: dict = data["moves"]
        self.keyboard: dict = data.get("keyboard", {})
        tiktok = data.get("tiktok", {})
        self.tiktok_rules: list[dict] = tiktok.get("rules", [])
        self.default_side: str = tiktok.get("default_side", "auto")
        self._alternate = itertools.cycle("AB")

    @classmethod
    def load(cls, path: str | Path) -> "RuleBook":
        with open(path, encoding="utf-8") as f:
            return cls(json.load(f))

    def resolve_key(self, key: str) -> Event | None:
        rule = self.keyboard.get(key.lower())
        if not rule or rule["move"] not in self.moves:
            return None
        return Event(side=rule["side"], move=rule["move"], source="keyboard")

    def resolve_tiktok(self, kind: str, name: str = "", user: str | None = None,
                       diamonds: int = 0, count: int = 1) -> Event | None:
        """Primeira regra que casar vence; coloque as mais específicas antes."""
        for rule in self.tiktok_rules:
            if rule["kind"] != kind:
                continue
            if rule.get("name", "*") not in ("*", name):
                continue
            if diamonds < rule.get("min_diamonds", 0):
                continue
            side = rule.get("side", self.default_side)
            if side == "auto":
                side = next(self._alternate)
            return Event(side=side, move=rule["move"], source=kind,
                         user=user, count=count)
        return None


class EventSource(ABC):
    """Interface comum para qualquer fonte de eventos."""

    def __init__(self, rulebook: RuleBook, queue: EventQueue) -> None:
        self.rulebook = rulebook
        self.queue = queue

    @abstractmethod
    def start(self) -> None: ...

    @abstractmethod
    def stop(self) -> None: ...


class KeyboardSource(EventSource):
    """Simulação local: o main.py repassa cada tecla para handle_key()."""

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def handle_key(self, key_name: str) -> bool:
        event = self.rulebook.resolve_key(key_name)
        if event:
            self.queue.push(event)
        return event is not None


class TikTokLiveSource(EventSource):
    """Ainda não implementada.

    A validar antes de codar:
      1. Qual fonte de eventos usar (API oficial do TikTok, se disponível
         para o seu caso, ou uma biblioteca/serviço de terceiros).
      2. O que os termos da plataforma permitem para esse uso.
      3. Nomes/IDs reais de presentes e reações para preencher o JSON.

    Quando houver uma fonte, ela deve rodar em outra thread (ou asyncio) e,
    a cada evento recebido, fazer:

        event = self.rulebook.resolve_tiktok(kind="gift", name=nome,
                                             user=apelido, diamonds=valor)
        if event:
            self.queue.push(event)
    """

    def start(self) -> None:
        raise NotImplementedError("Integração com o TikTok ainda não implementada.")

    def stop(self) -> None:
        pass
