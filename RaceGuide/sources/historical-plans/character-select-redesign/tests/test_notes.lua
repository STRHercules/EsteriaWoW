--[==[ test_notes.lua -------------------------------------------------------------
    Proves notes are hygienic, persistable, and that the editor's Cancel really
    discards (spec 12, 33).
]==]

local N = ECS.Notes;

N.Reset();

-- ---------------------------------------------------------------- 1. normalisation
ECS_EQ(N.Normalise("  Main tank  "), "Main tank", "1a: trimmed");
ECS_EQ(N.Normalise("Main    tank"), "Main tank", "1b: internal runs collapsed");
ECS_EQ(N.Normalise("Main\ttank"), "Main tank", "1c: tabs become spaces");
ECS_EQ(N.Normalise("Main\ntank"), "Main tank", "1d: newlines become spaces");
ECS_EQ(N.Normalise("a\0b"), "a b", "1e: NUL cannot survive into the payload");
ECS_EQ(N.Normalise(""), "", "1f: empty stays empty");
ECS_EQ(N.Normalise(nil), "", "1g: nil becomes empty, not an error");
ECS_EQ(N.Normalise(42), "", "1h: a number becomes empty, not an error");

-- 1i: the persisted delimiters must never survive normalisation
ECS_CHECK(string.find(N.Normalise("a\30b"), "\30", 1, true) == nil,
    "1i: record separator stripped");
ECS_CHECK(string.find(N.Normalise("a\31b"), "\31", 1, true) == nil,
    "1j: unit separator stripped");

local long = string.rep("x", 500);
ECS_EQ(#N.Normalise(long), N.MAX_LENGTH, "1k: over-long notes are truncated");
ECS_CHECK(#N.Normalise(string.rep("y", N.MAX_LENGTH) .. "      ") <= N.MAX_LENGTH,
    "1l: trailing space after truncation is trimmed");

ECS_CHECK(N.IsEmpty("   "), "1m: whitespace-only counts as empty");
ECS_CHECK(not N.IsEmpty("x"), "1n: real text is not empty");

-- ---------------------------------------------------------------- 2. set / get / clear
local changed = N.Set("esteria:zach", "Main tank");
ECS_EQ(changed, true, "2a: first set reports a change");
ECS_EQ(N.Get("esteria:zach"), "Main tank", "2b: stored");
ECS_CHECK(N.Has("esteria:zach"), "2c: Has is true");

ECS_EQ(N.Set("esteria:zach", "Main tank"), false, "2d: setting the same value is not a change");
ECS_EQ(N.Set("esteria:zach", "Bank alt"), true, "2e: changing reports a change");
ECS_EQ(N.Get("esteria:zach"), "Bank alt", "2f: updated");

ECS_EQ(N.Set("esteria:zach", "   "), true, "2g: setting blank clears it");
ECS_EQ(N.Get("esteria:zach"), nil, "2h: blank stores nothing");
ECS_CHECK(not N.Has("esteria:zach"), "2i: Has is false again");

ECS_EQ(N.Set("", "text"), false, "2j: empty key rejected");
ECS_EQ(N.Set(nil, "text"), false, "2k: nil key rejected");
ECS_EQ(N.Get(nil), nil, "2l: nil key lookup is safe");

N.Set("esteria:a", "one");
ECS_CHECK(N.Clear("esteria:a") == true, "2m: clear removes");
ECS_CHECK(N.Clear("esteria:a") == false, "2n: clearing again is a no-op");
ECS_CHECK(N.Clear(nil) == false, "2o: nil clear is a no-op");

-- ---------------------------------------------------------------- 3. counting and replace
N.Reset();
N.Set("k1", "one");
N.Set("k2", "two");
N.Set("k3", "three");
ECS_EQ(N.Count(), 3, "3a: count");

-- 3b: a malformed map must be dropped, never raise
N.Replace({
    ["good"] = "fine",
    ["bad_number"] = 12345,
    ["bad_empty"] = "",
    [42] = "numeric key",
    ["whitespace"] = "   ",
});
ECS_EQ(N.Count(), 1, "3c: only the well-formed entry survives");
ECS_EQ(N.Get("good"), "fine", "3d: the good entry is kept");
ECS_EQ(N.Replace(nil), N.notes, "3e: replacing with nil clears safely");
ECS_EQ(N.Count(), 0, "3f: nothing left");

-- 3g: Replace also normalises what it accepts
N.Replace({ ["k"] = "  a   b  " });
ECS_EQ(N.Get("k"), "a b", "3g: replaced text is normalised");

-- ---------------------------------------------------------------- 4. export
N.Reset();
N.Set("k1", "one");
N.Set("k2", "two");
local exported = N.Export();
ECS_EQ(exported["k1"], "one", "4a: export contains the note");
-- 4b: export must be a copy, not the live table
exported["k1"] = "mutated";
ECS_EQ(N.Get("k1"), "one", "4b: export is a copy, not a live reference");

-- 4c: forget removes a deleted character's note
ECS_CHECK(N.Forget("k1") == true, "4c: forget removes the note");
ECS_EQ(N.Get("k1"), nil, "4d: note is gone");

-- ---------------------------------------------------------------- 5. editor
N.Reset();
N.Set("esteria:zach", "Main tank");

ECS_CHECK(N.BeginEdit("esteria:zach"), "5a: editor opens");
ECS_CHECK(N.IsEditing(), "5b: editing state reported");
ECS_EQ(N.GetDraftKey(), "esteria:zach", "5c: draft key");
ECS_EQ(N.GetDraft(), "Main tank", "5d: draft seeded from the stored note");

-- 5e: Cancel must leave the stored note untouched
N.SetDraft("Something else");
ECS_EQ(N.GetDraft(), "Something else", "5e: draft updated");
N.CancelEdit();
ECS_CHECK(not N.IsEditing(), "5f: editor closed");
ECS_EQ(N.Get("esteria:zach"), "Main tank", "5g: CANCEL DID NOT MODIFY THE STORED NOTE");

-- 5h: Commit applies
N.BeginEdit("esteria:zach");
N.SetDraft("Bank alt");
local committed, key = N.CommitEdit();
ECS_CHECK(committed == true, "5h: commit reports a change");
ECS_EQ(key, "esteria:zach", "5i: commit returns the key");
ECS_EQ(N.Get("esteria:zach"), "Bank alt", "5j: stored note updated");
ECS_CHECK(not N.IsEditing(), "5k: editor closed after commit");

-- 5l: committing without a change reports no change
N.BeginEdit("esteria:zach");
local unchanged = N.CommitEdit();
ECS_EQ(unchanged, false, "5l: committing an unchanged draft reports no change");

-- 5m: committing an emptied draft clears the note
N.BeginEdit("esteria:zach");
N.SetDraft("   ");
N.CommitEdit();
ECS_EQ(N.Get("esteria:zach"), nil, "5m: committing blank clears the note");

-- 5n: ClearDraft wipes immediately and stays in the editor
N.Set("esteria:nat", "Herbalism / Alchemy");
N.BeginEdit("esteria:nat");
N.ClearDraft();
ECS_EQ(N.Get("esteria:nat"), nil, "5n: ClearDraft removes the stored note");
ECS_CHECK(N.IsEditing(), "5o: ClearDraft leaves the editor open");
N.CancelEdit();

-- 5p: editor on a character with no note starts empty
N.BeginEdit("esteria:fresh");
ECS_EQ(N.GetDraft(), "", "5p: draft starts empty for an unnoted character");
N.CancelEdit();

-- 5q: editing is rejected for a bad key
ECS_EQ(N.BeginEdit(nil), false, "5q: nil key rejected");
ECS_EQ(N.BeginEdit(""), false, "5r: empty key rejected");
ECS_CHECK(not N.IsEditing(), "5s: no draft was created");

-- 5t: draft operations without an open editor are safe no-ops
ECS_EQ(N.SetDraft("x"), false, "5t: SetDraft with no editor is a no-op");
ECS_EQ(N.CommitEdit(), false, "5u: CommitEdit with no editor is a no-op");
ECS_EQ(N.CancelEdit(), false, "5v: CancelEdit with no editor is a no-op");
ECS_EQ(N.GetDraft(), nil, "5w: GetDraft with no editor returns nil");

-- 5x: opening a second editor replaces the first without applying it
N.Set("esteria:one", "first");
N.Set("esteria:two", "second");
N.BeginEdit("esteria:one");
N.SetDraft("edited but abandoned");
N.BeginEdit("esteria:two");
ECS_EQ(N.GetDraftKey(), "esteria:two", "5x: second editor takes over");
ECS_EQ(N.Get("esteria:one"), "first", "5y: the abandoned draft was NOT applied");
N.CancelEdit();
