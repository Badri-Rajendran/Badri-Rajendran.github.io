"""In-memory sliding-window rate limiter (per Cloud Run instance)."""

import threading
import time
from collections import deque


class SlidingWindowLimiter:
    """Allows at most `limit` hits per key within any `window_seconds` span."""

    def __init__(self, limit: int, window_seconds: float, clock=time.monotonic, sweep_every: int = 1_000):
        self.limit = limit
        self.window = window_seconds
        self._clock = clock
        self._sweep_every = sweep_every
        self._calls = 0
        self._hits: dict[str, deque] = {}
        self._lock = threading.Lock()

    def hit(self, key: str) -> float:
        """Record a hit and return 0, or return the seconds to wait if the key is over its limit."""
        if self.limit <= 0:
            return self.window   # a limit of 0 disables the endpoint; refuse, don't crash
        with self._lock:
            now = self._clock()
            self._calls += 1
            if self._calls % self._sweep_every == 0:
                self._sweep(now)

            hits = self._hits.setdefault(key, deque())
            while hits and hits[0] <= now - self.window:
                hits.popleft()
            if len(hits) >= self.limit:
                return hits[0] + self.window - now
            hits.append(now)
            return 0

    def _sweep(self, now: float) -> None:
        """Drop keys whose newest hit has left the window, so memory stays bounded."""
        for key in [k for k, hits in self._hits.items() if not hits or hits[-1] <= now - self.window]:
            del self._hits[key]
