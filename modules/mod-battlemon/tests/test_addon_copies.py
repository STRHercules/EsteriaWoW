"""The addon source in the repo must equal both copies in the 3d-version package.

    python tests/test_addon_copies.py "<package root, e.g. G:/Downloads/HDWoWModels/3d-version>"

Fix any difference with tools/sync_addon.py (--from-package or --to-package).
"""
import os
import subprocess
import sys

tool = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'tools', 'sync_addon.py')
result = subprocess.run([sys.executable, tool, sys.argv[1]], capture_output=True, text=True)
print(result.stdout.strip())
sys.exit(result.returncode)
