"""Entry point for the application."""

import argparse
from .utils import Utils
from .logging import setup_logging


class AppCLI:
    """Entry point for the application."""

    def __init__(self, outputfolder: str = ""):
        self.outputfolder = outputfolder
        Utils.logger = setup_logging(outputfolder)

    def action1(self) -> None:
        """
        Wrapper for calling other modules
        """
        Utils.logger.info("Executing action 1...")

    def action2(self) -> str:
        """
        Wrapper for calling other modules
        """
        Utils.logger.error("Executing action 2 with error...")

    def all(self) -> None:
        """Performs all of the actions in order."""
        self.action1()
        self.action2()


if __name__ == "__main__":
    valid_actions = ["action1", "action2", "all"]
    parser = argparse.ArgumentParser(description="AI app")
    parser.add_argument(
        "--outputfolder",
        help="Name of the folder inside output/ where user generated content will be saved for this run.",
        required=True,
    )
    parser.add_argument(
        "--actions",
        help=f'Actions to perform, if empty all actions will be executed, valid actions = {", ".join(valid_actions)}',
        required=False,
    )
    args = parser.parse_args()
    cli = AppCLI(args.outputfolder)
    switch = {"action1": cli.action1, "action2": cli.action2, "all": cli.all}
    if args.actions == "all" or not args.actions:
        cli.all()
    else:
        actions = args.actions.split("-")
        for action in actions:
            call = switch.get(action)
            call()
