# Retail Source Cache

This directory contains the tracked Retail source profile plus local, ignored extraction caches.

- `build.yaml` selects online or local source mode and pins the Retail product/build policy.
- `db2/` receives only DB2 tables required for race discovery and customization analysis.
- `races/<slug>/` receives only assets resolved for that race, such as M2, SKIN, SKEL, ANIM, BLP, and normalized source manifests.

Do not place a complete Retail client here. Raw Blizzard assets are ignored by Git and excluded from generated packages.
