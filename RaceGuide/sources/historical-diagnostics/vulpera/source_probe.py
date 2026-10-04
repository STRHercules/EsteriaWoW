import json, sys, struct
from pathlib import Path
sys.path.insert(0, r'R:\Users\Zach\Documents\GitHub\EsteriaWoW\tools')
import vulpera_race_pack as v
from wotlkconv.m2 import parse_m2, parse_skin
from PIL import Image
layouts=v.p.load_json(v.ROOT/'reports/texture-layouts.json')
print('LAYERS', layouts.get('ChrModelTextureLayer'), 'MATS', layouts.get('ChrModelMaterial'))
for sex in ('male','female'):
    source=next((v.SOURCE/'custom/vulpera/character/vulpera'/sex).glob('*.m2'))
    m=parse_m2(source.read_bytes()); raw=parse_m2((v.ROOT/'raw'/f'{v.MODELS[sex]}.m2').read_bytes())
    skin=parse_skin(source.with_name(source.stem+'00.skin').read_bytes())
    print('MODEL',sex,source,[(i,t['type'],t['filename']) for i,t in enumerate(m.textures)], 'RAW',raw.texture_file_ids)
    print('GEOS',[(v.e.v.u16(x,0),v.e.v.u16(x,6),v.e.v.u16(x,10)) for x in skin.submeshes])
    print('ATTACH',[(a.get('id'),a) for a in m.attachments if a.get('id')==11])
    for i,b in enumerate(skin.batches):
        print('BATCH',i, 'mesh',v.e.v.u16(b,4), 'shader',v.e.v.u16(b,2),'combo',m.texture_combos[v.e.v.u16(b,16):v.e.v.u16(b,16)+v.e.v.u16(b,14)])
    for i,o in enumerate(v.audit()[sex]['options']):
        print('OPT',i,o['label'],[(c['ID'],c.get('Name_lang'),[(e['ChrCustomizationGeosetID'],e['ChrCustomizationMaterialID'],e['RelatedChrCustomizationChoiceID']) for e in c['elements']]) for c in o['choices']])
