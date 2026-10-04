import json
import re
from pathlib import Path

root = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW")
registry = root / "modules/mod-custom-server/data/races/race_registry.json"
text = registry.read_text()
data = json.loads(text)
start = text.index('  "npc_only": [')
end = text.index('\n  ],', start) + len('\n  ],')
text = text[:start] + '  "npc_only": [\n' + ',\n'.join(
    '    ' + json.dumps(row) for row in data['npc_only']) + '\n  ],' + text[end:]
registry.write_text(text, encoding='utf-8', newline='\n')
sql = root / "data/sql/updates/pending_db_world/rev_20261001100000000.sql"
assert ';;' not in sql.read_text()
parts = sql.read_text().split('SET @EARTHEN := ')[1:]
assert [p.split(';')[0] for p in parts] == ['48', '49']
for part in parts:
    assert len(re.findall('DELETE FROM', part)) == 7
    assert len(re.findall('INSERT INTO', part)) == 7
print('Earthen SQL: scoped idempotent rows, races 48/49; schema reused')
