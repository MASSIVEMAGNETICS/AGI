#!/usr/bin/env python3
"""
Victor Research Indexer
- Reads a folder of .txt research exports
- Clusters documents (TF-IDF + KMeans)
- Detects exact duplicates (sha256)
- Writes: RESEARCH_MANIFEST.json, VICTOR_RESEARCH_INDEX.md, VICTOR_RESEARCH_SYNTHESIS.md

Usage:
  python victor_research_indexer.py --root "C:\path\to\research" --k 8

No external dependencies beyond scikit-learn (optional). If sklearn missing, it falls back to keyword-only manifest.
"""
from __future__ import annotations
import argparse, os, re, json, hashlib, datetime
from collections import Counter, defaultdict

def read_text(path: str, max_chars: int = 200000) -> str:
    with open(path, "rb") as f:
        raw = f.read()
    return raw.decode("utf-8", errors="replace")[:max_chars]

def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def tokenize(text: str):
    return re.findall(r"[A-Za-z][A-Za-z0-9_\-]{2,}", text.lower())

DEFAULT_CLUSTER_NAMES = {
  0:"GUI / Web / Agents / Backend wiring",
  1:"Runtime kernel, pulse/logger, asyncio plumbing",
  2:"OmegaTensor autodiff / tensor engine",
  3:"Model configs, fractal blocks, state/cortex parameters",
  4:"Narrative/consciousness, identity, voice, family lore",
  5:"Tooling/workflows, search/tools orchestration, prompts",
  6:"Magnetics/metamaterials/energy concepts",
  7:"General Victor/Fractal memory/architecture notes",
}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True, help="Folder containing .txt files")
    ap.add_argument("--k", type=int, default=8, help="Number of clusters")
    ap.add_argument("--out", default=None, help="Output folder (defaults to --root)")
    args = ap.parse_args()

    root = os.path.abspath(args.root)
    out = os.path.abspath(args.out or root)
    os.makedirs(out, exist_ok=True)

    txt_files = [os.path.join(root, f) for f in os.listdir(root) if f.lower().endswith(".txt")]
    txt_files.sort()

    items = []
    texts = []
    names = []
    for p in txt_files:
        name = os.path.basename(p)
        text = read_text(p, max_chars=200000)
        texts.append(text)
        names.append(name)
        items.append({
            "file": name,
            "bytes": os.path.getsize(p),
            "sha256": sha256_file(p),
        })

    # duplicates
    dup = defaultdict(list)
    for it in items:
        dup[it["sha256"]].append(it["file"])
    dup = {h:fl for h,fl in dup.items() if len(fl) > 1}

    cluster_id = {name: None for name in names}
    cluster_terms = {}
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.cluster import KMeans
        stop = set("""
the a an and or but if then else to of in for on with as by from at into is are was were be been being this that these those it its
i you we they them he she his her our your their not no yes do does did doing done can could should would will just like more most very about over under across
def return import class print none true false self init__ str int float list dict tuple set optional any torch nn np numpy pandas json time datetime os sys pathlib typing dataclass enum try except raise pass break continue yield lambda async await
""".split())
        vec = TfidfVectorizer(stop_words=list(stop), max_features=8000, ngram_range=(1,2))
        X = vec.fit_transform(texts)
        km = KMeans(n_clusters=args.k, random_state=0, n_init=10)
        labels = km.fit_predict(X)
        feats = vec.get_feature_names_out()
        for name, lab in zip(names, labels):
            cluster_id[name] = int(lab)
        centers = km.cluster_centers_
        for cid in range(args.k):
            top = centers[cid].argsort()[-12:][::-1]
            cluster_terms[int(cid)] = [feats[i] for i in top]
    except Exception as e:
        # fallback: no sklearn available
        # naive keyword clustering: leave cluster_id None
        pass

    for it in items:
        cid = cluster_id.get(it["file"])
        it["cluster_id"] = cid
        it["cluster_name"] = DEFAULT_CLUSTER_NAMES.get(cid) if cid is not None else None

    manifest = {
        "generated_utc": datetime.datetime.utcnow().isoformat() + "Z",
        "count": len(items),
        "duplicates": dup,
        "cluster_terms": cluster_terms,
        "items": items,
    }
    with open(os.path.join(out, "RESEARCH_MANIFEST.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    # index markdown
    md = []
    md.append("# Victor Research Bundle — Index\n")
    md.append(f"Generated: {manifest['generated_utc']}\n")
    if cluster_terms:
        md.append("## Clusters\n")
        byc = defaultdict(list)
        for it in items:
            byc[it["cluster_id"]].append(it["file"])
        for cid in sorted([c for c in byc.keys() if c is not None]):
            md.append(f"### {cid}. {DEFAULT_CLUSTER_NAMES.get(cid,'Cluster')}\n")
            md.append(f"**Signal terms:** {', '.join(cluster_terms.get(cid, [])[:12])}\n")
            md.append(f"*Files:* {len(byc[cid])}\n")
            for fn in byc[cid][:20]:
                md.append(f"- {fn}")
            if len(byc[cid]) > 20:
                md.append(f"- … (+{len(byc[cid]) - 20} more)")
            md.append("")
    md.append("## Exact duplicates (sha256)\n")
    if dup:
        for h, fl in dup.items():
            md.append(f"- {', '.join(fl)}")
    else:
        md.append("- None detected")
    md.append("")
    with open(os.path.join(out, "VICTOR_RESEARCH_INDEX.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(md))

    print("Wrote:", os.path.join(out, "RESEARCH_MANIFEST.json"))
    print("Wrote:", os.path.join(out, "VICTOR_RESEARCH_INDEX.md"))

if __name__ == "__main__":
    main()
