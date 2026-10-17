"""Fila de eventos thread-safe.

Fontes reais (WebSocket/asyncio) rodam fora da thread do jogo e só chamam
`push()`. O loop do jogo chama `drain()` uma vez por quadro, consumindo no
máximo N eventos, para que rajadas de presentes não travem a renderização.
"""
from __future__ import annotations

import threading
import time
from collections import deque
from dataclasses import dataclass, field


@dataclass
class Event:
    side: str                 # "A" ou "B": quem ataca
    move: str                 # chave em gift_rules.json -> "moves"
    source: str = "keyboard"  # "keyboard", "like", "gift", "comment"...
    user: str | None = None   # apelido de quem enviou (se houver)
    count: int = 1
    created_at: float = field(default_factory=time.monotonic)


class EventQueue:
    def __init__(self, maxsize: int = 200) -> None:
        self._items: deque[Event] = deque()
        self._lock = threading.Lock()
        self.maxsize = maxsize
        self.dropped = 0

    def push(self, event: Event) -> None:
        with self._lock:
            if len(self._items) >= self.maxsize:
                self._items.popleft()  # descarta o mais antigo
                self.dropped += 1
            self._items.append(event)

    def drain(self, max_per_frame: int = 3) -> list[Event]:
        with self._lock:
            n = min(max_per_frame, len(self._items))
            return [self._items.popleft() for _ in range(n)]

    def clear(self) -> None:
        with self._lock:
            self._items.clear()

    def __len__(self) -> int:
        with self._lock:
            return len(self._items)
