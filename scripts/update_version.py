import subprocess
import sys
from pathlib import Path

import toml


def get_git_tag():
    """
    Get the latest Git tag from the current commit.
    """
    try:
        tag = (
            subprocess.check_output(["git", "describe", "--tags", "--abbrev=0"])
            .strip()
            .decode()
        )
        return tag
    except subprocess.CalledProcessError as e:
        print("Error: Unable to get Git tag. Are you sure this commit has a tag?")
        sys.exit(1)


def update_pyproject_version(tag):
    """
    Update the version in pyproject.toml to match the given tag.
    """
    pyproject_path = Path(__file__).resolve().parent.parent / "pyproject.toml"
    if not pyproject_path.exists():
        print(f"Error: {pyproject_path} does not exist.")
        sys.exit(1)

    pyproject = toml.load(pyproject_path)

    # Update the version
    if "tool" in pyproject and "poetry" in pyproject["tool"]:
        pyproject["tool"]["poetry"]["version"] = tag
    else:
        print("Error: pyproject.toml does not have a [tool.poetry] section.")
        sys.exit(1)

    # Write back the updated file
    with open(pyproject_path, "w") as f:
        toml.dump(pyproject, f)

    print(f"Successfully updated pyproject.toml version to {tag}")


def main():
    tag = get_git_tag()
    print(f"Found Git tag: {tag}")
    update_pyproject_version(tag)


if __name__ == "__main__":
    main()
