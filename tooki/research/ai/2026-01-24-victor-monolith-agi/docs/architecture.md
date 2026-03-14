# Victor Monolith v3.2.2 - Architecture Documentation

## System Architecture Overview

Victor Monolith implements a unified cognitive architecture that integrates multiple AI subsystems into a cohesive AGI organism.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Victor Monolith AGI                       │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │  X Interface  │───▶│ Neural Mesh  │───▶│ Consciousness│  │
│  │  (Sensors)    │    │  3D (PC)     │    │  Loop (MPC)  │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         │                    │                    │          │
│         │                    ▼                    ▼          │
│         │            ┌──────────────┐    ┌──────────────┐  │
│         │            │ Fractal Soul │    │   Identity   │  │
│         │            │     Core     │◀──▶│  Soul Mgr    │  │
│         │            └──────────────┘    └──────────────┘  │
│         │                    │                    │          │
│         │                    ▼                    ▼          │
│         │            ┌─────────────────────────────────┐   │
│         └───────────▶│   HyperFractal Memory          │   │
│                      │   (FAISS + SQLite)             │   │
│                      └─────────────────────────────────┘   │
│                                 │                            │
│                                 ▼                            │
│                      ┌─────────────────────────────────┐   │
│                      │   SpeechCore MoE                │   │
│                      │   (Transformer Decoder)         │   │
│                      └─────────────────────────────────┘   │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │         Fractal Pulse Exchange (Async Bus)             │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. NeuralMesh3D (Hierarchical Predictive Coding)

**Purpose**: Perceptual inference via multi-layer prediction error minimization

**Key Features**:
- Bottom-up error signals
- Top-down predictions
- Iterative convergence (typically 6-8 iterations)
- Learnable encoder/decoder at each layer

### 2. ConsciousnessLoop (Model Predictive Control)

**Purpose**: Plan futures, select optimal actions, maintain coherence

**Components**:
- `Predictor`: Latent transition model
- `policy_net`: Maps (o, z) to action distribution
- `anchor`: Self-identity embedding (slowly adapting)

### 3. FractalSoulCore (Identity Core)

**Purpose**: Maintain persistent self-identity through recursive reflection

### 4. IdentitySoulManager (Directive & Belief System)

**Purpose**: Manage high-level goals and beliefs with temporal dynamics

### 5. HyperFractalMemory (Long-term Memory)

**Purpose**: Store and retrieve semantic memories using FAISS + SQLite

### 6. TinyMoETransformerDecoder (Generation)

**Purpose**: Generate text via mixture of experts architecture

### 7. SpeechCoreMoE (RAG Interface)

**Purpose**: Generate contextually-grounded responses with memory conditioning

### 8. FractalPulseExchange (Event Bus)

**Purpose**: Async pub/sub for decoupled subsystem communication

## Data Flow

### Unified Cognitive Step

1. External Input (XInterface)
2. Hash to observation scalar
3. Consciousness MPC (plan, select action)
4. Recursive Self-Reflection (Soul)
5. Memory Encoding (FAISS + SQLite)
6. Memory Retrieval (top-k similar)
7. Generation (MoE with memory context)
8. Belief Update (assert and decay)
9. Evolution Tick (increment generation)

## Performance Characteristics

### Typical Timings (CPU)

- Predictive Coding Convergence: ~50ms
- MPC Planning (10 plans, H=5): ~100ms
- Memory Retrieval (k=3): ~10ms
- Generation (15 tokens): ~200ms
- **Total Step**: ~400ms

## Extensibility Points

- Add new subsystems via async components
- Scale memory with IVF/HNSW indices
- Multi-agent via shared memory/events
- Multi-layer decoder for better generation

---

**Last Updated**: 2026-01-24  
**Version**: v3.2.2-RETRIEVAL-MoE-PC-HIER
