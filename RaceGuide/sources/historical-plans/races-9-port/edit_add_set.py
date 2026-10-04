import pathlib

path = pathlib.Path("fix_item_component_prefixes.py")
text = path.read_text(encoding="utf-8")

marker = 'def main() -> None:\n    parser = argparse.ArgumentParser()\n'
addition = ('def main() -> None:\n'
            '    parser = argparse.ArgumentParser()\n'
            '    parser.add_argument("--set", action="append", default=[], metavar="RACE=CODE",\n'
            '                        help="override one race\'s ClientPrefix, repeatable")\n')
assert marker in text, "main() anchor missing"
text = text.replace(marker, addition, 1)

anchor = '    args = parser.parse_args()\n'
override = ('    args = parser.parse_args()\n'
            '    for item in args.set:\n'
            '        race, _sep, code = item.partition("=")\n'
            '        PREFIXES[int(race)] = code\n')
assert anchor in text, "parse_args anchor missing"
text = text.replace(anchor, override, 1)
path.write_text(text, encoding="utf-8")
print("added --set")
