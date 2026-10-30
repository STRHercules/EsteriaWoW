#ifndef ACORE_KYRIAN_RACIALS_H
#define ACORE_KYRIAN_RACIALS_H

#include <cstdint>

namespace KyrianRacials
{
    constexpr std::uint8_t Race = 75;
    constexpr std::uint32_t AscendedWings = 111104;
    constexpr std::uint32_t Purity = 111105;
    constexpr std::uint32_t Courage = 111106;
    constexpr std::uint32_t SoulGuide = 111107;
    constexpr std::uint32_t Craft = 111108;
    constexpr std::uint32_t SpiritSpeed = 111109;
    constexpr std::uint32_t Charge = 111110;
    constexpr std::uint32_t ChargeImpact = 111111;
    constexpr std::uint32_t ChargeSlow = 111112;
    constexpr std::uint32_t ChargeRing = 111113;
    constexpr std::uint32_t FallReductionPercent = 50;
    constexpr float ChargeRange = 25.0f;
    constexpr float ChargeStatCoefficient = 0.15f;
    constexpr float ChargeDamagePerLevel = 2.0f;
    constexpr std::uint32_t ChargeRingTickPercent = 10;
    constexpr std::uint32_t ChargeDiveBonusPercent = 20;
}

#endif
