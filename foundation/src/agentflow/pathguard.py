"""Which paths belong to an agentflow workspace, so tools and shell commands of an agent can be kept out of them.

Paths are made absolute, cleaned of ``.``/``..``/repeated separators and symbolic links, and compared by name
without regard to case where the platform's file system ignores it (``os.path.normcase``). A directory only counts as
a workspace when it holds the config file, so an unrelated folder with the same name is left alone.
"""

import os
import re
from collections.abc import Callable
from pathlib import Path

from agentflow.constants import CONFIG_FILE, WORKSPACE_DIR

# Both kinds of separator split a path: on Windows a model may write either, and elsewhere a backslash in a
# name is rare enough that treating it as a separator only makes the check stricter.
_SEPARATORS = re.compile(r"[\\/]+")


class WorkspaceWritePolicy:
    """``WriteTargetPolicy`` that protects everything under a ``.agentflow/`` directory that holds a config file."""

    def __init__(self, normcase: Callable[[str], str] = os.path.normcase) -> None:
        self._fold = normcase

    def is_protected(self, target: Path | str, cwd: Path) -> bool:
        resolved = self._resolve(target, cwd)
        parts = [part for part in _SEPARATORS.split(resolved) if part]
        wanted = self._fold(WORKSPACE_DIR)
        for index, part in enumerate(parts):
            if self._fold(part) == wanted and self._is_workspace(resolved, parts[: index + 1]):
                return True
        return False

    @staticmethod
    def _resolve(target: Path | str, cwd: Path) -> str:
        text = os.fspath(target)
        if not os.path.isabs(text):
            text = os.path.join(cwd, text)
        return os.path.realpath(text)

    @staticmethod
    def _is_workspace(resolved: str, parts: list[str]) -> bool:
        # Rebuild the directory from the resolved string, keeping its drive or leading separator.
        head = os.path.splitdrive(resolved)[0]
        prefix = head + (os.sep if resolved[len(head) :].startswith(("/", "\\")) else "")
        return (Path(prefix, *parts) / CONFIG_FILE).is_file()
