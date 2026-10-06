//go:build e2e

package session_test

import (
	"encoding/binary"
	"testing"
	"time"

	"github.com/azerothcore/AzerothGhost/client"
	"github.com/azerothcore/AzerothGhost/e2e/e2eharness"
	"github.com/azerothcore/azerothcore-wotlk/e2e/internal/meta"
)

// Esteria Cosmetics: a real cast, wing replacement and aura cancellation must reach Character Select.
// Requires the custom wing spells; rendering itself is covered by the native harness and manual client gate.
func TestSession_CosmeticWingCharacterSelect(t *testing.T) {
	meta.Begin(t, meta.TestMeta{Tags: []string{"short", "protocol", "cosmetics"}, Runtime: "short", Category: "protocol/session"})
	bot := e2eharness.NewSolo(t, e2eharness.ScenarioOpts{Prefix: "WingSel", Level: 80})
	bot.TeleportPad(t, e2eharness.PackagePad(t))
	const firstWing, secondWing uint32 = 970340, 970388
	for _, spell := range []uint32{firstWing, secondWing} {
		if !bot.World.KnowsSpell(spell) {
			e2eharness.Preconditionf(t, "Esteria cosmetic wing %d was not granted to this character", spell)
		}
	}

	assertRoster := func(want uint32) {
		t.Helper()
		bot.Save(t)
		// The pinned harness closes its socket on logout. Reconnect through its normal lifecycle,
		// then request the same account-scoped roster to inspect the state saved by that logout.
		bot.Relog(t)
		packets := make(chan []byte, 1)
		cancel := bot.World.AddPacketHook(func(op uint16, payload []byte) {
			if op == client.SmsgCharEnum {
				select {
				case packets <- append([]byte(nil), payload...):
				default:
				}
			}
		})
		defer cancel()
		if err := bot.World.RequestCharList(); err != nil {
			e2eharness.HarnessFailf(t, "character list request: %v", err)
		}
		var payload []byte
		select {
		case payload = <-packets:
		case <-time.After(15 * time.Second):
			e2eharness.HarnessFailf(t, "character list response timed out")
		}
		var got uint32
		if len(payload) >= 8 && binary.LittleEndian.Uint32(payload[len(payload)-4:]) == 0x31475743 {
			count := int(binary.LittleEndian.Uint32(payload[len(payload)-8:]))
			if count > 100 || count > (len(payload)-8)/12 {
				e2eharness.Assertf(t, "invalid CWG1 wing count %d", count)
			}
			start := len(payload) - 8 - count*12
			for offset := start; offset < len(payload)-8; offset += 12 {
				if binary.LittleEndian.Uint64(payload[offset:]) == bot.GUID {
					got = binary.LittleEndian.Uint32(payload[offset+8:])
				}
			}
		}
		if got != want {
			e2eharness.Assertf(t, "guid=0x%X Character Select wing=%d want=%d", bot.GUID, got, want)
		}
	}

	assertRoster(0) // Knowing every wing does not equip one.
	bot.CastMust(t, firstWing, bot.GUID, 10*time.Second)
	e2eharness.WaitUnitAura(t, bot.World, bot.GUID, firstWing, 10*time.Second)
	assertRoster(firstWing)
	bot.CastMust(t, secondWing, bot.GUID, 10*time.Second)
	e2eharness.WaitUnitAura(t, bot.World, bot.GUID, secondWing, 10*time.Second)
	bot.AssertAuraConsumed(t, firstWing, 10*time.Second, 0)
	assertRoster(secondWing)
	if err := bot.World.CancelAura(secondWing); err != nil {
		e2eharness.HarnessFailf(t, "cancel wing aura: %v", err)
	}
	bot.AssertAuraConsumed(t, secondWing, 10*time.Second, 0)
	assertRoster(0)
	t.Logf("PASS guid=0x%X Character Select follows no wing -> %d -> %d -> no wing", bot.GUID, firstWing, secondWing)
}
