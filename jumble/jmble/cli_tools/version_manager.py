""" CLI Tool to manage Poetry project versions """

import os
import re
import sys
import toml

from ..general_modules import utils
from ..general_modules.utils import e_open

VERSION_PATTERN = r"\d+\.\d+\.\d+"


def get_version_numbers(version: str) -> tuple[int]:
    """Get version numbers from version string"""

    return tuple(int(num) for num in version.split("."))


def main():
    """Main function"""

    args = utils.get_inputs()

    if args.h or args.help:
        print("Help text")
        return

    dir_path = args.path or os.getcwd()
    pyproject_file = os.path.join(dir_path, "pyproject.toml")

    if not os.path.exists(pyproject_file):
        raise FileNotFoundError("pyproject.toml not found")

    with e_open(pyproject_file) as file:
        pyproject = toml.load(file)

    current_version = utils.get_nested(pyproject, "tool.poetry.version")

    if not current_version:
        raise ValueError("Version not found in pyproject.toml")

    if not re.match(VERSION_PATTERN, current_version):
        raise ValueError(
            "Invalid version format in pyproject.toml, you will need to change format or update manually. Please use x.x.x"
        )

    major, minor, patch = get_version_numbers(current_version)

    new_version = None
    set_version = args.s or args.set

    if isinstance(set_version, str):
        set_version = set_version.strip()
        if not re.match(VERSION_PATTERN, set_version):
            raise ValueError("Invalid version format, please use x.x.x")

        new_version = set_version
    else:
        if args.major or args.M:
            major += 1
            minor = 0
            patch = 0
        elif args.minor or args.m:
            minor += 1
            patch = 0
        elif args.patch or args.p:
            patch += 1
        else:
            raise ValueError("Invalid arguments, please use -M, -m, -p or -s")

        new_version = f"{major}.{minor}.{patch}"

    print(f"Current version: {current_version}")
    print(f"New version: {new_version}")
    if new_version == current_version:
        print("Versions are the same, no changes made")
        return

    print("Updating pyproject.toml")
    pyproject["tool"]["poetry"]["version"] = new_version

    with e_open(pyproject_file, "w") as file:
        toml.dump(pyproject, file)


if __name__ == "__main__":
    main()
