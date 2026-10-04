$ErrorActionPreference = "Stop"
py -3.12 -m venv .venv
& .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev]"
Write-Host "Bootstrap complete. Run: raceporter doctor"
Write-Host "Default Retail source mode is online; no full Retail install is required."
