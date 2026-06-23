from __future__ import annotations

import shutil
import subprocess
import sys
from collections.abc import Callable, Sequence
from pathlib import Path

RunCommand = Callable[[Sequence[str]], int]
PrintFn = Callable[[str], None]

COURSE_OF_ACTION = (
    "Could not create .venv.",
    "Your system Python may be missing venv/ensurepip support.",
    "",
    "On Ubuntu/Debian, run:",
    "  sudo apt update && sudo apt install -y python3 python3-venv python3-pip make",
    "  rm -rf .venv && make setup",
    "",
    "If sudo is not available but uv is installed, run:",
    "  rm -rf .venv && make setup-uv",
)


def _run_subprocess(command: Sequence[str]) -> int:
    return subprocess.run(command, check=False).returncode


def _create_venv_with_system_python(venv_path: Path) -> int:
    return subprocess.run(
        ["python3", "-m", "venv", str(venv_path)],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    ).returncode


def _print_lines(print_fn: PrintFn, *lines: str) -> None:
    for line in lines:
        print_fn(line)


def _default_print(message: str) -> None:
    print(message, flush=True)


def _install_with_pip(run_command: RunCommand, pip_path: Path, requirements_path: Path) -> int:
    return run_command([str(pip_path), "install", "-r", str(requirements_path)])


def _bootstrap_with_uv(
    run_command: RunCommand,
    venv_path: Path,
    python_path: Path,
    requirements_path: Path,
    print_fn: PrintFn,
) -> int:
    _print_lines(
        print_fn,
        "",
        "Falling back to uv to create a local environment automatically...",
    )
    if run_command(["uv", "venv", "--clear", str(venv_path)]) != 0:
        return 1
    return run_command(
        [
            "uv",
            "pip",
            "install",
            "--python",
            str(python_path),
            "-r",
            str(requirements_path),
        ]
    )


def ensure_project_environment(
    repo_root: Path | None = None,
    *,
    has_uv: bool | None = None,
    run_command: RunCommand | None = None,
    print_fn: PrintFn = _default_print,
    force_uv: bool = False,
) -> int:
    root = repo_root or Path.cwd()
    venv_path = root / ".venv"
    pip_path = venv_path / "bin" / "pip"
    python_path = venv_path / "bin" / "python"
    requirements_path = root / "requirements.txt"
    runner = run_command or _run_subprocess
    uv_available = has_uv if has_uv is not None else shutil.which("uv") is not None

    if force_uv:
        if not uv_available:
            print_fn("uv is required for setup-uv. Install uv or use make setup.")
            return 1
        return _bootstrap_with_uv(runner, venv_path, python_path, requirements_path, print_fn)

    if pip_path.exists():
        return _install_with_pip(runner, pip_path, requirements_path)

    if run_command is not None:
        venv_creation_exit_code = run_command(["python3", "-m", "venv", str(venv_path)])
    else:
        venv_creation_exit_code = _create_venv_with_system_python(venv_path)

    if venv_creation_exit_code == 0 and pip_path.exists():
        return _install_with_pip(runner, pip_path, requirements_path)

    if uv_available:
        return _bootstrap_with_uv(runner, venv_path, python_path, requirements_path, print_fn)

    print_fn("")
    _print_lines(print_fn, *COURSE_OF_ACTION)
    return 1


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    force_uv = "--uv" in args
    return ensure_project_environment(force_uv=force_uv)


if __name__ == "__main__":
    raise SystemExit(main())
