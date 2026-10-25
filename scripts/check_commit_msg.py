import re
import sys
from pathlib import Path

TRAILER = re.compile(r"^co-authored-by:", re.IGNORECASE)


def check(message: str) -> list[str]:
    """
    Check a commit message against the project rule: one subject line, no body, no co-author trailer.

    Args:
        message (str): The raw commit message, including any lines git added as comments.

    Returns:
        list[str]: A description of each violation, empty when the message is valid.
    """
    lines = [line for line in message.splitlines() if not line.startswith("#") and line.strip()]

    problems = []
    if not lines:
        problems.append("the commit message is empty")
    if len(lines) > 1:
        problems.append("the commit message must be a single subject line with no body")
    if any(TRAILER.match(line) for line in lines):
        problems.append("the commit message must not contain a Co-Authored-By trailer")
    return problems


def main() -> int:
    """
    Validate the commit message file passed as the first argument.

    Returns:
        int: 0 when the message is valid, 1 otherwise.
    """
    problems = check(Path(sys.argv[1]).read_text())
    for problem in problems:
        print(f"commit-msg: {problem}", file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
