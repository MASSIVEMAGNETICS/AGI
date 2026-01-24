# Quick Start Guide: Uploading Research to Tooki

This guide will help you quickly upload your research to the Tooki Research Lab repository.

## Step-by-Step Upload Process

### 1. Choose the Right Category

Determine where your research belongs:
- **`/research/ai`** - AI/ML models, experiments, deep learning, NLP, computer vision
- **`/research/code`** - Algorithms, software engineering, programming languages, tools
- **`/research/papers`** - Research papers, publications, technical reports
- **`/research/experiments`** - Experimental results, benchmarks, comparative studies

### 2. Create Your Project Folder

Create a dated folder with a descriptive name:

```bash
cd research/[category]
mkdir YYYY-MM-DD-your-project-name
cd YYYY-MM-DD-your-project-name
```

**Naming Example**: `2024-03-15-transformer-sentiment-analysis`

### 3. Copy the Templates

Use the provided templates to structure your project:

```bash
# Copy the README template
cp ../../docs/PROJECT_TEMPLATE.md ./README.md

# Copy the metadata template
cp ../../docs/METADATA_TEMPLATE.json ./METADATA.json
```

### 4. Organize Your Files

Create a standard structure:

```bash
mkdir -p code data results docs

# Add your files
mv /path/to/your/code/* ./code/
mv /path/to/your/data/* ./data/
mv /path/to/your/results/* ./results/
```

### 5. Fill Out Documentation

Edit the README.md file:
- Replace placeholders with your project details
- Document objectives, methodology, and results
- Include setup and reproduction instructions
- Add references and related work

Edit METADATA.json:
- Update all fields with accurate information
- Add proper tags and keywords
- Include author information
- Document dependencies

### 6. Verify Your Upload

Check your project structure:

```bash
# Should look like this:
your-project/
├── README.md          # ✅ Complete documentation
├── METADATA.json      # ✅ Accurate metadata
├── code/             # ✅ Your implementation
├── data/             # ✅ Data descriptions
├── results/          # ✅ Your findings
└── docs/             # ✅ Additional docs
```

### 7. Test Your Documentation

Ensure reproducibility:
- [ ] Can someone else understand your project from the README?
- [ ] Are all dependencies listed?
- [ ] Do the instructions work on a fresh environment?
- [ ] Are all results documented?

### 8. Commit and Push

```bash
# From repository root
git add research/[category]/YYYY-MM-DD-your-project-name
git commit -m "Add [Your Project Name] research"
git push
```

### 9. Submit Pull Request

- Create a pull request with a clear title
- Describe what research you're adding
- Mention any special considerations
- Wait for review and feedback

## Quick Checklist

Before submitting, verify:
- [ ] Project in correct category
- [ ] Folder named with date: YYYY-MM-DD-name
- [ ] README.md is complete and clear
- [ ] METADATA.json is filled out
- [ ] Code is documented
- [ ] Results are included
- [ ] No sensitive data (API keys, credentials)
- [ ] Large files use Git LFS or are linked externally
- [ ] .gitignore prevents unwanted files

## Common Patterns

### AI/ML Project
```
2024-06-15-image-classifier/
├── README.md
├── METADATA.json
├── requirements.txt
├── code/
│   ├── model.py
│   ├── train.py
│   └── evaluate.py
├── data/
│   └── README.md
└── results/
    ├── metrics.json
    └── figures/
```

### Code Research Project
```
2024-08-20-sorting-algorithms/
├── README.md
├── METADATA.json
├── src/
│   ├── quicksort.py
│   └── mergesort.py
├── benchmarks/
│   └── results.csv
└── tests/
    └── test_algorithms.py
```

### Research Paper
```
2024-10-10-paper-title/
├── README.md
├── METADATA.json
├── manuscript/
│   ├── paper.md
│   └── paper.pdf
├── figures/
└── code/
    └── experiments/
```

## Tips for Success

1. **Be Descriptive**: Clear names and documentation help others understand your work
2. **Be Complete**: Include everything needed to understand and reproduce
3. **Be Organized**: Follow the standard structure for consistency
4. **Be Mindful**: Don't upload sensitive data or excessive file sizes
5. **Be Helpful**: Write documentation as if you're helping your future self

## Need Help?

- Check the [example project](/research/ai/example-project) for reference
- Review the [full documentation](/docs/STRUCTURE.md)
- Read the [contributing guidelines](/CONTRIBUTING.md)
- Open an issue for questions

## Example Commands

Complete example for uploading a new AI project:

```bash
# 1. Navigate to AI research directory
cd research/ai

# 2. Create your project folder
mkdir 2024-12-01-my-awesome-project
cd 2024-12-01-my-awesome-project

# 3. Create structure
mkdir -p code data results docs

# 4. Copy templates
cp ../../docs/PROJECT_TEMPLATE.md ./README.md
cp ../../docs/METADATA_TEMPLATE.json ./METADATA.json

# 5. Add your files
cp -r ~/my-project/code/* ./code/
cp -r ~/my-project/results/* ./results/

# 6. Edit documentation
nano README.md
nano METADATA.json

# 7. Commit
cd ../../..
git add research/ai/2024-12-01-my-awesome-project
git commit -m "Add my awesome AI project"
git push

# 8. Create PR on GitHub
```

---

**Ready to upload?** Start with Step 1 and follow the guide. Your research contributions are valuable!
