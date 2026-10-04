import json
import struct
import subprocess
from pathlib import Path

from minidump.minidumpfile import MinidumpFile
from minidump.constants import MINIDUMP_STREAM_TYPE
MINIDUMP_STREAM_TYPE._missing_ = classmethod(lambda cls, value: cls.UnusedStream)

dump = MinidumpFile.parse('G:/3.3.5a - Dev/Errors/2026-10-01 00.22.34 Crash.dmp')
reader = dump.get_reader()

def read(address, size):
    try:
        return reader.read(address, size)
    except Exception:
        return b''

def u(address):
    return int.from_bytes(read(address, 4), 'little')

for frame in (0x0dd3f834, 0x0dd3f8a4, 0x0dd3fa68):
    print(hex(frame), [(hex(frame+i),hex(u(frame+i))) for i in range(-24,40,4)])
    for offset in (8,12,16,20):
        pointer=u(frame+offset)
        print('ARG',hex(pointer),read(pointer,80).hex())
print('timestamp descriptor', read(0x072bb878,32).hex())
model=u(0x44f1cb70+0x2c)
header=u(model+0x150)
print('model',hex(model),read(model+0x3c,180).split(b'\0')[0], 'header',hex(header))
print('bone array',hex(u(header+48)),u(header+44))
print('bone1',read(u(header+48)+88,88).hex())
for track_at in (0x072bb864,0x072bb878,0x072bb88c):
    times=u(track_at+8)
    print('track',hex(track_at),'slot58',read(times+58*8,8).hex(),'slot81',read(times+81*8,8).hex())

sql = '''SELECT guid,name,race,class,gender,online FROM acore_characters.characters WHERE race IN (45,52,53);
SHOW COLUMNS FROM acore_world.playercreateinfo_skills;
SELECT * FROM acore_world.playercreateinfo_skills WHERE raceMask <> 0 LIMIT 3;
SELECT c.guid,c.race,s.skill,s.value,s.max FROM acore_characters.characters c
LEFT JOIN acore_characters.character_skills s ON s.guid=c.guid
AND s.skill IN (98,109,111,113,115,137,138,139,140,141,313,315,673,759) WHERE c.race IN (45,52,53);
SELECT c.guid,c.race,s.spell,s.active,s.disabled FROM acore_characters.characters c
LEFT JOIN acore_characters.character_spell s ON s.guid=c.guid
AND s.spell IN (668,669,670,671,672,813,814,815,816,817,7340,7341,17737,29932) WHERE c.race IN (45,52,53);'''
result = subprocess.run(['docker','exec','-i','ac-database','sh','-c',
    'MYSQL_PWD="$MYSQL_ROOT_PASSWORD" mysql -uroot --batch'],input=sql,text=True,capture_output=True)
print(result.stdout,result.stderr)
