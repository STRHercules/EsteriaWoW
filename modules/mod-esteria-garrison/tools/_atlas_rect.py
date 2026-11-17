import importlib.util
from pathlib import Path
p = Path(r"g:\risServer\EsteriaWoW\modules\mod-esteria-garrison\tools\build_retail_architect.py")
spec = importlib.util.spec_from_file_location("arch", p)
arch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(arch)
members, sheets = arch.load_atlases()
name = "Garr_MissionList-IconBG"
print(name, members.get(name))
# sheets keyed by atlas id; member tuple includes atlas
print("sheets sample", list(sheets.items())[:1])
