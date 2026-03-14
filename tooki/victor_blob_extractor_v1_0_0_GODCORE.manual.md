# Victor Blob Extractor Manual (v1.0.0-BLOB-EXTRACTOR-GODCORE)

## Segment detection rules
A segment starts at either:
1. A line beginning with `# FILE:`
2. A line beginning with `###` that has a `# FILE:` header within the next 15 lines

The `FILE:` value becomes the extracted relative path beneath the output directory.

## Extraction
- Writes are atomic (tmp + fsync + replace)
- Absolute-path writes are prevented by stripping a leading `/`

## AST parsing (Python only)
For `.py` segments:
- Parses AST
- Extracts class names, function names, import targets
- Syntax errors are added to warnings

## Exports
- `--json`: structure report
- `--sqlite`: index database (`segments`, `symbols`)
- `--dot`: Graphviz DOT graph
- `--ingest`: Victor ingestion envelope with trust scoring signals

## Usage
```bash
python victor_blob_extractor_v1_0_0_GODCORE.py --input "BLOB.txt" --out "./extracted"   --json "./extracted/report.json"   --sqlite "./extracted/report.sqlite"   --dot "./extracted/graph.dot"   --ingest "./extracted/ingest.json"
```

Dry-run:
```bash
python victor_blob_extractor_v1_0_0_GODCORE.py --input "BLOB.txt" --out "./extracted" --dry-run --json "./extracted/report.json"
```
