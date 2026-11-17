"""Check cosmetic spell routing against the actual spellbook Lua."""
from pathlib import Path
import unittest

from lupa.lua51 import LuaRuntime


class CosmeticSpellbookTest(unittest.TestCase):
    def setUp(self):
        self.lua = LuaRuntime(unpack_returned_tuples=True)
        self.lua.execute("""
            bit = { band = function() return 0 end }
            addon = { SpellbookModule = { CLASS=1, GENERAL=2, PET=3, COSMETIC=4 } }
            known = {}
            function IsSpellKnown(id) return known[id] end
            function GetNumSpellTabs() return #tabs end
            function GetSpellTabInfo(tab) return tab == 1 and 'General' or 'Arms' end
            function GetTalentTabInfo(tree) return 'Tree' .. tree end
            function CreateFrame() return { SetScript=function() end, RegisterEvent=function() end } end
        """)
        source = Path(__file__).resolve().parents[1] / (
            "client-customization/DragonUICosmeticTab/spellbook/book_catalog.lua"
        )
        self.lua.execute(source.read_text(encoding="utf-8"), "DragonUI", self.lua.globals().addon)
        self.lua.execute("""
            Book = addon.SpellbookModule
            tabs = { {}, {} }
            function Book.ReadTab(tab) return tabs[tab] end
            filters = { hideUnlearned=true, allRanks=false }
            function add(tab, id, name)
                table.insert(tabs[tab], { spellID=id, name=name, book='spell', index=id })
                known[id] = true
            end
        """)

    def test_all_emotes_move_out_of_general_and_hero_into_named_sections(self):
        self.lua.execute("""
            add(1, 9500100, 'Teleport: Home')
            add(2, 100, 'Class ability')
            add(1, 970200, 'Wings A')
            add(2, 970201, 'Wings B')
            for id = 9500103, 9500210 do add(id % 2 + 1, id, 'Emote ' .. id) end
            local cosmetics = Book.BuildSections(Book.COSMETIC, filters)
            assert(#cosmetics == 2)
            assert(cosmetics[1].title == 'Wings' and #cosmetics[1].entries == 2)
            assert(cosmetics[2].title == 'Emotes' and #cosmetics[2].entries == 108)
            local general = Book.BuildSections(Book.GENERAL, filters)
            assert(#general == 1 and #general[1].entries == 1)
            assert(general[1].entries[1].spellID == 9500100)
            local hero = Book.BuildSections(Book.CLASS, filters)
            assert(#hero == 1 and #hero[1].entries == 1 and hero[1].entries[1].spellID == 100)
        """)

    def test_emote_only_character_gets_cosmetics_and_search_keeps_section(self):
        self.lua.execute("""
            add(1, 9500200, 'Closed')
            assert(Book.CategoryExists(Book.COSMETIC))
            filters.query = 'closed'
            local sections = Book.BuildSections(Book.COSMETIC, filters)
            assert(#sections == 1 and sections[1].title == 'Emotes')
            assert(#sections[1].entries == 1 and sections[1].entries[1].name == 'Closed')
            filters.query = 'missing'
            assert(#Book.BuildSections(Book.COSMETIC, filters) == 0)
        """)


if __name__ == "__main__":
    unittest.main()
