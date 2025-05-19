"""Entry point for the application."""

import argparse
import sys
from .generate_embeddings import EmbeddingsGenerator
from .utils import Utils
from .logging import setup_logging


class AppCLI:
    """Entry point for the application."""

    def __init__(self, book_filename: str = ""):
        self.book_filename = book_filename
        self.outputfolder = Utils.strip_extension(book_filename)
        Utils.logger = setup_logging(self.outputfolder)
        self.embeddings = False

    def generatedb(self) -> None:
        """
        Wrapper for calling the GenerateEmbeddings module
        """
        Utils.logger.info("Generating embeddings database...")
        embeddings_generator = EmbeddingsGenerator(self.book_filename)
        if embeddings_generator.generate_embeddings():
            Utils.logger.info(
                "Finished embeddings generation, vector database at /output/%s...",
                self.outputfolder,
            )
            self.embeddings = True
        else:
            Utils.logger.critical("Embeddings generation failed, see logs for details.")
            sys.exit(1)

    def ask(self) -> str:
        """
        Wrapper for calling the chat module
        """
        if self.embeddings:
            Utils.logger.info("Asking about the book...")
        else:
            Utils.logger.critical(
                "Embeddings database has not been generated or cannot be found, run generatedb first"
            )
            sys.exit(1)

    def all(self) -> None:
        """Performs all of the actions in order."""
        self.generatedb()
        self.ask()


if __name__ == "__main__":
    valid_actions = ["generatedb", "ask", "all"]
    parser = argparse.ArgumentParser(description="AI app")
    parser.add_argument(
        "--book",
        help=(
            "Name of the book in /data/, the same name will be used for the output/ folder "
            "where user generated files will reside."
        ),
        required=True,
    )
    parser.add_argument(
        "--actions",
        help=(
            f"Actions to perform, if empty all actions will be executed, valid actions = {', '.join(valid_actions)}."
            " ask may only be called after generatedb has been completed"
        ),
        required=False,
    )
    args = parser.parse_args()
    cli = AppCLI(args.book)
    switch = {"generatedb": cli.generatedb, "ask": cli.ask, "all": cli.all}
    if args.actions == "all" or not args.actions:
        cli.all()
    else:
        actions = args.actions.split("-")
        for action in actions:
            call = switch.get(action)
            call()
