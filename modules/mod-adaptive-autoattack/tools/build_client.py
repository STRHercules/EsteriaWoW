#!/usr/bin/env python3
"""Build patches from a user's own client. Never modify the supplied client."""
from pathlib import Path
import argparse,hashlib,json,struct
from lib.clientfs import ClientFiles
from lib.mpq import MPQArchive,write_archive

def unpack(data):
    magic,n,f,r,s=struct.unpack_from('<4s4I',data)
    if magic!=b'WDBC' or r!=f*4 or len(data)!=20+n*r+s: raise ValueError('Unsupported DBC layout')
    return [list(struct.unpack_from('<'+'I'*f,data,20+i*r)) for i in range(n)],bytearray(data[20+n*r:]),f
def pack(rows,strings,f):
    return struct.pack('<4s4I',b'WDBC',len(rows),f,4*f,len(strings))+b''.join(struct.pack('<'+'I'*f,*row) for row in rows)+strings
def name(row,strings,text):
    for i in range(136,152):row[i]=0
    row[136]=len(strings);strings.extend(text.encode()+b'\0')

def description(row,strings,text):
    # Do not inherit class-specific Auto Shot text (including Hunter haste).
    for i in range(170,186):row[i]=0
    row[170]=len(strings);strings.extend(text.encode()+b'\0')
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--client',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--locale',default='enUS')
    args=parser.parse_args()
    client=args.client.resolve();out=args.output.resolve()
    if out==client or out.is_relative_to(client):raise SystemExit('Output must be outside the client directory.')
    if out.exists():raise SystemExit('Output already exists; choose a new directory to preserve prior builds.')
    data_dir=client/'Data'
    with ClientFiles(str(data_dir),args.locale) as fs:
        spells,_=fs.find('DBFilesClient\\Spell.dbc')
        abilities,_=fs.find('DBFilesClient\\SkillLineAbility.dbc')
    rows,strings,f=unpack(spells)
    if f!=234:raise ValueError('Requires the 3.3.5a Spell.dbc layout')
    byid={row[0]:row for row in rows}
    if any(id in byid for id in (970100,970101,970102)):raise ValueError('Reserved spell IDs already exist; merge manually before upgrading.')
    for src,id,label in ((75,970100,'Auto Ranged'),(2764,970101,'Auto Throw'),(5019,970102,'Wand Attack')):
        row=byid[src].copy();row[0]=id;row[6]|=0x20;row[208:212]=[0]*4
        name(row,strings,label)
        description(row,strings,{
            970100:'Automatically attacks with your equipped ranged weapon. Switches to melee when the target is in melee range and resumes ranged attacks when the target moves away. Normal weapon requirements apply.',
            970101:'Automatically attacks with your equipped thrown weapon.',
            970102:'Automatically attacks with your equipped wand.',
        }[id])
        if id==970100:row[69]=262156|65536|524288
        else:row[4]|=0x80
        if id==970101:
            row[5]&=~0x200
            row[6]&=~0x100000
        rows.append(row)
    name(byid[6603],strings,'Auto Melee')
    sla,sla_strings,sla_fields=unpack(abilities)
    if sla_fields!=14:raise ValueError('Unsupported SkillLineAbility layout')
    if any(row[0] in (970100,970101,970102) for row in sla):raise ValueError('Reserved skill mapping IDs already exist')
    for id in (970100,970101,970102):sla.append([id,183,id,0,0,0,0,0,0,0,0,0,0,0])
    payload={'DBFilesClient\\Spell.dbc':pack(rows,strings,f),'DBFilesClient\\SkillLineAbility.dbc':pack(sla,sla_strings,sla_fields)}
    out.mkdir(parents=True)
    manifest={}
    for relative in ('Data/patch-Z.MPQ',f'Data/{args.locale}/patch-{args.locale}-Z.MPQ'):
        existing=client/relative;files={}
        if existing.exists():
            archive=MPQArchive(existing)
            names=archive.read_file('(listfile)').decode().splitlines()
            files={n:archive.read_file(n) for n in names if n and n not in ('(listfile)','(attributes)')}
        files.update(payload)
        target=out/relative;target.parent.mkdir(parents=True,exist_ok=True);write_archive(target,files)
        check=MPQArchive(target)
        for key,value in files.items():assert check.read_file(key)==value
        manifest[relative]={'previous_sha256':hashlib.sha256(existing.read_bytes()).hexdigest() if existing.exists() else None,'sha256':hashlib.sha256(target.read_bytes()).hexdigest()}
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2))
    print('Verified both client patches. Original client unchanged. Back up client archives and close WoW before copying generated files.')
if __name__=='__main__':main()
