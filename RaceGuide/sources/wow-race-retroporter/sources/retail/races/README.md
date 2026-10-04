# Per-Race Retail Source Cache

`raceporter fetch <race>` targets this directory.

Expected shape:

```text
races/
└── maghar_orc/
    ├── manifest.json
    ├── inventory.json
    ├── male/
    │   ├── model/
    │   ├── animations/
    │   ├── textures/
    │   └── customization/
    └── female/
        ├── model/
        ├── animations/
        ├── textures/
        └── customization/
```

These files are source assets, not distributable project output. They are ignored by Git and packaging.
