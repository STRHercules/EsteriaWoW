#include "core/DeterministicRng.h"
#include "core/IdPool.h"
#include "core/AppearanceCatalog.h"
#include "core/ItemGenerator.h"

#include <cassert>
#include <iostream>
#include <set>

using namespace ProceduralItems;

static void test_rng_is_deterministic()
{
    DeterministicRng a(0x12345678ULL);
    DeterministicRng b(0x12345678ULL);
    for (int i = 0; i < 32; ++i)
        assert(a.nextU64() == b.nextU64());
}

static void test_id_pool_allocates_first_unused_and_never_recycles()
{
    IdPool pool;
    pool.addRange({"leather_chest", 2000000, 2000003, 4, 2, 5});
    std::set<uint32_t> used{2000000, 2000002};
    auto first = pool.allocate("leather_chest", used);
    assert(first.has_value() && *first == 2000001);
    used.insert(*first);
    auto second = pool.allocate("leather_chest", used);
    assert(second.has_value() && *second == 2000003);
    used.insert(*second);
    assert(!pool.allocate("leather_chest", used).has_value());
}

static void test_appearance_catalog_refuses_incompatible_or_missing_assets()
{
    AppearanceCatalog catalog;
    catalog.add({"leather_chest", 12345, 10, 30, 10});
    DeterministicRng rng(42);
    auto valid = catalog.choose("leather_chest", 20, rng);
    assert(valid.has_value() && valid->displayId == 12345);
    auto wrongPool = catalog.choose("mail_chest", 20, rng);
    assert(!wrongPool.has_value());
    auto wrongLevel = catalog.choose("leather_chest", 60, rng);
    assert(!wrongLevel.has_value());
}

static void test_generator_is_deterministic_and_uses_verified_display()
{
    AppearanceCatalog catalog;
    catalog.add({"leather_chest", 54321, 1, 80, 100});
    ItemGenerator generator(catalog);

    GenerationRequest req;
    req.seed = 999;
    req.level = 20;
    req.itemLevel = 25;
    req.quality = ItemQuality::Rare;
    req.role = ItemRole::Hunter;
    req.poolKey = "leather_chest";

    auto a = generator.generate(req);
    auto b = generator.generate(req);
    assert(a.has_value() && b.has_value());
    assert(a->name == b->name);
    assert(a->displayId == 54321);
    assert(a->stats == b->stats);
    assert(!a->stats.empty());
}

static void test_generator_fails_without_verified_display()
{
    AppearanceCatalog catalog;
    ItemGenerator generator(catalog);
    GenerationRequest req;
    req.seed = 1;
    req.level = 10;
    req.itemLevel = 10;
    req.quality = ItemQuality::Uncommon;
    req.role = ItemRole::Melee;
    req.poolKey = "sword_1h";
    assert(!generator.generate(req).has_value());
}

int main()
{
    test_rng_is_deterministic();
    test_id_pool_allocates_first_unused_and_never_recycles();
    test_appearance_catalog_refuses_incompatible_or_missing_assets();
    test_generator_is_deterministic_and_uses_verified_display();
    test_generator_fails_without_verified_display();
    std::cout << "All procedural-item core tests passed.\n";
    return 0;
}
