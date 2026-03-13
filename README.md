# Victor Intelligence System — Unified Monorepo

This repository is a unified monorepo that combines the following sub-repositories via `git subtree`:

| Directory | Source Repository |
|-----------|-------------------|
| `Victor_Synthetic_Super_Intelligence/` | https://github.com/MASSIVEMAGNETICS/Victor_Synthetic_Super_Intelligence |
| `tooki/` | https://github.com/MASSIVEMAGNETICS/tooki |
| `conscious-river/` | https://github.com/MASSIVEMAGNETICS/conscious-river |

## Updating a subtree

To pull the latest changes from an upstream repository into a subtree prefix:

```bash
git subtree pull --prefix=Victor_Synthetic_Super_Intelligence https://github.com/MASSIVEMAGNETICS/Victor_Synthetic_Super_Intelligence.git main
git subtree pull --prefix=tooki https://github.com/MASSIVEMAGNETICS/tooki.git main
git subtree pull --prefix=conscious-river https://github.com/MASSIVEMAGNETICS/conscious-river.git main
```
