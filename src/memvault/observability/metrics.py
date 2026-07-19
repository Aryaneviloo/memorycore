from dataclasses import dataclass, field
from threading import Lock


@dataclass
class Metrics:
    """
    Simple in-process metrics counter.

    Will add Prometheus or StatsD in later version
    thread safe via a lock since FastAPI handles request concurrently.
    """

    memories_inserted: int = 0
    memories_retrieved: int = 0
    memories_deleted: int = 0
    searches_performed: int = 0
    consolidations_performed: int = 0
    total_latency_ms: float = 0.0
    request_count: int = 0
    _lock: Lock = field(default_factory=Lock, repr=False)

    def record_request(self, latency_ms: float) -> None:
        with self._lock:
            self.request_count += 1
            self.total_latency_ms += latency_ms

    def increment(self, counter: str) -> None:
        with self._lock:
            current = getattr(self, counter, 0)
            setattr(self, counter, current + 1)

    @property
    def avg_latency_ms(self) -> float:
        if self.request_count == 0:
            return 0.0
        return round(self.total_latency_ms / self.request_count, 2)

    def to_dict(self) -> dict:
        return {
            "memories_inserted": self.memories_inserted,
            "memories_retrieved": self.memories_retrieved,
            "memories_deleted": self.memories_deleted,
            "searches_performed": self.searches_performed,
            "consolidations_performed": self.consolidations_performed,
            "request_count": self.request_count,
            "avg_latency_ms": self.avg_latency_ms,
        }


# Global singleton — one metrics instance per process
_metrics = Metrics()


def get_metrics() -> Metrics:
    return _metrics
