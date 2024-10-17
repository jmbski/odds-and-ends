""" CLI tool to automate git push commands """

import os
import sys

from ..general_modules import utils

LOCAL_DIR = os.getcwd()


def get_branch() -> str:
    """Get the current git branch

    Returns:
        str: The current git branch
    """

    return utils.cmdx("git branch --show-current")


def has_origin_branch(branch: str) -> bool:
    """Check if the branch has an origin

    Args:
        branch (str): The branch to check

    Returns:
        bool: True if the branch has an origin, False otherwise
    """

    return bool(utils.cmdx(f"git branch -r --list origin/{branch}"))


def get_unstaged_changes() -> list[str]:
    """Get the unstaged changes in the current git repository

    Returns:
        list[str]: List of files with unstaged changes
    """

    return [
        file.strip() for file in utils.cmdx("git diff --name-only").splitlines()
    ] or []


def add_files(files: list[str]) -> None:
    """Add files to the git staging area

    Args:
        files (list[str]): List of files to add
    """

    utils.cmdx(f"git add {' '.join(files)}")


def get_repository_root() -> str:
    """Get the root directory of the current git repository

    Returns:
        str: The root directory of the current git repository
    """

    return utils.cmdx("git rev-parse --show-toplevel")


def main():
    """Main function"""

    branch = get_branch()

    if not branch:
        print("No branch found")
        sys.exit(1)

    commit_message = " ".join(sys.argv[1:]).strip()
    commit_message = commit_message or "Update files"

    has_origin = has_origin_branch(branch)
    repo_root = get_repository_root().strip()
    untracked_files = [os.path.join(repo_root, file) for file in get_unstaged_changes()]

    print(f"Untracked files: {untracked_files}")

    print("Adding files to staging area")

    add_files(untracked_files)

    print(f"Committing changes with message: \n{commit_message}\n")
    utils.cmdx(f'git commit -m "{commit_message}"')

    print("Pushing changes")
    if not has_origin:
        print("No origin branch found, creating one")
        utils.cmdx(f"git push --set-upstream origin {branch}")
    else:
        utils.cmdx("git push")


if __name__ == "__main__":
    main()
