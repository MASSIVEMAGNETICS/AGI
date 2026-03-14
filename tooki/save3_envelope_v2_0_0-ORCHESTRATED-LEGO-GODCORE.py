# ==========================================================
# FILE: save3_envelope_v2_0_0-ORCHESTRATED-LEGO-GODCORE.py
# VERSION: v2.0.0-SAVE3-ENVELOPE-LEGO-GODCORE
# NAME: SAVE3 Envelope + Lego Orchestrator
# AUTHOR: Brandon "iambandobandz" Emery x Victor (Fractal Architect Mode)
# PURPOSE: A standalone, dependency-free envelope standard that lets modules
#          discover each other in a folder, negotiate compatibility, and
#          "snap together" (register + wire) like Legos.
# LICENSE: Proprietary - Massive Magnetics / Ethica AI / BHeard Network
# ==========================================================

from __future__ import annotations

import dataclasses
import hashlib
import hmac
import importlib.util
import inspect
import json
import os
import sys
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

# ------------------------------
# Orchestrated Instruction Block
# ------------------------------
# Every file that wants to be a "Lego module" should expose:
#     def module_spec() -> dict
#     (optional) def module_init(ctx: "LegoContext") -> None
#
# Drop two+ modules in the same folder, run:
#     python save3_envelope_v2_0_0-ORCHESTRATED-LEGO-GODCORE.py build --dir .
#
# The orchestrator will:
# 1) Discover specs
# 2) Verify envelopes + signatures (if configured)
# 3) Resolve dependencies
# 4) Call module_init(ctx) in dependency order

ORCHESTRATED_INSTRUCTION = {
    "role": "universal_module_envelope_and_autowire",
    "how_to_use": [
        "Put this file and your module .py files in one folder.",
        "Each module must define module_spec() returning a dict (SAVE3ModuleSpec fields).",
        "Optionally define module_init(ctx) to wire resources once deps are satisfied.",
        "Run: python save3_envelope_v2_0_0-ORCHESTRATED-LEGO-GODCORE.py build --dir <folder>",
        "Run: python save3_envelope_v2_0_0-ORCHESTRATED-LEGO-GODCORE.py demo to see a working example."
    ],
    "compatibility_contract": [
        "Specs declare provides/requires capabilities and version constraints.",
        "Resolver ensures no missing deps and detects cycles.",
        "Context offers a small service registry for modules to share objects."
    ],
}

# ------------------------------
# Errors
# ------------------------------

class Save3Error(Exception):
    pass

class SpecError(Save3Error):
    pass

class SignatureError(Save3Error):
    pass

class DependencyError(Save3Error):
    pass

# ------------------------------
# Utilities
# ------------------------------

def _sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def _now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")

def _safe_json_dumps(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def _coerce_semver(v: str) -> Tuple[int, int, int]:
    if not isinstance(v, str) or not v:
        raise SpecError(f"Invalid version: {v!r}")
    s = v.strip()
    if s.startswith("v"):
        s = s[1:]
    parts = s.split(".")
    if len(parts) != 3:
        raise SpecError(f"Version must be semver 'x.y.z' (got {v!r})")
    try:
        return (int(parts[0]), int(parts[1]), int(parts[2]))
    except Exception as e:
        raise SpecError(f"Version parts must be ints (got {v!r})") from e

def _semver_ge(a: str, b: str) -> bool:
    return _coerce_semver(a) >= _coerce_semver(b)

def _semver_lt(a: str, b: str) -> bool:
    return _coerce_semver(a) < _coerce_semver(b)

# ------------------------------
# SAVE3 Envelope + Module Spec
# ------------------------------

@dataclass
class SAVE3Envelope:
    schema: str = "SAVE3-ENVELOPE"
    schema_version: str = "v2.0.0"
    created_at: str = field(default_factory=_now_iso)

    module_id: str = ""
    module_name: str = ""
    module_version: str = ""
    author: str = "Brandon x Victor"
    license: str = "Proprietary"

    payload_type: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)

    payload_sha256: str = ""
    signature_alg: str = "none"      # "none" | "hmac-sha256"
    signature: str = ""              # hex digest

    def finalize(self, secret: Optional[bytes] = None) -> "SAVE3Envelope":
        canonical_payload = _safe_json_dumps(self.payload).encode("utf-8")
        self.payload_sha256 = _sha256_bytes(canonical_payload)
        if secret:
            self.signature_alg = "hmac-sha256"
            self.signature = hmac.new(secret, canonical_payload, hashlib.sha256).hexdigest()
        else:
            self.signature_alg = "none"
            self.signature = ""
        return self

    def verify(self, secret: Optional[bytes] = None) -> None:
        canonical_payload = _safe_json_dumps(self.payload).encode("utf-8")
        sha = _sha256_bytes(canonical_payload)
        if sha != self.payload_sha256:
            raise SignatureError("Payload SHA mismatch (envelope tampered or not finalized).")
        if self.signature_alg == "none":
            return
        if self.signature_alg != "hmac-sha256":
            raise SignatureError(f"Unsupported signature_alg: {self.signature_alg}")
        if not secret:
            raise SignatureError("Signature requires secret but none provided.")
        expect = hmac.new(secret, canonical_payload, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expect, self.signature):
            raise SignatureError("Bad signature.")

    def to_dict(self) -> Dict[str, Any]:
        return dataclasses.asdict(self)

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "SAVE3Envelope":
        try:
            return SAVE3Envelope(**d)
        except TypeError as e:
            raise SpecError(f"Bad envelope dict: {e}") from e

@dataclass
class SAVE3ModuleSpec:
    schema: str = "SAVE3-MODULE-SPEC"
    schema_version: str = "v2.0.0"

    module_id: str = ""
    name: str = ""
    version: str = ""
    entrypoint: str = ""
    provides: List[str] = field(default_factory=list)
    requires: List[str] = field(default_factory=list)
    requires_versions: Dict[str, Dict[str, str]] = field(default_factory=dict)

    description: str = ""
    tags: List[str] = field(default_factory=list)

    def validate(self) -> None:
        if not self.module_id or not isinstance(self.module_id, str):
            raise SpecError("module_id required")
        if not self.name:
            raise SpecError("name required")
        _coerce_semver(self.version)
        if not isinstance(self.provides, list) or not all(isinstance(x, str) and x for x in self.provides):
            raise SpecError("provides must be list[str]")
        if not isinstance(self.requires, list) or not all(isinstance(x, str) and x for x in self.requires):
            raise SpecError("requires must be list[str]")
        if not isinstance(self.requires_versions, dict):
            raise SpecError("requires_versions must be dict")
        for cap, c in self.requires_versions.items():
            if cap not in self.requires:
                raise SpecError(f"requires_versions specified for {cap!r} but cap not in requires")
            if not isinstance(c, dict):
                raise SpecError(f"constraint for {cap!r} must be dict")
            if "min" in c:
                _coerce_semver(c["min"])
            if "max_exclusive" in c:
                _coerce_semver(c["max_exclusive"])

# ------------------------------
# Lego Context (service registry)
# ------------------------------

class LegoContext:
    def __init__(self) -> None:
        self._services: Dict[str, Any] = {}
        self._specs_by_cap: Dict[str, SAVE3ModuleSpec] = {}

    def provide(self, capability: str, obj: Any, provider_spec: SAVE3ModuleSpec) -> None:
        if capability in self._services:
            raise DependencyError(f"Capability already provided: {capability}")
        self._services[capability] = obj
        self._specs_by_cap[capability] = provider_spec

    def require(self, capability: str) -> Any:
        if capability not in self._services:
            raise DependencyError(f"Missing required capability: {capability}")
        return self._services[capability]

    def provider_spec(self, capability: str) -> Optional[SAVE3ModuleSpec]:
        return self._specs_by_cap.get(capability)

# ------------------------------
# Discovery
# ------------------------------

def _load_module_from_path(py_path: str):
    name = f"lego_{_sha256_bytes(py_path.encode('utf-8'))[:12]}"
    spec = importlib.util.spec_from_file_location(name, py_path)
    if spec is None or spec.loader is None:
        raise Save3Error(f"Cannot import module at {py_path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)  # type: ignore[attr-defined]
    return mod

def discover_specs(folder: str) -> List[Tuple[str, SAVE3ModuleSpec, Optional[callable]]]:
    out: List[Tuple[str, SAVE3ModuleSpec, Optional[callable]]] = []
    for root, _, files in os.walk(folder):
        for fn in files:
            if not fn.endswith(".py"):
                continue
            path = os.path.join(root, fn)
            if os.path.abspath(path) == os.path.abspath(__file__):
                continue
            mod = _load_module_from_path(path)
            if not hasattr(mod, "module_spec"):
                continue
            spec_dict = mod.module_spec()
            if not isinstance(spec_dict, dict):
                raise SpecError(f"{path}: module_spec() must return dict")
            ms = SAVE3ModuleSpec(**spec_dict)
            ms.entrypoint = path
            ms.validate()
            init_fn = getattr(mod, "module_init", None)
            if init_fn is not None and not callable(init_fn):
                raise SpecError(f"{path}: module_init must be callable if present")
            out.append((path, ms, init_fn))
    return out

# ------------------------------
# Dependency resolution
# ------------------------------

def _build_provider_map(specs: List[SAVE3ModuleSpec]) -> Dict[str, SAVE3ModuleSpec]:
    providers: Dict[str, SAVE3ModuleSpec] = {}
    for s in specs:
        for cap in s.provides:
            if cap in providers:
                raise DependencyError(f"Duplicate provider for capability {cap!r}: {providers[cap].module_id} vs {s.module_id}")
            providers[cap] = s
    return providers

def _check_version_constraints(consumer: SAVE3ModuleSpec, cap: str, provider: SAVE3ModuleSpec) -> None:
    c = consumer.requires_versions.get(cap)
    if not c:
        return
    if "min" in c and not _semver_ge(provider.version, c["min"]):
        raise DependencyError(f"{consumer.module_id} requires {cap} >= {c['min']} but provider {provider.module_id} is {provider.version}")
    if "max_exclusive" in c and not _semver_lt(provider.version, c["max_exclusive"]):
        raise DependencyError(f"{consumer.module_id} requires {cap} < {c['max_exclusive']} but provider {provider.module_id} is {provider.version}")

def resolve_init_order(specs: List[SAVE3ModuleSpec]) -> List[SAVE3ModuleSpec]:
    providers = _build_provider_map(specs)
    deps: Dict[str, List[str]] = {s.module_id: [] for s in specs}
    rev: Dict[str, List[str]] = {s.module_id: [] for s in specs}
    by_id = {s.module_id: s for s in specs}

    for s in specs:
        for cap in s.requires:
            if cap not in providers:
                raise DependencyError(f"{s.module_id} requires missing capability {cap!r}")
            p = providers[cap]
            _check_version_constraints(s, cap, p)
            if p.module_id == s.module_id:
                continue
            deps[s.module_id].append(p.module_id)
            rev[p.module_id].append(s.module_id)

    indeg = {mid: len(set(deps[mid])) for mid in deps}
    queue = [mid for mid, d in indeg.items() if d == 0]
    order: List[str] = []

    while queue:
        mid = queue.pop(0)
        order.append(mid)
        for consumer_mid in rev[mid]:
            indeg[consumer_mid] -= 1
            if indeg[consumer_mid] == 0:
                queue.append(consumer_mid)

    if len(order) != len(specs):
        remaining = [mid for mid in indeg if indeg[mid] > 0]
        raise DependencyError(f"Dependency cycle detected among: {remaining}")

    return [by_id[mid] for mid in order]

# ------------------------------
# Envelope wrapping
# ------------------------------

def wrap_spec(spec: SAVE3ModuleSpec, secret: Optional[bytes] = None) -> SAVE3Envelope:
    env = SAVE3Envelope(
        module_id=spec.module_id,
        module_name=spec.name,
        module_version=spec.version,
        payload_type="module_spec",
        payload=dataclasses.asdict(spec),
    )
    env.finalize(secret=secret)
    return env

# ------------------------------
# Build / Snap Together
# ------------------------------

def lego_build(folder: str, secret: Optional[bytes] = None, verbose: bool = True) -> Dict[str, Any]:
    discovered = discover_specs(folder)
    specs = [s for _, s, _ in discovered]
    if not specs:
        raise Save3Error(f"No modules with module_spec() found under: {folder}")

    order = resolve_init_order(specs)
    init_by_id: Dict[str, Optional[callable]] = {s.module_id: None for s in specs}
    for _, s, init_fn in discovered:
        init_by_id[s.module_id] = init_fn
    providers = _build_provider_map(specs)

    envelopes: Dict[str, SAVE3Envelope] = {}
    for s in specs:
        env = wrap_spec(s, secret=secret)
        env.verify(secret=secret)
        envelopes[s.module_id] = env

    ctx = LegoContext()

    core_spec = SAVE3ModuleSpec(
        module_id="save3.core",
        name="SAVE3 Core",
        version="v2.0.0",
        provides=["save3.spec_registry"],
        requires=[],
        requires_versions={},
        description="Provides the envelope registry",
        tags=["save3"]
    )
    ctx.provide("save3.spec_registry", {"envelopes": {k: v.to_dict() for k, v in envelopes.items()}}, provider_spec=core_spec)

    report: List[Dict[str, Any]] = []
    for s in order:
        init_fn = init_by_id.get(s.module_id)
        if verbose:
            print(f"[LEGO] init {s.module_id} ({s.version}) requires={s.requires} provides={s.provides}")
        for cap in s.requires:
            if cap not in ctx._services:
                p = providers[cap]
                raise DependencyError(
                    f"Capability {cap!r} required by {s.module_id} but provider {p.module_id} did not publish it via ctx.provide()."
                )
        t0 = time.time()
        if init_fn:
            sig = inspect.signature(init_fn)
            if len(sig.parameters) != 1:
                raise SpecError(f"{s.module_id}: module_init(ctx) must take exactly 1 parameter")
            init_fn(ctx)
        dt = time.time() - t0
        report.append({"module_id": s.module_id, "version": s.version, "init_seconds": round(dt, 6)})

    return {
        "folder": os.path.abspath(folder),
        "modules_in_init_order": [dataclasses.asdict(s) for s in order],
        "report": report,
        "capabilities_published": sorted(list(ctx._services.keys())),
    }

# ------------------------------
# Demo modules (written to disk)
# ------------------------------

_DEMO_ALPHA = """def module_spec():
    return {
        "module_id": "demo.alpha",
        "name": "Demo Alpha (Provider)",
        "version": "v1.0.0",
        "provides": ["demo.greeting"],
        "requires": [],
        "requires_versions": {},
        "description": "Provides a greeting service",
        "tags": ["demo"]
    }

def module_init(ctx):
    # publish a greeting function
    ctx.provide("demo.greeting", lambda name: f"Hello, {name}.", provider_spec=module_spec_obj())

def module_spec_obj():
    # minimal provider spec object; orchestrator stores it for provenance
    return type("Spec", (), {
        "module_id": "demo.alpha",
        "name": "Demo Alpha (Provider)",
        "version": "v1.0.0",
        "provides": ["demo.greeting"],
        "requires": [],
        "requires_versions": {}
    })()
"""

_DEMO_BRAVO = """def module_spec():
    return {
        "module_id": "demo.bravo",
        "name": "Demo Bravo (Consumer)",
        "version": "v1.0.0",
        "provides": ["demo.message"],
        "requires": ["demo.greeting"],
        "requires_versions": {"demo.greeting": {"min": "v1.0.0", "max_exclusive": "v2.0.0"}},
        "description": "Consumes greeting and publishes message",
        "tags": ["demo"]
    }

def module_init(ctx):
    greet = ctx.require("demo.greeting")
    ctx.provide("demo.message", greet("Bando"), provider_spec=module_spec_obj())

def module_spec_obj():
    return type("Spec", (), {
        "module_id": "demo.bravo",
        "name": "Demo Bravo (Consumer)",
        "version": "v1.0.0",
        "provides": ["demo.message"],
        "requires": ["demo.greeting"],
        "requires_versions": {"demo.greeting": {"min": "v1.0.0", "max_exclusive": "v2.0.0"}}
    })()
"""

def _write_demo(folder: str) -> None:
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, "demo_alpha.py"), "w", encoding="utf-8") as f:
        f.write(_DEMO_ALPHA)
    with open(os.path.join(folder, "demo_bravo.py"), "w", encoding="utf-8") as f:
        f.write(_DEMO_BRAVO)

# ------------------------------
# CLI
# ------------------------------

def _parse_args(argv: List[str]) -> Dict[str, Any]:
    args = {"cmd": "help", "dir": ".", "secret": None, "verbose": True}
    if len(argv) < 2:
        return args
    args["cmd"] = argv[1]
    i = 2
    while i < len(argv):
        if argv[i] == "--dir":
            args["dir"] = argv[i + 1]
            i += 2
        elif argv[i] == "--secret":
            args["secret"] = argv[i + 1].encode("utf-8")
            i += 2
        elif argv[i] == "--quiet":
            args["verbose"] = False
            i += 1
        else:
            raise Save3Error(f"Unknown arg: {argv[i]}")
    return args

def main(argv: List[str]) -> int:
    try:
        a = _parse_args(argv)
        cmd = a["cmd"]
        if cmd in ("help", "-h", "--help"):
            print("Commands:")
            print("  build --dir <folder> [--secret <shared_secret>] [--quiet]")
            print("  demo  (writes demo modules into ./_save3_demo and builds them)")
            return 0
        if cmd == "demo":
            demo_dir = os.path.join(os.getcwd(), "_save3_demo")
            _write_demo(demo_dir)
            result = lego_build(demo_dir, secret=a["secret"], verbose=a["verbose"])
            print(json.dumps(result, indent=2))
            return 0
        if cmd == "build":
            result = lego_build(a["dir"], secret=a["secret"], verbose=a["verbose"])
            print(json.dumps(result, indent=2))
            return 0
        raise Save3Error(f"Unknown command: {cmd}")
    except Exception as e:
        print(f"[SAVE3][ERROR] {type(e).__name__}: {e}", file=sys.stderr)
        return 2

if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
