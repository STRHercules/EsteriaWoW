$ErrorActionPreference = "Stop"
pytest -q
python -m raceporter doctor
python -m raceporter fetch maghar_orc --dry-run
python -m raceporter plan maghar_orc
python -m raceporter build maghar_orc --dry-run
