"""Entry point for the application."""

import argparse
from pathlib import Path
import sys
from dotenv import load_dotenv
from app.assistant import Assistant
from app.generate_embeddings import EmbeddingsGenerator
from app.utils import Utils
from app.logging import setup_logging


class AppCLI:
    """Entry point for the application."""

    def __init__(self, book_filename: str = ""):
        self.book_filename = book_filename
        self.output_folder = Utils.strip_extension(book_filename)
        Utils.logger = setup_logging(self.output_folder)
        self.embeddings_collection = Utils.get_embeddings_db(self.output_folder)

    def generatedb(self) -> None:
        """
        Wrapper for calling the GenerateEmbeddings module
        """
        Utils.logger.info("Generating embeddings database...")
        embeddings_generator = EmbeddingsGenerator(self.book_filename)
        embeddings = embeddings_generator.generate_embeddings()
        if embeddings:
            Utils.logger.info(
                "Finished embeddings generation, vector database at /output/%s...",
                self.output_folder,
            )
            self.embeddings_collection = embeddings
        else:
            Utils.logger.critical("Embeddings generation failed, see logs for details.")
            sys.exit(1)

    def ask(self) -> str:
        """
        Wrapper for calling the chat module
        """
        if self.embeddings_collection:
            assistant = Assistant(self.book_filename, self.embeddings_collection)
            while True:
                user_input = input(
                    f"Ask a question about {self.book_filename} or type 'exit' to finish the session: "
                )
                if user_input == "exit":
                    Utils.logger.info("Finalizing session...")
                    break
                data = assistant.ask(user_input)
                print(data.get("answer", ""))
                print("References: ")
                print("\n".join(list(data.get("references", ""))))
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
    load_dotenv(dotenv_path = Path(__file__).resolve().parents[2] / ".env" )
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
