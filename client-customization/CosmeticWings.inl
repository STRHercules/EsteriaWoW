// Character Select only. The catalog is derived from installed Cosmetics state-kit attachments.
namespace
{
    struct CosmeticWing
    {
        unsigned spell;
        unsigned attachment;
        float scale;
        char model[260];
    };
    static_assert(sizeof(CosmeticWing) == 272);

    std::vector<CosmeticWing> const& CosmeticWings()
    {
        static std::vector<CosmeticWing> const wings = []
        {
            std::vector<CosmeticWing> result;
            FILE* file = CatalogFile(L"EsteriaCosmeticWings.bin");
            if (!file)
                return result;
            unsigned header[3]{};
            bool valid = std::fread(header, sizeof(header), 1, file) == 1
                && header[0] == 0x31475743 && header[1] == 1 && header[2] <= 4096;
            for (unsigned i = 0; valid && i < header[2]; ++i)
            {
                CosmeticWing wing{};
                valid = std::fread(&wing, sizeof(wing), 1, file) == 1 && wing.spell
                    && wing.attachment == 16 && std::isfinite(wing.scale) && wing.scale > 0
                    && wing.scale <= 100 && wing.model[0] && std::memchr(wing.model, 0, sizeof(wing.model));
                if (valid)
                    result.push_back(wing);
            }
            valid = valid && std::fgetc(file) == EOF;
            std::fclose(file);
            if (!valid)
                result.clear();
            return result;
        }();
        return wings;
    }

    std::unordered_map<std::uint64_t, unsigned> cosmeticWingRoster;
    std::unordered_map<void*, unsigned> cosmeticWingSelections;
    struct BoundCosmeticWing
    {
        void* instance;
        unsigned spell;
    };
    std::unordered_map<void*, BoundCosmeticWing> boundCosmeticWings;

    void ForgetCosmeticWing(void* character)
    {
        auto it = boundCosmeticWings.find(character);
        if (it == boundCosmeticWings.end())
            return;
        void* wing = it->second.instance;
        // Retain our own reference: a stock component refresh may already have detached the child.
        if (Field<void*>(wing, 0x48))
            Native<void(__thiscall*)(void*)>(0x008274F0)(wing);
        Native<void(__thiscall*)(void*)>(0x00824ED0)(wing);
        boundCosmeticWings.erase(it);
    }

    void UpdateCosmeticWing(void* character)
    {
        auto selected = cosmeticWingSelections.find(character);
        unsigned spell = selected == cosmeticWingSelections.end() ? 0 : selected->second;
        auto const& catalog = CosmeticWings();
        auto definition = std::find_if(catalog.begin(), catalog.end(),
            [spell](CosmeticWing const& wing) { return wing.spell == spell; });
        void* parent = Field<void*>(character, 0x38);
        auto bound = boundCosmeticWings.find(character);
        if (bound != boundCosmeticWings.end())
        {
            if (definition != catalog.end() && bound->second.spell == spell
                && parent && Field<void*>(bound->second.instance, 0x48) == parent)
                return;
            ForgetCosmeticWing(character);
        }
        if (definition == catalog.end() || !parent || !(Field<unsigned>(parent, 0x10) & 1)
            || !Native<int(__thiscall*)(void*, unsigned)>(0x008273D0)(parent, definition->attachment))
            return;
        void* scene = Field<void*>(parent, 0x28);
        if (!scene)
            return;
        void* child = Native<void*(__thiscall*)(void*, char const*, unsigned)>(0x0081F8F0)(
            scene, definition->model, 0);
        if (!child)
            return;
        Native<void(__thiscall*)(void*, int, int, int, int, float, int, int)>(0x00832AB0)(
            child, -1, 0, -1, 0, 1.0f, 1, 1);
        float origin[3]{};
        Native<void(__thiscall*)(void*, float const*, float, float)>(0x008251D0)(
            child, origin, 0, definition->scale);
        Native<void(__thiscall*)(void*, void*, unsigned, void*, int)>(0x00831630)(
            child, parent, definition->attachment, nullptr, 0);
        if (Field<void*>(child, 0x48) != parent)
        {
            Native<void(__thiscall*)(void*)>(0x00824ED0)(child);
            return;
        }
        boundCosmeticWings[character] = {child, spell};
    }
}
