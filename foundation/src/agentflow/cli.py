"""Command-line entry point for agentflow."""

import argparse
from importlib.metadata import version


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="agentflow")
    parser.add_argument(
        "--version", action="version", version=f"agentflow {version('agentflow')}"
    )
    parser.parse_args(argv)
