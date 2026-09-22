from pathlib import Path
import subprocess,os
import tempfile,shlex
workspace=None
if os.environ.get('AAA_TEST_DIR'):
    out=Path(os.environ['AAA_TEST_DIR']);out.mkdir(parents=True,exist_ok=True)
else:
    workspace=tempfile.TemporaryDirectory()
    out=Path(workspace.name)
stub=r'''
#pragma once
#include <cstdint>
#include <cassert>
using uint32=uint32_t;
struct ObjectGuid { uint32 id=0; uint32 GetCounter() const{return id;} bool operator==(ObjectGuid b)const{return id==b.id;} bool operator!=(ObjectGuid b)const{return id!=b.id;} };
enum {RANGED_ATTACK, CURRENT_AUTOREPEAT_SPELL, UNIT_STATE_MELEE_ATTACKING, SHEATH_STATE_RANGED, SHEATH_STATE_MELEE, TRIGGERED_NONE, SPELL_CAST_OK};
enum {ITEM_SUBCLASS_WEAPON_BOW=2,ITEM_SUBCLASS_WEAPON_GUN=3,ITEM_SUBCLASS_WEAPON_CROSSBOW=18,ITEM_SUBCLASS_WEAPON_THROWN=16,ITEM_SUBCLASS_WEAPON_WAND=19};
struct ItemTemplate {uint32 SubClass=2;};
struct Item { ItemTemplate value; ItemTemplate* GetTemplate(){return &value;} };
struct Unit {ObjectGuid guid{2};bool alive=true;bool near=false; ObjectGuid GetGUID(){return guid;}bool IsAlive(){return alive;} };
struct Spell;
struct Player:Unit {
    Unit* victim=nullptr;Spell* current=nullptr;Item item;bool melee=false,moving=false;int sheath=0,stopPackets=0,shots=0;
    Player(){guid.id=1;}
    Item* GetWeaponForAttack(int,bool){return &item;} bool HasSpell(uint32 id){return id!=75;}
    Spell* GetCurrentSpell(int){return current;}void InterruptSpell(int){current=nullptr;}
    bool IsMounted(){return false;} bool IsValidAttackTarget(Unit*t){return t&&t->alive;}
    bool IsWithinMeleeRange(Unit*t){return t->near;} void ClearUnitState(int){melee=false;}
    void Attack(Unit*t,bool m){victim=t;melee=m;} Unit* GetVictim(){return victim;}
    void SendMeleeAttackStop(Unit*){++stopPackets;}void SetSheath(int s){sheath=s;}
    bool isMoving(){return moving;}bool IsNonMeleeSpellCast(bool,bool,bool){return false;}
    void AttackStop();
};
struct SpellInfo {uint32 Id;};
struct SpellCastTargets {Unit* target=nullptr;void SetUnitTarget(Unit*t){target=t;}ObjectGuid GetUnitTargetGUID(){return target->guid;} };
struct Spell { Player*p;SpellInfo const*info;SpellCastTargets m_targets;
    Spell(Player*a,SpellInfo const*b,int):p(a),info(b){} SpellInfo const*GetSpellInfo(){return info;}
    void InitExplicitTargets(SpellCastTargets const&t){m_targets=t;}int CheckCast(bool){return SPELL_CAST_OK;}
    void prepare(SpellCastTargets const*t){m_targets=*t;p->current=this;++p->shots;}
};
struct Manager {SpellInfo native{75};SpellInfo info[3]={{970100},{970101},{970102}};SpellInfo const*GetSpellInfo(uint32 id){return id==75?&native:&info[id-970100];}};
inline Manager manager;inline Manager*sSpellMgr=&manager;
namespace ObjectAccessor { inline Unit*GetUnit(Player&p,ObjectGuid id){return p.victim&&p.victim->guid==id?p.victim:nullptr;} }
#define LOG_INFO(...) ((void)0)
#define LOG_DEBUG(...) ((void)0)
struct Config { template<class T> T GetOption(char const*,T value){return value;} };
inline Config config;inline Config*sConfigMgr=&config;
'''
(out/'stub.h').write_text(stub)
for name in ('Player.h','Item.h','ObjectAccessor.h','Spell.h','SpellInfo.h','SpellMgr.h','Log.h','Config.h'):
    (out/name).write_text('#include "stub.h"\n')
source=(Path(__file__).resolve().parents[1]/'src/AdaptiveAutoAttack.cpp').resolve().as_posix()
test=r'''
void Player::AttackStop(){victim=nullptr;melee=false;}
int main(){
 { Player p; Unit enemy; Spell native(&p,sSpellMgr->GetSpellInfo(75),TRIGGERED_NONE);
   SpellCastTargets t;t.SetUnitTarget(&enemy);native.prepare(&t);
   RangedAutoStop(&p);assert(p.current==&native);p.InterruptSpell(CURRENT_AUTOREPEAT_SPELL); }
 for(uint32 kind:{2u,3u,18u,16u,19u}){
  Player p;Unit enemy;p.item.value.SubClass=kind;
  RangedAutoStart(&p,&enemy);assert(!p.melee&&p.victim==&enemy&&p.stopPackets==1);
  RangedAutoUpdate(&p,1);assert(!p.current);
  RangedAutoClientCancel(&p);RangedAutoUpdate(&p,100);assert(p.current&&!p.melee);
  assert(p.current->GetSpellInfo()->Id==(kind==16?970101u:kind==19?970102u:75u));
  auto first=p.current;RangedAutoUpdate(&p,300);assert(p.current==first);
  enemy.near=true;RangedAutoUpdate(&p,100);assert(p.melee&&!p.current);
  RangedAutoClientCancel(&p);assert(p.victim==&enemy&&p.melee);
  enemy.near=false;RangedAutoUpdate(&p,100);assert(!p.melee&&!p.current);
  RangedAutoClientCancel(&p);RangedAutoUpdate(&p,100);assert(p.current&&!p.melee);
  RangedAutoClientCancel(&p);assert(!p.current&&!p.victim);
  RangedAutoUpdate(&p,2000);assert(!p.current&&!p.victim);
  RangedAutoStart(&p,&enemy);p.AttackStop();RangedAutoUpdate(&p,2000);assert(!p.current&&!p.victim);
  RangedAutoStart(&p,&enemy);RangedAutoUpdate(&p,1100);assert(p.current); // client sends no acknowledgement
  enemy.alive=false;RangedAutoUpdate(&p,100);assert(!p.current);
 }
}
'''
(out/'test.cpp').write_text('#include "'+source+'"\n'+test)
command=shlex.split(os.environ.get('CXX','c++'))
subprocess.run(command+['-std=c++17','-I'+str(out),str(out/'test.cpp'),'-o',str(out/'test.exe')],check=True)
subprocess.run([str(out/'test.exe')],check=True)
print('PASS: packaged controller transitions and explicit stop cases with stubbed core.')
