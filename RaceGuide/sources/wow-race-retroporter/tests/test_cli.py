from raceporter.cli import build_parser


def test_cli_exposes_expected_commands():
    parser = build_parser()
    commands = parser._subparsers._group_actions[0].choices
    assert set(commands) == {"doctor", "fetch", "plan", "build", "status", "reset"}


def test_online_doctor_does_not_require_local_only_source_tool(project_root, capsys):
    from raceporter.cli import command_doctor

    assert command_doctor(project_root) == 0
    output = capsys.readouterr().out
    assert "wow_export" in output
    assert "cascexplorer" not in output
    assert "Local CASC:   not required" in output
