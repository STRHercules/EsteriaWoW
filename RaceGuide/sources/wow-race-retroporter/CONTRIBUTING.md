# Contributing

Keep changes small, testable, and reproducible.

Before submitting changes:

```bash
pytest -q
python -m raceporter doctor
python -m raceporter fetch maghar_orc --dry-run
python -m raceporter build maghar_orc --dry-run
```

Do not commit downloaded Retail DB2s, M2/SKIN/SKEL/ANIM/BLP assets, CASC cache payloads, third-party tool binaries, generated MPQs, or mutable workspace output.

Changes to source acquisition must preserve both online and optional local source modes unless the architecture documentation explicitly changes.
