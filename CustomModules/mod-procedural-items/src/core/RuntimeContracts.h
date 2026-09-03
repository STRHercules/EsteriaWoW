#pragma once

#include "core/Types.h"

#include <cstdint>
#include <string>

namespace ProceduralItems
{
enum class RuntimeRegisterStatus
{
    Registered,
    AlreadyPresent,
    Unsupported,
    Rejected
};

class IRuntimeItemRegistry
{
public:
    virtual ~IRuntimeItemRegistry() = default;
    virtual RuntimeRegisterStatus registerTemplate(std::uint32_t entry, GeneratedItemDraft const& item, std::string& error) = 0;
};

class IGeneratedItemPersistence
{
public:
    virtual ~IGeneratedItemPersistence() = default;
    virtual bool isEntryPermanentlyUsed(std::uint32_t entry) const = 0;
    virtual bool persist(std::uint32_t entry, GeneratedItemDraft const& item, std::uint32_t generationVersion, std::string const& source, std::string& error) = 0;
};
}
