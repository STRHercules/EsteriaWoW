// Included in NativeAppearance.cpp's private namespace after the shared selection reader.
struct HaranirImages
{
    std::array<std::uint8_t, 13> fields{};
    unsigned race = 0;
    unsigned gender = 2;
    std::array<std::string, 9> paths;
    std::array<std::shared_ptr<void>, 9> textures;
    std::string lower;
    std::string upper;
};

std::unordered_map<void*, HaranirImages> haranirImages;

bool WriteHaranirBlp(std::string const& relative, std::vector<unsigned char> pixels,
    unsigned width, unsigned height, bool indexed)
{
    char executable[MAX_PATH]{};
    if (!GetModuleFileNameA(nullptr, executable, MAX_PATH))
        return false;
    char* slash = std::strrchr(executable, '\\');
    if (!slash)
        return false;
    slash[1] = 0;
    std::string absolute = executable + relative;
    FILE* existing = nullptr;
    if (!fopen_s(&existing, absolute.c_str(), "rb"))
    {
        unsigned char header[24]{};
        bool cached = std::fread(header, sizeof(header), 1, existing) == 1
            && !std::memcmp(header, "BLP2", 4) && header[8] == (indexed ? 1 : 3)
            && Field<unsigned>(header, 20) == 1172 && header[11] == 1
            && Field<unsigned>(header, 12) == width && Field<unsigned>(header, 16) == height;
        std::fclose(existing);
        if (cached)
            return true;
    }
    using Microsoft::WRL::ComPtr;
    struct Apartment
    {
        HRESULT result = CoInitializeEx(nullptr, COINIT_APARTMENTTHREADED);
        ~Apartment()
        {
            if (SUCCEEDED(result))
                CoUninitialize();
        }
    } apartment;
    if (FAILED(apartment.result) && apartment.result != RPC_E_CHANGED_MODE)
        return false;
    ComPtr<IWICImagingFactory> factory;
    ComPtr<IWICPalette> palette;
    if (indexed && (FAILED(CoCreateInstance(CLSID_WICImagingFactory, nullptr, CLSCTX_INPROC_SERVER,
        IID_PPV_ARGS(&factory))) || FAILED(factory->CreatePalette(&palette))))
        return false;
    std::vector<unsigned char> data(1172);
    std::memcpy(data.data(), "BLP2", 4);
    Field<unsigned>(data.data(), 4) = 1;
    data[8] = indexed ? 1 : 3;
    data[9] = indexed ? 0 : 8;
    data[10] = 8;
    data[11] = 1;
    Field<unsigned>(data.data(), 12) = width;
    Field<unsigned>(data.data(), 16) = height;
    for (unsigned mip = 0; mip < 16; ++mip)
    {
        std::vector<unsigned char> level;
        if (indexed)
        {
            ComPtr<IWICBitmap> bitmap;
            ComPtr<IWICFormatConverter> converter;
            if (FAILED(factory->CreateBitmapFromMemory(width, height, GUID_WICPixelFormat32bppRGBA,
                width * 4, static_cast<UINT>(pixels.size()), pixels.data(), &bitmap)))
                return false;
            if (!mip)
            {
                if (FAILED(palette->InitializeFromBitmap(bitmap.Get(), 256, FALSE)))
                    return false;
                WICColor colors[256]{};
                UINT count = 0;
                if (FAILED(palette->GetColors(256, colors, &count)))
                    return false;
                for (unsigned i = 0; i < count; ++i)
                    Field<unsigned>(data.data(), 148 + i * 4) = colors[i] & 0xffffff;
            }
            level.resize(width * height);
            if (FAILED(factory->CreateFormatConverter(&converter))
                || FAILED(converter->Initialize(bitmap.Get(), GUID_WICPixelFormat8bppIndexed,
                    WICBitmapDitherTypeNone, palette.Get(), 0, WICBitmapPaletteTypeCustom))
                || FAILED(converter->CopyPixels(nullptr, width, static_cast<UINT>(level.size()), level.data())))
                return false;
        }
        else
        {
            level = pixels;
            for (unsigned i = 0; i < level.size(); i += 4)
                std::swap(level[i], level[i + 2]);
        }
        Field<unsigned>(data.data(), 20 + mip * 4) = static_cast<unsigned>(data.size());
        Field<unsigned>(data.data(), 84 + mip * 4) = static_cast<unsigned>(level.size());
        data.insert(data.end(), level.begin(), level.end());
        if (width == 1 || height == 1)
            break;
        unsigned nextWidth = (std::max)(1u, width / 2);
        unsigned nextHeight = (std::max)(1u, height / 2);
        std::vector<unsigned char> smaller(nextWidth * nextHeight * 4);
        for (unsigned y = 0; y < nextHeight; ++y)
            for (unsigned x = 0; x < nextWidth; ++x)
                for (unsigned channel = 0; channel < 4; ++channel)
                {
                    unsigned sum = 0;
                    for (unsigned dy = 0; dy < 2; ++dy)
                        for (unsigned dx = 0; dx < 2; ++dx)
                            sum += pixels[((y * 2 + dy) * width + x * 2 + dx) * 4 + channel];
                    smaller[(y * nextWidth + x) * 4 + channel] = static_cast<unsigned char>(sum / 4);
                }
        pixels = std::move(smaller);
        width = nextWidth;
        height = nextHeight;
    }
    for (std::size_t i = std::strlen(executable); i < absolute.size(); ++i)
        if (absolute[i] == '\\')
            CreateDirectoryA(absolute.substr(0, i).c_str(), nullptr);
    std::string temporary = absolute + ".next";
    FILE* file = nullptr;
    if (fopen_s(&file, temporary.c_str(), "wb"))
        return false;
    bool written = std::fwrite(data.data(), 1, data.size(), file) == data.size();
    written = std::fclose(file) == 0 && written;
    if (!written || !MoveFileExA(temporary.c_str(), absolute.c_str(),
        MOVEFILE_REPLACE_EXISTING | MOVEFILE_WRITE_THROUGH))
    {
        DeleteFileA(temporary.c_str());
        return false;
    }
    return true;
}

template<class Options>
bool ComposeHaranir(void* character, Options const& options, HaranirImages& images)
{
    auto fields = HighmountainFields(character);
    auto const network = earthenNetworkAppearance.find(character);
    if (network != earthenNetworkAppearance.end())
    {
        fields = network->second;
        SetHighmountainFields(character, fields);
    }
    unsigned gender = Field<unsigned>(character, 0x1C);
    unsigned race = Field<unsigned>(character, 0x18);
    if (!ValidateExtended(race, gender, fields))
        return false;
    if (images.race == race && images.gender == gender && images.fields == fields)
        return true;
    FILE* input = CatalogFile(RetailTextureBank(race));
    if (!input)
        return false;
    unsigned header[4]{};
    bool valid = std::fread(header, sizeof(header), 1, input) == 1 && header[0] == 0x31544845
        && header[1] == 1 && header[2] <= 4096;
    HaranirImages next;
    next.fields = fields;
    next.race = race;
    next.gender = gender;
    auto decompress = reinterpret_cast<LONG(WINAPI*)(USHORT, PUCHAR, ULONG, PUCHAR, ULONG, PULONG)>(
        GetProcAddress(GetModuleHandleW(L"ntdll.dll"), "RtlDecompressBuffer"));
    for (unsigned group = 0; valid && group < next.paths.size(); ++group)
    {
        std::vector<unsigned char> pixels;
        unsigned width = 0;
        unsigned height = 0;
        std::uint64_t seen = 0;
        std::uint64_t hash = 14695981039346656037ull ^ header[3] ^ 3;
        for (auto const& record : RetailSelections(race))
        {
            if (record.kind != 3 || record.gender != gender || record.target != group)
                continue;
            bool selected = true;
            for (unsigned selector : record.choices)
                if (selector != 0xffffffff)
                {
                    unsigned index = selector & 65535;
                    if (index >= options.size())
                    {
                        selected = false;
                        break;
                    }
                    auto const& option = options[index];
                    selected = selected && fields[option.field] / option.factor % option.count == selector >> 16;
                }
            unsigned target = 0;
            unsigned blend = 0;
            if (!selected || sscanf_s(record.path, "%u:%u", &target, &blend) != 2 || target >= 64
                || (seen & (std::uint64_t{1} << target)))
                continue;
            seen |= std::uint64_t{1} << target;
            unsigned item[3]{};
            if (!decompress || std::fseek(input, record.value, SEEK_SET)
                || std::fread(item, sizeof(item), 1, input) != 1 || !item[0] || !item[1]
                || item[0] > 512 || item[1] > 512 || item[2] > 2 * 1024 * 1024)
            {
                valid = false;
                break;
            }
            std::vector<unsigned char> packed(item[2]);
            std::vector<unsigned char> layer(item[0] * item[1] * 4);
            ULONG size = 0;
            if (std::fread(packed.data(), 1, packed.size(), input) != packed.size()
                || decompress(2, layer.data(), static_cast<ULONG>(layer.size()), packed.data(), item[2], &size)
                || size != layer.size())
            {
                valid = false;
                break;
            }
            hash = (hash ^ record.value) * 1099511628211ull;
            if (pixels.empty())
            {
                pixels.resize(layer.size());
                width = item[0];
                height = item[1];
            }
            if (width != item[0] || height != item[1])
            {
                valid = false;
                break;
            }
            for (unsigned i = 0; i < layer.size(); i += 4)
            {
                unsigned alpha = layer[i + 3];
                unsigned priorAlpha = pixels[i + 3];
                unsigned outputAlpha = alpha * 255 + priorAlpha * (255 - alpha);
                for (unsigned channel = 0; channel < 3; ++channel)
                    pixels[i + channel] = static_cast<unsigned char>(
                        outputAlpha ? (layer[i + channel] * alpha * 255
                            + pixels[i + channel] * priorAlpha * (255 - alpha) + outputAlpha / 2) / outputAlpha : 0);
                pixels[i + 3] = static_cast<unsigned char>((outputAlpha + 127) / 255);
            }
        }
        if (pixels.empty())
            continue;
        char name[160]{};
        sprintf_s(name, "Interface\\AddOns\\EsteriaAppearanceCache\\%s\\%u-%u-%016llx.blp",
            RetailCacheFamily(race), gender, group, static_cast<unsigned long long>(hash));
        next.paths[group] = name;
        // ponytail: disk cache retains visited combinations; add bounded eviction if client disk usage warrants it.
        if (group != 1)
            valid = WriteHaranirBlp(next.paths[group], pixels, width, height, group == 0);
        else
        {
            // The catalogs project source sections into Wrath's 256x192 face destination first.
            if (height != 192 || width != 256)
            {
                valid = false;
                break;
            }
            next.lower = next.paths[group] + "-lower.blp";
            next.upper = next.paths[group] + "-upper.blp";
            std::vector<unsigned char> upper(pixels.begin(), pixels.begin() + width * 64 * 4);
            std::vector<unsigned char> lower(pixels.begin() + width * 64 * 4, pixels.end());
            valid = WriteHaranirBlp(next.upper, upper, width, 64, true)
                && WriteHaranirBlp(next.lower, lower, width, height - 64, true);
        }
    }
    std::fclose(input);
    // Names remain inside our client cache. The native filesystem resolver rejected both relative and
    // absolute paths during live Glue tests; validated buffers are passed to the native decoders below.
    if (valid)
    {
        char executable[MAX_PATH]{};
        if (!GetModuleFileNameA(nullptr, executable, MAX_PATH))
            return false;
        char* slash = std::strrchr(executable, '\\');
        if (!slash)
            return false;
        slash[1] = 0;
        for (auto& path : next.paths)
            if (!path.empty())
                path = executable + path;
        if (!next.lower.empty())
            next.lower = executable + next.lower;
        if (!next.upper.empty())
            next.upper = executable + next.upper;
        if (next.lower.size() >= 128 || next.upper.size() >= 128)
            return false;
    }
    if (valid)
        images = std::move(next);
    else
        OutputDebugStringA("Esteria: Retail material composition failed\n");
    return valid;
}

char const* HaranirLayerPath(void* character, unsigned kind, unsigned slot)
{
    unsigned race = Field<unsigned>(character, 0x18);
    if (race != 20 && race != 50 && race != 51 && !CreatureAppearance::Uses(race))
        return nullptr;
    auto& images = haranirImages[character];
    bool valid;
    if (CreatureAppearance::Uses(race))
        valid = ComposeHaranir(character, CreatureAppearance::Options(race, Field<unsigned>(character, 0x1C)), images);
    else if (race == 20)
        valid = Field<unsigned>(character, 0x1C) == 0
            ? ComposeHaranir(character, VulperaAppearance::MaleOptions, images)
            : ComposeHaranir(character, VulperaAppearance::FemaleOptions, images);
    else
        valid = Field<unsigned>(character, 0x1C) == 0
            ? ComposeHaranir(character, HaranirAppearance::MaleOptions, images)
            : ComposeHaranir(character, HaranirAppearance::FemaleOptions, images);
    if (!valid)
        return "";
    if (kind == 0 && slot == 0)
        return images.paths[0].c_str();
    if (kind == 0 && slot == 1)
        return images.paths[4].c_str();
    if (kind == 1 && slot < 2)
        return slot ? images.upper.c_str() : images.lower.c_str();
    if (kind == 3 && slot == 0)
        return images.paths[2].c_str();
    return "";
}

std::vector<unsigned char> HaranirBlpData(char const* path)
{
    FILE* file = nullptr;
    if (fopen_s(&file, path, "rb"))
        return {};
    std::fseek(file, 0, SEEK_END);
    long length = std::ftell(file);
    std::rewind(file);
    std::vector<unsigned char> bytes;
    if (length >= 1172 && length <= 8 * 1024 * 1024)
    {
        bytes.resize(length);
        if (std::fread(bytes.data(), 1, bytes.size(), file) != bytes.size())
            bytes.clear();
    }
    std::fclose(file);
    if (bytes.empty() || Field<unsigned>(bytes.data(), 0) != 0x32504C42
        || Field<unsigned>(bytes.data(), 4) != 1 || (bytes[8] != 1 && bytes[8] != 3)
        || !Field<unsigned>(bytes.data(), 12) || Field<unsigned>(bytes.data(), 12) > 512
        || !Field<unsigned>(bytes.data(), 16) || Field<unsigned>(bytes.data(), 16) > 512)
        return {};
    for (unsigned i = 0; i < 16; ++i)
    {
        unsigned offset = Field<unsigned>(bytes.data(), 20 + i * 4);
        unsigned size = Field<unsigned>(bytes.data(), 84 + i * 4);
        if ((offset || size) && (offset < 1172 || offset > bytes.size() || !size || size > bytes.size() - offset))
            return {};
        unsigned width = (std::max)(1u, Field<unsigned>(bytes.data(), 12) >> i);
        unsigned height = (std::max)(1u, Field<unsigned>(bytes.data(), 16) >> i);
        unsigned expected = bytes[8] == 3 ? width * height * 4 : width * height;
        if (bytes[8] == 1)
        {
            if (bytes[9] != 0 && bytes[9] != 1 && bytes[9] != 4 && bytes[9] != 8)
                return {};
            expected += (width * height * bytes[9] + 7) / 8;
        }
        if (size && size != expected)
            return {};
    }
    return bytes;
}

void* HaranirLoadLayer(char const* path)
{
    auto bytes = HaranirBlpData(path);
    if (bytes.empty() || bytes[8] != 1 || bytes.size() > 0xfffff)
        return nullptr;
    void* layer = Native<void*(__cdecl*)(char const*)>(0x004F3930)(path);
    if (!layer || Field<void*>(layer, 0xAC))
        return layer;
    // Match the stock callback's allocator, dimensions, palette flag and mip count. Its destructor
    // owns this buffer and frees it through the same client allocator; no helper pointer is retained.
    if (Field<void*>(layer, 0x18))
        return layer;
    void* buffer = Native<void*(__stdcall*)(unsigned, char const*, unsigned, unsigned)>(0x0076E540)(
        static_cast<unsigned>(bytes.size()), "HaranirLayer", 0, 0);
    if (!buffer)
    {
        Native<void(__cdecl*)(void*)>(0x004F31A0)(layer);
        return nullptr;
    }
    std::memcpy(buffer, bytes.data(), bytes.size());
    Field<void*>(layer, 0xAC) = buffer;
    Field<unsigned>(layer, 0xB0) = static_cast<unsigned>(bytes.size());
    Field<std::uint16_t>(layer, 0x1C) = static_cast<std::uint16_t>(Field<unsigned>(buffer, 12));
    Field<std::uint16_t>(layer, 0x1E) = static_cast<std::uint16_t>(Field<unsigned>(buffer, 16));
    unsigned mips = 0;
    while (mips < 16 && Field<unsigned>(buffer, 20 + mips * 4))
        ++mips;
    Field<unsigned>(layer, 0x20) = mips | (unsigned(bytes[9]) << 8) | (bytes[9] ? 0 : 0x10000);
    return layer;
}

std::shared_ptr<void> HaranirLoadTexture(char const* path)
{
    auto bytes = HaranirBlpData(path);
    if (bytes.empty())
        return {};
    void* allocation = Native<void*(__stdcall*)(unsigned, char const*, unsigned, unsigned)>(0x0076E540)(
        0x170, "HaranirTexture", 0, 0);
    if (!allocation)
        return {};
    void* texture = Native<void*(__thiscall*)(void*)>(0x004B8770)(allocation);
    Native<void*(__cdecl*)(void*, char const*)>(0x0047BF50)(texture, path);
    std::strncpy(static_cast<char*>(texture) + 0x6C, path, 0x103);
    Field<char>(texture, 0x6C + 0x103) = 0;
    void* payload = bytes.data();
    unsigned decoder = static_cast<unsigned>(Address(0x004B7BD0));
    unsigned decoded = 0;
    __asm
    {
        mov eax, texture
        push payload
        call decoder
        add esp, 4
        mov decoded, eax
    }
    auto result = std::shared_ptr<void>(texture, [](void* value)
    {
        Native<void(__cdecl*)(void*)>(0x0047BF30)(value);
    });
    if (!decoded)
        return {};
    return result;
}

void SetHaranirMaterials(void* character)
{
    if (!HaranirLayerPath(character, 0, 0))
        return;
    auto const found = haranirImages.find(character);
    void* instance = Field<void*>(character, 0x38);
    if (found == haranirImages.end() || !instance)
        return;
    unsigned const slots[] = {0, 0, 6, 5, 8, 12, 13, 9, 10};
    for (unsigned group = 2; group < found->second.paths.size(); ++group)
    {
        auto const& path = found->second.paths[group];
        if (path.empty())
            continue;
        auto& texture = found->second.textures[group];
        if (!texture)
            texture = HaranirLoadTexture(path.c_str());
        if (texture)
        {
            Native<void(__thiscall*)(void*, unsigned, void*)>(0x00825260)(instance, slots[group], texture.get());
        }
    }
}
