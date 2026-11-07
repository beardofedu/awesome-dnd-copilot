#!/usr/bin/env python3
"""Preview or install selected committed campaign resources into a local directory."""

import argparse
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import sys

SOURCE = Path(__file__).absolute().parents[2]
TEMPLATE = PurePosixPath("campaign-creation/templates/campaign-starter")
FILE_REFERENCE = re.compile(r"`([A-Za-z0-9_][A-Za-z0-9_./-]*)`")


class InstallError(Exception):
    pass


def clean_relative(value):
    path = PurePosixPath(value)
    if not value or path.is_absolute() or any(p in ("", ".", "..") for p in value.split("/")):
        raise InstallError(f"Unsafe relative path: {value!r}")
    return path


def check_no_symlinks(path):
    """Reject symlinks in existing path components, without resolving them."""
    path = Path(os.path.abspath(path))
    current = Path(path.anchor)
    for component in path.parts[1:]:
        current = current / component
        try:
            info = current.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(info.st_mode):
            raise InstallError(f"Symlink not allowed: {current}")


def complete_kit(source, files):
    root = PurePosixPath(*files[0].parts[:3])
    names = {path.relative_to(root).as_posix() for path in files}
    if "README.md" not in names or not any(
            "/" not in name and name.endswith(".prompt.md") for name in names):
        return False
    readme = source.joinpath(*root.parts, "README.md")
    try:
        check_no_symlinks(readme)
        if not readme.is_file():
            return False
        lines = readme.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError, InstallError):
        return False

    # Check explicitly listed kit files, not paths mentioned in usage examples.
    in_files_section = False
    in_file_table = False
    for line in lines:
        if line.startswith("## "):
            in_files_section = line[3:].strip().lower() in {"files", "contents"}
        if re.match(r"^\|\s*file\s*\|", line, re.IGNORECASE):
            in_file_table = True
            continue
        if in_file_table and not line.startswith("|"):
            in_file_table = False
        text = line.split("|", 2)[1] if in_file_table and line.startswith("|") else (
            line if in_files_section and re.match(r"^\s*[-*]\s", line) else "")
        for name in FILE_REFERENCE.findall(text):
            try:
                clean_relative(name)
            except InstallError:
                return False
            if name not in names:
                return False
    return True


def discover(source):
    check_no_symlinks(source)
    try:
        result = subprocess.run(["git", "-C", str(source), "ls-tree", "-r", "--name-only", "-z", "HEAD"],
                                check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except (OSError, subprocess.CalledProcessError) as exc:
        raise InstallError(f"Cannot enumerate committed source files: {exc}") from exc
    paths = [clean_relative(os.fsdecode(p)) for p in result.stdout.split(b"\0") if p]
    profiles, agents, kits, starter = {}, {}, {}, []
    for path in paths:
        parts = path.parts
        if len(parts) == 2 and parts[1] == "copilot-instructions.md" and not parts[0].startswith("."):
            profiles[parts[0]] = path
        elif len(parts) == 3 and parts[1] == "agents" and path.suffix == ".md":
            agents[f"{parts[0]}/{parts[2]}"] = path
        elif len(parts) >= 4 and parts[1] == "session-kits":
            kits.setdefault(f"{parts[0]}/{parts[2]}", []).append(path)
        elif path.is_relative_to(TEMPLATE) and path != TEMPLATE:
            starter.append(path)
    kits = {name: files for name, files in kits.items() if complete_kit(Path(source), files)}
    return profiles, agents, kits, starter


def plan(source, destination, profile, agent_names, kit_names, with_starter):
    if ".." in Path(destination).parts or ".." in Path(source).parts:
        raise InstallError("Traversal in source or destination is not allowed")
    source = Path(os.path.abspath(source))
    destination = Path(os.path.abspath(destination))
    check_no_symlinks(source)
    check_no_symlinks(destination)
    if not source.is_dir() or not destination.is_dir():
        raise InstallError("Source and destination must be existing directories")
    protected = {Path("/"), Path.home(), Path("/root"), Path("/home")}
    system_trees = {Path("/etc"), Path("/usr"), Path("/var"), Path("/opt"),
                    Path("/bin"), Path("/sbin"), Path("/dev"), Path("/proc"), Path("/sys")}
    if (destination in protected or any(p == destination or p in destination.parents for p in system_trees)
            or destination == source or source in destination.parents or destination in source.parents):
        raise InstallError("Unsafe destination: choose a separate campaign directory, not a system root or source tree")
    profiles, agents, kits, starter = discover(source)
    if profile not in profiles:
        raise InstallError(f"Unknown profile: {profile}")
    mappings = [(profiles[profile], PurePosixPath(".github/copilot-instructions.md"))]
    for name in agent_names:
        if name not in agents:
            raise InstallError(f"Unknown agent: {name}")
        mappings.append((agents[name], PurePosixPath(".github/agents") / agents[name].name))
    for name in kit_names:
        if name not in kits:
            raise InstallError(f"Unknown or incomplete kit: {name}")
        for path in kits[name]:
            mappings.append((path, PurePosixPath(".github/session-kits") / path.parts[2] /
                             path.relative_to(PurePosixPath(*path.parts[:3]))))
    if with_starter:
        if not starter:
            raise InstallError("No committed starter template found")
        mappings.extend((path, path.relative_to(TEMPLATE)) for path in starter)
    entries, targets = [], set()
    for src_rel, dst_rel in mappings:
        clean_relative(str(src_rel))
        clean_relative(str(dst_rel))
        src = source.joinpath(*src_rel.parts)
        dst = destination.joinpath(*dst_rel.parts)
        check_no_symlinks(src)
        check_no_symlinks(dst)
        if dst in targets:
            raise InstallError(f"Multiple selections target {dst}")
        targets.add(dst)
        if dst.exists():
            raise InstallError(f"Destination already exists: {dst}")
        parent = dst.parent
        while parent != destination:
            if parent.exists() and not parent.is_dir():
                raise InstallError(f"Destination parent is not a directory: {parent}")
            parent = parent.parent
        try:
            if not src.is_file():
                raise InstallError(f"Source is not a regular file: {src}")
            data = src.read_bytes()
        except OSError as exc:
            raise InstallError(f"Cannot read source {src}: {exc}") from exc
        entries.append((src_rel, dst, data))
    # Detect a planned file that would also need to be a parent directory.
    for _, dst, _ in entries:
        if any(parent in targets for parent in dst.parents):
            raise InstallError(f"Conflicting planned paths: {dst}")
    return entries


def apply(entries, destination):
    created_files, created_dirs = [], []
    try:
        for _, dst, data in entries:
            missing = []
            parent = dst.parent
            while parent != destination and not parent.exists():
                missing.append(parent)
                parent = parent.parent
            check_no_symlinks(parent)
            for directory in reversed(missing):
                directory.mkdir()
                created_dirs.append(directory)
            check_no_symlinks(dst)
            # Exclusive creation prevents replacing a file that appears after preflight.
            with dst.open("xb") as output:
                created_files.append(dst)
                output.write(data)
    except (OSError, InstallError) as exc:
        errors = []
        for path in reversed(created_files):
            try:
                path.unlink()
            except OSError as error:
                errors.append(f"{path}: {error}")
        for path in reversed(created_dirs):
            try:
                path.rmdir()
            except OSError as error:
                errors.append(f"{path}: {error}")
        detail = f"; rollback incomplete: {'; '.join(errors)}" if errors else ""
        raise InstallError(f"Installation failed: {exc}{detail}") from exc


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", nargs="?", help="existing campaign directory")
    parser.add_argument("--list", action="store_true", help="list committed available resources")
    parser.add_argument("--profile", help="exactly one profile name")
    parser.add_argument("--agent", action="append", default=[], help="agent identifier; repeatable")
    parser.add_argument("--kit", action="append", default=[], help="complete kit identifier; repeatable")
    parser.add_argument("--starter", action="store_true", help="include the empty campaign starter")
    parser.add_argument("--apply", action="store_true", help="write files; default is preview")
    args = parser.parse_args(argv)
    try:
        if args.list:
            if args.destination or args.profile or args.agent or args.kit or args.starter or args.apply:
                raise InstallError("--list cannot be combined with installation options")
            profiles, agents, kits, _ = discover(SOURCE)
            for label, items in (("Profiles", profiles), ("Agents", agents), ("Complete kits", kits)):
                print(f"{label}:")
                for name in sorted(items):
                    print(f"  {name}")
            return 0
        if not args.destination or not args.profile:
            raise InstallError("A destination and exactly one --profile are required")
        if sum(1 for arg in (argv if argv is not None else sys.argv[1:]) if arg == "--profile" or arg.startswith("--profile=")) != 1:
            raise InstallError("Specify --profile exactly once")
        entries = plan(SOURCE, args.destination, args.profile, args.agent, args.kit, args.starter)
        print("Apply:" if args.apply else "Preview (no files written):")
        for src, dst, _ in entries:
            print(f"  {src} -> {dst}")
        if args.apply:
            apply(entries, Path(os.path.abspath(args.destination)))
        return 0
    except (InstallError, OSError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
