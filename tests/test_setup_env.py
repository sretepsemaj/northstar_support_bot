from backend.core.setup_env import ensure_project_environment


def test_setup_env_falls_back_to_uv_when_python_venv_fails(tmp_path):
    repo_root = tmp_path
    calls = []
    outputs = []

    def fake_run(command):
        calls.append(tuple(command))
        if command[:3] == ["python3", "-m", "venv"]:
            return 1
        return 0

    def fake_print(message=""):
        outputs.append(message)

    exit_code = ensure_project_environment(
        repo_root=repo_root,
        has_uv=True,
        run_command=fake_run,
        print_fn=fake_print,
    )

    assert exit_code == 0
    assert calls == [
        ("python3", "-m", "venv", str(repo_root / ".venv")),
        ("uv", "venv", "--clear", str(repo_root / ".venv")),
        (
            "uv",
            "pip",
            "install",
            "--python",
            str(repo_root / ".venv" / "bin" / "python"),
            "-r",
            str(repo_root / "requirements.txt"),
        ),
    ]
    assert any("Falling back to uv" in line for line in outputs)


def test_setup_env_uses_existing_pip_when_virtualenv_is_ready(tmp_path):
    repo_root = tmp_path
    pip_path = repo_root / ".venv" / "bin" / "pip"
    pip_path.parent.mkdir(parents=True)
    pip_path.write_text("#!/bin/sh\n")
    calls = []

    exit_code = ensure_project_environment(
        repo_root=repo_root,
        has_uv=False,
        run_command=lambda command: calls.append(tuple(command)) or 0,
    )

    assert exit_code == 0
    assert calls == [
        (str(pip_path), "install", "-r", str(repo_root / "requirements.txt")),
    ]


def test_setup_env_reports_failure_when_python_venv_fails_and_uv_is_missing(tmp_path):
    repo_root = tmp_path
    outputs = []

    exit_code = ensure_project_environment(
        repo_root=repo_root,
        has_uv=False,
        run_command=lambda command: 1,
        print_fn=lambda message="": outputs.append(message),
    )

    assert exit_code == 1
    assert any("Could not create .venv." in line for line in outputs)
    assert any("make setup-uv" in line for line in outputs)
