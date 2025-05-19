"""Shared utilities for the app."""

import pathlib


class Utils:
    """Utilities for the CV builder."""

    logger = None

    def __init__(self, output_folder_name):
        self.output_folder_name = output_folder_name

    @staticmethod
    def get_output_path(output_folder_name: str, create: bool = False) -> str:
        """
        Returns the absolute output path for a given folder name.

        Args:
        output_folder_name (str): The name of the folder inside /output/ whose absolute path is requiered
        create (bool, optional): Whether to create the directory if it doesn't exist. Defaults to False.

        Returns:
        str: The absolute path to the required output folder.
        """
        path = f"output/{output_folder_name}"
        root_path = pathlib.Path(__file__).resolve().parents[2]
        output_path = root_path / path
        if create:
            pathlib.Path(output_path).mkdir(exist_ok=True)
        return output_path

    @staticmethod
    def get_data_path() -> str:
        """
        Returns the absolute data path.

        Returns:
        str: the absolute path to the /data/ folder of the app
        """
        path = "data"
        root_path = pathlib.Path(__file__).resolve().parents[2]
        data_path = root_path / path
        return data_path

    @staticmethod
    def save_file_to_output(
        output_folder_name: str, file_name: str, content: str, create: bool = True
    ) -> bool:
        """
        Saves a text file to a subfolder in /output, if the folder doesnt exists it is created

        Args:
        output_folder_name (str): The name of the folder inside /output/ where the file should be stored
        file_name (str): The name with which the file will be saved
        content (str): The tex content of the file to be saved
        create (bool, optional): Whether to create the directory if it doesn't exist. Defaults to False.

        Returns:
        bool: Wether the file was saved successfully, if the save fails file.write will raise an exception.
        """
        output_path = Utils.get_output_path(output_folder_name, create=create)
        with open(f"{output_path}/{file_name}", "w", encoding="utf-8") as file:
            file.write(content)
            print(f"Saving to output/{file_name}")

        return True
