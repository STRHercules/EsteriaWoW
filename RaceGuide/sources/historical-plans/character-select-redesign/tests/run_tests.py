"""Offline test runner for the Esteria Character Select Lua modules.

Runs the REAL module sources on a genuine Lua 5.1 runtime (lupa.lua51), which is
the interpreter family the WoW 3.3.5a client uses. This lets the critical
visual-index / real-index invariant be proven WITHOUT launching the client.

Usage:
    python .agents/plans/character-select-redesign/tests/run_tests.py
"""

from __future__ import annotations

import sys
from pathlib import Path

try:
    from lupa.lua51 import LuaRuntime
except ImportError:  # pragma: no cover
    print("FATAL: lupa with the lua51 runtime is required (pip install lupa)")
    raise SystemExit(2)

HERE = Path(__file__).resolve().parent
SRC = HERE.parent / "src" / "GlueXML"

# The frame shim is test-only scaffolding: it lets the roster modules be exercised
# headlessly on real Lua 5.1 instead of only inside the client.
SHIM = "frame_shim.lua"

# Loaded in the same order GlueXML.toc will load them: pure data/logic first,
# no frame access anywhere.
MODULES = [
    "ECS_Constants.lua",
    "ECS_Schema.lua",
    "ECS_Order.lua",
    "ECS_Data.lua",
    "ECS_Persistence.lua",
    "ECS_Notes.lua",
    "ECS_Anim.lua",
    "ECS_Search.lua",
    "ECS_Modal.lua",
    "ECS_Row.lua",
    "ECS_Roster.lua",
    "ECS_Tooltip.lua",
    "ECS_UI.lua",
    "ECS_Integrate.lua",
]

# Files that CANNOT be executed headlessly because they touch client globals at
# file scope (CharacterSelect.lua assigns to the XML-created `CharacterSelect`
# table at load). They are still compiled, so a syntax error is caught here
# rather than by crashing the client.
SYNTAX_ONLY = [
    "CharacterSelect.lua",
]

PRELUDE = r"""
-- Minimal assertion helpers so the Lua test files stay readable.
ECS_TEST = { passed = 0, failed = 0, failures = {} };

function ECS_CHECK(condition, message)
    if ( condition ) then
        ECS_TEST.passed = ECS_TEST.passed + 1;
    else
        ECS_TEST.failed = ECS_TEST.failed + 1;
        ECS_TEST.failures[#ECS_TEST.failures + 1] = tostring(message);
    end
    return condition and true or false;
end

function ECS_EQ(actual, expected, message)
    local ok = (actual == expected);
    if ( not ok ) then
        ECS_TEST.failed = ECS_TEST.failed + 1;
        ECS_TEST.failures[#ECS_TEST.failures + 1] =
            string.format("%s (expected %s, got %s)", tostring(message),
                tostring(expected), tostring(actual));
    else
        ECS_TEST.passed = ECS_TEST.passed + 1;
    end
    return ok;
end

-- Compile a source file without running it. Used for glue files that need client
-- globals at file scope, so a syntax error is caught here instead of by crashing
-- the client on load.
function ECS_SYNTAX_CHECK(source, name)
    local chunk, err = loadstring(source, name);
    if ( not chunk ) then
        ECS_TEST.failed = ECS_TEST.failed + 1;
        ECS_TEST.failures[#ECS_TEST.failures + 1] =
            "SYNTAX " .. tostring(name) .. ": " .. tostring(err);
        return false;
    end
    ECS_TEST.passed = ECS_TEST.passed + 1;
    return true;
end
"""


def load_modules(lua: LuaRuntime) -> None:
    lua.execute(PRELUDE)

    shim = HERE / SHIM
    if shim.exists():
        lua.execute(shim.read_text(encoding="utf-8"))
        lua.execute("SHIM.Install()")

    for name in MODULES:
        path = SRC / name
        if not path.exists():
            continue  # a module not yet written is not an error while building
        try:
            lua.execute(path.read_text(encoding="utf-8"))
        except Exception as exc:  # surface the Lua error with the file name
            raise SystemExit(f"{name} failed to load:\n{exc}") from exc


def syntax_check(lua: LuaRuntime) -> None:
    check = lua.globals().ECS_SYNTAX_CHECK
    for name in SYNTAX_ONLY:
        path = SRC / name
        if not path.exists():
            continue
        check(path.read_text(encoding="utf-8"), name)


def function_block(source: str, signature: str) -> str:
    start = source.index(signature)
    end = source.index("\nfunction ", start + len(signature))
    return source[start:end]


def contract_check() -> int:
    """Replicate the pins from tools/test_character_select_contract.py.

    That test cannot run in this checkout (it reads a client path that does not
    exist here), so the same assertions are enforced locally to make sure editing
    CharacterSelect.lua cannot silently break the agreed contract.
    """
    failures = 0
    lua_text = (SRC / "CharacterSelect.lua").read_text(encoding="utf-8")

    def expect(condition: bool, label: str) -> None:
        nonlocal failures
        if not condition:
            failures += 1
            print(f"  CONTRACT FAIL: {label}")

    keydown = function_block(lua_text, "function CharacterSelect_OnKeyDown(self,key)")
    expect('elseif ( key == "DOWN" or key == "RIGHT" )' in keydown,
           "keydown DOWN/RIGHT branch must test `key`")
    expect("arg1" not in keydown, "keydown handler must not reference arg1")

    # Both arrow directions must delegate to ECS's VISUAL ordering. Only
    # DOWN/RIGHT used to, so under a custom order or an active filter, DOWN moved
    # to the next row the user could actually see while UP jumped to an unrelated
    # server index. The stock branch stays as the no-ECS fallback.
    expect("ECS.Integrate.StepSelection(1)" in keydown,
           "keydown DOWN must delegate to the ECS visual order")
    expect("ECS.Integrate.StepSelection(-1)" in keydown,
           "keydown UP must delegate to the ECS visual order")
    expect("CharacterSelect_SelectCharacter(self.selectedIndex - 1)" in keydown,
           "keydown UP keeps the stock fallback when ECS is absent")
    expect("CharacterSelect_SelectCharacter(self.selectedIndex + 1)" in keydown,
           "keydown DOWN keeps the stock fallback when ECS is absent")

    update = function_block(lua_text, "function UpdateCharacterList()")
    expect("CharacterSelectCharacterScrollChild:SetHeight(viewportHeight + maxOffset * CHARACTER_SELECT_ROW_HEIGHT)" in update,
           "scroll child height expression")
    expect("CharacterSelectCharacterScrollFrame:UpdateScrollChildRect()" in update,
           "UpdateScrollChildRect call")

    handler = function_block(lua_text, "function CharacterSelect_OnVerticalScroll(self, offset)")
    expect("GlueScrollFrame_OnVerticalScroll(self, offset)" in handler,
           "GlueScrollFrame_OnVerticalScroll call")
    expect("CharacterSelect_SetScrollOffset(offset / CHARACTER_SELECT_ROW_HEIGHT)" in handler,
           "pixel-to-row scroll conversion")

    print(f"  contract pins: {'all satisfied' if failures == 0 else str(failures) + ' BROKEN'}")
    return failures


def wiring_check() -> int:
    """Find public functions that no production code ever calls.

    This exists because of a real miss: the drag path shipped with `UpdatePress`
    tested and defined but reachable only from mouse-DOWN, which fires once - so
    the drop target never moved and every release was a no-op. Unit tests called
    the function directly and could not see that nothing else did.

    A function referenced ONLY from test files is therefore a warning: it is
    either dead code or a wiring gap.
    """
    import re

    # Leading whitespace is allowed: aliases are often declared inside a function
    # (`local anim = ECS.Anim;`), and requiring column 0 hid those and made real
    # uses look like dead code.
    alias_re = re.compile(r"^\s*local\s+([A-Za-z_]\w*)\s*=\s*ECS\.([A-Za-z_]\w*)", re.M)
    module_re = re.compile(r"ECS\.([A-Za-z_]\w*)\s*=\s*ECS\.\1\s*or\s*\{\}")
    def_re = re.compile(r"function\s+([A-Za-z_]\w*)\.([A-Za-z_]\w*)\s*\(")
    def2_re = re.compile(r"([A-Za-z_]\w*)\.([A-Za-z_]\w*)\s*=\s*function\s*\(")
    local_fn_re = re.compile(r"local\s+function\s+([A-Za-z_]\w*)\s*\(")
    # `O.Normalise = Normalise;` - a local function published onto the module.
    def3_re = re.compile(r"([A-Za-z_]\w*)\.([A-Za-z_]\w*)\s*=\s*([A-Za-z_]\w*)\s*;")

    # A CALL is written `X.Y(`. A USE covers both calls and values passed to
    # pcall - `pcall(ECS.UI.Build, x)` is a perfectly good use and requiring a
    # paren made the audit report live code as dead.
    alias_call_re = re.compile(r"([A-Za-z_]\w*)\.([A-Za-z_]\w*)\s*\(")
    alias_any_re = re.compile(r"([A-Za-z_]\w*)\.([A-Za-z_]\w*)")
    direct_call_re = re.compile(r"ECS\.([A-Za-z_]\w*)\.([A-Za-z_]\w*)\s*\(")
    direct_any_re = re.compile(r"ECS\.([A-Za-z_]\w*)\.([A-Za-z_]\w*)")

    sources = {p.name: p.read_text(encoding="utf-8") for p in sorted(SRC.glob("ECS_*.lua"))}
    sources.setdefault("CharacterSelect.lua", (SRC / "CharacterSelect.lua").read_text(encoding="utf-8"))

    modules = set()
    for text in sources.values():
        modules.update(module_re.findall(text))

    defined: dict[str, set[str]] = {}
    referenced: dict[str, set[str]] = {}
    call_form: dict[str, set[str]] = {}
    # `O.SearchBlob = SearchBlob;` publishes a local function. Callers INSIDE that
    # file reach it by the local name, so scanning for `O.SearchBlob(` finds
    # nothing and reported live code as dead. Track those pairs explicitly.
    published_local: dict[str, set[str]] = {}

    def blank(match: re.Match) -> str:
        """Erase a definition site so it cannot masquerade as a call."""
        return " " * len(match.group(0))

    for name, text in sources.items():
        amap = dict(alias_re.findall(text))
        local_functions = set(local_fn_re.findall(text))

        for alias, member in def_re.findall(text) + def2_re.findall(text):
            module = amap.get(alias)
            if module:
                defined.setdefault(f"ECS.{module}.{member}", set()).add(name)
        for alias, member, target in def3_re.findall(text):
            module = amap.get(alias)
            if module and target in local_functions:
                full = f"ECS.{module}.{member}"
                defined.setdefault(full, set()).add(name)
                published_local.setdefault(full, set()).add(f"{name}\0{target}")

        # CRITICAL: strip definition sites before hunting references. Without this
        # every `function X.Y(` line matches the call pattern and every function
        # looks self-referenced, so the audit silently reports nothing.
        scrubbed = def_re.sub(blank, text)
        scrubbed = def2_re.sub(blank, scrubbed)
        scrubbed = def3_re.sub(blank, scrubbed)

        for alias, member in alias_call_re.findall(scrubbed):
            module = amap.get(alias)
            if module:
                call_form.setdefault(f"ECS.{module}.{member}", set()).add(name)
        for alias, member in alias_any_re.findall(scrubbed):
            module = amap.get(alias)
            if module:
                referenced.setdefault(f"ECS.{module}.{member}", set()).add(name)
        for module, member in direct_call_re.findall(scrubbed):
            call_form.setdefault(f"ECS.{module}.{member}", set()).add(name)
        for module, member in direct_any_re.findall(scrubbed):
            referenced.setdefault(f"ECS.{module}.{member}", set()).add(name)

        # A published local called by its own name in this file is USED, just not
        # through the public path.
        for full, pairs in published_local.items():
            for pair in pairs:
                owner, local_name = pair.split("\0")
                if owner != name:
                    continue
                if re.search(rf"(?<![\w.]){re.escape(local_name)}\s*\(", scrubbed):
                    referenced.setdefault(full, set()).add(f"{name} (internal)")

    # Whether the TESTS touch a function matters, because "no production caller"
    # covers two very different situations:
    #
    #   * referenced by a test only -> either an intentional seam (a Reset/accessor
    #     the tests drive directly) or a WIRING GAP: a function that is tested and
    #     correct but that production never reaches. That second case is the bug
    #     class this audit exists for.
    #   * referenced nowhere at all -> plain dead code.
    #
    # Reports that did not separate these were unusable: a list of 58 names, most
    # of them legitimate, hid the handful that actually mattered.
    test_referenced: set[str] = set()
    for path in sorted(HERE.glob("test_*.lua")):
        text = path.read_text(encoding="utf-8")
        amap = dict(alias_re.findall(text))
        for alias, member in alias_any_re.findall(text):
            module = amap.get(alias)
            if module:
                test_referenced.add(f"ECS.{module}.{member}")
        for module, member in direct_any_re.findall(text):
            test_referenced.add(f"ECS.{module}.{member}")

    orphaned = []
    for full, where in sorted(defined.items()):
        if not referenced.get(full):
            orphaned.append((full, sorted(where)))

    test_only = [(f, w) for f, w in orphaned if f in test_referenced]
    dead = [(f, w) for f, w in orphaned if f not in test_referenced]

    print(f"  public functions defined : {len(defined)}")
    print(f"  no production caller     : {len(orphaned)}")
    print(f"    test-only (seam or gap)  : {len(test_only)}")
    for full, where in test_only:
        print(f"      {full}  (defined in {', '.join(where)})")
    print(f"    referenced nowhere       : {len(dead)}")
    for full, where in dead:
        print(f"      {full}  (defined in {', '.join(where)})")

    # INVARIANT, enforced: every public function is reached by production code,
    # used in-file under its local name, or exercised by a test. Anything else is
    # dead weight that makes the next reader trust a function that does nothing -
    # and in this project dead weight has repeatedly hidden real wiring gaps.
    # A test-only entry is a warning rather than a failure because a test seam
    # (Reset, an accessor) is legitimate; it is printed loudly so a wiring gap
    # cannot hide inside it unnoticed.

    # A CALL to something never defined is a hard error: it is a nil call at
    # runtime, silently swallowed by the pcall guards. Field accesses such as
    # ECS.Order.visible are excluded by only looking at call form, and by only
    # considering ECS module names we actually know about.
    undefined = []
    for full, where in sorted(call_form.items()):
        if full in defined:
            continue
        module = full.split(".")[1]
        if module not in modules:
            continue
        undefined.append((full, sorted(where)))
    if undefined:
        print("\n  CALLS WITH NO DEFINITION (would be a nil call at runtime):")
        for full, where in undefined:
            print(f"    {full}  (called in {', '.join(where)})")

    print(f"  undefined references     : {len(undefined)}")
    print(f"  dead code (hard failure) : {len(dead)}")
    return len(undefined) + len(dead)


def main() -> int:
    lua = LuaRuntime(unpack_returned_tuples=True)
    load_modules(lua)
    syntax_check(lua)
    contract_failures = contract_check()
    undefined_refs = wiring_check()

    test_files = sorted(HERE.glob("test_*.lua"))
    if not test_files:
        print("no test files found")
        return 2

    for path in test_files:
        try:
            lua.execute(path.read_text(encoding="utf-8"))
        except Exception as exc:
            raise SystemExit(f"{path.name} failed:\n{exc}") from exc

    failures = list(lua.eval("ECS_TEST.failures").values())
    passed = lua.eval("ECS_TEST.passed")
    failed = lua.eval("ECS_TEST.failed") + contract_failures + undefined_refs

    print(f"Lua runtime: {lua.eval('_VERSION')}")
    print(f"modules    : {', '.join(MODULES)}")
    print(f"tests      : {len(test_files)} file(s)")
    print(f"assertions : {passed} passed, {failed} failed")
    if failures:
        print("\nFAILURES:")
        for message in failures:
            print(f"  - {message}")
    print("\n" + ("ALL TESTS PASSED" if failed == 0 else "TESTS FAILED"))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
