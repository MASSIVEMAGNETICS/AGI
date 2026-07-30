from __future__ import annotations

import math
import time
import uuid
from dataclasses import asdict, dataclass, field
from typing import Any


MEMORY_KINDS = frozenset(
    {
        "episodic",
        "semantic",
        "procedural",
        "reflection",
        "observation",
        "decision",
        "prediction",
        "outcome",
    }
)


@dataclass(frozen=True, slots=True)
class ModelConfig:
    vocab_size: int
    d_model: int = 96
    n_heads: int = 4
    n_layers: int = 2
    max_seq_len: int = 128
    dropout: float = 0.05
    pos_dim: int = 8
    eps: float = 1e-6
    content_distance_weight: float = 0.10
    causal: bool = True

    def validate(self) -> None:
        if self.vocab_size <= 1:
            raise ValueError("vocab_size must be greater than 1")
        if self.d_model <= 0:
            raise ValueError("d_model must be positive")
        if self.n_heads <= 0 or self.d_model % self.n_heads:
            raise ValueError("d_model must be divisible by positive n_heads")
        if self.n_layers <= 0:
            raise ValueError("n_layers must be positive")
        if self.max_seq_len < 2:
            raise ValueError("max_seq_len must be at least 2")
        if self.pos_dim < 3:
            raise ValueError("pos_dim must be at least 3")
        if not 0.0 <= self.dropout < 1.0:
            raise ValueError("dropout must be in [0, 1)")
        if self.eps <= 0.0:
            raise ValueError("eps must be positive")
        if self.content_distance_weight < 0.0:
            raise ValueError("content_distance_weight cannot be negative")


@dataclass(frozen=True, slots=True)
class AttentionTelemetry:
    mean_mass: float
    mean_force: float
    max_force: float
    mean_attention_entropy: float
    gravity_constants: tuple[float, ...]
    softening_constants: tuple[float, ...]

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class CognitionPulse:
    component: str
    correlation_id: str
    timestamp: float
    metrics: dict[str, Any]

    @classmethod
    def from_telemetry(
        cls,
        component: str,
        telemetry: dict[str, Any],
        correlation_id: str | None = None,
    ) -> "CognitionPulse":
        if not component.strip():
            raise ValueError("component cannot be empty")
        return cls(
            component=component,
            correlation_id=correlation_id or str(uuid.uuid4()),
            timestamp=time.time(),
            metrics=dict(telemetry),
        )

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class MemoryRecord:
    content: str
    source: str
    kind: str = "episodic"
    vector: list[float] | None = None
    embedding_model: str | None = None
    importance: float = 0.5
    confidence: float = 0.5
    source_quality: float = 0.5
    tags: list[str] = field(default_factory=list)
    relation_ids: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    consolidated: bool = False
    episode_id: str | None = None
    supersedes_id: str | None = None
    created_at: float = field(default_factory=time.time)
    deleted_at: float | None = None
    record_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    schema_version: int = 1

    def validate(self) -> None:
        if not self.content.strip():
            raise ValueError("content cannot be empty")
        if not self.source.strip():
            raise ValueError("source cannot be empty")
        if self.kind not in MEMORY_KINDS:
            raise ValueError(f"unsupported memory kind: {self.kind}")
        for name, value in (
            ("importance", self.importance),
            ("confidence", self.confidence),
            ("source_quality", self.source_quality),
        ):
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be in [0, 1]")
        if self.vector is not None:
            if not self.vector:
                raise ValueError("vector cannot be empty when supplied")
            if not all(math.isfinite(float(value)) for value in self.vector):
                raise ValueError("vector must contain only finite numbers")
        if self.created_at <= 0.0:
            raise ValueError("created_at must be positive")
        if self.schema_version != 1:
            raise ValueError("unsupported record schema_version")


@dataclass(frozen=True, slots=True)
class RetrievalResult:
    score: float
    similarity: float
    effective_mass: float
    recency: float
    source_quality: float
    record: MemoryRecord
    why_recalled: str

