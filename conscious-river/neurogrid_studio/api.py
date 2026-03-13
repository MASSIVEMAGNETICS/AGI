"""
NeuroGrid Studio – FastAPI server with WebSocket streaming.

Endpoints
---------
GET  /                   → Serve the web UI (index.html)
GET  /static/{path}      → Static assets (JS / CSS)
GET  /api/health         → Health check
GET  /api/grid/stats     → Current grid statistics
GET  /api/grid/snapshot  → Full grid snapshot (JSON)
GET  /api/cell/{r}/{c}   → Explain a single cell
POST /api/train/start    → Start a training run (returns run_id)
POST /api/train/stop     → Stop the running training
POST /api/train/accept   → Accept a recommendation (action key)
WS   /ws/train           → Real-time training event stream
"""

from __future__ import annotations

import asyncio
import json
import os
import time
import uuid
from pathlib import Path
from typing import Dict, Optional

import numpy as np
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .grid_nn import GridNN
from .training import AutoMLRecommender, TrainingConfig, TrainingLoop

# Path to the bundled web UI
_WEB_DIR = Path(__file__).parent / "web"


# ---------------------------------------------------------------------------
# Request / response models (module-level for FastAPI introspection)
# ---------------------------------------------------------------------------


class TrainingStartRequest(BaseModel):
    grid_size: int = Field(default=64, ge=4, le=1024)
    depth: int = Field(default=8, ge=1, le=64)
    epochs: int = Field(default=10, ge=1, le=1000)
    steps_per_epoch: int = Field(default=100, ge=1, le=10000)
    learning_rate: float = Field(default=1e-3, gt=0)
    sparsity: float = Field(default=0.1, ge=0, le=1)
    loss_fn: str = Field(default="mse")
    seed: Optional[int] = Field(default=None)


class AcceptRecommendationRequest(BaseModel):
    action: str



def create_app() -> FastAPI:
    """Factory function – create and configure the FastAPI application."""

    app = FastAPI(
        title="NeuroGrid Studio API",
        description="Real-time synthetic neural network training platform",
        version="0.1.0",
    )

    # ------------------------------------------------------------------
    # Application state
    # ------------------------------------------------------------------

    state: Dict = {
        "grid": None,          # active GridNN instance
        "loop": None,          # active TrainingLoop
        "run_id": None,        # UUID of current run
        "task": None,          # asyncio.Task for background training
        "config": None,        # active TrainingConfig
        "recommender": AutoMLRecommender(),
    }

    # ------------------------------------------------------------------
    # Static files & web UI
    # ------------------------------------------------------------------

    static_dir = _WEB_DIR / "static"
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    @app.get("/", response_class=HTMLResponse, include_in_schema=False)
    async def serve_ui() -> HTMLResponse:
        index = _WEB_DIR / "index.html"
        if index.exists():
            return HTMLResponse(content=index.read_text(), status_code=200)
        return HTMLResponse(
            content="<h1>NeuroGrid Studio</h1><p>Web UI not found – start API only.</p>",
            status_code=200,
        )

    # ------------------------------------------------------------------
    # Health
    # ------------------------------------------------------------------

    @app.get("/api/health")
    async def health() -> dict:
        return {
            "status": "ok",
            "timestamp": time.time(),
            "grid_active": state["grid"] is not None,
            "training_active": state["task"] is not None and not state["task"].done(),
        }

    # ------------------------------------------------------------------
    # Grid endpoints
    # ------------------------------------------------------------------

    @app.get("/api/grid/stats")
    async def grid_stats() -> dict:
        if state["grid"] is None:
            raise HTTPException(status_code=404, detail="No grid initialised. Start a training run first.")
        return state["grid"].get_stats()

    @app.get("/api/grid/snapshot")
    async def grid_snapshot(sample_rate: int = 1) -> dict:
        if state["grid"] is None:
            raise HTTPException(status_code=404, detail="No grid initialised.")
        return {
            "run_id": state["run_id"],
            "cells": state["grid"].get_grid_snapshot(sample_rate=sample_rate),
        }

    @app.get("/api/cell/{row}/{col}")
    async def explain_cell(row: int, col: int) -> dict:
        if state["grid"] is None:
            raise HTTPException(status_code=404, detail="No grid initialised.")
        try:
            return state["grid"].explain_cell(row, col)
        except IndexError as exc:
            raise HTTPException(status_code=400, detail=str(exc))

    # ------------------------------------------------------------------
    # Training control
    # ------------------------------------------------------------------

    @app.post("/api/train/start")
    async def train_start(req: TrainingStartRequest) -> dict:
        # Stop any existing run
        if state["task"] and not state["task"].done():
            if state["loop"]:
                state["loop"].stop()
            state["task"].cancel()
            try:
                await state["task"]
            except (asyncio.CancelledError, Exception):
                pass

        run_id = str(uuid.uuid4())
        config = TrainingConfig(
            grid_size=req.grid_size,
            grid_depth=req.depth,
            epochs=req.epochs,
            steps_per_epoch=req.steps_per_epoch,
            learning_rate=req.learning_rate,
            sparsity=req.sparsity,
            loss_fn=req.loss_fn,
            seed=req.seed,
        )
        grid = GridNN(
            size=config.grid_size,
            depth=config.grid_depth,
            learning_rate=config.learning_rate,
            sparsity=config.sparsity,
            seed=config.seed,
        )
        loop = TrainingLoop(config=config, grid=grid)

        state.update(
            grid=grid,
            loop=loop,
            run_id=run_id,
            config=config,
        )

        # Background training task – results streamed via WebSocket
        async def _run_background() -> None:
            async for _ in loop.run_async():
                pass  # WebSocket clients pull from the loop directly

        state["task"] = asyncio.create_task(_run_background())

        return {"run_id": run_id, "status": "started", "config": config.__dict__}

    @app.post("/api/train/stop")
    async def train_stop() -> dict:
        if state["loop"]:
            state["loop"].stop()
        if state["task"] and not state["task"].done():
            state["task"].cancel()
        return {"status": "stopped"}

    @app.post("/api/train/accept")
    async def accept_recommendation(req: AcceptRecommendationRequest) -> dict:
        if state["config"] is None or state["loop"] is None:
            raise HTTPException(status_code=400, detail="No active training run.")
        new_cfg = state["recommender"].apply_recommendation(req.action, state["config"])
        state["config"] = new_cfg
        state["loop"].config = new_cfg
        if state["grid"]:
            state["grid"].learning_rate = new_cfg.learning_rate
        return {"status": "applied", "action": req.action, "new_config": new_cfg.__dict__}

    # ------------------------------------------------------------------
    # WebSocket streaming
    # ------------------------------------------------------------------

    @app.websocket("/ws/train")
    async def ws_train(websocket: WebSocket) -> None:
        """
        Real-time training event stream.

        The client optionally sends a JSON config to start/restart training:
          {"grid_size": 64, "epochs": 20, ...}
        Events are streamed back as JSON objects with event_type:
          "step" | "epoch" | "recommendation" | "complete" | "error"
        """
        await websocket.accept()
        try:
            # Wait for optional start config from client
            raw = await asyncio.wait_for(websocket.receive_text(), timeout=2.0)
            client_config = TrainingStartRequest(**json.loads(raw))
        except (asyncio.TimeoutError, Exception):
            client_config = TrainingStartRequest()

        config = TrainingConfig(
            grid_size=client_config.grid_size,
            grid_depth=client_config.depth,
            epochs=client_config.epochs,
            steps_per_epoch=client_config.steps_per_epoch,
            learning_rate=client_config.learning_rate,
            sparsity=client_config.sparsity,
            loss_fn=client_config.loss_fn,
            seed=client_config.seed,
        )
        grid = GridNN(
            size=config.grid_size,
            depth=config.grid_depth,
            learning_rate=config.learning_rate,
            sparsity=config.sparsity,
            seed=config.seed,
        )
        loop = TrainingLoop(config=config, grid=grid)
        state.update(grid=grid, loop=loop, config=config, run_id=str(uuid.uuid4()))

        try:
            async for event in loop.run_async():
                await websocket.send_json(event.to_dict())
                # Check for client stop message (non-blocking)
                try:
                    msg = await asyncio.wait_for(websocket.receive_text(), timeout=0.01)
                    if msg == "stop":
                        loop.stop()
                except asyncio.TimeoutError:
                    pass
        except WebSocketDisconnect:
            loop.stop()
        except Exception as exc:
            try:
                await websocket.send_json({"event_type": "error", "message": str(exc)})
            except Exception:
                pass
        finally:
            try:
                await websocket.close()
            except Exception:
                pass

    return app


# ---------------------------------------------------------------------------
# Entry point: python -m neurogrid_studio.api
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(create_app(), host="0.0.0.0", port=8000, log_level="info")
