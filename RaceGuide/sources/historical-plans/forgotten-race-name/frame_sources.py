"""Record the winning native race-label consumers for the requested in-game UI."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'tools'))
import retroported_race_pack as p

with p.ClientFiles(str(p.CLIENT_DEFAULT / 'Data'), 'enUS') as client:
    for name in ('PaperDollFrame.lua', 'CharacterFrame.lua', 'GameTooltip.lua', 'TargetFrame.lua', 'PlayerFrame.lua'):
        data, winner = client.find('Interface\\FrameXML\\' + name)
        lines = data.decode('utf-8-sig').splitlines()
        for index, line in enumerate(lines):
            if 'UnitRace(' in line:
                print(name, winner, index + 1, '\n'.join(lines[max(0, index - 2):index + 5]))
