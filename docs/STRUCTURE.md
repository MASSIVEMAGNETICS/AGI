# Repository Structure

This document explains the organization of the Tooki Research Lab repository.

## Root Directory

```
tooki/
├── .gitignore              # Ignore patterns for research artifacts
├── README.md               # Main project overview
├── CONTRIBUTING.md         # Contribution guidelines
├── research/               # Main research directory
│   ├── README.md          # Research overview
│   ├── ai/                # AI research projects
│   ├── code/              # Code research projects
│   ├── papers/            # Research papers
│   └── experiments/       # Experimental results
└── docs/                  # Additional documentation
    └── STRUCTURE.md       # This file
```

## Research Categories

### AI Research (`/research/ai/`)

Contains artificial intelligence and machine learning research:
- **Models**: Neural network architectures and implementations
- **Datasets**: Data collection and preprocessing pipelines
- **Training**: Training scripts and configurations
- **Evaluation**: Model evaluation and benchmarking
- **Applications**: Applied AI projects and demos

Typical project structure:
```
ai/YYYY-MM-DD-project-name/
├── README.md
├── METADATA.json
├── code/
│   ├── models/
│   ├── training/
│   └── evaluation/
├── data/
│   └── description.md
├── results/
│   ├── metrics.json
│   └── visualizations/
└── docs/
    └── methodology.md
```

### Code Research (`/research/code/`)

Contains software engineering and programming research:
- **Algorithms**: Algorithm implementations and analysis
- **Languages**: Programming language studies
- **Tools**: Development tools and utilities
- **Optimization**: Code optimization experiments
- **Frameworks**: Framework comparisons and development

Typical project structure:
```
code/YYYY-MM-DD-project-name/
├── README.md
├── METADATA.json
├── src/
│   └── implementation/
├── benchmarks/
│   └── results/
├── tests/
│   └── test_suite/
└── docs/
    └── analysis.md
```

### Papers (`/research/papers/`)

Contains research papers and publications:
- **Original**: Original research papers
- **Reviews**: Literature reviews and surveys
- **Reports**: Technical reports
- **Presentations**: Conference and seminar materials

Typical paper structure:
```
papers/YYYY-MM-DD-paper-title/
├── README.md
├── METADATA.json
├── manuscript/
│   ├── paper.md
│   └── paper.pdf
├── figures/
├── references.bib
└── supplementary/
```

### Experiments (`/research/experiments/`)

Contains experimental setups and results:
- **Configurations**: Experiment configurations
- **Data**: Raw and processed results
- **Analysis**: Statistical analysis and visualizations
- **Logs**: Execution logs and traces

Typical experiment structure:
```
experiments/YYYY-MM-DD-experiment-name/
├── README.md
├── METADATA.json
├── setup/
│   ├── config.yaml
│   └── environment.yml
├── data/
│   ├── raw/
│   └── processed/
├── analysis/
│   └── notebooks/
└── results/
    └── summary.md
```

## Documentation (`/docs/`)

Additional documentation and guides:
- **Tutorials**: How-to guides
- **Standards**: Coding and documentation standards
- **Architecture**: System architecture documents
- **Processes**: Workflow and process documentation

## File Naming Conventions

### Directories
- Use lowercase with hyphens: `my-project-name`
- Include dates for time-based organization: `2026-01-24-project`
- Be descriptive but concise

### Files
- Use lowercase with hyphens: `experiment-results.md`
- Use common extensions: `.md`, `.py`, `.json`, `.yaml`
- Prefix related files: `01-setup.md`, `02-training.md`

### Special Files
- `README.md` - Project overview (required)
- `METADATA.json` - Structured metadata (required)
- `requirements.txt` - Python dependencies
- `package.json` - JavaScript dependencies
- `.gitignore` - Ignore patterns

## Metadata Format

Each project should include a `METADATA.json` file:

```json
{
  "title": "Human-readable Project Title",
  "date": "YYYY-MM-DD",
  "authors": [
    "Author Name 1",
    "Author Name 2"
  ],
  "tags": [
    "machine-learning",
    "nlp",
    "transformers"
  ],
  "category": "ai",
  "subcategory": "natural-language-processing",
  "status": "completed",
  "license": "MIT",
  "description": "Brief description of the project",
  "related": [
    "/research/ai/2025-12-01-related-project"
  ],
  "publications": [
    "https://arxiv.org/abs/..."
  ],
  "dependencies": {
    "python": "3.9+",
    "frameworks": ["pytorch", "transformers"]
  }
}
```

## Large Files and Data

### Git LFS
For files larger than 50MB:
1. Install Git LFS: `git lfs install`
2. Track file types: `git lfs track "*.pth"`
3. Commit `.gitattributes`

### External Storage
For very large datasets:
1. Store on external platform (S3, Google Drive, etc.)
2. Include download script in project
3. Document access instructions

### Compression
- Compress large text files: `.gz`, `.zip`
- Use efficient formats: `.parquet`, `.hdf5`
- Provide checksums: `sha256sum`

## Security Considerations

Never commit:
- API keys or credentials
- Personal information
- Proprietary data without permission
- Large binary files without LFS
- Temporary or cache files

Always:
- Review commits before pushing
- Use `.gitignore` effectively
- Sanitize notebooks before committing
- Document data sources and licenses

## Maintenance

### Regular Tasks
- Update README files as projects evolve
- Archive completed projects
- Clean up temporary files
- Update cross-references

### Quality Checks
- Validate metadata JSON
- Check for broken links
- Verify reproducibility
- Review documentation completeness

## Examples

See existing projects in each category for examples of proper structure and documentation.
