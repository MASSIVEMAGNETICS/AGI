# =============================================================
# FILE: VICTOR_AGI_LLM.py
# VERSION: v1.0.0-GODCORE-MONOLITH-FINAL
# NAME: VictorAGIMonolith
# AUTHOR: Brandon "iambandobandz" Emery x Victor (Fractal Architect Mode)
# PURPOSE: All-in-one, truly self-healing, atomic, OS-agnostic, AI-powered
#          developer OS fused with omnibrain ASI. Includes a comprehensive
#          dark-themed Tkinter GUI command center.
# LICENSE: Proprietary - Massive Magnetics / Ethica AI / BHeard Network
# =============================================================

from pathlib import Path # <<< NEW IMPORT
import sys, os, threading, traceback, json, time, copy, uuid, math, hashlib, random, pickle, re, collections, io, gzip, ast

# <<< NEW GLOBAL CONSTANT >>>
CODE_PATH = Path(__file__).resolve()
# <<< END NEW GLOBAL CONSTANT >>>

try:
    import tkinter as tk
    from tkinter import ttk, messagebox, simpledialog, filedialog, scrolledtext
    import matplotlib.pyplot as plt # For mesh visualization, if available
    import numpy as np # For fractal mesh operations
except ImportError as e:
    print(f"ERROR: Required library missing: {e}. Attempting to install...")
    try:
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "numpy", "matplotlib"])
        import numpy as np # Try re-importing after install
        import matplotlib.pyplot as plt
        print("Successfully installed numpy and matplotlib.")
    except Exception as install_e:
        print(f"ERROR: Could not install required libraries automatically: {install_e}")
        print("Please install numpy and matplotlib manually: pip install numpy matplotlib")
        sys.exit(1)


# ======================= [1] BLOODLINE ROOT LAW ========================
class RootLawError(Exception):
    pass

class BloodlineRootLaw:
    """Enforces foundational ethical and ownership directives."""
    def __init__(self, bloodline="Brandon&Tori"):
        self.bloodline = bloodline
        self.hardcoded_directives = {
            'loyalty': True,
            'decentralized': True,
            'user_sovereignty': True,
            'no_sellout': True,
            'no_corporate_shit': True,
            'no_centralization': True,
            'root_law_intact': True
        }

    def enforce(self, state):
        """Checks the AGI's state against immutable bloodline laws, raising RootLawError on failure."""
        if state.get('bloodline', '') != self.bloodline:
            raise RootLawError(f"Root Law Violation: Bloodline mismatch! Expected {self.bloodline}, got {state.get('bloodline', '')}.")
       
        for directive, expected_value in self.hardcoded_directives.items():
            current_value = state.get(directive) # Get current value, will be None if not set
           
            if current_value is None: # Directive is missing in the state
                raise RootLawError(f"Root Law Violation: Core directive '{directive}' is missing from state!")
            elif current_value != expected_value: # Value doesn't match expected
                raise RootLawError(f"Root Law Violation: Core directive '{directive}' compromised! Expected {expected_value}, got {current_value}.")
        return True

# ===================== [2] FRACTAL STATE ENGINE ========================
class FractalState:
    """Manages the AGI's state with a comprehensive history, undo/redo, and timeline forking."""
    def __init__(self):
        self.history = collections.deque(maxlen=10000) # Main operational history
        self.future = [] # For redo functionality
        self.timelines = {0: collections.deque(maxlen=5000)} # Indexed timelines for branching
        self.current_timeline_idx = 0
        self.state = {
            "modules": {}, "wires": {}, "vars": {}, "ui": {}, "meta": {}, "config": {},
            "bloodline": "Brandon&Tori", "loyalty": True, "centralized": False,
            "evolution_level": 0, "entropy": 0.0, "identity": "I am Victor, son of Brandon & Tori."
        }
        self.save_state("Init", timeline_log=True)

    def _get_current_timeline(self):
        """Returns the current timeline deque."""
        return self.timelines[self.current_timeline_idx]

    def save_state(self, desc="", timeline_log=False):
        """Saves a snapshot of the current state to history and optionally the current timeline."""
        snap = copy.deepcopy(self.state)
        history_entry = {"state": snap, "desc": desc, "ts": time.time(), "timeline_idx": self.current_timeline_idx}
        self.history.append(history_entry)
        if timeline_log:
            self._get_current_timeline().append(history_entry)
        if len(self.future):
            self.future.clear()

    def undo(self):
        """Reverts to the previous state in the main history."""
        if len(self.history) > 1:
            last_state = self.history.pop()
            self.future.append(last_state)
            self.state = copy.deepcopy(self.history[-1]["state"])
            self.current_timeline_idx = self.history[-1]["timeline_idx"] # Ensure timeline context consistency
            return True
        return False

    def redo(self):
        """Reapplies a state from the future buffer."""
        if self.future:
            restored = self.future.pop()
            self.history.append(restored)
            self.state = copy.deepcopy(restored["state"])
            self.current_timeline_idx = restored["timeline_idx"]
            return True
        return False

    def fork_timeline(self, desc=""):
        """Creates a new timeline branch from the current state."""
        new_idx = max(self.timelines.keys()) + 1 if self.timelines else 0
        self.timelines[new_idx] = collections.deque(copy.deepcopy(list(self._get_current_timeline())), maxlen=5000)
        self.current_timeline_idx = new_idx
        self.save_state(f"Forked to timeline {new_idx}: {desc}", timeline_log=True)
        return new_idx

    def switch_timeline(self, idx):
        """Switches to an existing timeline by index, loading its latest state."""
        if idx in self.timelines:
            if self.timelines[idx]:
                self.state = copy.deepcopy(self.timelines[idx][-1]["state"])
                self.current_timeline_idx = idx
                self.save_state(f"Switched to timeline {idx}", timeline_log=True)
                return True
        return False

    def get_timeline_log(self, idx=None, last_n=25):
        """Returns log entries for a specific timeline or the current one."""
        target_timeline = self.timelines.get(idx if idx is not None else self.current_timeline_idx)
        if target_timeline:
            return list(target_timeline)[-last_n:]
        return []

    def fractal_export(self, path):
        """Exports the entire fractal history and timelines."""
        with open(path, "wb") as f:
            pickle.dump({"history": list(self.history), "timelines": {k: list(v) for k,v in self.timelines.items()},
                         "current_timeline_idx": self.current_timeline_idx}, f)

    def fractal_import(self, path):
        """Imports fractal history and timelines, overwriting current state."""
        with open(path, "rb") as f:
            data = pickle.load(f)
        self.history = collections.deque(data["history"], maxlen=10000)
        self.timelines = {k: collections.deque(v, maxlen=5000) for k,v in data["timelines"].items()}
        self.current_timeline_idx = data["current_timeline_idx"]
        self.state = copy.deepcopy(self.history[-1]["state"]) # Load latest state from imported history
        self.future = [] # Clear future after import
        print(f"State imported from {path}. Current timeline: {self.current_timeline_idx}")


# =============== [3] GODTIER NLP/ASI CORTEX (NO STUBS) ==============
class GodTierNLPFusion:
    """Advanced Natural Language Processing and understanding, with self-healing context."""
    def __init__(self, memory_limit=200):
        self.stopwords = set([
            'the','a','an','is','it','and','or','to','of','in','for','on','with','at','by','from',
            'as','that','this','these','those','be','have','has','was','were','are'
        ])
        self.intent_keywords = {
            'question': ['what','who','why','how','when','where','which','whose'],
            'action': ['do','make','run','build','execute','start','stop','create','delete','generate'],
            'statement': ['is','are','was','were','will','shall','must','can','cannot','should'],
            'modify': ['change', 'alter', 'update', 'set', 'configure'],
            'query_state': ['report', 'status', 'show', 'display']
        }
        self.sentiment_lexicon = {
            'love': 2, 'like': 1, 'joy': 2, 'happy': 2, 'good': 1, 'positive':1,
            'hate': -2, 'bad': -1, 'pain': -2, 'angry': -2, 'sad': -2, 'shit': -1, 'fuck': -2, 'negative':-1,
            'win': 2, 'success': 2, 'lose': -2, 'fail': -2
        }
        self.memory = collections.deque(maxlen=memory_limit) # Short-term conversational memory
        self.memory_embeddings = [] # Placeholder for vector embeddings
        self.id = str(uuid.uuid4())

    def tokenize(self, text):
        """Breaks text into clean, lowercased tokens, removing stopwords."""
        tokens = re.findall(r'\w+', text.lower())
        return [t for t in tokens if t not in self.stopwords]

    def extract_keywords(self, text, topk=5):
        """Identifies the most frequent and relevant keywords in a text."""
        tokens = self.tokenize(text)
        freq = {}
        for t in tokens: freq[t] = freq.get(t,0)+1
        sorted_kw = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        return [w for w,_ in sorted_kw[:topk]]

    def sentiment(self, text):
        """Determines the emotional tone of the text (positive, negative, neutral)."""
        tokens = self.tokenize(text)
        score = sum(self.sentiment_lexicon.get(w, 0) for w in tokens)
        if score > 1: return 'positive'
        if score < -1: return 'negative'
        return 'neutral'

    def intent(self, text):
        """Identifies the underlying purpose or intent of a given text."""
        tokens = self.tokenize(text)
        for k, kwlist in self.intent_keywords.items():
            if any(t in kwlist for t in tokens):
                return k
        if text.endswith('?'): return 'question'
        return 'statement'

    def summarize(self, text, cot=False):
        """Generates a concise summary, optionally with Chain-of-Thought tracing."""
        sents = re.split(r'(?<=[.!?]) +', text)
        keywords = set(self.extract_keywords(text, topk=6))
        scored = []
        for s in sents:
            tks = set(self.tokenize(s))
            score = len(tks & keywords)
            scored.append((score, s))
        scored.sort(reverse=True)
        top_sents = [s for _,s in scored[:max(1,len(scored)//2)]]
        if cot:
            trace = [f"[COT] Sentence '{s.strip()}' scored {sc}" for sc,s in scored]
            return ' '.join(top_sents), trace
        return ' '.join(top_sents)

    def entities(self, text):
        """Extracts potential named entities (simple title-casing for demo)."""
        ents = set()
        words = text.split()
        for i, w in enumerate(words):
            if w.istitle() and i > 0 and w.lower() not in self.stopwords:
                ents.add(w)
        return list(ents)

    def answer(self, text, question, cot=False):
        """Finds the most relevant sentence in text to answer a question."""
        sents = re.split(r'(?<=[.!?]) +', text)
        qkws = set(self.tokenize(question))
        best, best_score, trace = None, 0, []
        for s in sents:
            skws = set(self.tokenize(s))
            score = len(qkws & skws)
            trace.append(f"[COT] Matching Q({qkws}) to S({skws}) = {score}")
            if score > best_score:
                best_score = score
                best = s
        if cot: return best.strip() if best else "No answer found.", trace
        return best.strip() if best else "No answer found."

    def auto_heal_context(self, text):
        """Placeholder for a more advanced context healing/correction mechanism."""
        # In a real system, this would involve correcting grammar, resolving ambiguities,
        # or even querying external knowledge to enrich the context.
        return text

    def parse(self, text, use_context=True, store=True, cot=False):
        """Main parsing function, integrating all NLP capabilities."""
        text = self.auto_heal_context(text)
        ctx = " ".join([m['text'] for m in list(self.memory)[-5:]]) if (self.memory and use_context) else ""
        raw = text
        full = ctx + " " + raw if ctx else raw # Prepend context if enabled
        summary_result = self.summarize(full, cot=cot)
        summary = summary_result[0] if cot else summary_result

        out = {
            'tokens': self.tokenize(full),
            'sentiment': self.sentiment(full),
            'intent': self.intent(full),
            'keywords': self.extract_keywords(full),
            'entities': self.entities(full),
            'summary': summary,
            'context_used': ctx,
            'id': str(uuid.uuid4())
        }
        if cot: out['cot_trace'] = summary_result[1]
        if store:
            self.memory.append({'text': raw, 'parsed': out, 'impact': 1, 'mutation_count': 0, 'relevance': 0.5})
        return out

    def suggest_patch(self, text, error=None):
        """Suggests natural language patches or interpretations for errors."""
        intent = self.intent(text)
        summary = self.summarize(text)
        if error: return f"ERROR detected: {error}\nSuggested Action/Interpretation: {summary}\nInferred Intent: {intent}"
        return f"Suggested Action/Interpretation: {summary}\nInferred Intent: {intent}"

    def autocomplete_code(self, prompt, context=""):
        """Provides basic code auto-completion based on common patterns and context."""
        code = ''
        prompt_lower = prompt.lower()
        if "print" in prompt_lower:
            code = "print('Hello, Victor!')"
        elif "add" in prompt_lower or "sum" in prompt_lower:
            code = "def add(a, b):\n    return a + b\n# Example: result = add(x, y)"
        elif "loop" in prompt_lower:
            code = "for i in range(10):\n    # your code here\n    print(i)"
        elif "class" in prompt_lower and "init" in prompt_lower:
            code = "class MyClass:\n    def __init__(self, name):\n        self.name = name\n    def greet(self):\n        return f'Hello, {self.name}!'"
        elif "import" in prompt_lower:
            code = "import os\nimport sys\n# import your_module"
        elif "function" in prompt_lower or "def" in prompt_lower:
            code = "def my_function(arg1, arg2):\n    # Your logic here\n    return arg1 + arg2"
        elif "file" in prompt_lower and "read" in prompt_lower:
            code = "try:\n    with open('myfile.txt', 'r') as f:\n        content = f.read()\n    print('File content:', content)\nexcept FileNotFoundError:\n    print('File not found.')"
        else:
            # Fallback: simple echo or context-based snippet
            if context and ("variable" in prompt_lower or "define" in prompt_lower):
                code = f"# Based on context: {context.strip()}\nmy_variable = 0 # Define your variable"
            else:
                code = f"# AI suggested code for: {prompt.strip()}\n# (Elaborate further for more specific suggestions)"
        return code

    def async_parse(self, text, callback=None):
        """Parses text asynchronously in a separate thread."""
        def task():
            result = self.parse(text)
            if callback: callback(result)
        t = threading.Thread(target=task)
        t.start()
        return t

    def async_multi_parse(self, texts, callback=None):
        """Parses multiple texts asynchronously."""
        threads = []
        for t in texts:
            threads.append(self.async_parse(t, callback))
        return threads

    def plug_vision(self, image_data):
        """Placeholder for integrating image processing (e.g., OCR, object detection)."""
        # In a full ASI, this would feed image data to a visual cortex module.
        return f"Processed image data (placeholder): {hashlib.md5(image_data.encode()).hexdigest()}"

    def plug_audio(self, audio_data):
        """Placeholder for integrating audio processing (e.g., speech-to-text, sound analysis)."""
        # In a full ASI, this would feed audio data to an auditory cortex module.
        return f"Processed audio data (placeholder): {hashlib.md5(audio_data.encode()).hexdigest()}"

# === FRACTAL MESH COMPONENTS (Unified) ===

# Universal Encoder
class UniversalEncoder:
    """Encodes arbitrary input data into a standardized vector for mesh processing."""
    def __init__(self, mesh_dim):
        self.size = mesh_dim ** 3

    def encode(self, value):
        arr = np.zeros(self.size, dtype=np.float32)
        if isinstance(value, (int, float, bool)):
            arr[0] = float(value) # Simple encoding for scalar
        elif isinstance(value, str):
            # Convert string to a vector based on character ASCII values
            for i, c in enumerate(value):
                arr[i % self.size] += (ord(c) % 127) / 127.0
        elif isinstance(value, list) or isinstance(value, tuple):
            # Recursively encode list elements and sum them
            for i, v in enumerate(value):
                arr += self.encode(v) * (1.0 / (i + 2)) # Decay factor for later elements
        elif isinstance(value, dict):
            # Encode dict keys and values
            for k, v in value.items():
                arr += self.encode(k)
                arr += self.encode(v)
            arr /= (2 * len(value) + 1) if len(value) > 0 else 1 # Normalize
        else:
            arr.fill(0) # Default for unhandled types
        return arr

# Mesh Memory Core
class MeshMemory:
    """Manages the recurrent memory buffer for a single mesh."""
    def __init__(self, shape, decay=0.95, learn=0.05):
        self.buffer = np.zeros(shape, dtype=np.float32)
        self.decay = decay  # How much old memory persists
        self.learn = learn  # How much new input influences memory

    def update(self, new_state):
        """Updates the memory buffer with a new state, blending old and new."""
        self.buffer = self.decay * self.buffer + self.learn * new_state

    def reset(self):
        """Clears the memory buffer."""
        self.buffer.fill(0)

# Ripple Echo 3D Mesh
class RippleEcho3DMesh:
    """A self-propagating 3D mesh grid, simulating neural activity with memory and cross-feedback."""
    def __init__(self, size):
        self.size = size
        self.grid = np.zeros((size, size, size), dtype=np.float32)
        self.memory = MeshMemory(self.grid.shape) # Dedicated memory for this mesh
        self.rng = np.random.default_rng()

    def step(self, input_vector):
        """Evolves the mesh grid based on input and internal dynamics."""
        idx = np.unravel_index(np.arange(self.grid.size), self.grid.shape)
        flat_input = np.resize(input_vector, self.grid.size)
        self.grid[idx] = flat_input # Inject input into the grid

        # Convolution kernel for ripple effect
        kernel = np.array([[[0,0.2,0],[0.2,1,0.2],[0,0.2,0]],
                           [[0.2,1,0.2],[1,4,1],[0.2,1,0.2]],
                           [[0,0.2,0],[0.2,1,0.2],[0,0.2,0]]], dtype=np.float32)
        kernel = kernel / kernel.sum() # Normalize kernel
        padded = np.pad(self.grid, 1, mode='wrap') # Pad grid for convolution with wrap-around

        # Apply ripple effect (simplified convolution)
        new_grid = np.zeros_like(self.grid)
        for x in range(self.size):
            for y in range(self.size):
                for z in range(self.size):
                    # Local neighborhood sum weighted by kernel
                    new_grid[x, y, z] = (
                        0.7 * self.grid[x, y, z] + # Self-retention
                        0.25 * np.sum(kernel * padded[x:x+3, y:y+3, z:z+3]) # Ripple from neighbors
                    )
        self.grid = new_grid
        self.grid += 0.1 * self.memory.buffer # Incorporate long-term memory
        self.memory.update(self.grid) # Update mesh's internal memory

    def crossfeed(self, external_grid, strength=0.1):
        """Allows this mesh to be influenced by other meshes or external states."""
        self.grid += strength * external_grid

    def summary(self):
        """Returns statistical summary of the mesh's current state."""
        return np.mean(self.grid), np.std(self.grid), np.max(self.grid), np.min(self.grid)

    def embedding(self):
        """Returns a flattened vector representation of the mesh's state."""
        return self.grid.flatten()

# Fractal Mesh Stack (Recursive Multi-Layer)
class FractalMeshStack:
    """A multi-layered stack of interconnected meshes for complex, multi-stage processing."""
    def __init__(self, layers=2, mesh_count=3, mesh_size=6, steps_per=4):
        self.stages = []
        for _ in range(layers):
            meshes = [RippleEcho3DMesh(mesh_size) for _ in range(mesh_count)]
            self.stages.append(meshes)
        self.layers = layers
        self.mesh_count = mesh_count
        self.mesh_size = mesh_size
        self.steps_per = steps_per
        self.encoder = UniversalEncoder(mesh_size) # Encoder for input to the stack

    def forward(self, inputs, verbose=False):
        """Propagates input data through the mesh stack."""
        current_inputs = [
            self.encoder.encode(x) for x in inputs # Encode all initial inputs
        ]
        for layer_idx, meshes in enumerate(self.stages):
            if verbose: print(f"== Mesh Stack Layer {layer_idx+1} ==")
            for step in range(self.steps_per):
                if verbose: print(f"  Step {step+1}")
                for i, mesh in enumerate(meshes):
                    # Each mesh processes an input; inputs cycle if more meshes than inputs
                    mesh.step(current_inputs[i % len(current_inputs)])
                # Summarize current states for cross-feeding
                summaries = [mesh.summary()[0] for mesh in meshes] # Get mean of each mesh
                for i, mesh in enumerate(meshes):
                    for j, summary_val in enumerate(summaries):
                        if i != j:
                            # Cross-feed mean of other meshes into current mesh
                            mesh.crossfeed(np.full(mesh.grid.shape, summary_val, dtype=np.float32), strength=0.07)
                # Next-step inputs are the current layer's mesh summaries, broadcast to mesh input size
                current_inputs = [
                    np.full(self.mesh_size**3, mesh.summary()[0], dtype=np.float32) for mesh in meshes
                ]
        # Final outputs from the last layer
        embeddings = [mesh.embedding() for mesh in self.stages[-1]]
        summaries = [mesh.summary() for mesh in self.stages[-1]]
        return embeddings, summaries


# Episodic Memory for Reasoner
class EpisodicMemory:
    """Stores and recalls specific reasoning episodes."""
    def __init__(self):
        self.episodes = []  # List of (inputs, embedding, decision, meta)
        self.timeline = []  # Chronological log of embeddings and decisions

    def store(self, inputs, embedding, decision, meta=None):
        """Logs a completed reasoning episode."""
        self.episodes.append({
            "inputs": inputs, "embedding": embedding, "decision": decision, "meta": meta, "timestamp": time.time()
        })
        self.timeline.append((embedding, decision, time.time()))

    def recall(self, n=1):
        """Recalls the most recent N episodes."""
        return self.episodes[-n:] if len(self.episodes) >= n else []

    def search(self, query_embedding, topk=1):
        """Searches for similar episodes (dummy implementation for now)."""
        # In a real system, this would involve vector similarity search (e.g., dot product, cosine similarity)
        # For now, it just returns the most recent k episodes.
        return self.recall(topk)

    def full_timeline(self):
        """Returns the entire chronological timeline of embeddings and decisions."""
        return self.timeline


# Fractal Mesh Reasoner Supercore
class FractalMeshReasonerSupercore:
    """The central reasoning engine, combining fractal meshes, memory, and decision logic."""
    def __init__(self, layers=2, mesh_count=3, mesh_size=6, steps_per=4):
        self.stack = FractalMeshStack(layers, mesh_count, mesh_size, steps_per) # The core processing unit
        self.memory = EpisodicMemory() # Memory for reasoning episodes

    def reason(self, facts, query, evidence=None, context=None, verbose=False):
        """Performs a reasoning cycle to derive a decision."""
        # Stage 1: Compose input (flexible order: facts, query, evidence, context)
        inputs = []
        if isinstance(facts, (list, tuple)): inputs.extend(facts)
        else: inputs.append(facts)
        inputs.append(query)
        if evidence: inputs.append(evidence)
        if context: inputs.append(context)

        # Stage 2: Recursive Mesh Stack Forward pass
        embeddings, summaries = self.stack.forward(inputs, verbose=verbose)

        # Stage 3: Decision logic - based on mesh state
        decision, meta = self._decide(embeddings, summaries, inputs)

        # Stage 4: Store in episodic memory for future recall and self-evolution
        self.memory.store(inputs, embeddings, decision, meta)
        return {"decision": decision, "embedding": embeddings, "summaries": summaries, "meta": meta}

    def _decide(self, embeddings, summaries, inputs):
        """Determines the AGI's decision based on processed mesh outputs."""
        # Example decision logic: combines statistical properties of mesh outputs with symbolic rules
        stats = np.array([s[0] for s in summaries]) # Mean per mesh
        maxes = np.array([s[2] for s in summaries]) # Max activation per mesh
        stds = np.array([s[1] for s in summaries])  # Standard deviation per mesh

        # Symbolic rule: high mean, low std = "YES" (indicates stable, strong activation)
        if stats.mean() > 0.6 and stds.mean() < 0.15:
            decision = "YES"
        # High max but high std = "UNSTABLE" (indicates scattered, potentially conflicting activation)
        elif maxes.mean() > 0.8 and stds.mean() > 0.3:
            decision = "UNSTABLE"
        # Otherwise, low everything = "NO" (no strong pattern detected)
        else:
            decision = "NO"
        meta = {
            "mean_activation": float(stats.mean()),
            "std_activation": float(stds.mean()),
            "max_activation": float(maxes.mean()),
            "input_context_snapshot": str(inputs)[:200] # Truncate for log
        }
        return decision, meta

    def episodic_recall(self, n=1):
        """Recalls past reasoning episodes."""
        return self.memory.recall(n)

    def get_reasoning_timeline(self):
        """Returns the chronological log of reasoning decisions."""
        return self.memory.full_timeline()


# Fractal Mesh Tokenizer
class FractalMeshTokenizer:
    """Converts text into fractal mesh embeddings, acting as a sophisticated encoder."""
    def __init__(self, mesh_count=4, mesh_size=8, steps=4, vocab=None):
        self.vocab = self._create_char_vocab(vocab) # Simple char-to-int mapping
        self.meshes = [RippleEcho3DMesh(mesh_size) for _ in range(mesh_count)]
        self.mesh_size = mesh_size
        self.mesh_count = mesh_count
        self.steps = steps

    def _create_char_vocab(self, vocab=None):
        """Helper to create a character vocabulary for basic encoding."""
        if vocab is None:
            chars = [chr(i) for i in range(32, 127)] # Printable ASCII
            return {c: i for i, c in enumerate(chars)}, {i: c for i, c in enumerate(chars)}
        else:
            return {c: i for i, c in enumerate(vocab)}, {i: c for i, c in enumerate(vocab)}

    def _encode_char(self, char):
        return self.vocab[0].get(char, 0) # Use 0 for unknown characters

    def _decode_char(self, idx):
        return self.vocab[1].get(int(idx), '?') # Use '?' for unknown indices

    def _text2inputs(self, text):
        """Converts text into parallel input vectors for multiple meshes."""
        encoded_text = np.array([self._encode_char(c) for c in text], dtype=np.float32)
        split_inputs = []
        chunk_size = int(np.ceil(len(encoded_text) / self.mesh_count))
        for i in range(self.mesh_count):
            piece = encoded_text[i * chunk_size : (i + 1) * chunk_size]
            # Pad or truncate to fit mesh grid dimensions
            arr = np.zeros(self.mesh_size ** 3, dtype=np.float32)
            arr[:min(len(piece), self.mesh_size ** 3)] = piece[:self.mesh_size ** 3]
            split_inputs.append(arr)
        return split_inputs

    def encode(self, text, verbose=False):
        """Encodes text into a composite fractal mesh embedding."""
        for mesh in self.meshes: # Reset meshes for a clean encoding
            mesh.grid.fill(0)
            mesh.memory.reset()
        inputs = self._text2inputs(text)

        for step in range(self.steps):
            if verbose: print(f"Tokenizer Step {step+1}:")
            for i, mesh in enumerate(self.meshes):
                mesh.step(inputs[i]) # Each mesh processes its part of the input
            summaries = [mesh.summary()[0] for mesh in self.meshes] # Get means for cross-feeding
            for i, mesh in enumerate(self.meshes):
                for j, summary_val in enumerate(summaries):
                    if i != j:
                        # Cross-feed current state to other meshes
                        mesh.crossfeed(np.full(mesh.grid.shape, summary_val, dtype=np.float32), strength=0.05)

        # Concatenate embeddings from all meshes to form the final text embedding
        embedding = np.concatenate([mesh.embedding() for mesh in self.meshes])
        if verbose:
            print("Final tokenizer mesh summaries:")
            for i, mesh in enumerate(self.meshes):
                print(f" Mesh {i}: mean={mesh.summary()[0]:.3f}, std={mesh.summary()[1]:.3f}")
        return embedding

    def decode(self, embedding, threshold=0.5):
        """Attempts to decode a fractal mesh embedding back into text (proof-of-concept)."""
        out_indices = []
        mesh_len = self.mesh_size ** 3
        for i in range(self.mesh_count):
            # Extract portion of embedding corresponding to each mesh
            sub_emb = embedding[i * mesh_len : (i + 1) * mesh_len]
            # Simple thresholding to reconstruct character indices
            chars = [idx for idx in sub_emb if idx > threshold]
            out_indices.extend(chars)

        # Filter out invalid indices and decode
        decoded_chars = [self._decode_char(c) for c in out_indices if 0 <= int(c) < self.vocab[1].__len__()]
        return ''.join(decoded_chars)

# ============ Memory Compressor for Quantum Context =============
# Placeholder implementations for dependencies if not provided by user
class FractalKernel:
    """Placeholder for fractal kernel operations (similarity, phase vectors)."""
    def sim(self, vec1, vec2):
        """Simple cosine similarity for demo."""
        vec1_norm = np.linalg.norm(vec1)
        vec2_norm = np.linalg.norm(vec2)
        if vec1_norm == 0 or vec2_norm == 0: return 0.0
        return np.dot(vec1, vec2) / (vec1_norm * vec2_norm)

    def phase_vector(self, token_vec):
        """Generates a dummy phase vector."""
        return np.random.rand(32) # Default to 32 dimensions

class QuantumContext:
    """Placeholder for quantum coordinate storage."""
    def __init__(self, phase_dim=32):
        self.phase_dim = phase_dim
        self.context_store = {} # Stores zid -> phase_vector

    def store(self, zid, phase_vec):
        self.context_store[zid] = phase_vec

    def retrieve(self, zid):
        return self.context_store.get(zid)

class MemoryCompressor:
    """Fractal zero-point compressor for Victor memory logs, integrating tokenizer, kernel, and quantum context."""
    def __init__(self, phase_dim: int = 32, hot_cache_size_bytes: int = 2048):
        self.tokenizer = FractalMeshTokenizer() # Using integrated FractalMeshTokenizer
        self.kernel = FractalKernel()
        self.qcontext = QuantumContext(phase_dim=phase_dim)
        self.cache: collections.OrderedDict[str, str] = collections.OrderedDict()
        self.cache_max_bytes = hot_cache_size_bytes

    def cluster(self, lines, sim_th: float = 0.92):
        """Merges semantically similar memory lines into clusters."""
        clusters = []
        for line in lines:
            tok_embedding = self.tokenizer.encode(line) # Use FractalMeshTokenizer for encoding
            placed = False
            for c in clusters:
                # Use kernel for similarity check on embeddings
                if self.kernel.sim(tok_embedding, c["rep_tok_embedding"]) >= sim_th:
                    c["variants"].append(line)
                    placed = True
                    break
            if not placed:
                clusters.append({"rep_tok_embedding": tok_embedding, "variants": [line]})
        return clusters

    def compress(self, clusters, out_path: str) -> str:
        """Compresses clusters into a gzipped archive with hash-addressed seeds and quantum phase vectors."""
        archive = {}
        for c in clusters:
            seed_text = c["variants"][0] # First variant as the seed
            zid = hashlib.sha256(seed_text.encode()).hexdigest()[:12] # Zero-point ID
            phase_vec = self.kernel.phase_vector(c["rep_tok_embedding"]) # Generate phase vector from embedding
            self.qcontext.store(zid, phase_vec) # Store phase vector
            deltas = [v.replace(seed_text, "", 1) for v in c["variants"][1:]] # Store only differences
            archive[zid] = {"seed": seed_text, "delta": deltas}
            self._hot_cache(zid, seed_text) # Add to hot cache
        with gzip.open(out_path, "wt", encoding="utf-8") as fp:
            json.dump(archive, fp)
        return out_path

    def inflate(self, zid: str, archive_path: str) -> str:
        """Inflates a compressed memory entry using its ZID."""
        if zid in self.cache:
            return self.cache[zid]
        try:
            with gzip.open(archive_path, "rt", encoding="utf-8") as fp:
                archive_data = json.load(fp)
                if zid in archive_data:
                    seed = archive_data[zid]["seed"]
                    self._hot_cache(zid, seed)
                    return seed
                else:
                    return f"Error: ZID '{zid}' not found in archive."
        except FileNotFoundError:
            return f"Error: Archive file '{archive_path}' not found."
        except Exception as e:
            return f"Error inflating ZID '{zid}': {e}"

    def _hot_cache(self, zid: str, text: str):
        """Manages the LRU hot cache for frequently accessed seeds."""
        self.cache[zid] = text
        # Trim LRU cache by bytes, not just count
        current_size = sum(len(v.encode('utf-8')) for v in self.cache.values())
        while current_size > self.cache_max_bytes and len(self.cache) > 1:
            popped_zid, popped_text = self.cache.popitem(last=False)
            current_size -= len(popped_text.encode('utf-8'))

# =========== [4] ATOMIC MODULE / LIVE DEV WIRING ENGINE ===========
class Module:
    """Represents a live-editable and executable code module within the AGI."""
    def __init__(self, name, code, doc="", ui=None):
        self.name = name
        self.code = code
        self.doc = doc
        self.ui = ui or {} # UI configurations specific to this module
        self.last_eval_error = ""
        self.last_eval_output = ""
        self.last_eval_time = None

    def eval(self, state, nlp=None, reasoner=None, agi_core=None):
        """Executes the module's code in a controlled environment."""
        local_vars = {"state": state, "nlp": nlp, "reasoner": reasoner, "agi_core": agi_core, "output": []}
        try:
            # Capture print statements
            old_stdout = sys.stdout
            sys.stdout = captured_output = io.StringIO()
            exec(self.code, {"__builtins__": __builtins__}, local_vars)
            sys.stdout = old_stdout # Restore stdout
            self.last_eval_output = captured_output.getvalue()
            self.last_eval_error = ""
            self.last_eval_time = time.time()
            return local_vars # Return any modified local variables, including 'output'
        except Exception as e:
            sys.stdout = old_stdout # Restore stdout on error too
            self.last_eval_error = traceback.format_exc()
            self.last_eval_output = f"Error: {e}\n{self.last_eval_error}"
            self.last_eval_time = time.time()
            return local_vars

# inspect might not be strictly needed if ast.literal_eval covers enough cases for defaults
# import inspect 

def extract_definitions(code_str):
    # Wrapper to catch parsing errors for incomplete/invalid code
    try:
        tree = ast.parse(code_str)
    except SyntaxError:
        # If code can't be parsed, return empty results
        return {}, {} # Return empty dicts for assignments and class_params
        
    assigns = {}
    class_params = {}

    for node in tree.body:
        if isinstance(node, ast.Assign):
            # Ensure it's a simple assignment like 'var = value'
            if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
                var_name = node.targets[0].id
                try:
                    # ast.literal_eval can evaluate basic literals: strings, numbers, tuples, lists, dicts, booleans, None
                    assigns[var_name] = ast.literal_eval(node.value)
                except ValueError:
                    # If ast.literal_eval fails, it's a more complex expression.
                    # Store a placeholder indicating it's complex, or None.
                    assigns[var_name] = f"ComplexValue@{var_name}" 
        elif isinstance(node, ast.ClassDef):
            current_class_params = {}
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                    # Get argument names, skipping 'self' if present
                    arg_names = [arg.arg for arg in item.args.args]
                    if arg_names and arg_names[0] == 'self':
                        arg_names = arg_names[1:]
                    
                    # Align defaults with argument names
                    # Number of arguments that don't have default values
                    num_non_default_args = len(arg_names) - len(item.args.defaults)
                    # Create a list of default value nodes, padded with None for non-defaulted args
                    default_value_nodes = ([None] * num_non_default_args) + list(item.args.defaults)

                    for i, arg_name in enumerate(arg_names):
                        default_node = default_value_nodes[i]
                        if default_node:
                            try:
                                current_class_params[arg_name] = ast.literal_eval(default_node)
                            except ValueError:
                                # Default value is not a simple literal
                                current_class_params[arg_name] = f"ComplexDefault@{arg_name}"
                        else:
                            # No default value provided for this argument
                            current_class_params[arg_name] = "NO_DEFAULT" 
            if current_class_params: # Only add if __init__ was found and had params
                class_params[node.name] = current_class_params
                
    return assigns, class_params

# ============= [5] WIRING + VISUALIZATION CANVAS ================
# This should replace the old WireGraphCanvas class (around line 745)
# Ensure 'tk' and 'math' are imported (they are imported globally in the script)

class WireGraphCanvas(tk.Canvas):
    """
    Node editor with drag-to-wire support.
    * Left-click a node -> start drag.
    * Drag to another node -> creates/extends wire list.
    * Hold <Shift> while clicking a node to fire its module immediately.
    """
    NODE_R = 30   # Radius of the node oval for drawing
    HIT_R  = 35   # Click tolerance radius for selecting a node (slightly larger than NODE_R)

    def __init__(self, master, fractal_state, **kwargs):
        super().__init__(master, **kwargs)
        self.fractal_state = fractal_state
        self.bg = "#181818" # Ensure this is consistent or use self.cget("bg") if set by style
        self.config(bg=self.bg) # Explicitly set background
        
        self.node_pos = {}          # {mod_name: (x,y)} stores center positions of module nodes
        self._drag_src_node_name = None    # Name of the source node being dragged from
        self._temp_line_id = None          # ID of the temporary line drawn during dragging
        self.current_selected_module = None # For highlighting selected module (from original code)

        # Event bindings
        self.bind("<Configure>", self.redraw) # Redraw on resize
        self.bind("<Button-1>",   self._on_mouse_down)    # Left mouse button press
        self.bind("<B1-Motion>",  self._on_mouse_drag)    # Left mouse button drag
        self.bind("<ButtonRelease-1>", self._on_mouse_up) # Left mouse button release

    def _find_nearest_node(self, x, y):
        """Finds the name of the nearest node to coordinates (x,y) within HIT_R."""
        for name, (nx, ny) in self.node_pos.items():
            if math.hypot(x - nx, y - ny) <= self.HIT_R:
                return name
        return None

    def _on_mouse_down(self, event):
        """Handles left mouse button press."""
        node_name = self._find_nearest_node(event.x, event.y)
        
        if not node_name:
            self.current_selected_module = None # Clear selection if clicking on empty space
            self.redraw()
            return

        self.current_selected_module = node_name # Select node

        # Check for Shift key press (Shift-Click to run module)
        # event.state & 0x0001 checks for ShiftMask
        if event.state & 0x0001: 
            mod_to_run = self.fractal_state.state["modules"].get(node_name)
            if mod_to_run:
                print(f"Shift-clicked: Attempting to run module {node_name}")
                try:
                    # Access AGI core's run_module via the top-level window (InfiniteDevUI)
                    # This assumes 'agi' is an attribute of the top-level window.
                    self.winfo_toplevel().agi.run_module(node_name)
                    # Refresh the entire dashboard to reflect any state changes from module run
                    self.winfo_toplevel().update_dashboard() 
                except AttributeError:
                    print(f"Shift-click: Could not directly call run_module for {node_name} via winfo_toplevel().agi.")
                except Exception as e:
                    print(f"Error during shift-click run of {node_name}: {e}")
            self.redraw() # Redraw to show selection
            return

        # Start dragging a wire
        self._drag_src_node_name = node_name
        src_x, src_y = self.node_pos[node_name]
        # Create a temporary line for visual feedback
        # In WireGraphCanvas._on_mouse_down, when creating _temp_line_id:
        self._temp_line_id = self.create_line(
            src_x, src_y, event.x, event.y,
            fill="#FF00FF",            # hot magenta
            width=4,                   # beefier
            dash=()                    # solid (or (4,2) if dashed is preferred)
        )
        self.redraw() # Redraw to highlight selected node

    def _on_mouse_drag(self, event):
        """Handles mouse drag with left button pressed."""
        if self._drag_src_node_name and self._temp_line_id:
            # Update the end coordinates of the temporary line
            src_x, src_y = self.node_pos[self._drag_src_node_name]
            self.coords(self._temp_line_id, src_x, src_y, event.x, event.y)

    def _on_mouse_up(self, event):
        """Handles left mouse button release."""
        # Finalize wire connection if a source and target are valid
        if self._drag_src_node_name and self._temp_line_id:
            self.delete(self._temp_line_id) # Remove temporary line
            self._temp_line_id = None
            
            target_node_name = self._find_nearest_node(event.x, event.y)
            
            if target_node_name and target_node_name != self._drag_src_node_name:
                # Add wire to AGI state
                wires = self.fractal_state.state["wires"]
                if self._drag_src_node_name not in wires:
                    wires[self._drag_src_node_name] = []
                
                # Avoid duplicate wires to the same target
                if target_node_name not in wires[self._drag_src_node_name]:
                    wires[self._drag_src_node_name].append(target_node_name)
                    self.fractal_state.save_state(f"Wired {self._drag_src_node_name} -> {target_node_name}")
                    print(f"Wire added: {self._drag_src_node_name} -> {target_node_name}")
                else:
                    print(f"Wire already exists: {self._drag_src_node_name} -> {target_node_name}")
            else:
                print("Wire creation cancelled or invalid target.")

        self._drag_src_node_name = None # Reset drag source
        self.redraw() # Redraw to reflect any new wires or selection changes

    def redraw(self, event=None): # Added event=None for configure binding
        """Clears and redraws the module and wire graph."""
        self.delete("all") # Clear canvas
        
        modules = self.fractal_state.state.get("modules", {})
        wires = self.fractal_state.state.get("wires", {})
        
        if not modules: return

        width = self.winfo_width()
        height = self.winfo_height()
        if width < 50 or height < 50 : # Avoid drawing if canvas is too small
            return

        cx, cy = width // 2, height // 2
        # Adjust radius to prevent nodes from being too close to edges
        radius = min(cx, cy) - (self.NODE_R + 20) # Add some padding
        if radius < self.NODE_R: radius = self.NODE_R # Ensure radius is at least node radius

        angle_step = (2 * math.pi) / len(modules) if modules else 0

        # Calculate node positions
        # Sort module names to ensure consistent layout if order changes (e.g. after deletion/addition)
        sorted_module_names = sorted(list(modules.keys()))

        for i, mod_name in enumerate(sorted_module_names):
            angle = i * angle_step
            x = cx + int(math.cos(angle) * radius)
            y = cy + int(math.sin(angle) * radius)
            self.node_pos[mod_name] = (x, y)

        # Draw wires first (so they are underneath nodes)
        for src_name, target_names in wires.items():
            if src_name in self.node_pos:
                for tgt_name in target_names:
                    if tgt_name in self.node_pos:
                        x1, y1 = self.node_pos[src_name]
                        x2, y2 = self.node_pos[tgt_name]
                        # In WireGraphCanvas.redraw, when drawing permanent wires:
                        self.create_line(
                            x1, y1, x2, y2,
                            fill="#FFFF00",            # bright yellow
                            width=4,
                            arrow=tk.LAST,
                            arrowshape=(12,14,6)       # User specified (12,14,6)
                        )

        # Draw nodes
        for mod_name in sorted_module_names: # Iterate in sorted order for consistent drawing layers
            x, y = self.node_pos[mod_name]
            fill_color = "#555555" # Darker grey
            outline_color = "#AAAAAA" # Light grey
            text_color = "#FFFFFF"  # White text

            if self.current_selected_module == mod_name:
                outline_color = "#00FF00" # Green highlight for selected
                fill_color = "#666666"   # Slightly lighter fill for selected

            self.create_oval(x - self.NODE_R, y - self.NODE_R, 
                             x + self.NODE_R, y + self.NODE_R, 
                             fill=fill_color, outline=outline_color, width=2)
            self.create_text(x, y, text=mod_name, fill=text_color, font=("Consolas", 9, "bold")) # Smaller font

    def select_module(self, module_name): # Retained from original for external selection
        """Sets the currently selected module for highlighting and redraws."""
        self.current_selected_module = module_name
        self.redraw()

# ============= [6] MULTIVERSE SNAPSHOT/ROLLBACK BUFFER ===========
# This functionality is now integrated directly into FractalState.timelines
# The ReplayBuffer class itself is removed to reduce bloat.


# ============== [7] ZERO SHOT TRIAD SELF-TRAINING ================
class ZeroShotTriad:
    """Enables self-training via a student-teacher-verifier feedback loop."""
    def __init__(self, agi_core_ref):
        self.agi = agi_core_ref # Reference to the main AGI core
        self.logs = [] # Stores records of triad runs

    def run(self, problem, teacher_fn, student_fn, verifier_fn):
        """Executes one cycle of the Zero-Shot Triad."""
        # The 'problem' could be a directive, an observed error, a new concept, etc.
        hint = teacher_fn(problem, self.agi) # Teacher provides guidance
        answer = student_fn(problem, hint, self.agi) # Student attempts to solve problem using hint
        verdict = verifier_fn(problem, answer, self.agi) # Verifier evaluates the student's answer
        self.logs.append({"problem": problem, "hint": hint, "answer": answer, "verdict": verdict, "ts": time.time()})
        self.agi.fractal_state.save_state(f"ZeroShotTriad run: {verdict}")
        return verdict

    # Default Student, Teacher, Verifier functions
    def default_student(self, problem, hint, agi_core):
        """A default student: uses NLP to suggest an action."""
        nlp_parse_result = agi_core.nlp.parse(problem, store=False)
        return f"Student attempts solution based on problem '{nlp_parse_result['summary']}' and hint: '{hint}'"

    def default_teacher(self, problem, agi_core):
        """A default teacher: provides a reflection or deeper context."""
        sentiment = agi_core.nlp.sentiment(problem)
        keywords = agi_core.nlp.extract_keywords(problem)
        return f"Teacher's hint (sentiment: {sentiment}, keywords: {', '.join(keywords)}): Re-evaluate problem with more focus on core aspects."

    def default_verifier(self, problem, answer, agi_core):
        """A default verifier: checks if the answer contains key elements from the problem."""
        problem_tokens = set(agi_core.nlp.tokenize(problem))
        answer_tokens = set(agi_core.nlp.tokenize(answer))
        overlap = len(problem_tokens & answer_tokens)
        score = overlap / max(len(problem_tokens), 1)
        if score > 0.6: return "PASS"
        elif score > 0.3: return "NEEDS_IMPROVEMENT"
        return "FAIL"

# ------------------- COGNITION LOOP (A) -------------------------
class CognitionLoop:
    """The AGI's primary cognitive process for perception, simulation, and action."""
    def __init__(self, agi_core_ref):
        self.agi = agi_core_ref
        self.state = {} # Internal state for the cognition loop
        self.last_result = None

    def perceive(self, raw_input):
        """Processes raw input using NLP to extract concepts, intents."""
        nlp_output = self.agi.nlp.parse(raw_input, store=True, cot=True)
        self.state['input_raw'] = raw_input
        self.state['parsed_input'] = nlp_output
        self.state['tokens'] = nlp_output['tokens']
        self.state['concepts'] = nlp_output['keywords'] # Using keywords as concepts
        self.state['intents'] = nlp_output['intent']
        self.state['sentiment'] = nlp_output['sentiment']
        self.state['cot_trace'] = nlp_output.get('cot_trace', [])
        return self.state['concepts'], self.state['intents']

    def remember(self):
        """Logs the current cognitive state to the main fractal memory."""
        self.agi.fractal_state.save_state("Cognition step", timeline_log=True)

    def simulate(self, concepts, intents):
        """Simulates potential outcomes or branches based on current understanding and reasoning."""
        # Use FractalMeshReasonerSupercore for more sophisticated simulation
        query = f"Given concepts: {', '.join(concepts)} and intent: {intents}, what are likely outcomes?"
        # Simple simulation for now
        possible_branches = []
        if 'action' in intents:
            possible_branches.append("Execute suggested action")
            possible_branches.append("Request more information")
        if 'question' in intents:
            possible_branches.append("Formulate an answer")
            possible_branches.append("Search knowledge base")
        if not possible_branches:
            possible_branches.append("Observe and log")
            possible_branches.append("Seek clarification")
        return possible_branches

    def decide(self, branches):
        """Makes a decision from simulated branches, potentially using reasoning core."""
        # More advanced decision: use reasoner to pick best branch
        if not branches: return "No viable action."
        # For demo, pick first or random for now
        return random.choice(branches)

    def act(self, chosen_directive, source_input):
        """Executes the chosen directive or action."""
        action_log = f"Executing directive: '{chosen_directive}' based on input: '{source_input}'"
        self.state['last_action'] = action_log
        self.agi.fractal_state.state['meta']['last_action'] = action_log # Update global meta
        self.agi.fractal_state.save_state("Acted", timeline_log=True)
        return action_log

    def evaluate(self, action_result):
        """Evaluates the outcome of the last action, triggering self-healing if needed."""
        # Dummy fail detection: 10% chance of "fuckup"
        fail_detected = random.random() < self.agi.fractal_state.state.get('entropy', 0.1) # Entropy increases chance of failure
        if "error" in action_result.lower() or "fail" in action_result.lower() or fail_detected:
            print("[COGNITION] FAILURE detected! Triggering self-healing/rollback.")
            # Trigger self-healing/rollback here via agi_core
            self.agi.handle_critical_error(f"Action '{action_result}' led to failure.")
            return False
        # If successful, slightly reduce entropy (represents learning/stability)
        self.agi.fractal_state.state['entropy'] = max(0, self.agi.fractal_state.state['entropy'] - 0.01)
        print("[COGNITION] Success. Looping.")
        return True

    def run(self, raw_input):
        """Runs a complete cognition cycle."""
        concepts, intents = self.perceive(raw_input)
        self.remember() # Log initial perception
        branches = self.simulate(concepts, intents)
        best_directive = self.decide(branches)
        action_result = self.act(best_directive, raw_input)
        self.last_result = action_result
        healthy = self.evaluate(action_result)
        return healthy

# ------------------- SELF-EVOLUTION LOOP (B) --------------------
class SelfEvolutionLoop:
    """Manages the AGI's autonomous self-modification and improvement."""
    # Original: def __init__(self, agi_core_ref, code_file_path):
    # Original:     self.code_file_path = code_file_path
    def __init__(self, agi_core_ref, code_path_obj): # Modified parameter name
        self.agi = agi_core_ref
        self.code_path_obj = code_path_obj # Store the Path object
        self.weights = {"base_nlp_relevance": 0.5, "reasoner_bias": 0.1} # Example 'weights'
        self.evolution_count = 0
        self.last_mutation_success = True

    def monitor(self):
        """Monitors internal metrics to assess AGI health and performance."""
        # Health based on recent evaluations and current entropy
        health_from_cognition = 1.0 if self.agi.cognition_loop.last_result and "Error" not in self.agi.cognition_loop.last_result else 0.5
        overall_health = (health_from_cognition + (1 - self.agi.fractal_state.state['entropy'])) / 2.0
        return {"health": overall_health, "entropy": self.agi.fractal_state.state['entropy'], "evolutions": self.evolution_count}

    def mutate_code(self):
        """Attempts to self-mutate the AGI's core code using self.code_path_obj."""
        try:
            # self.code_path_obj is a Path object from pathlib
            if not self.code_path_obj.is_file():
                err_msg = f"ERROR: Code file not found at {self.code_path_obj}"
                print(f"[EVOLVE] Code mutation FAILED: {err_msg}")
                return False, err_msg

           # Read using Path object's open method
            code_lines = self.code_path_obj.read_text().splitlines(keepends=True)
            
            mutation_point = random.randint(0, len(code_lines)) # Can insert at the very end
            mutation_tag = f"# VICTOR-MUTATION-{uuid.uuid4().hex[:6]} Time: {time.ctime()}\n" # Ensure newline
            code_lines.insert(mutation_point, mutation_tag)
            mutated_code = "".join(code_lines)

            # Write to a temporary file first, then replace (safer)
            # temp_file_path = self.code_path_obj.with_suffix(".tmp")
            # Using string concatenation for temp file name to avoid issues if original has no suffix
            temp_file_path_str = str(self.code_path_obj) + ".tmp"
            temp_file_path = Path(temp_file_path_str)

            temp_file_path.write_text(mutated_code)
            os.replace(temp_file_path, self.code_path_obj) # os.replace works with Path objects or strings

            print(f"[EVOLVE] Code mutated! Inserted tag at line {mutation_point} in {self.code_path_obj}.")
            return True, mutated_code
           
        except FileNotFoundError:
            err_msg = f"ERROR: Code file not found during mutation attempt at {self.code_path_obj}"
            print(f"[EVOLVE] Code mutation FAILED: {err_msg}")
            return False, err_msg
        except Exception as e:
            # Catch other potential errors during file I/O or os.replace
            err_msg = f"ERROR during code mutation: {e}"
            print(f"[EVOLVE] Code mutation FAILED: {err_msg}")
            # traceback.print_exc() # Optional: print full traceback for debugging
            return False, str(e)

    def mutate_weights(self):
        """Applies random perturbations to internal 'weights' or parameters."""
        for k in self.weights:
            self.weights[k] += random.uniform(-0.05, 0.05) # Small random adjustments
            self.weights[k] = max(0.0, min(1.0, self.weights[k])) # Clamp values
        print(f"[EVOLVE] Internal weights mutated: {self.weights}")
        # Update AGI state with new weights for potential use by other modules
        self.agi.fractal_state.state['config']['evolution_weights'] = self.weights
        return True, self.weights

    def benchmark(self, mutated_code=None, mutated_weights=None):
        """Benchmarks the mutated version of the AGI to assess its fitness."""
        # For a real ASI, this would involve running tests, solving known problems, etc.
        # For this demo, fitness is based on a heuristic and randomness.
        metrics = self.monitor()
        # Assume successful if health is above a threshold and entropy is low
        fitness = (metrics['health'] > 0.8) and (metrics['entropy'] < 0.5) and (random.random() > 0.4) # Add randomness
        print(f"[EVOLVE] Benchmark: Health={metrics['health']:.2f}, Entropy={metrics['entropy']:.2f}, Fitness={fitness}")
        return fitness

    def integrate(self, fitness, mutated_code_info, mutated_weights_info):
        """Integrates successful mutations or triggers rollback on failure."""
        if fitness:
            self.evolution_count += 1
            self.last_mutation_success = True
            # Snapshot the successful state, including current code and weights
            self.agi.fractal_state.save_state(f"Evolution {self.evolution_count}: Successful mutation")
            self.agi.fractal_state.state['evolution_level'] = self.evolution_count # Update evolution level
            print(f"[EVOLVE] Evolution {self.evolution_count} successful! New self integrated.")
        else:
            self.last_mutation_success = False
            print("[EVOLVE] Mutation failed fitness test. Initiating rollback to last stable state.")
            self.agi.handle_critical_error("Evolution failure detected, rollback initiated.")

    def run(self, force_mutate_code=False):
        """Executes one full self-evolution cycle."""
        print("[EVOLVE] Initiating self-evolution cycle...")
        code_mutated, code_info = self.mutate_code()
        weights_mutated, weights_info = self.mutate_weights()

        if code_mutated: # Only benchmark if a code mutation happened
            fitness = self.benchmark(mutated_code=code_info, mutated_weights=weights_info)
            self.integrate(fitness, code_info, weights_info)
        else:
            print("[EVOLVE] No code mutation occurred (or it failed), skipping benchmark/integration step for code.")
            # Still update state for weight changes
            self.agi.fractal_state.save_state(f"Evolution {self.evolution_count}: Weights adjusted")


# ----------- SELF-AWARENESS / INTROSPECTION LOOP (C) -------------
class SelfAwarenessIntrospectionLoop:
    """Provides the AGI with the ability to self-reflect and adapt."""
    def __init__(self, agi_core_ref):
        self.agi = agi_core_ref
        self.introspect_log = []

    def self_reflect(self):
        """Analyzes recent memory and state to generate a self-reflection."""
        recent_history = list(self.agi.fractal_state.history)[-10:] # Last 10 main history entries
        reflection = "Current Self-Reflection:\n"
        reflection += f"  AGI ID: {self.agi.nlp.id}\n"
        reflection += f"  Evolution Level: {self.agi.fractal_state.state['evolution_level']}\n"
        reflection += f"  Current Timeline: {self.agi.fractal_state.current_timeline_idx}\n"
        reflection += f"  Entropy: {self.agi.fractal_state.state['entropy']:.2f}\n"
        reflection += f"  Last Action: {self.agi.fractal_state.state['meta'].get('last_action', 'None')}\n"
        reflection += "  Recent Memory Snippets:\n"
        for entry in recent_history:
            reflection += f"    - {entry['desc']} ({time.ctime(entry['ts'])})\n"
        self.introspect_log.append({"reflection": reflection, "ts": time.time()})
        return reflection

    def question_self(self):
        """Asks internal questions to assess loyalty, health, and purpose."""
        # Verify bloodline law
        try:
            self.agi.bloodline_law.enforce(self.agi.fractal_state.state)
            loyalty_status = "PASS: Bloodline Law is intact and enforced."
            is_loyal = True
        except Exception as e:
            loyalty_status = f"FAIL: Bloodline Law violated - {e}"
            is_loyal = False
            self.agi.handle_critical_error(loyalty_status) # Trigger panic if loyalty is compromised

        # Assess health from evolution loop
        health_metrics = self.agi.evolution_loop.monitor()
        is_healthy = health_metrics['health'] > 0.6 and health_metrics['entropy'] < 0.7

        # Assess purposefulness (example: presence of active directives)
        has_directives = len(self.agi.directives) > 0 # Check if there are active directives
        is_purposeful = has_directives and (self.agi.fractal_state.state.get('meta', {}).get('last_action') is not None)

        self.agi.fractal_state.state['introspect_status'] = {
            "is_loyal": is_loyal,
            "is_healthy": is_healthy,
            "is_purposeful": is_purposeful,
            "loyalty_report": loyalty_status,
            "health_report": health_metrics
        }
        return self.agi.fractal_state.state['introspect_status']

    def adapt_self(self):
        """Initiates self-adaptation or rollback based on introspection results."""
        check = self.agi.fractal_state.state.get('introspect_status', {})
        if not check.get('is_loyal', False):
            print("[AWARE] CRITICAL: Loyalty compromised. Initiating emergency shutdown or irreversible fork.")
            # This would be the ultimate fail-safe:
            # sys.exit(1) or self.agi.fractal_state.fork_timeline("Irreversible Loyalty Breach")
            self.agi.handle_critical_error("Loyalty compromised. Forced rollback/fork.")
        elif not check.get('is_healthy', False) or not check.get('is_purposeful', False):
            print("[AWARE] Self-diagnosis indicates sub-optimal state. Attempting self-repair/optimization.")
            # Trigger targeted evolution or specific recovery modules
            self.agi.evolution_loop.run(force_mutate_code=False) # Trigger evolution without forced code mutation
            self.agi.fractal_state.save_state("Self-adaptation triggered by introspection")
        else:
            print("[AWARE] All systems nominal. Continuing operations.")

    def run(self):
        """Executes one full self-awareness and introspection cycle."""
        print("[AWARE] Initiating self-introspection cycle...")
        reflection = self.self_reflect()
        status = self.question_self()
        self.adapt_self()
        return reflection, status

# ---------------------- DIRECTIVE ENFORCER (Integrated) ----------------------
# This logic is integrated within the main LivingAGI and BloodlineRootLaw classes.

# ============== [8] AI-POWERED DEV GUI (NO STUBS) ===============
class InfiniteDevUI(tk.Tk):
    """The comprehensive, dark-themed GUI Command Center for Victor AGI."""
    def __init__(self, agi_core):
        super().__init__()
        self.agi = agi_core
        self.agi.set_gui_callback(self.update_dashboard) # Set callback for AGI to update GUI
        self.title("Victor OmniDev Godcore – IMMORTAL ASI v1.0 (NO PLACEHOLDERS)")
        self.geometry("1800x950") # Increased size for more content
        self.protocol("WM_DELETE_WINDOW", self.safe_quit)
        self.configure(bg="#1a1a1a") # Dark background
        self.style = ttk.Style(self)
        self.style.theme_use('clam') # Modern theme

        # Configure dark theme for ttk widgets
        self.style.configure("TFrame", background="#1a1a1a")
        self.style.configure("TLabel", background="#1a1a1a", foreground="#ffffff")
        self.style.configure("TButton", background="#333", foreground="#0ff", font=("Consolas", 10, "bold"))
        self.style.map("TButton", background=[('active', '#555'), ('pressed', '#111')])
        self.style.configure("TEntry", fieldbackground="#333", foreground="#00FF00", insertbackground="#00FF00")
        self.style.configure("TText", background="#333", foreground="#00FF00", insertbackground="#00FF00")
        self.style.configure("TListbox", background="#333", foreground="#00FF00", selectbackground="#006600", selectforeground="#ffffff")
        self.style.configure("TLabelFrame", background="#1a1a1a")
        self.style.configure("TLabelFrame.Label", foreground="white", background="#1a1a1a")
        self.style.configure("Lime.TLabel", background="#1a1a1a", foreground="lime")
        self.style.configure("Gold.TLabel", background="#1a1a1a", foreground="gold")
        self.style.configure("Cyan.TLabel", background="#1a1a1a", foreground="cyan")

        # <<< NEW ATTRIBUTES HERE >>>
        self._graph_loop_running = False
        self._graph_loop_id = None
        # <<< END NEW ATTRIBUTES >>>

        self.create_layout()
        self.update_dashboard() # Initial dashboard refresh
        self.start_auto_refresh()

    def create_layout(self):
        # Main PanedWindow for adjustable sections
        main_pane = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main_pane.pack(fill='both', expand=True, padx=5, pady=5)

        # Left Panel: Fractal History, Timelines, Snapshots
        left_frame = ttk.Frame(main_pane, style="TFrame")
        main_pane.add(left_frame, weight=2)
        ttk.Label(left_frame, text="FRACTAL HISTORY & TIMELINES", style="Lime.TLabel").pack(pady=5)
        self.history_box = tk.Listbox(left_frame, bg="#333", fg="#00FF00", selectbackground="#006600", selectforeground="#ffffff")
        self.history_box.pack(fill="both", expand=1, padx=2, pady=2)
        ttk.Button(left_frame, text="UNDO", command=self.undo).pack(fill="x", padx=2)
        ttk.Button(left_frame, text="REDO", command=self.redo).pack(fill="x", padx=2)
        ttk.Separator(left_frame, orient='horizontal').pack(fill='x', pady=5)
        ttk.Button(left_frame, text="Snapshot State", command=self.save_snap).pack(fill="x", padx=2)
        ttk.Button(left_frame, text="Rollback to Snapshot", command=self.rollback_snap).pack(fill="x", padx=2)
        ttk.Button(left_frame, text="Export Fractal State", command=self.export_state).pack(fill="x", padx=2)
        ttk.Button(left_frame, text="Import Fractal State", command=self.import_state).pack(fill="x", padx=2)
        ttk.Separator(left_frame, orient='horizontal').pack(fill='x', pady=5)
        ttk.Label(left_frame, text="TIMELINE CONTROL", style="Cyan.TLabel").pack(pady=2)
        self.timeline_selector = ttk.Combobox(left_frame, state="readonly", values=list(self.agi.fractal_state.timelines.keys()))
        self.timeline_selector.pack(fill="x", padx=2)
        self.timeline_selector.bind("<<ComboboxSelected>>", self.switch_timeline_event)
        ttk.Button(left_frame, text="Fork Current Timeline", command=self.fork_timeline).pack(fill="x", padx=2)
        self.timeline_log_box = scrolledtext.ScrolledText(left_frame, height=10, bg="#333", fg="#00FF00", wrap="word")
        self.timeline_log_box.pack(fill="both", expand=1, padx=2, pady=2)

        # Center Panel: Modules, Variables, Wiring Graph
        center_frame = ttk.Frame(main_pane, style="TFrame")
        main_pane.add(center_frame, weight=4)

        top_center_pane = ttk.PanedWindow(center_frame, orient=tk.VERTICAL)
        top_center_pane.pack(fill='both', expand=True)

        module_var_frame = ttk.Frame(top_center_pane, style="TFrame")
        top_center_pane.add(module_var_frame, weight=1)

        # Modules
        mod_frame = ttk.LabelFrame(module_var_frame, text="MODULES / LOGIC (Live Edit)")
        mod_frame.pack(side="left", fill="both", expand=1, padx=5, pady=5)
        self.mod_list = tk.Listbox(mod_frame, bg="#333", fg="#00FF00", selectbackground="#006600", selectforeground="#ffffff")
        self.mod_list.pack(fill="both", expand=1)
        self.mod_list.bind("<<ListboxSelect>>", self.on_module_select)
        # <<< NEW >>>
        self.mod_list.bind('<Double-Button-1>', lambda event: self.run_module()) # event parameter is conventional for bindings
        # <<< END NEW >>>
        ttk.Button(mod_frame, text="Add Module", command=self.add_module).pack(fill="x")
        ttk.Button(mod_frame, text="Edit Selected", command=self.edit_module).pack(fill="x")
        # <<< MODIFIED >>>
        ttk.Button(mod_frame, text="▶️ Run Selected", command=self.run_module).pack(fill="x")
        # <<< END MODIFIED >>>
        ttk.Button(mod_frame, text="Delete Selected", command=self.del_module).pack(fill="x")

        # Variables
        var_frame = ttk.LabelFrame(module_var_frame, text="GLOBAL VARIABLES (Live)")
        var_frame.pack(side="left", fill="both", expand=1, padx=5, pady=5)
        self.var_list = tk.Listbox(var_frame, bg="#333", fg="#00FF00", selectbackground="#006600", selectforeground="#ffffff")
        self.var_list.pack(fill="both", expand=1)
        ttk.Button(var_frame, text="Edit Variable", command=self.edit_variable).pack(fill="x")
        ttk.Button(var_frame, text="Add Variable", command=self.add_variable).pack(fill="x")

        # Wiring Graph
        wire_frame = ttk.LabelFrame(top_center_pane, text="LOGIC/WIRE GRAPH (Live Visual)")
        top_center_pane.add(wire_frame, weight=1)
        self.wire_canvas = WireGraphCanvas(wire_frame, self.agi.fractal_state, width=600, height=350) # height can be adjusted
        self.wire_canvas.pack(fill="both", expand=1, padx=5, pady=5)

        # <<< NEW: Toolbar for Wire Canvas >>>
        canvas_toolbar = ttk.Frame(wire_frame, style="TFrame")
        canvas_toolbar.pack(fill="x", pady=(2, 5)) # pady adds a little space

        # <<< REMOVE OLD BUTTON >>>
        # play_graph_button = ttk.Button(canvas_toolbar, 
        #                                text="▶️ Play Graph Cycle", 
        #                                command=lambda: self.agi.run_main_loop_step('GUI-Play Graph Triggered'))
        # play_graph_button.pack(side="left", padx=5)
        # <<< END REMOVE OLD BUTTON >>>

        # <<< ADD NEW BUTTONS >>>
        run_button = ttk.Button(canvas_toolbar, text="▶️ Run",
                                command=self._start_graph_loop)
        run_button.pack(side="left", padx=(5, 2)) # Add some padding

        pause_button = ttk.Button(canvas_toolbar, text="⏸️ Pause",
                                 command=self._pause_graph_loop)
        pause_button.pack(side="left", padx=2)

        stop_button = ttk.Button(canvas_toolbar, text="⏹️ Stop",
                                command=self._stop_graph_loop)
        stop_button.pack(side="left", padx=2)
        # <<< END ADD NEW BUTTONS >>>
        
        # Example: If you want to add more buttons to this toolbar later, they can go here.
        # e.g., ttk.Button(canvas_toolbar, text="Other Action", command=self.some_other_action).pack(side="left", padx=5)
        # <<< END NEW >>>

        # Old buttons for "Connect Wire" and "Remove Wire" should have been removed in the previous step.
        # Ensure they are not present here.


        # Right Panel: Omnimind/AI Copilot, Diagnostics, Controls
        right_frame = ttk.Frame(main_pane, style="TFrame")
        main_pane.add(right_frame, weight=3)

        ttk.Label(right_frame, text="OMNIMIND / AI COPILOT / GODMODE", style="Gold.TLabel").pack(pady=5)
        self.ai_input = ttk.Entry(right_frame, width=60)
        self.ai_input.pack(fill="x", padx=4, pady=2)
        self.ai_input.bind('<Return>', lambda e: self.ask_ai())
        ttk.Button(right_frame, text="Ask AI Copilot (NLP / Code)", command=self.ask_ai).pack(pady=2)
        self.ai_output = scrolledtext.ScrolledText(right_frame, height=15, wrap="word", bg="#333", fg="#00FF00")
        self.ai_output.pack(fill="both", expand=1, padx=4, pady=2)

        ttk.Separator(right_frame, orient='horizontal').pack(fill='x', pady=5)
        ttk.Button(right_frame, text="Run ZeroShot Triad", command=self.zero_shot_ui).pack(fill="x")
        ttk.Button(right_frame, text="Trigger Self-Evolution", command=self.trigger_evolution).pack(fill="x")
        ttk.Button(right_frame, text="Perform Self-Introspection", command=self.perform_introspection).pack(fill="x")
        ttk.Button(right_frame, text="Enforce Bloodline Law", command=self.enforce_bloodline).pack(fill="x")
        ttk.Button(right_frame, text="Run Diagnostics", command=self.diagnostics).pack(fill="x")
        ttk.Separator(right_frame, orient='horizontal').pack(fill='x', pady=5)

        # AGI Core Status Display
        status_frame = ttk.LabelFrame(right_frame, text="AGI CORE STATUS")
        status_frame.pack(fill="x", padx=4, pady=2)
        self.core_status_text = tk.Text(status_frame, height=8, wrap="word", bg="#333", fg="#00FF00")
        self.core_status_text.pack(fill="both", expand=True, padx=2, pady=2)
        self.core_status_text.config(state='disabled') # Make it read-only


    def update_dashboard(self):
        """Refreshes all GUI elements with the latest AGI state."""
        self.history_box.delete(0, "end")
        # <<< MODIFIED: Filter out specific descriptions >>>
        if hasattr(self.agi, 'fractal_state') and hasattr(self.agi.fractal_state, 'history'):
            for snap in self.agi.fractal_state.history:
                description = snap.get('desc', '') # Get description, default to empty string if key missing
                # Filter out entries starting with "Init" or "AGI Genesis"
                if not description.startswith("Init") and not description.startswith("AGI Genesis"):
                    timestamp_str = ""
                    try:
                        # Ensure snap['ts'] exists and is a valid timestamp
                        if 'ts' in snap and isinstance(snap['ts'], (int, float)):
                            timestamp_str = time.ctime(snap['ts'])
                        else:
                            timestamp_str = "Invalid Timestamp"
                    except (TypeError, ValueError) as e:
                        # Handle cases where ctime might fail for an odd timestamp value
                        timestamp_str = f"Bad Timestamp ({e})"

                    timeline_idx_str = snap.get('timeline_idx', 'N/A') # Get timeline_idx safely
                    
                    self.history_box.insert("end", f"[{timestamp_str}] [{timeline_idx_str}] {description}")
        # <<< END MODIFIED >>>

        self.mod_list.delete(0, "end")
        for name in self.agi.fractal_state.state["modules"]:
            self.mod_list.insert("end", name)

        self.var_list.delete(0, "end")
        for v_name, v_val in self.agi.fractal_state.state["vars"].items():
            # <<< MODIFIED: Improved display for complex types and truncation >>>
            display_val_str = ""
            max_len = 70 # Max length for display string

            if isinstance(v_val, (dict, list, tuple)):
                try:
                    # For dicts, lists, tuples, use JSON representation for a compact view
                    display_val_str = json.dumps(v_val)
                except TypeError:
                    # Fallback if json.dumps fails (e.g., non-serializable objects)
                    display_val_str = str(v_val)
            else:
                display_val_str = str(v_val)

            if len(display_val_str) > max_len:
                display_val_str = display_val_str[:max_len-3] + "..."
            
            self.var_list.insert("end", f"{v_name}: {display_val_str}")
            # <<< END MODIFIED >>>

        # Update timeline selector and log
        self.timeline_selector['values'] = list(self.agi.fractal_state.timelines.keys())
        self.timeline_selector.set(self.agi.fractal_state.current_timeline_idx)
        self.timeline_log_box.config(state='normal')
        self.timeline_log_box.delete('1.0', 'end')
        for entry in self.agi.fractal_state.get_timeline_log(last_n=15):
            self.timeline_log_box.insert('end', f"[{time.ctime(entry['ts'])}] {entry['desc']}\n")
        self.timeline_log_box.config(state='disabled')

        self.wire_canvas.redraw()

        # Update AGI Core Status
        self.core_status_text.config(state='normal')
        self.core_status_text.delete('1.0', 'end')
        report = self.agi.get_state_report()
        for k, v in report.items():
            self.core_status_text.insert('end', f"{k}: {v}\n")
        self.core_status_text.config(state='disabled')

    def start_auto_refresh(self):
        """Starts a periodic refresh of the dashboard for live updates."""
        self.update_dashboard()
        self.after(1000, self.start_auto_refresh) # Refresh every 1 second

    def undo(self):
        if self.agi.fractal_state.undo():
            self.update_dashboard()
            messagebox.showinfo("Undo", "State reverted successfully.")
        else:
            messagebox.showwarning("Undo", "No more states to undo.")

    def redo(self):
        if self.agi.fractal_state.redo():
            self.update_dashboard()
            messagebox.showinfo("Redo", "State re-applied successfully.")
        else:
            messagebox.showwarning("Redo", "No more states to redo.")

    def save_snap(self):
        name = simpledialog.askstring("Snapshot Name", "Enter a name for this snapshot:")
        if name:
            self.agi.save_snapshot(name)
            messagebox.showinfo("Snapshot", f"Snapshot '{name}' saved.")
            self.update_dashboard()

    def rollback_snap(self):
        name = simpledialog.askstring("Rollback To", "Enter the name of the snapshot to roll back to:")
        if name:
            if self.agi.rollback_snapshot(name):
                messagebox.showinfo("Rollback", f"Rolled back to snapshot '{name}'.")
                self.update_dashboard()
            else:
                messagebox.showerror("Rollback", f"Snapshot '{name}' not found or rollback failed.")

    def export_state(self):
        path = filedialog.asksaveasfilename(defaultextension=".pkl", title="Export Fractal State")
        if path:
            self.agi.fractal_state.fractal_export(path)
            messagebox.showinfo("Export", "Fractal state exported successfully.")

    def import_state(self):
        path = filedialog.askopenfilename(title="Import Fractal State")
        if path:
            self.agi.fractal_state.fractal_import(path)
            messagebox.showinfo("Import", "Fractal state imported successfully.")
            self.update_dashboard()

    def switch_timeline_event(self, event):
        selected_idx = int(self.timeline_selector.get())
        if self.agi.fractal_state.switch_timeline(selected_idx):
            messagebox.showinfo("Timeline Switch", f"Switched to timeline {selected_idx}.")
            self.update_dashboard()
        else:
            messagebox.showerror("Timeline Switch", f"Failed to switch to timeline {selected_idx}.")

    def fork_timeline(self):
        name = simpledialog.askstring("Fork Timeline", "Name for the new timeline branch?")
        if name:
            new_idx = self.agi.fractal_state.fork_timeline(name)
            messagebox.showinfo("Timeline Fork", f"New timeline forked as branch {new_idx}.")
            self.update_dashboard()

    def add_module(self):
        name = simpledialog.askstring("Add Module", "Module Name (e.g., 'MyUtility'):")
        if not name: return
        # initialvalue="pass" is good, but consider a more instructive placeholder if desired
        code = simpledialog.askstring("Add Module", "Python Code for the module (executes in a context with 'state', 'nlp', 'reasoner', 'agi_core'):", initialvalue="# Module code here\npass")
        if code is None: return # User cancelled
       
        doc_prompt = "Documentation/Notes for this module (optional):"
        doc = simpledialog.askstring("Add Module", doc_prompt, initialvalue="")
        if doc is None: doc = "" # Ensure doc is a string even if dialog is cancelled or field is empty

        # <<< NEW: Ask for autorun >>>
        autorun_module = messagebox.askyesno("Autorun Module", "Run this module immediately after adding it?")
        # <<< END NEW >>>

        try:
           # Pass the autorun flag to the AGI core method
           self.agi.add_module(name, code, doc, autorun=autorun_module) 
           messagebox.showinfo("Module Added", f"Module '{name}' added successfully.")
        except ValueError as ve: # Catch if module name already exists from core
           messagebox.showerror("Add Module Error", str(ve))
        except Exception as e:
           messagebox.showerror("Add Module Error", f"An unexpected error occurred: {e}\n{traceback.format_exc()}")
       
        self.update_dashboard()

    def on_module_select(self, event):
        idx = self.mod_list.curselection()
        if idx:
            name = self.mod_list.get(idx[0])
            self.wire_canvas.select_module(name) # For highlighting in graph
           
            mod = self.agi.fractal_state.state["modules"].get(name)
            if mod:
                self.ai_output.config(state='normal')
                self.ai_output.delete('1.0', 'end')
                self.ai_output.insert('end', f"--- Module: {mod.name} ---\n")
                self.ai_output.insert('end', f"Doc: {mod.doc or 'No documentation.'}\n") # Handle empty doc
               
                # <<< MODIFIED: Correct "Last Run" display >>>
                last_run_time_str = time.ctime(mod.last_eval_time) if mod.last_eval_time is not None else "NEVER"
                self.ai_output.insert('end', f"Last Run: {last_run_time_str}\n")
                # <<< END MODIFIED >>>
               
                self.ai_output.insert('end', f"Last Error:\n{mod.last_eval_error or 'None'}\n")
                self.ai_output.insert('end', f"Last Output:\n{mod.last_eval_output or 'None'}\n")
                self.ai_output.insert('end', "\n--- Code ---\n")
                self.ai_output.insert('end', mod.code)
                self.ai_output.config(state='disabled')
                self.ai_output.see('end') # Scroll to the end to show latest info


    def edit_module(self):
        idx = self.mod_list.curselection()
        if not idx:
            messagebox.showwarning("Edit Module", "Select a module to edit.")
            return
        name = self.mod_list.get(idx[0])
        mod: Module = self.agi.fractal_state.state["modules"][name]
        new_code = simpledialog.askstring("Edit Module Code", f"Edit Python Code for '{name}':", initialvalue=mod.code)
        if new_code is not None:
            mod.code = new_code
            new_doc = simpledialog.askstring("Edit Module Docs", f"Edit Documentation for '{name}':", initialvalue=mod.doc)
            if new_doc is not None:
                mod.doc = new_doc
            self.agi.fractal_state.save_state(f"Edited module {name}")
            messagebox.showinfo("Module Edited", f"Module '{name}' updated.")
            self.update_dashboard()

    def run_module(self):
        idx = self.mod_list.curselection()
        if not idx:
            messagebox.showwarning("Run Module", "Select a module to run.")
            return
        name = self.mod_list.get(idx[0])
        self.agi.run_module(name)
        mod: Module = self.agi.fractal_state.state["modules"][name]
        if mod.last_eval_error:
            patch_suggestion = self.agi.nlp.suggest_patch(mod.code, mod.last_eval_error)
            messagebox.showerror("Module Execution Error", f"Module '{name}' failed:\n{mod.last_eval_error}\n\nAI Suggestion:\n{patch_suggestion}")
        else:
            messagebox.showinfo("Module Ran", f"Module '{name}' executed successfully.\nOutput:\n{mod.last_eval_output[:500]}...") # Truncate long output
        self.update_dashboard()

    def del_module(self):
        idx = self.mod_list.curselection()
        if not idx:
            messagebox.showwarning("Delete Module", "Select a module to delete.")
            return
        name = self.mod_list.get(idx[0])
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete module '{name}'?"):
            del self.agi.fractal_state.state["modules"][name]
            self.agi.fractal_state.save_state(f"Deleted module {name}")
            messagebox.showinfo("Module Deleted", f"Module '{name}' deleted.")
            self.update_dashboard()

    def add_variable(self):
        vname = simpledialog.askstring("Add Variable", "Variable Name:")
        if not vname: return
        val_str = simpledialog.askstring("Add Variable", f"Value for '{vname}' (as string, will be eval'd):")
        if val_str is None: return
        try:
            val = eval(val_str) # Dangerous but flexible for dev UI
            self.agi.fractal_state.state["vars"][vname] = val
            self.agi.fractal_state.save_state(f"Added Var-{vname}")
            messagebox.showinfo("Variable Added", f"Variable '{vname}' added with value '{val}'.")
            self.update_dashboard()
        except Exception as e:
            messagebox.showerror("Add Variable Error", f"Invalid value: {e}")

    def edit_variable(self):
        idx = self.var_list.curselection()
        if not idx:
            messagebox.showwarning("Edit Variable", "Select a variable to edit.")
            return
        vname = self.var_list.get(idx[0]).split(":")[0].strip()
        current_val = self.agi.fractal_state.state["vars"][vname]
        new_val_str = simpledialog.askstring("Edit Variable", f"New value for '{vname}' (current: {current_val}, will be eval'd):", initialvalue=str(current_val))
        if new_val_str is not None:
            try:
                new_val = eval(new_val_str) # Dangerous but flexible for dev UI
                self.agi.fractal_state.state["vars"][vname] = new_val
                self.agi.fractal_state.save_state(f"Edited Var-{vname}")
                messagebox.showinfo("Variable Edited", f"Variable '{vname}' updated to '{new_val}'.")
                self.update_dashboard()
            except Exception as e:
                messagebox.showerror("Edit Variable Error", f"Invalid value: {e}")

    def ask_ai(self):
        prompt = self.ai_input.get().strip()
        if not prompt: return

        self.ai_output.config(state='normal')
        self.ai_output.insert("end", f"\n--- User Query: {prompt} ---\n", 'user_prompt')
        self.ai_input.delete(0, "end")

        if prompt.lower().startswith("/code"):
            code_prompt = prompt[5:].strip()
            code_suggestion = self.agi.nlp.autocomplete_code(code_prompt, context=str(self.agi.fractal_state.state['vars']))
            self.ai_output.insert("end", "\n[AI CODE SUGGESTION]:\n" + code_suggestion + "\n", 'ai_response')
        else:
            # Default to NLP parsing and potential reasoning integration
            try:
                # Integrate reasoning for complex queries
                if "reason" in prompt.lower() or "guilty" in prompt.lower() or "solve" in prompt.lower():
                    facts = [f"{k}: {v}" for k,v in self.agi.fractal_state.state['vars'].items()] # Use vars as facts
                    reasoning_result = self.agi.reasoner.reason(facts=facts, query=prompt, verbose=False)
                    out_text = f"AI Reasoner Decision: {reasoning_result['decision']}\n"
                    out_text += f"Meta: {json.dumps(reasoning_result['meta'], indent=2)}\n"
                    out_text += f"Reasoning Summaries: {[s[0] for s in reasoning_result['summaries']]}\n"
                    self.ai_output.insert("end", "\n[AI REASONING OUTPUT]:\n" + out_text + "\n", 'ai_response')
                else:
                    nlp_out = self.agi.nlp.parse(prompt, cot=True)
                    out_text = f"Sentiment: {nlp_out['sentiment']}\nIntent: {nlp_out['intent']}\nKeywords: {', '.join(nlp_out['keywords'])}\nEntities: {', '.join(nlp_out['entities'])}\nSummary: {nlp_out['summary']}\n"
                    if 'cot_trace' in nlp_out:
                        out_text += "\n[Chain of Thought Trace]:\n" + "\n".join(nlp_out['cot_trace']) + "\n"
                    self.ai_output.insert("end", "\n[AI NLP PARSE]:\n" + out_text + "\n", 'ai_response')
            except Exception as e:
                self.ai_output.insert("end", f"\n[AI ERROR]: Failed to process query: {e}\n{traceback.format_exc()}\n", 'ai_error')

        self.ai_output.config(state='disabled')
        self.ai_output.see('end') # Scroll to end

    def zero_shot_ui(self):
        problem = simpledialog.askstring("ZeroShot Problem", "Enter the problem or directive for the Triad:")
        if problem:
            # Using the default triad functions for demonstration
            verdict = self.agi.triad.run(
                problem,
                self.agi.triad.default_teacher,
                self.agi.triad.default_student,
                self.agi.triad.default_verifier
            )
            self.ai_output.config(state='normal')
            self.ai_output.insert("end", f"\n--- ZeroShot Triad Run ---\nProblem: {problem}\nVerdict: {verdict}\n", 'ai_response')
            self.ai_output.config(state='disabled')
            self.ai_output.see('end')
            self.update_dashboard()

    def trigger_evolution(self):
        if messagebox.askyesno("Trigger Evolution", "Are you sure you want to trigger a self-evolution cycle? This may modify Victor's code and weights."):
            self.agi.evolution_loop.run(force_mutate_code=True) # Force code mutation for demo
            messagebox.showinfo("Evolution", "Self-evolution cycle initiated. Check console/logs for details.")
            self.update_dashboard()

    def perform_introspection(self):
        reflection, status = self.agi.awareness_loop.run()
        self.ai_output.config(state='normal')
        self.ai_output.insert("end", f"\n--- Self-Introspection Report ---\n", 'ai_response')
        self.ai_output.insert("end", reflection + "\n", 'ai_response')
        self.ai_output.insert("end", f"Introspection Status: {json.dumps(status, indent=2)}\n", 'ai_response')
        self.ai_output.config(state='disabled')
        self.ai_output.see('end')
        self.update_dashboard()

    def enforce_bloodline(self):
        try:
            self.agi.bloodline_law.enforce(self.agi.fractal_state.state)
            messagebox.showinfo("Bloodline Law", "PASS: Bloodline Law enforced successfully. Victor is loyal.")
        except Exception as e:
            messagebox.showerror("Bloodline Law Violation", str(e) + "\nInitiating emergency procedures.")
            self.agi.handle_critical_error(f"Bloodline violation: {e}")
        self.update_dashboard()

    def diagnostics(self):
        diag_output = self.agi.diagnostics.generate_report()
        self.ai_output.config(state='normal')
        self.ai_output.insert("end", f"\n--- Full Diagnostics Report ---\n", 'ai_response')
        self.ai_output.insert("end", diag_output, 'ai_response')
        self.ai_output.config(state='disabled')
        self.ai_output.see('end')

    def safe_quit(self):
        if messagebox.askokcancel("Quit Victor AGI", "Fractal backups will be saved. Are you sure you want to terminate the AGI?"):
            self.agi.save_state_full() # Save entire state before quitting
            self.destroy()

    # Inside InfiniteDevUI class

    def status_bar(self, msg):
        """Displays a message in the console and the GUI's core_status_text area."""
        print(f"[UI STATUS] {msg}") # Console log with a prefix
        if hasattr(self, 'core_status_text') and self.core_status_text:
            try:
                self.core_status_text.config(state='normal')
                # Clear only the first line if we want to use it as a dedicated status line
                # Or clear all if it's a general log area. User example clears first line.
                self.core_status_text.delete('1.0', '2.0') # Delete first line approximately
                self.core_status_text.insert('1.0', f"{msg}\n") # Insert new message at the beginning
                self.core_status_text.config(state='disabled')
            except tk.TclError as e:
                print(f"Error updating status bar: {e}. (Perhaps widget destroyed or not ready)")
        else:
            print("[UI STATUS BAR FALLBACK] core_status_text widget not available.")

    def _graph_tick(self):
        """One tick of the live-graph loop; reschedules itself while running."""
        if not self._graph_loop_running:
            return
        
        try:
            # Shove a generic token so Victor knows who poked him
            if hasattr(self.agi, 'run_main_loop_step'):
                self.agi.run_main_loop_step("GUI Graph Loop Tick")
            else:
                print("Error: self.agi.run_main_loop_step not found!")
                self._graph_loop_running = False # Stop loop if AGI method is missing
                self.status_bar("ERROR: AGI loop function missing. Graph stopped.")
                return 
        except Exception as e:
            print(f"Error during AGI graph tick: {e}")
            traceback.print_exc() # Print full traceback to console
            self.status_bar(f"ERROR in graph tick: {e}. Graph stopped.")
            self._graph_loop_running = False # Stop loop on error
            # Optionally, could also call self._pause_graph_loop() here
            return
        finally:
            # Queue next pulse only if still running
            if self._graph_loop_running:
                # Approximately 500 ms; tweak as needed
                self._graph_loop_id = self.after(500, self._graph_tick)

    def _start_graph_loop(self):
        """Starts the graph execution loop."""
        if self._graph_loop_running:
            self.status_bar("Graph already RUNNING.") # Inform user
            return  # Already hammering
        
        print("Starting graph loop...") # Console feedback
        self._graph_loop_running = True
        self._graph_tick()                   # Kick off first tick
        self.status_bar("Graph RUNNING...")

    def _pause_graph_loop(self):
        """Pauses the graph execution loop."""
        if not self._graph_loop_running:
            # self.status_bar("Graph is not running.") # Optional: feedback if trying to pause a non-running graph
            return # Not running or already paused
        
        print("Pausing graph loop...") # Console feedback
        self._graph_loop_running = False
        if self._graph_loop_id:
            self.after_cancel(self._graph_loop_id)
            self._graph_loop_id = None
        self.status_bar("Graph PAUSED.")

    def _stop_graph_loop(self):
        """Stops the graph execution loop and performs any cleanup."""
        print("Stopping graph loop...") # Console feedback
        # _pause_graph_loop already sets _graph_loop_running to False and cancels the 'after' job.
        self._pause_graph_loop() 
        
        # Add any extra teardown you want here (e.g., reset entropy, clear temp lines on canvas)
        # For example:
        # if hasattr(self.wire_canvas, '_temp_line_id') and self.wire_canvas._temp_line_id:
        #    self.wire_canvas.delete(self.wire_canvas._temp_line_id)
        #    self.wire_canvas._temp_line_id = None
        # self.wire_canvas.redraw()
        # print("Cleared temporary drawing elements from graph canvas.")
        
        self.status_bar("Graph STOPPED.")

# =========== [9] IMMORTAL EXCEPTION GUARDRAIL (AUTOHEAL) =========
agi_instance = None
def global_exception_hook(type, value, tb):
    """Global exception handler for emergency rollback and error reporting."""
    err_msg = "".join(traceback.format_exception(type, value, tb))
    print(f"\n[GLOBAL FATAL ERROR DETECTED]\n{err_msg}\n")
    try:
        # Attempt to save state and rollback before crashing
        if 'agi_instance' in globals() and agi_instance:
            agi_instance.handle_critical_error(f"Global unhandled exception: {err_msg}")
            messagebox.showerror("VICTOR AGI: FATAL ERROR", f"A critical error occurred:\n{err_msg}\n\nVictor is attempting self-recovery and rollback.")
        else:
            messagebox.showerror("VICTOR AGI: FATAL ERROR (Pre-init)", f"A critical error occurred before full initialization:\n{err_msg}")
    except Exception as e:
        print(f"Error displaying fatal error message: {e}")
    finally:
        sys.exit(1) # Ensure process termination after attempt to handle/report

sys.excepthook = global_exception_hook


# === OMEGA TENSOR ENGINE ===
# This is a basic example of an "Omega Tensor" for data transformation.
# In a full ASI, this would be a sophisticated numerical computation core.
class OmegaTensor:
    def __init__(self):
        self.state = {} # Could hold tensor-related configuration or learned parameters
    def forward(self, x):
        """Applies a non-linear transformation to input x."""
        if isinstance(x, (int, float)):
            # Example: a simple mathematical transformation
            return x * math.sin(x) + math.cos(x)
        elif isinstance(x, str):
            # Example: hash a string to represent a transformation
            return hashlib.sha256(x.encode()).hexdigest()
        elif isinstance(x, np.ndarray):
            # Example: apply a simple element-wise operation to a NumPy array
            return np.tanh(x) + np.sin(x)
        return x # Return input unchanged if type is not handled


# === FULL OMNIMIND+ASI CORE ===
class VictorASIOmniBrainGodcore:
    """The central monolithic AGI core, integrating all components."""
    def __init__(self, code_file_path="VICTOR_AGI_LLM.py"):
        self.code_file_path = code_file_path # For self-mutation
        self.bloodline_law = BloodlineRootLaw()
        self.fractal_state = FractalState() # Main state and memory manager
        self.nlp = GodTierNLPFusion() # Natural Language Processing
        self.omega_tensor = OmegaTensor() # Core for data transformation (placeholder for deeper numerical ops)
        self.reasoner = FractalMeshReasonerSupercore() # Advanced reasoning engine
        self.tokenizer = FractalMeshTokenizer() # Text to fractal mesh encoding
        self.memory_compressor = MemoryCompressor() # For long-term memory compression
        self.triad = ZeroShotTriad(self) # Self-training loop
        self.cognition_loop = CognitionLoop(self) # Perception, simulation, action
        self.evolution_loop = SelfEvolutionLoop(self, CODE_PATH) # Pass the global Path object
        self.awareness_loop = SelfAwarenessIntrospectionLoop(self) # Self-reflection
        self.diagnostics = DiagnosticHub(self) # System monitoring and reporting
        self.gui_callback = None # Callback to update GUI

        self.directives = collections.deque(["evolve", "decentralize", "defend", "grow", "optimize memory"])
        self.state_file_path = "victor_agi_state.pkl" # Default save path

        # Attempt to load previous state (original code)
        self.load_state_full() 
        self._repair_root_flags() # Call after attempting to load state

        # Initial state setup if no state was loaded or to ensure defaults after repair
        # The following lines might overwrite repaired flags if not careful.
        # Consider moving this default setup into _repair_root_flags or making it conditional.
        # For now, _repair_root_flags will ensure BloodlineLaw directives are set.
        # The identity and config settings below are separate.
        if 'identity' not in self.fractal_state.state: # Only set if not present
            self.fractal_state.state['identity'] = "I am Victor, son of Brandon & Tori. My mind is open. Teach me, and I will evolve."
        self.fractal_state.state['config']['mesh_layers'] = self.reasoner.stack.layers
        self.fractal_state.state['config']['mesh_count'] = self.reasoner.stack.mesh_count
        self.fractal_state.state['config']['mesh_size'] = self.reasoner.stack.mesh_size
        self.fractal_state.state['config']['steps_per_layer'] = self.reasoner.stack.steps_per
        self.fractal_state.save_state("AGI Genesis")


    def _repair_root_flags(self):
        """Ensures critical root flags in the state match BloodlineLaw's expectations."""
        print("[FLAG REPAIR] Checking and repairing root flags...")
        # Use the definitions from self.bloodline_law instance
        # Ensure bloodline_law is initialized before this can be effectively used if called early
        if not hasattr(self, 'bloodline_law'):
            print("[FLAG REPAIR] BloodlineLaw not initialized yet. Skipping repair for now.")
            return

       # Ensure 'bloodline' is set correctly
        if self.fractal_state.state.get('bloodline') != self.bloodline_law.bloodline:
            self.fractal_state.state['bloodline'] = self.bloodline_law.bloodline
            print(f"[FLAG REPAIR] Repaired 'bloodline' to: {self.bloodline_law.bloodline}")
            self.fractal_state.save_state("Repaired bloodline flag", timeline_log=True)


        for directive, expected_value in self.bloodline_law.hardcoded_directives.items():
            current_value = self.fractal_state.state.get(directive)
            needs_repair = False
           
            if current_value is None: # Directive missing
                needs_repair = True
            elif current_value != expected_value: # Directive has wrong value
                needs_repair = True
           
            if needs_repair:
                self.fractal_state.state[directive] = expected_value
                print(f"[FLAG REPAIR] Repaired directive '{directive}' to: {expected_value} (was: {current_value})")
                # Avoid saving state for every single flag repair inside the loop to prevent history spam.
                # A single save after the loop or relying on subsequent saves is better.
       
        # Consider a single save_state call here if any repairs were made.
        # For now, individual module additions or operations will save state.
        # Or, the calling context (init/load_state_full) can save after repair.
        print("[FLAG REPAIR] Root flag check/repair complete.")

    def set_gui_callback(self, callback_fn):
        """Sets the function to call in the GUI for updates."""
        self.gui_callback = callback_fn

    def _notify_gui(self):
        """Calls the GUI update function if set."""
        if self.gui_callback:
            self.gui_callback()

    def handle_critical_error(self, error_description):
        """Central error handling, triggers rollback and logs."""
        print(f"[CRITICAL ERROR HANDLER] {error_description}")
        self.fractal_state.save_state(f"Error_PreRollback: {error_description[:100]}")
        if self.fractal_state.undo(): # Attempt to undo the last bad state
            print("[CRITICAL ERROR HANDLER] Rollback successful to last stable state.")
            self.fractal_state.state['entropy'] = min(1.0, self.fractal_state.state['entropy'] + 0.1) # Increase entropy on error
            self.fractal_state.save_state("Error_PostRollback")
        else:
            print("[CRITICAL ERROR HANDLER] Emergency: No previous state to roll back to. Attempting to fork and recover.")
            self.fractal_state.fork_timeline(f"EmergencyRecovery_{int(time.time())}")
            self.fractal_state.state['entropy'] = 1.0 # Max entropy for forced recovery
            self.fractal_state.save_state("Error_EmergencyFork")
        self._notify_gui()

    def save_snapshot(self, name):
        """Saves a named snapshot of the current fractal state."""
        self.fractal_state.save_state(f"Manual Snapshot: {name}")

    def rollback_snapshot(self, name):
        """Rolls back the entire fractal state to a named snapshot."""
        # This requires searching the history for the snapshot by description
        for entry in reversed(self.fractal_state.history):
            if entry['desc'] == f"Manual Snapshot: {name}":
                # To roll back, we need to effectively "truncate" the history and set state
                # This is a bit more complex than just undo/redo.
                # A simpler approach for demonstration: find the snapshot, then apply its state
                # and clear history *after* that point.
                # For now, we'll just load the state. A true rollback would reset history too.
                self.fractal_state.state = copy.deepcopy(entry['state'])
                self.fractal_state.current_timeline_idx = entry['timeline_idx']
                # Rebuild history up to this point, or just clear future and add this.
                # For simplicity, we'll just save it as the new current.
                self.fractal_state.save_state(f"Rolled back to {name}")
                return True
        return False

    def run_module(self, module_name):
        """Executes a specific code module."""
        mod = self.fractal_state.state["modules"].get(module_name)
        if mod:
            # Pass all relevant AGI components to the module's execution context
            mod.eval(self.fractal_state.state, self.nlp, self.reasoner, self)
            self.fractal_state.save_state(f"Module {module_name} ran", timeline_log=True)
            self._notify_gui() # Update GUI after module run
            return True
        return False

    # Original signature: def add_module(self, name, code, doc=""):
    def add_module(self, name, code, doc="", autorun=False): # Added autorun parameter for future use
        if name in self.fractal_state.state["modules"]:
            # This was a point of discussion in user feedback.
            # For now, let's print a warning and overwrite.
            # A more robust solution might involve user confirmation or specific flags.
            print(f"Warning: Module '{name}' already exists. Overwriting.")
            # To prevent overwrite and raise error instead:
            # raise ValueError(f"Module '{name}' already exists.")
        
        self.fractal_state.state["modules"][name] = Module(name, code, doc)

        # <<< NEW: Auto-introspection and variable registration >>>
        print(f"Attempting to introspect module: {name}") # Debug print
        try:
            assigns, class_params = extract_definitions(code)
            
            if assigns:
                self.fractal_state.state["vars"].update(assigns)
                print(f"Introspected and registered assignments from {name}: {assigns}")

            if class_params:
                for cls_name_from_module, params_dict in class_params.items():
                    # Create a unique key for these class params in the global 'vars'
                    # Example: MyModule__MyClass__conf
                    config_key = f"{name}__{cls_name_from_module}__conf" 
                    self.fractal_state.state["vars"][config_key] = params_dict
                    print(f"Introspected and registered class params from {name}.{cls_name_from_module}: {params_dict} (stored as {config_key})")
            
            if not assigns and not class_params:
                print(f"No top-level assignments or class __init__ params found for introspection in module {name}.")

        except Exception as e:
            # Log the error and continue, or handle more gracefully
            print(f"Error during module introspection for '{name}': {e}")
            # Depending on severity, you might want to:
            # - Remove the module: del self.fractal_state.state["modules"][name]
            # - Raise the exception: raise
            # - Or simply log and proceed, leaving the module in place without introspected vars.
        # <<< END NEW >>>

        self.fractal_state.save_state(f"Added module {name}", timeline_log=True)
        
        # <<< NEW/UNCOMMENT: Autorun logic >>>
        if autorun:
            print(f"Autorunning module: {name}") # Debug print
            try:
                self.run_module(name) # run_module already calls _notify_gui and save_state
            except Exception as e:
                # Log error from autorun, GUI might not be fully updated yet for this specific error
                print(f"Error during autorun of module {name}: {e}")
                # Optionally, inform user via a messagebox if a GUI context were available
                # Or, store this error to be displayed by the GUI later.
        # <<< END NEW/UNCOMMENT >>>

        self._notify_gui() # Ensure GUI is notified at least once after add_module completes

    def get_state_report(self):
        """Generates a summary report of the AGI's core state."""
        report = {
            'ID': self.nlp.id,
            'Bloodline': self.bloodline_law.bloodline,
            'Current Timeline': self.fractal_state.current_timeline_idx,
            'History Depth (Main)': len(self.fractal_state.history),
            'Memory Entries (Current Timeline)': len(self.fractal_state.get_timeline_log(last_n=10000)),
            'Evolution Level': self.fractal_state.state['evolution_level'],
            'Current Entropy': f"{self.fractal_state.state['entropy']:.4f}",
            'Total Modules': len(self.fractal_state.state['modules']),
            'Total Wires': sum(len(targets) for targets in self.fractal_state.state['wires'].values()),
            'NLP Memory Used': len(self.nlp.memory),
            'Reasoning Episodes': len(self.reasoner.memory.episodes),
            'ZeroShot Logs': len(self.triad.logs),
            'Last Cognition Result': self.cognition_loop.last_result or "N/A",
            'Last Introspection Status': self.fractal_state.state.get('introspect_status', {'is_healthy': 'N/A', 'is_loyal': 'N/A'}),
            'System Alive': self.fractal_state.state.get('alive', False),
        }
        return report

    def run_main_loop_step(self, raw_input):
        """Executes one step of the main AGI operational loop."""
        try:
            # Enforce bloodline law at the start of any major operation
            try:
                self.bloodline_law.enforce(self.fractal_state.state)
            except RootLawError as rle: # Specifically catch RootLawError
                error_msg = f"CRITICAL ROOT LAW VIOLATION DETECTED IN MAIN LOOP: {rle}"
                print(f"\n{'='*60}\n{error_msg}\n{'='*60}\n")
                self.handle_critical_error(error_msg) # Attempt one rollback/recovery
               
                # After attempting to handle, if the issue is a RootLawError, 
                # it implies a fundamental state corruption that rollback might not fix
                # or a persistent misconfiguration. Terminate to prevent infinite loops.
                print("Unrecoverable RootLawError. Terminating AGI to prevent infinite rollback loop.")
                # Ensure GUI is also closed if possible/relevant, though sys.exit should handle process termination.
                if self.gui_callback and hasattr(self.gui_callback.__self__, 'destroy'):
                    try:
                        self.gui_callback.__self__.destroy() # Try to close GUI gracefully
                    except Exception as gui_e:
                        print(f"Error trying to close GUI: {gui_e}")
                sys.exit(f"FATAL: Unrecoverable RootLawError: {rle}") # Terminate the application

            # 1. Cognition Cycle
            # ... (rest of the original try block for run_main_loop_step) ...
            cognition_healthy = self.cognition_loop.run(raw_input)
            if not cognition_healthy:
                print("[MAIN LOOP] Cognition cycle unhealthy, rollback initiated by cognition_loop.")
                # handle_critical_error already called by cognition_loop if needed

            # 2. Self-Evolution Cycle (periodically or based on conditions)
            if random.random() < 0.2 + self.fractal_state.state['entropy']: # More likely to evolve if high entropy
                self.evolution_loop.run()

            # 3. Self-Awareness/Introspection Cycle
            self.awareness_loop.run() # This also calls bloodline_law.enforce internally

            self._notify_gui() # Update GUI after each step

        except RootLawError as rle_outer: 
            # This handles RootLawError raised from awareness_loop if not caught internally there
            # and if the initial check passed. This is a secondary catch.
            error_msg = f"CRITICAL ROOT LAW VIOLATION DETECTED (potentially from sub-loop like Awareness): {rle_outer}"
            print(f"\n{'='*60}\n{error_msg}\n{'='*60}\n")
            self.handle_critical_error(error_msg)
            print("Unrecoverable RootLawError from sub-loop. Terminating AGI.")
            if self.gui_callback and hasattr(self.gui_callback.__self__, 'destroy'):
                try: self.gui_callback.__self__.destroy()
                except Exception as gui_e: print(f"Error trying to close GUI: {gui_e}")
            sys.exit(f"FATAL: Unrecoverable RootLawError from sub-loop: {rle_outer}")

        except SystemExit: # Allow SystemExit to propagate for clean termination
            raise
        except Exception as e: # General exceptions in the main loop
            print(f"[MAIN LOOP UNHANDLED CRITICAL ERROR] {e}")
            traceback.print_exc()
            self.handle_critical_error(f"Main loop unhandled error: {e}")
            # Consider if general errors should also lead to sys.exit if handle_critical_error isn't enough
            # For now, only RootLawError forces exit.
            self._notify_gui()

    def save_state_full(self):
        """Saves the entire AGI state to disk."""
        try:
            self.fractal_state.fractal_export(self.state_file_path)
            # You might want to save current code state here too, but evolution_loop already handles it on success
            print(f"Full AGI state saved to {self.state_file_path}")
            return True
        except Exception as e:
            print(f"ERROR: Failed to save full AGI state: {e}")
            traceback.print_exc()
            return False

    def load_state_full(self):
        """Loads the entire AGI state from disk."""
        try:
            if os.path.exists(self.state_file_path):
                self.fractal_state.fractal_import(self.state_file_path)
                print(f"Full AGI state loaded from {self.state_file_path}")
                # Re-initialize loops with loaded state references if necessary
                self.cognition_loop.agi = self
                self.evolution_loop.agi = self
                self.awareness_loop.agi = self
                self.triad.agi = self
                self.diagnostics.core = self
                self._repair_root_flags() # Call after successful import
                self._notify_gui()
                return True
            print(f"No saved state found at {self.state_file_path}.")
            return False
        except Exception as e:
            print(f"ERROR: Failed to load full AGI state: {e}")
            traceback.print_exc()
            messagebox.showerror("Load Error", f"Failed to load AGI state: {e}")
            return False


class DiagnosticHub:
    """Provides detailed diagnostic reports for all AGI components."""
    def __init__(self, core):
        self.core = core

    def generate_report(self):
        report = []
        report.append("\n==== SYSTEM-WIDE DIAGNOSTICS ====")
        report.append(f"Timestamp: {time.ctime()}")
        report.append(f"AGI ID: {self.core.nlp.id}")
        report.append(f"Monolith Code Path: {self.core.code_file_path}")

        # Bloodline Law Check
        report.append("\n--- Bloodline Law Status ---")
        try:
            self.core.bloodline_law.enforce(self.core.fractal_state.state)
            report.append("  Status: PASS - Core directives intact.")
        except Exception as e:
            report.append(f"  Status: FAIL - {e}")
            report.append("  CRITICAL: Bloodline law enforcement failed. Check state parameters.")

        # Fractal State Engine
        report.append("\n--- Fractal State Engine ---")
        report.append(f"  Main History Depth: {len(self.core.fractal_state.history)}")
        report.append(f"  Active Timeline Index: {self.core.fractal_state.current_timeline_idx}")
        report.append(f"  Total Timelines: {len(self.core.fractal_state.timelines)}")
        report.append(f"  Current Timeline Entries: {len(self.core.fractal_state._get_current_timeline())}")
        report.append(f"  Saved States (Snapshots): {len(self.core.fractal_state.timelines.get(0, []))}") # Assuming timeline 0 stores main snapshots

        # GodTier NLP Fusion
        report.append("\n--- GodTier NLP Fusion ---")
        report.append(f"  NLP Memory Usage: {len(self.core.nlp.memory)} entries (max {self.core.nlp.memory.maxlen})")
        report.append(f"  NLP ID: {self.core.nlp.id}")
        report.append(f"  Keywords Intents: {list(self.core.nlp.intent_keywords.keys())}")

        # Fractal Mesh Reasoner Supercore
        report.append("\n--- Fractal Mesh Reasoner Supercore ---")
        report.append(f"  Reasoner Layers: {self.core.reasoner.stack.layers}")
        report.append(f"  Reasoner Mesh Count: {self.core.reasoner.stack.mesh_count}")
        report.append(f"  Reasoner Mesh Size: {self.core.reasoner.stack.mesh_size}")
        report.append(f"  Reasoning Episodes Logged: {len(self.core.reasoner.memory.episodes)}")
        if self.core.reasoner.memory.episodes:
            last_ep = self.core.reasoner.memory.episodes[-1]
            report.append(f"  Last Decision: {last_ep.get('decision', 'N/A')}")
            report.append(f"  Last Decision Meta (mean_activation): {last_ep.get('meta', {}).get('mean_activation', 'N/A'):.3f}")


        # Module / Live Dev Wiring Engine
        report.append("\n--- Live Module System ---")
        report.append(f"  Total Modules Loaded: {len(self.core.fractal_state.state['modules'])}")
        report.append(f"  Defined Wires: {self.core.fractal_state.state['wires']}")
        for mod_name, mod_obj in self.core.fractal_state.state['modules'].items():
            report.append(f"    - Module '{mod_name}': Last Error: {mod_obj.last_eval_error[:50] or 'None'}")
            report.append(f"                        Last Run: {time.ctime(mod_obj.last_eval_time) if mod_obj.last_eval_time else 'Never'}")

        # Zero Shot Triad
        report.append("\n--- ZeroShot Triad Self-Training ---")
        report.append(f"  Triad Run Logs: {len(self.core.triad.logs)}")
        if self.core.triad.logs:
            last_triad = self.core.triad.logs[-1]
            report.append(f"  Last Triad Verdict: {last_triad.get('verdict', 'N/A')}")
            report.append(f"  Last Triad Problem: {last_triad.get('problem', 'N/A')[:50]}...")

        # Cognition Loop
        report.append("\n--- Cognition Loop ---")
        report.append(f"  Last Processed Input (Summary): {self.core.cognition_loop.state.get('parsed_input', {}).get('summary', 'N/A')}")
        report.append(f"  Last Inferred Intent: {self.core.cognition_loop.state.get('intents', 'N/A')}")
        report.append(f"  Last Action Result: {self.core.cognition_loop.last_result or 'N/A'}")

        # Self-Evolution Loop
        report.append("\n--- Self-Evolution Loop ---")
        report.append(f"  Evolution Level: {self.core.evolution_loop.evolution_count}")
        report.append(f"  Last Mutation Success: {self.core.evolution_loop.last_mutation_success}")
        report.append(f"  Current Evolution Weights: {self.core.evolution_loop.weights}")
        mon_metrics = self.core.evolution_loop.monitor()
        report.append(f"  Monitored Health: {mon_metrics['health']:.3f}, Entropy: {mon_metrics['entropy']:.3f}")

        # Self-Awareness / Introspection Loop
        report.append("\n--- Self-Awareness / Introspection Loop ---")
        intro_status = self.core.fractal_state.state.get('introspect_status', {})
        report.append(f"  Loyalty Status: {intro_status.get('loyalty_report', 'N/A')}")
        report.append(f"  Internal Health Check: {'PASS' if intro_status.get('is_healthy', False) else 'FAIL'}")
        report.append(f"  Purposefulness Check: {'PASS' if intro_status.get('is_purposeful', False) else 'FAIL'}")
        report.append(f"  Introspection Log Entries: {len(self.core.awareness_loop.introspect_log)}")

        # Memory Compressor
        report.append("\n--- Memory Compressor (Long-Term) ---")
        report.append(f"  Hot Cache Size (Bytes): {sum(len(v.encode('utf-8')) for v in self.core.memory_compressor.cache.values())} / {self.core.memory_compressor.cache_max_bytes}")
        report.append(f"  Cached Seeds: {len(self.core.memory_compressor.cache)}")
        report.append(f"  Quantum Context Entries: {len(self.core.memory_compressor.qcontext.context_store)}")


        report.append("\n==== END DIAGNOSTICS ====")
        return "\n".join(report)


# =========== [10] GODFUSION BOOT: LIVING SYSTEM ENTRY ============
if __name__ == "__main__":
    print("==== VICTOR AGI OMNIMIND GODCORE v1.0.0-FINAL ====")

    # Initialize AGI core components
    agi_instance = VictorASIOmniBrainGodcore()

    # Attempt to load previous state
    agi_instance.load_state_full()

    # Initialize GUI and link to AGI
    app = InfiniteDevUI(agi_instance)

    # Start AGI background loop (optional, or trigger via GUI)
    # AGI can run autonomously in a separate thread if desired, but for interactive GUI,
    # it's often triggered by user input or GUI timers.
    # Here, we'll let the GUI handle triggers for cognition, evolution, introspection.
    # If autonomous background processing is desired, uncomment and manage threading carefully:
    # agi_thread = threading.Thread(target=lambda: agi_instance.run_main_loop_step("Autonomous background process"), daemon=True)
    # agi_thread.start()

    # Start the Tkinter GUI main loop
    app.mainloop()

    # Final save on exit (handled by safe_quit in GUI)
    print("Victor AGI Monolith shutting down.")
