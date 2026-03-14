# holon_meta_analysis_v3.py
# VERSION: v3.0.0-HOLONMETA-TRUST-HANDOVER
# Adds: Bayesian time-decayed TrustModelBeta + Multi-Agent Handover framework (ACK+RESULT)
# Backwards-compatible with holon framework v2 style (signature parsing, adapters, registry, bus)

from __future__ import annotations

import asyncio
import concurrent.futures
import hashlib
import json
import threading
import time
import traceback
import ast
import re
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple, Set

# -----------------------
# Minimal signature parsing (from v2)
# -----------------------
_SIG_RE = re.compile(
    r"^\s*(?P<fname>[A-Za-z_]\w*)\s*"
    r"\(\s*(?P<params>.*?)\s*\)\s*"
    r"->\s*(?P<ret>.+?)\s*$"
)


@dataclass(frozen=True)
class ParamSpec:
    name: str
    typ: str


@dataclass(frozen=True)
class SigSpec:
    func_name: str
    params: Tuple[ParamSpec, ...]
    returns: str

    def shape(self, ignore_func_name: bool = True) -> str:
        fn = "*" if ignore_func_name else self.func_name
        p = ",".join(ps.typ.strip() for ps in self.params)
        return f"{fn}({p})->{self.returns.strip()}"


def parse_signature(sig: str) -> SigSpec:
    m = _SIG_RE.match(sig)
    if not m:
        raise ValueError(f"Invalid signature: {sig!r}")
    fname = m.group("fname").strip()
    params_str = m.group("params").strip()
    ret = m.group("ret").strip()
    params: List[ParamSpec] = []
    if params_str:
        parts = [p.strip() for p in params_str.split(",") if p.strip()]
        for part in parts:
            if ":" in part:
                n, t = [x.strip() for x in part.split(":", 1)]
            else:
                n, t = "arg", part.strip()
            params.append(ParamSpec(n, t))
    return SigSpec(fname, tuple(params), ret)


# -----------------------
# Message Bus (async)
# -----------------------
class MessageBus:
    """Async in-process pub/sub bus used by handover manager."""
    def __init__(self):
        self._subs: Dict[str, List[Callable[[Any], Any]]] = {}
        self._lock = asyncio.Lock()

    async def publish(self, channel: str, message: Any):
        async with self._lock:
            subs = list(self._subs.get(channel, []))
        coros = []
        for cb in subs:
            try:
                result = cb(message)
                if asyncio.iscoroutine(result):
                    coros.append(result)
            except Exception:
                traceback.print_exc()
        if coros:
            await asyncio.gather(*coros, return_exceptions=True)

    async def subscribe(self, channel: str, callback: Callable[[Any], Any]):
        async with self._lock:
            self._subs.setdefault(channel, []).append(callback)

    async def unsubscribe(self, channel: str, callback: Callable[[Any], Any]):
        async with self._lock:
            if channel in self._subs:
                try:
                    self._subs[channel].remove(callback)
                except ValueError:
                    pass


# -----------------------
# DNA verifier / compile helper (lightweight guard)
# -----------------------
class DNAVerifier(ast.NodeVisitor):
    DISALLOWED_CALLS = {"eval", "exec", "open", "__import__", "compile", "input"}

    def __init__(self):
        self.found_process = False

    def visit_Import(self, node):  # type: ignore[override]
        raise ValueError("Imports are disallowed in DNA code.")

    def visit_ImportFrom(self, node):  # type: ignore[override]
        raise ValueError("Imports are disallowed in DNA code.")

    def visit_FunctionDef(self, node: ast.FunctionDef):  # type: ignore[override]
        if node.name != "process":
            raise ValueError("Only a function named 'process' is allowed in DNA code.")
        self.found_process = True
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):  # type: ignore[override]
        if isinstance(node.func, ast.Name) and node.func.id in self.DISALLOWED_CALLS:
            raise ValueError(f"Disallowed call in DNA code: {node.func.id}()")
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute):  # type: ignore[override]
        if node.attr.startswith("__") and node.attr != "__name__":
            raise ValueError("Dunder attribute access is disallowed in DNA code.")
        self.generic_visit(node)


def compile_dna_process(code: str, holon_name: str) -> Callable[[Any, Any], Any]:
    tree = ast.parse(code)
    verifier = DNAVerifier()
    verifier.visit(tree)
    if not verifier.found_process:
        raise ValueError("DNA code must define process(self, input_data).")
    safe_builtins = {
        "True": True, "False": False, "None": None,
        "len": len, "range": range, "min": min, "max": max, "sum": sum,
        "int": int, "float": float, "str": str, "dict": dict, "list": list,
        "json": json,
    }
    env_globals = {"__builtins__": safe_builtins}
    env_locals: Dict[str, Any] = {}
    code_obj = compile(tree, filename=f"<DNA:{holon_name}>", mode="exec")
    exec(code_obj, env_globals, env_locals)
    proc = env_locals.get("process")
    if not callable(proc):
        raise ValueError("DNA compiled but no callable 'process' found.")
    return proc


# -----------------------
# Capability & Trust Model
# -----------------------
@dataclass
class Capability:
    name: str
    signature: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def sig(self) -> SigSpec:
        return parse_signature(self.signature)


@dataclass
class TrustModelBeta:
    """Beta-distribution trust model with time-decay and optional latency weighting.

    alpha, beta are continuous (not integer counts) to allow decay multiplication.
    half_life_seconds: time it takes for prior alpha/beta mass to halve.
    """
    alpha: float = 1.0  # success pseudo-count
    beta: float = 1.0   # failure pseudo-count
    last_update_ts: float = field(default_factory=lambda: time.time())
    half_life_seconds: float = 24 * 3600  # default 24h half-life
    latency_scale_ms: float = 500.0  # latency scale for weighting (ms)
    history: List[Tuple[float, bool, int]] = field(default_factory=list)  # (ts, success, latency_ms)

    def _decay_factor(self, now: Optional[float] = None) -> float:
        now = now or time.time()
        dt = max(0.0, now - self.last_update_ts)
        # exponential decay with half-life
        return 0.5 ** (dt / max(1.0, self.half_life_seconds))

    def _apply_decay(self, now: Optional[float] = None):
        f = self._decay_factor(now)
        # multiply existing pseudo-count mass by decay factor
        self.alpha *= f
        self.beta *= f
        self.last_update_ts = now or time.time()

    def record_outcome(self, success: bool, latency_ms: int = 0):
        """Record success/failure with latency-based weighting and time-decay."""
        now = time.time()
        # decay prior mass before adding the new observation
        self._apply_decay(now)
        # latency weighting: faster successes count more, slower ones less
        # weight in (0, 1], we use an exponential decay on latency
        latency_weight = float(1.0 / (1.0 + (latency_ms / max(1.0, self.latency_scale_ms))))
        # final increment
        increment = latency_weight if latency_weight > 0 else 0.1
        if success:
            self.alpha += increment
        else:
            self.beta += increment
        self.history.append((now, success, latency_ms))
        # update timestamp
        self.last_update_ts = now

    def mean(self) -> float:
        denom = (self.alpha + self.beta)
        return (self.alpha / denom) if denom > 0 else 0.5

    def variance(self) -> float:
        a, b = self.alpha, self.beta
        denom = (a + b) ** 2 * (a + b + 1)
        return (a * b / denom) if denom > 0 else 0.0

    def effective_count(self) -> float:
        return self.alpha + self.beta

    def snapshot(self) -> Dict[str, Any]:
        return {
            "alpha": self.alpha,
            "beta": self.beta,
            "mean": self.mean(),
            "variance": self.variance(),
            "effective_count": self.effective_count(),
            "last_update_ts": self.last_update_ts,
            "history_len": len(self.history),
        }


@dataclass
class Contract:
    source: Capability
    target: Capability
    adapter: Callable[[Any], Any]
    trust_model: TrustModelBeta = field(default_factory=TrustModelBeta)
    reason: str = ""

    @property
    def trust_score(self) -> float:
        return self.trust_model.mean()

    def record_outcome(self, success: bool, latency_ms: int = 0):
        self.trust_model.record_outcome(success, latency_ms)


# -----------------------
# Holon + MetaHolon (executor)
# -----------------------
def _safe_call_process(func: Callable, holon: "Holon", input_data: Any):
    try:
        return func(holon, input_data)
    except Exception:
        traceback.print_exc()
        return {"error": "process_failed", "holon": holon.name}


class Holon:
    EXEC_TIMEOUT = 1.0
    _EXECUTOR = concurrent.futures.ThreadPoolExecutor(max_workers=8)

    def __init__(self, name: str, dna_code: str, capabilities: List[Capability]):
        self.name = name
        self.dna = type("DNA", (), {"code": dna_code})()
        # id includes caps fingerprint to avoid collisions
        caps_fp = "|".join(sorted([c.name + ":" + c.signature for c in capabilities]))
        self.id = hashlib.sha256((self.dna.code + "\n" + caps_fp).encode("utf-8")).hexdigest()
        self.capabilities = list(capabilities)
        self.contracts: List[Contract] = []
        self.message_bus: Optional[MessageBus] = None
        self.state: Dict[str, Any] = {}
        self._compiled_process: Optional[Callable[[Any, Any], Any]] = None

    def bind_bus(self, bus: MessageBus):
        self.message_bus = bus

    def _compile_dna(self) -> Optional[Callable]:
        if self._compiled_process is not None:
            return self._compiled_process
        try:
            self._compiled_process = compile_dna_process(self.dna.code, self.name)
            return self._compiled_process
        except Exception:
            traceback.print_exc()
            return None

    def process(self, input_data: Any) -> Any:
        func = self._compile_dna()
        if not func:
            return input_data
        fut = self._EXECUTOR.submit(_safe_call_process, func, self, input_data)
        try:
            return fut.result(timeout=self.EXEC_TIMEOUT)
        except concurrent.futures.TimeoutError:
            return {"error": "dna_execution_timeout", "holon": self.name}
        except Exception as e:
            return {"error": "dna_execution_error", "holon": self.name, "exception": repr(e)}

    def find_contracts_to(self, other: "Holon") -> List[Contract]:
        # return contracts originating from this holon targeting other's capabilities
        out = []
        for c in self.contracts:
            if c.target.name in [cap.name for cap in other.capabilities]:
                out.append(c)
        return out


class MetaHolon(Holon):
    def __init__(self, holons: List[Holon], capabilities: List[Capability], contracts: List[Contract]):
        name = "Merged_" + "_".join(h.name for h in holons)
        merged_dna = """
def process(self, input_data):
    outputs = {}
    for h in self.holons:
        outputs[h.name] = h.process(input_data)
    return outputs
""".strip()
        super().__init__(name, merged_dna, capabilities)
        self.holons = holons
        self.contracts = contracts

    def compare_capabilities(self) -> str:
        lines = ["Comparison Report:"]
        for idx, h in enumerate(self.holons):
            lines.append(f"- Holon {idx+1}: {h.name} (id={h.id[:8]})")
            for cap in h.capabilities:
                lines.append(f"    - CAP: {cap.name} | {cap.signature}")
        lines.append("")
        lines.append("Contracts and Trust:")
        if not self.contracts:
            lines.append("  (no contracts)")
        else:
            for ct in sorted(self.contracts, key=lambda x: -x.trust_score):
                snap = ct.trust_model.snapshot()
                lines.append(f"  - {ct.source.name} -> {ct.target.name} | trust={ct.trust_score:.3f} | reason={ct.reason}")
                lines.append(f"      alpha={snap['alpha']:.3f}, beta={snap['beta']:.3f}, count={snap['effective_count']:.3f}, last_update={time.ctime(snap['last_update_ts'])}")
        return "\n".join(lines)


# -----------------------
# Handover Envelope & Manager
# -----------------------
@dataclass
class HandoverEnvelope:
    envelope_id: str
    origin_holon_id: str
    destination_holon_id: str
    payload: Any
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=lambda: time.time())


class HandoverManager:
    """Performs an async trusted handover via MessageBus with ACK+RESULT phases.

    Usage:
      mgr = HandoverManager(bus, trust_threshold=0.7)
      result = await mgr.handover(contract, envelope)
    """
    def __init__(self, bus: MessageBus, trust_threshold: float = 0.7, ack_timeout: float = 2.0, result_timeout: float = 5.0):
        self.bus = bus
        self.trust_threshold = float(trust_threshold)
        self.ack_timeout = ack_timeout
        self.result_timeout = result_timeout

    async def handover(self, contract: Contract, envelope: HandoverEnvelope) -> Dict[str, Any]:
        # enforce trust threshold
        if contract.trust_score < self.trust_threshold:
            return {"error": "trust_threshold", "trust": contract.trust_score, "threshold": self.trust_threshold}

        dest_chan = f"handover:{contract.target.name}:{contract.target.signature}"
        ack_chan = f"handover_ack:{envelope.envelope_id}"
        result_chan = f"handover_result:{envelope.envelope_id}"

        ack_event = asyncio.Event()
        result_future = asyncio.get_event_loop().create_future()

        async def ack_handler(msg):
            # expected simple ack message e.g., {"envelope_id": id, "status": "ok"}
            if isinstance(msg, dict) and msg.get("envelope_id") == envelope.envelope_id:
                ack_event.set()

        async def result_handler(msg):
            if isinstance(msg, dict) and msg.get("envelope_id") == envelope.envelope_id:
                if not result_future.done():
                    result_future.set_result(msg)

        # subscribe
        await self.bus.subscribe(ack_chan, ack_handler)
        await self.bus.subscribe(result_chan, result_handler)

        # publish envelope
        await self.bus.publish(dest_chan, {
            "envelope": envelope,
            "ack_channel": ack_chan,
            "result_channel": result_chan,
        })

        try:
            # wait ACK
            await asyncio.wait_for(ack_event.wait(), timeout=self.ack_timeout)
        except asyncio.TimeoutError:
            await self.bus.unsubscribe(ack_chan, ack_handler)
            await self.bus.unsubscribe(result_chan, result_handler)
            return {"error": "ack_timeout"}

        try:
            result_msg = await asyncio.wait_for(result_future, timeout=self.result_timeout)
            # Expect result_msg to include success/latency info for trust update
            success = result_msg.get("success", True)
            latency_ms = int(result_msg.get("latency_ms", 0))
            # update contract trust based on outcome
            contract.record_outcome(success, latency_ms)
            await self.bus.unsubscribe(ack_chan, ack_handler)
            await self.bus.unsubscribe(result_chan, result_handler)
            return {"status": "ok", "result": result_msg.get("result"), "success": success, "latency_ms": latency_ms}
        except asyncio.TimeoutError:
            await self.bus.unsubscribe(ack_chan, ack_handler)
            await self.bus.unsubscribe(result_chan, result_handler)
            # penalize contract for timeout
            contract.record_outcome(False, int(self.result_timeout * 1000))
            return {"error": "result_timeout"}


# -----------------------
# Simple Registry (minimal)
# -----------------------
class HolonRegistry:
    def __init__(self):
        self._holons: Dict[str, Holon] = {}
        self._meta: List[MetaHolon] = []
        self.bus = MessageBus()
        self._assembled_pairs: Set[Tuple[str, str]] = set()
        self._lock = threading.Lock()

    def register(self, holon: Holon):
        holon.bind_bus(self.bus)
        self._holons[holon.id] = holon
        # no auto assemble here; let user assemble pairwise by calling handshake or assemble_all
        print(f"[registry] registered {holon.name} id={holon.id[:8]}")

    def handshake(self, a: Holon, b: Holon) -> MetaHolon:
        # naive adapter synthesis: pairwise capability match yields contracts (identity)
        contracts: List[Contract] = []
        for sa in a.capabilities:
            for tb in b.capabilities:
                # if names are similar, create a contract with heuristic adapter
                adapter = (lambda x: x)
                reason = "identity" if sa.signature == tb.signature else "heuristic"
                contracts.append(Contract(source=sa, target=tb, adapter=adapter, reason=reason))
        meta = MetaHolon([a, b], a.capabilities + b.capabilities, contracts)
        # register meta
        with self._lock:
            pair = tuple(sorted((a.id, b.id)))
            if pair not in self._assembled_pairs:
                self._assembled_pairs.add(pair)
                self._meta.append(meta)
        return meta

    def get_meta(self) -> List[MetaHolon]:
        return list(self._meta)


# -----------------------
# Demo & tests when run as main
# -----------------------
if __name__ == "__main__":
    # build registry and holons
    registry = HolonRegistry()

    victor_dna = """
def process(self, input_data):
    # toy work
    return f"Victor processed: {input_data}"
"""
    victor_caps = [
        Capability("quantum_fractal_cognition", "process(input: Any) -> Any"),
        Capability("multi_agent_swarm", "orchestrate(tasks: List) -> Results"),
    ]
    victor = Holon("Victor", victor_dna, victor_caps)
    registry.register(victor)

    grok_dna = """
def process(self, input_data):
    # toy work simulating some latency
    return f"Grok says: {input_data}"
"""
    grok_caps = [
        Capability("llm_reasoning", "query(input: str) -> str"),
        Capability("real_time_search", "search(query: str) -> Results"),
    ]
    grok = Holon("Grok", grok_dna, grok_caps)
    registry.register(grok)

    # handshake -> create MetaHolon with contracts
    meta = registry.handshake(victor, grok)
    print(meta.compare_capabilities())

    # pick a contract to use (first one)
    contract = meta.contracts[0]
    print(f"Initial contract trust: {contract.trust_score:.3f}")

    # Simulate recording outcomes to grow a trust profile
    for i in range(5):
        contract.record_outcome(True, latency_ms=100 + i * 20)
    for i in range(2):
        contract.record_outcome(False, latency_ms=800 + i * 50)
    print(f"After observations, trust: {contract.trust_score:.3f}")
    print("Trust snapshot:", contract.trust_model.snapshot())

    # Now demonstrate handover via HandoverManager and MessageBus
    async def handover_demo():
        bus = registry.bus
        mgr = HandoverManager(bus, trust_threshold=0.3, ack_timeout=1.0, result_timeout=2.0)

        # receiver (Grok) subscribes to its handover channel and follows the ACK+RESULT protocol
        dest_chan = f"handover:{contract.target.name}:{contract.target.signature}"

        async def grok_handover_handler(msg):
            # extract envelope + channels
            envelope = msg.get("envelope")
            ack_ch = msg.get("ack_channel")
            result_ch = msg.get("result_channel")
            # send ACK immediately
            await bus.publish(ack_ch, {"envelope_id": envelope.envelope_id, "status": "ack"})
            # process payload (simulate latency)
            start = time.time()
            # call the grok holon's process synchronously
            res = grok.process(envelope.payload.get("data"))
            latency_ms = int((time.time() - start) * 1000)
            # publish result
            await bus.publish(result_ch, {
                "envelope_id": envelope.envelope_id,
                "result": res,
                "success": True,
                "latency_ms": latency_ms
            })

        await bus.subscribe(dest_chan, grok_handover_handler)

        # create envelope from Victor -> Grok
        env = HandoverEnvelope(
            envelope_id="env-001",
            origin_holon_id=victor.id,
            destination_holon_id=grok.id,
            payload={"data": "Hello from Victor"},
            metadata={"reason": "demo"}
        )

        result = await mgr.handover(contract, env)
        print("Handover result:", result)
        # print updated trust
        print("Updated trust after handover:", contract.trust_score)
        await bus.unsubscribe(dest_chan, grok_handover_handler)

    asyncio.run(handover_demo())

    # print final comparison with introspected trust values
    print("\nFinal MetaHolon report:")
    print(meta.compare_capabilities())