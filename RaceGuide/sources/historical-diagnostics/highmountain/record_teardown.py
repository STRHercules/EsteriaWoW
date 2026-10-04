import sys
sys.path.insert(0, r'R:\Users\Zach\Documents\GitHub\EsteriaWoW\tools')
import highmountain_teardown_repair as repair

path = repair.h.ROOT / 'integration/acceptance.json'
data = repair.h.p.load_json(path)
data['complete_animation_tracks']['live_acceptance'] = (
    'User reported Highmountain gameplay fully working; shared logout/exit failure diagnosed separately')
data['native_teardown_issue'] = {
    'reported': 'Every character logout or client exit crashes; NPC despawn also reproduces while playing',
    'fault_site': '0074604E: GUID-field notification-list unlink writes through null previous link',
    'watchpoint_evidence': {
        'victim_unit': 'BFE634D0', 'npc_entry': 3209, 'link': 'BFE6351C',
        'initialized_link_value': 'BFE63519', 'corrupt_value': '00000000',
        'writer': '0040CC70', 'caller': '004D533B', 'source_unit': 'BFE62080',
        'copied_field_offset': '0000024C', 'absolute_update_field': '00000093'
    },
    'root_cause': 'Padding observer registration has no stock old-value cache slot; fallback copy '
                  'overruns NPC snapshot storage into the next unit notification-list link',
    'repair': 'Remove unsupported cached-field observer; read padding after object update; '
              'reject non-unit objects; invalidate appearance state before freeing component',
    'checks': 'x86 update/free thunks, retained AL ABI, source fingerprint/foundation/Lua validation, '
              'native material/customization harness, live sixth-byte changes, guarded item memory, '
              'freed-context invalidation and component address reuse',
    'fresh_client_memory': 'All 24 nearby NPC GUID-field lists intact, including the watched NPC',
    'installation': repair.h.p.load_json(repair.STAGE / 'last-install.json'),
    'live_acceptance': 'Pending repeated logout/relog, ordinary-race logout, full exit and visual regressions'
}
repair.h.save(path, data)
print('Acceptance report records the confirmed writer, installed repair and pending live checks.')
