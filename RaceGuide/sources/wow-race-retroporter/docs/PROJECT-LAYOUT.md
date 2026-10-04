# Project Layout

```text
wow-race-retroporter/
├── README.md
├── AGENTS.md
├── ARCHITECTURE.md
├── GUIDE.md
├── TOOLS.md
├── ROADMAP.md
├── config/
│   ├── project.yaml
│   ├── tools.yaml
│   └── race_ids.yaml
├── races/
│   ├── _template.yaml
│   └── maghar_orc.yaml
├── sources/
│   └── retail/
│       ├── build.yaml          # tracked source profile
│       ├── db2/                # downloaded targeted DB2s, ignored
│       └── races/              # per-race raw source caches, ignored
├── cache/
│   └── casc/                   # disposable CDN/CASC cache, ignored
├── tools/                      # local converter binaries, ignored
├── src/raceporter/
├── templates/
├── workspace/
│   ├── extracted/
│   ├── converted/
│   ├── generated/
│   ├── packages/
│   ├── state/
│   └── logs/
├── tests/
└── docs/
```

The repository contains four categories of content:

1. **Tracked project source/config/docs**: safe to commit and share.
2. **Raw Retail source caches**: selected DB2/assets under `sources/`, ignored and never packaged.
3. **Temporary downloads/tools**: `cache/` and third-party binaries under `tools/`, ignored.
4. **Generated working data**: conversion/generated/package/state/log files under `workspace/`, ignored by default.

A complete Retail installation is not a repository category. Local CASC mode points at an external or user-selected installation path.
