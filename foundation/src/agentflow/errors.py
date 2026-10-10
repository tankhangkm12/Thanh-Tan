"""The single exception type agentflow raises for expected failures."""

from agentflow.constants import ExitCode


class AgentflowError(Exception):
    """An expected failure: the CLI prints the message and exits with ``code``."""

    def __init__(self, message: str, code: ExitCode) -> None:
        super().__init__(message)
        self.code = code
