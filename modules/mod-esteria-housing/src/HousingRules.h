#ifndef ESTERIA_HOUSING_RULES_H
#define ESTERIA_HOUSING_RULES_H

#include "HousingWire.h"
#include <cmath>
#include <cstdint>

// Edit validation with no server dependencies, so tests/rules_test.cpp can run it alone. The caller looks every fact
// up from its own state (never from the packet) and Check applies protocol.md's order. Nothing here trusts the client.
namespace EsteriaHousing
{
    using namespace EsteriaHousingWire;

    struct Edit
    {
        uint32_t seq = 0;
        uint32_t baseRevision = 0;
        uint8_t op = 0;
        uint64_t placedId = 0;
        uint32_t decorId = 0;
        float pos[3] = { 0, 0, 0 };
        float rot[4] = { 0, 0, 0, 1 };
        float scale = 1;
    };

    struct Facts
    {
        bool enabled = false;
        bool inHouse = false;          // the editor stands in a housing instance whose house exists
        bool isOwner = false;          // editor's account owns that house (from the DB)
        uint32_t lastSeq = 0;          // highest seq accepted or refused for this session
        uint32_t revision = 0;         // house revision now
        bool decorKnown = false;       // place: decorId is in the catalog and enabled
        uint32_t available = 0;        // place: owned - placed for this account
        bool placementKnown = false;   // move/remove: placedId belongs to this house
        uint32_t placed = 0;
        uint32_t maxDecor = 0;
        float boundsMin[3] = { 0, 0, 0 };
        float boundsMax[3] = { 0, 0, 0 };
        float minScale = 1;
        float maxScale = 1;
        float snapDegrees = 15;
        bool rateOk = true;
    };

    struct Final
    {
        float pos[3] = { 0, 0, 0 };
        float yaw = 0;                 // radians, [0, 2pi): the heading of rot, for logs and legacy callers
        float rot[4] = { 0, 0, 0, 1 }; // unit quaternion, xyzw
        float scale = 1;
    };

    inline bool Finite(float value) { return std::isfinite(value); }

    // Yaw of any quaternion, snapped. MVP decor only turns about Z.
    inline float SnapYaw(float const q[4], float snapDegrees)
    {
        double const pi = 3.14159265358979323846;
        double yaw = std::atan2(2.0 * (q[3] * q[2] + q[0] * q[1]), 1.0 - 2.0 * (q[1] * q[1] + q[2] * q[2]));
        double const step = snapDegrees * pi / 180.0;
        if (step > 0)
            yaw = std::round(yaw / step) * step;
        yaw = std::fmod(yaw, 2 * pi);
        if (yaw < 0)
            yaw += 2 * pi;
        if (yaw >= 2 * pi - 1e-6)
            yaw = 0;
        return float(yaw);
    }

    inline Result CheckTransform(Edit const& e, Facts const& f, Final& out)
    {
        for (float v : e.pos)
            if (!Finite(v))
                return BadTransform;
        for (float v : e.rot)
            if (!Finite(v))
                return BadTransform;
        if (!Finite(e.scale))
            return BadTransform;
        double const magnitude = std::sqrt(double(e.rot[0]) * e.rot[0] + double(e.rot[1]) * e.rot[1]
            + double(e.rot[2]) * e.rot[2] + double(e.rot[3]) * e.rot[3]);
        if (magnitude < 0.5 || magnitude > 2.0)
            return BadTransform;
        if (e.scale < f.minScale - 1e-4f || e.scale > f.maxScale + 1e-4f)
            return BadTransform;
        for (int i = 0; i < 3; ++i)
            if (e.pos[i] < f.boundsMin[i] || e.pos[i] > f.boundsMax[i])
                return OutOfBounds;

        float const unit[4] = { float(e.rot[0] / magnitude), float(e.rot[1] / magnitude),
            float(e.rot[2] / magnitude), float(e.rot[3] / magnitude) };
        for (int i = 0; i < 3; ++i)
            out.pos[i] = e.pos[i];
        // Any orientation (Expert mode turns decor about every axis); the client snaps, the server only normalizes.
        // A yaw-only rotation still snaps to snapDegrees, so the basic tools keep their steps.
        bool const yawOnly = std::fabs(unit[0]) < 1e-4f && std::fabs(unit[1]) < 1e-4f;
        out.yaw = SnapYaw(unit, yawOnly ? f.snapDegrees : 0);
        if (yawOnly)
        {
            out.rot[0] = 0;
            out.rot[1] = 0;
            out.rot[2] = std::sin(out.yaw / 2);
            out.rot[3] = std::cos(out.yaw / 2);
        }
        else
            for (int i = 0; i < 4; ++i)
                out.rot[i] = unit[i];
        out.scale = e.scale;
        return Ok;
    }

    // DuplicateSeq leaves lastSeq alone; every other result consumes the seq (the caller stores it).
    inline Result Check(Edit const& e, Facts const& f, Final& out)
    {
        if (!f.enabled)
            return Disabled;
        if (!f.inHouse)
            return NotInHouse;
        if (!f.isOwner)
            return NoPermission;
        if (e.seq <= f.lastSeq)
            return DuplicateSeq;
        if (!f.rateOk)
            return RateLimited;
        if (e.op != OpPlace && e.op != OpMove && e.op != OpRemove)
            return BadOp;
        if (e.baseRevision != f.revision)
            return StaleRevision;
        if (e.op == OpPlace)
        {
            if (e.placedId != 0 || !f.decorKnown)
                return UnknownDecor;
            if (f.available < 1)
                return NoneLeft;
        }
        else if (!f.placementKnown)
            return UnknownPlacement;
        if (e.op != OpRemove)
            if (Result r = CheckTransform(e, f, out); r != Ok)
                return r;
        if (e.op == OpPlace && f.placed + 1 > f.maxDecor)
            return OverBudget;
        return Ok;
    }

    // ---- shops and commissions
    inline constexpr uint32_t MaxListingPrice = 1000000000; // copper; a price must fit the int32 ModifyMoney takes

    // A listing sells `bundle` at a time, for `price` copper a bundle, from a held stack of `count`.
    inline bool ValidListing(uint32_t bundle, uint32_t count, uint32_t maxStack, uint32_t price)
    {
        return bundle >= 1 && bundle <= count && bundle <= maxStack && price >= 1 && price <= MaxListingPrice;
    }

    enum OrderState : uint8_t { OrderOpen = 0, OrderAccepted = 1, OrderCompleted = 2, OrderCancelled = 3, OrderExpired = 4 };

    inline bool OrderCan(uint8_t from, uint8_t to)
    {
        if (from == OrderOpen)
            return to == OrderAccepted || to == OrderCancelled || to == OrderExpired;
        if (from == OrderAccepted)
            return to == OrderOpen || to == OrderCompleted || to == OrderCancelled || to == OrderExpired;
        return false; // completed, cancelled and expired are final: escrow is paid out exactly once
    }
}

#endif
