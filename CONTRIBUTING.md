# Contributing to Tooki Research Lab

Thank you for contributing to our research archive! This guide will help you organize and upload your research effectively.

## Getting Started

1. Fork the repository
2. Create a branch for your research upload
3. Follow the structure guidelines below
4. Submit a pull request with clear descriptions

## Research Structure

### Naming Conventions

Use descriptive, hyphen-separated names:
- Projects: `YYYY-MM-DD-project-name`
- Files: `lowercase-with-hyphens.ext`
- Avoid spaces and special characters

### Required Files

Each research project must include:

#### 1. README.md
```markdown
# Project Title

## Overview
Brief description of the research

## Objectives
- Key goal 1
- Key goal 2

## Methodology
How the research was conducted

## Results
Key findings and outcomes

## References
Related work and citations
```

#### 2. METADATA.json
```json
{
  "title": "Project Title",
  "date": "YYYY-MM-DD",
  "authors": ["Author 1", "Author 2"],
  "tags": ["ai", "machine-learning", "nlp"],
  "category": "ai|code|papers|experiments",
  "status": "completed|in-progress|archived",
  "related": ["link-to-related-project"]
}
```

## Content Guidelines

### Code
- Include comments and documentation
- Provide setup instructions
- List dependencies in requirements.txt or package.json
- Include sample usage and examples

### Data
- Large datasets should use Git LFS or external links
- Include data descriptions and schemas
- Document preprocessing steps
- Provide sample data when possible

### Papers and Documents
- Use Markdown for text content when possible
- Include PDF versions for formal papers
- Add BibTeX citations
- Link to published versions

### Experiments
- Document experimental setup
- Include configuration files
- Provide reproducibility instructions
- Save result visualizations

## Upload Process

1. **Organize Your Content**
   - Place files in appropriate category folder
   - Create dated project directory
   - Add all required metadata

2. **Document Everything**
   - Write clear README files
   - Add inline code comments
   - Include setup instructions
   - Document any dependencies

3. **Test Locally**
   - Verify all links work
   - Check that examples run
   - Validate JSON metadata
   - Review for sensitive information

4. **Submit Pull Request**
   - Clear title and description
   - List main contributions
   - Mention any special considerations
   - Link related issues

## Best Practices

### DO
- ✅ Use clear, descriptive names
- ✅ Include comprehensive documentation
- ✅ Add proper attribution and citations
- ✅ Test code before uploading
- ✅ Use version control effectively
- ✅ Keep file sizes reasonable

### DON'T
- ❌ Upload binary files without Git LFS
- ❌ Include API keys or credentials
- ❌ Skip documentation
- ❌ Use proprietary data without permission
- ❌ Upload excessively large files
- ❌ Include personal or sensitive information

## Categories

### AI Research (`/research/ai`)
- Machine learning models
- Deep learning experiments
- NLP projects
- Computer vision
- Reinforcement learning

### Code Research (`/research/code`)
- Algorithm implementations
- Software engineering studies
- Programming language research
- Development tools
- Code optimization

### Papers (`/research/papers`)
- Research papers
- Technical reports
- Literature reviews
- Survey papers

### Experiments (`/research/experiments`)
- Experimental setups
- Result data
- Analysis notebooks
- Comparative studies

## Questions?

If you have questions about contributing:
1. Check existing research for examples
2. Review the documentation in `/docs`
3. Open an issue for clarification
4. Contact the maintainers

Thank you for contributing to Tooki Research Lab!
