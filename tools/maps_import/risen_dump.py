import sys, collections
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parent))
import lib, sirus
S = sirus.Sirus()
print('archives', len(S.handles))
T = {}
for t in ('Map','AreaTable','WorldMapArea','WorldMapOverlay','AreaPOI','WorldSafeLocs','AreaTrigger','LoadingScreens','Light','LightParams','LightSkybox','ZoneMusic','ZoneIntroMusicTable','SoundAmbience','SoundEntries','LightIntBand','LightFloatBand'):
    r = S.read_from(f'DBFilesClient\{t}.dbc')
    print(t, None if r is None else (r[0], len(r[1])), S.providers(f'DBFilesClient\{t}.dbc')[:4])
    if r: T[t] = lib.Dbc(r[1])
m = T['Map'].get(10001); print('Map', m[:5], lib.loc_texts(T['Map'], m, 5)[7:10], 'area', m[22], 'loading', m[57], 'desc', [lib.best_loc(T['Map'], m, s) for s in (23, 40)], m[58:66])
at = T['AreaTable']
rows = [r for r in at.rows if r[1] == 10001 or r[0] in (10050,10004,10433,10465)]
for r in rows: print('AT', r[0], 'cont', r[1], 'par', r[2], 'bit', r[3], 'fl', r[4], r[5:11], repr(lib.best_loc(at, r, 11)), r[28:36])
wma=T['WorldMapArea']
for r in wma.rows:
    if r[1]==10001: print('WMA', r[:3], wma.text(r[3]), [lib.u2f(x) for x in r[4:8]], r[8:])
wmo=T['WorldMapOverlay']; ids={r[0] for r in wma.rows if r[1]==10001}
for r in wmo.rows:
    if r[1] in ids: print('WMO', r[0], r[1], r[2:6], wmo.text(r[8]), r[9:])
poi=T['AreaPOI']
for r in poi.rows:
    if r[15]==10001: print('POI', r[0], repr(lib.best_loc(poi,r,18)), repr(lib.best_loc(poi,r,35)), r[1], r[2:11], r[16], r[17], r[52], r[53])
wsl=T['WorldSafeLocs']
for r in wsl.rows:
    if r[1]==10001: print('WSL', r[0], [lib.u2f(x) for x in r[2:5]], repr(lib.best_loc(wsl,r,5)))
for r in T['AreaTrigger'].rows:
    if r[1]==10001: print('TRG', r[0], [lib.u2f(x) for x in r[2:6]], r[6:])
ls=T['LoadingScreens']; m=T['Map'].get(10001); lr=ls.get(m[57]); print('LS', lr[0], ls.text(lr[1]), ls.text(lr[2]), lr[3])
lt=T['Light']
for r in lt.rows:
    if r[1]==10001: print('LIGHT', r[0], [lib.u2f(x) for x in r[2:7]], r[7:15])
