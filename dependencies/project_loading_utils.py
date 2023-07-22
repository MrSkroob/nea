import json
import zipfile


def load_project(file_name: str) -> dict:
    """Returns the json data inside the scratch project with given file name"""
    with zipfile.ZipFile(file_name, "r") as f:
        project_json = json.loads(f.read("project.json").decode("utf-8"))
    return project_json


def load_python_file(file_name: str) -> dict:
    """Returns the contents of a text file in a line by line array"""
    with open(file_name, "r") as f:
        return f.readlines()
