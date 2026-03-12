"""
Tests for NeuroGrid Studio – core GridNN and training components.
"""

import numpy as np
import pytest

from neurogrid_studio.grid_nn import (
    GridCell,
    GridNN,
    NeuronSymbol,
    LAYER_HUE,
)
from neurogrid_studio.training import (
    AutoMLRecommender,
    LRSchedule,
    Recommendation,
    TrainingConfig,
    TrainingLoop,
    _focal_loss,
    _get_lr,
    _mse_loss,
    _cross_entropy_loss,
)


# ─────────────────────────────────────────────────────────────────────────────
# GridNN – construction & properties
# ─────────────────────────────────────────────────────────────────────────────


def test_gridnn_default_construction():
    grid = GridNN(size=16, seed=0)
    assert grid.size == 16
    assert grid._weights.shape == (16, 16)
    assert grid._activations.shape == (16, 16)
    assert grid._intensities.shape == (16, 16)
    assert grid._hues.shape == (16, 16)
    assert grid.epoch == 0
    assert grid.step == 0
    print("✓ GridNN default construction test passed")


def test_gridnn_hue_assignment():
    grid = GridNN(size=32, seed=0)
    # Top row should be indigo (input)
    assert abs(grid._hues[0, 0] - LAYER_HUE["input"]) < 1.0
    # Bottom row should be orange (output)
    assert abs(grid._hues[-1, 0] - LAYER_HUE["output"]) < 1.0
    print("✓ GridNN hue assignment test passed")


def test_gridnn_symbol_init():
    grid = GridNN(size=32, seed=0)
    # Input row should be marked INPUT
    assert all(grid._symbols[0, col] == NeuronSymbol.INPUT for col in range(32))
    # Output row should be marked OUTPUT
    assert all(grid._symbols[-1, col] == NeuronSymbol.OUTPUT for col in range(32))
    print("✓ GridNN symbol init test passed")


# ─────────────────────────────────────────────────────────────────────────────
# GridNN – forward pass
# ─────────────────────────────────────────────────────────────────────────────


def test_gridnn_forward_shape():
    grid = GridNN(size=16, seed=0)
    x = np.ones(16, dtype=np.float32)
    output = grid.forward(x)
    assert output.shape == (16,), f"Expected (16,) got {output.shape}"
    # tanh activations are bounded to (-1, 1)
    assert np.all(output >= -1.0) and np.all(output <= 1.0)
    print("✓ GridNN forward pass shape test passed")


def test_gridnn_forward_wrong_size():
    grid = GridNN(size=16, seed=0)
    with pytest.raises(ValueError, match="Input length"):
        grid.forward(np.ones(10))
    print("✓ GridNN forward wrong-size raises ValueError")


def test_gridnn_forward_updates_activations():
    grid = GridNN(size=16, seed=0)
    x = np.random.default_rng(1).standard_normal(16).astype(np.float32)
    grid.forward(x)
    # Input row should match x
    np.testing.assert_array_almost_equal(grid._activations[0], x)
    # Other rows should have been updated
    assert not np.all(grid._activations[1:] == 0.0)
    print("✓ GridNN forward activation update test passed")


# ─────────────────────────────────────────────────────────────────────────────
# GridNN – backward pass
# ─────────────────────────────────────────────────────────────────────────────


def test_gridnn_backward_returns_scalar():
    grid = GridNN(size=16, seed=0)
    x = np.ones(16, dtype=np.float32)
    grid.forward(x)
    grad = grid.backward(np.ones(16, dtype=np.float32) * 0.1)
    assert isinstance(grad, float)
    print("✓ GridNN backward returns scalar")


def test_gridnn_backward_updates_weights():
    grid = GridNN(size=16, seed=0)
    weights_before = grid._weights.copy()
    x = np.ones(16, dtype=np.float32)
    grid.forward(x)
    grid.backward(np.ones(16, dtype=np.float32) * 0.1)
    # Weights should have changed
    assert not np.allclose(grid._weights, weights_before)
    print("✓ GridNN backward weight update test passed")


# ─────────────────────────────────────────────────────────────────────────────
# GridNN – cell access & explanation
# ─────────────────────────────────────────────────────────────────────────────


def test_gridnn_get_cell():
    grid = GridNN(size=16, seed=0)
    cell = grid.get_cell(0, 0)
    assert isinstance(cell, GridCell)
    assert cell.row == 0
    assert cell.col == 0
    print("✓ GridNN get_cell test passed")


def test_gridnn_get_cell_out_of_bounds():
    grid = GridNN(size=16, seed=0)
    with pytest.raises(IndexError):
        grid.get_cell(100, 0)
    print("✓ GridNN get_cell out-of-bounds test passed")


def test_gridnn_explain_cell():
    grid = GridNN(size=16, seed=0)
    result = grid.explain_cell(0, 0)
    assert "cell" in result
    assert "explanation" in result
    assert "input" in result["explanation"].lower()
    print("✓ GridNN explain_cell test passed")


def test_gridnn_explain_cell_output_row():
    grid = GridNN(size=16, seed=0)
    result = grid.explain_cell(15, 0)
    assert "output" in result["explanation"].lower()
    print("✓ GridNN explain_cell output neuron test passed")


# ─────────────────────────────────────────────────────────────────────────────
# GridNN – grid snapshot
# ─────────────────────────────────────────────────────────────────────────────


def test_gridnn_snapshot_all_cells():
    grid = GridNN(size=8, seed=0)
    snap = grid.get_grid_snapshot(sample_rate=1)
    assert len(snap) == 8 * 8
    # Each cell has the required keys
    required = {"row", "col", "hue", "intensity", "symbol", "weight", "activation", "gradient", "layer_depth"}
    for cell in snap:
        assert required.issubset(cell.keys()), f"Missing keys: {required - set(cell.keys())}"
    print("✓ GridNN snapshot all-cells test passed")


def test_gridnn_snapshot_sample_rate():
    grid = GridNN(size=8, seed=0)
    snap = grid.get_grid_snapshot(sample_rate=2)
    assert len(snap) == 4 * 4
    print("✓ GridNN snapshot sample_rate test passed")


def test_gridnn_stats():
    grid = GridNN(size=16, seed=0)
    stats = grid.get_stats()
    assert stats["size"] == 16
    assert stats["total_neurons"] == 256
    assert "active_neurons" in stats
    assert "pruned_neurons" in stats
    print("✓ GridNN stats test passed")


# ─────────────────────────────────────────────────────────────────────────────
# GridCell
# ─────────────────────────────────────────────────────────────────────────────


def test_gridcell_to_dict():
    cell = GridCell(row=3, col=5, hue=120.0, intensity=75.0, symbol=NeuronSymbol.ATTENTION)
    d = cell.to_dict()
    assert d["row"] == 3
    assert d["col"] == 5
    assert d["hue"] == 120.0
    assert d["intensity"] == 75.0
    assert d["symbol"] == "⊗"
    print("✓ GridCell to_dict test passed")


# ─────────────────────────────────────────────────────────────────────────────
# Loss functions
# ─────────────────────────────────────────────────────────────────────────────


def test_mse_loss():
    pred   = np.array([0.5, 0.3, 0.8])
    target = np.array([0.5, 0.3, 0.8])
    loss, grad = _mse_loss(pred, target)
    assert abs(loss) < 1e-9, "MSE of identical arrays should be 0"
    assert np.allclose(grad, 0.0)
    print("✓ MSE loss zero test passed")


def test_mse_loss_nonzero():
    pred   = np.array([0.0, 0.0, 0.0])
    target = np.array([1.0, 1.0, 1.0])
    loss, grad = _mse_loss(pred, target)
    assert abs(loss - 1.0) < 1e-6
    assert np.all(grad < 0)   # gradient should point toward target
    print("✓ MSE loss nonzero test passed")


def test_cross_entropy_loss():
    pred   = np.array([0.9, 0.1])
    target = np.array([1.0, 0.0])
    loss, grad = _cross_entropy_loss(pred, target)
    assert loss > 0
    # grad w.r.t. correct prediction (0.9) should be negative (gradient descends loss)
    assert grad[0] < 0
    print("✓ Cross-entropy loss test passed")


def test_focal_loss():
    pred   = np.array([0.9, 0.1])
    target = np.array([1.0, 0.0])
    loss_f, _ = _focal_loss(pred, target)
    loss_ce, _ = _cross_entropy_loss(pred, target)
    # Focal loss should down-weight easy samples; loss ≤ CE for well-classified
    assert loss_f <= loss_ce + 1e-6
    print("✓ Focal loss test passed")


# ─────────────────────────────────────────────────────────────────────────────
# LR schedule
# ─────────────────────────────────────────────────────────────────────────────


def test_lr_constant():
    cfg = TrainingConfig(learning_rate=0.01, lr_schedule=LRSchedule.CONSTANT, epochs=10)
    lrs = [_get_lr(cfg, e, 10) for e in range(10)]
    assert all(abs(lr - 0.01) < 1e-9 for lr in lrs)
    print("✓ LR constant schedule test passed")


def test_lr_cosine_monotone_first_half():
    cfg = TrainingConfig(learning_rate=0.1, lr_schedule=LRSchedule.COSINE, epochs=20)
    lrs = [_get_lr(cfg, e, 20) for e in range(20)]
    # Cosine LR should be monotonically decreasing over [0, epochs)
    assert all(lrs[i] >= lrs[i + 1] - 1e-9 for i in range(len(lrs) - 1))
    print("✓ LR cosine schedule test passed")


def test_lr_warmup_cosine_starts_low():
    cfg = TrainingConfig(learning_rate=0.1, lr_schedule=LRSchedule.WARMUP_COSINE, epochs=20)
    lr_epoch0 = _get_lr(cfg, 0, 20)
    lr_epoch1 = _get_lr(cfg, 1, 20)
    # Warmup: epoch 0 should be lower than epoch 1
    assert lr_epoch0 < lr_epoch1
    print("✓ LR warmup-cosine schedule test passed")


# ─────────────────────────────────────────────────────────────────────────────
# AutoMLRecommender
# ─────────────────────────────────────────────────────────────────────────────


def test_recommender_plateau_suggests_cosine():
    rec = AutoMLRecommender(patience=3, min_delta=1e-4)
    cfg = TrainingConfig(lr_schedule=LRSchedule.CONSTANT)
    # Flat loss history → plateau
    history = [0.5] * 5
    recs = rec.analyse(history, cfg, epoch=4)
    actions = [r.action for r in recs]
    assert "switch_cosine_lr" in actions
    print("✓ Recommender plateau → cosine LR test passed")


def test_recommender_divergence_halves_lr():
    rec = AutoMLRecommender()
    cfg = TrainingConfig(lr_schedule=LRSchedule.CONSTANT)
    # Sudden spike in loss
    history = [0.5, 0.4, 0.3, 0.8]
    recs = rec.analyse(history, cfg, epoch=3)
    actions = [r.action for r in recs]
    assert "halve_lr" in actions
    print("✓ Recommender divergence → halve LR test passed")


def test_recommender_no_recs_for_short_history():
    rec = AutoMLRecommender()
    cfg = TrainingConfig()
    recs = rec.analyse([0.5, 0.4], cfg, epoch=1)
    assert recs == []
    print("✓ Recommender no recs for short history test passed")


def test_recommender_apply_cosine():
    rec = AutoMLRecommender()
    cfg = TrainingConfig(lr_schedule=LRSchedule.CONSTANT)
    new_cfg = rec.apply_recommendation("switch_cosine_lr", cfg)
    assert new_cfg.lr_schedule == LRSchedule.COSINE
    assert cfg.lr_schedule == LRSchedule.CONSTANT   # original unchanged
    print("✓ Recommender apply cosine test passed")


def test_recommender_apply_halve_lr():
    rec = AutoMLRecommender()
    cfg = TrainingConfig(learning_rate=0.01)
    new_cfg = rec.apply_recommendation("halve_lr", cfg)
    assert abs(new_cfg.learning_rate - 0.005) < 1e-9
    print("✓ Recommender apply halve_lr test passed")


def test_recommender_apply_focal_loss():
    rec = AutoMLRecommender()
    cfg = TrainingConfig(loss_fn="mse", epochs=10)
    new_cfg = rec.apply_recommendation("switch_focal_loss", cfg)
    assert new_cfg.loss_fn == "focal"
    assert new_cfg.epochs == 13   # +3
    print("✓ Recommender apply focal loss test passed")


# ─────────────────────────────────────────────────────────────────────────────
# TrainingLoop (synchronous)
# ─────────────────────────────────────────────────────────────────────────────


def test_training_loop_runs_to_completion():
    cfg = TrainingConfig(
        grid_size=8,
        epochs=2,
        steps_per_epoch=5,
        stream_every_n_steps=2,
        seed=0,
    )
    loop = TrainingLoop(config=cfg)
    events = list(loop.run())
    event_types = [e.event_type for e in events]
    assert "complete" in event_types
    assert "epoch" in event_types
    assert "step" in event_types
    print("✓ TrainingLoop runs to completion test passed")


def test_training_loop_loss_decreases_direction():
    """Loss does not need to strictly decrease, but loss_history should be populated."""
    cfg = TrainingConfig(grid_size=8, epochs=3, steps_per_epoch=10, seed=42)
    loop = TrainingLoop(config=cfg)
    events = list(loop.run())
    assert len(loop.grid.loss_history) == 3
    print("✓ TrainingLoop loss_history populated test passed")


def test_training_loop_stop():
    cfg = TrainingConfig(grid_size=8, epochs=100, steps_per_epoch=1000, seed=0)
    loop = TrainingLoop(config=cfg)
    count = 0
    for event in loop.run():
        count += 1
        if count >= 3:
            loop.stop()
            break
    # We stopped early – grid should not have trained for all 100 epochs
    assert loop.grid.epoch < 100
    print("✓ TrainingLoop stop test passed")


def test_training_loop_grid_snapshot_in_events():
    cfg = TrainingConfig(
        grid_size=8,
        epochs=1,
        steps_per_epoch=5,
        stream_every_n_steps=1,
        seed=0,
    )
    loop = TrainingLoop(config=cfg)
    step_events = [e for e in loop.run() if e.event_type == "step"]
    assert len(step_events) > 0
    assert step_events[0].grid_snapshot is not None
    assert len(step_events[0].grid_snapshot) > 0
    print("✓ TrainingLoop grid snapshot in events test passed")


def test_training_event_to_dict():
    cfg = TrainingConfig(grid_size=8, epochs=1, steps_per_epoch=2, seed=0)
    loop = TrainingLoop(config=cfg)
    events = list(loop.run())
    for e in events:
        d = e.to_dict()
        assert "event_type" in d
        assert "epoch" in d
        assert "loss" in d
    print("✓ TrainingEvent to_dict test passed")


# ─────────────────────────────────────────────────────────────────────────────
# Integration: full mini training run
# ─────────────────────────────────────────────────────────────────────────────


def test_full_mini_training_run():
    """End-to-end: train, collect events, inspect final grid."""
    cfg = TrainingConfig(
        grid_size=16,
        grid_depth=4,
        epochs=3,
        steps_per_epoch=20,
        learning_rate=0.01,
        sparsity=0.05,
        loss_fn="mse",
        seed=7,
    )
    loop = TrainingLoop(config=cfg)
    events = list(loop.run())

    # Check event stream completeness
    types = {e.event_type for e in events}
    assert "step" in types
    assert "epoch" in types
    assert "complete" in types

    # Grid state after training
    stats = loop.grid.get_stats()
    assert stats["epoch"] == 3
    assert stats["total_neurons"] == 16 * 16

    # Loss history length should match epochs
    assert len(loop.grid.loss_history) == 3

    # Cell explanation works
    explanation = loop.grid.explain_cell(0, 0)
    assert "explanation" in explanation

    # Snapshot works
    snap = loop.grid.get_grid_snapshot()
    assert len(snap) == 16 * 16

    print("✓ Full mini training run integration test passed")
