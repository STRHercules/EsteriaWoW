# Packaging Policy

A generated race package may contain derived/custom project files needed by the user's 3.3.5a setup, but package collection must reject these top-level source directories:

```text
sources/
cache/
tools/
```

This prevents raw Retail source assets, temporary CASC blocks, and third-party binaries from being swept into a release.

Package staging should normally draw from:

```text
workspace/generated/<race>/
workspace/converted/<race>/
```

Before enabling automated package creation, the `validate` stage must be implemented and successful. The scaffold intentionally leaves the real package stage blocked until deep validation exists.
