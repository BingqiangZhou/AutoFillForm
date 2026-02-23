"""
YAML configuration file reader for survey rules.
"""
import os
import yaml


def list_yaml_files(directory):
    """
    List all YAML files in the given directory.

    Args:
        directory (str): The path to the directory to search for YAML files.

    Returns:
        list: A list of YAML file names (not full paths).
    """
    yaml_files = []
    for item in os.listdir(directory):
        if item.endswith('.yaml') or item.endswith('.yml'):
            yaml_files.append(item)
    return yaml_files


def read_yaml_file(file_path):
    """
    Read a YAML file and return its content.

    Args:
        file_path (str): Path to the YAML file.

    Returns:
        dict: The parsed YAML content.
    """
    with open(file_path, 'r', encoding="utf-8") as file:
        data = yaml.safe_load(file)
    return data


def read_data_from_yaml_file(folder_path, file_name=None):
    """
    Read a YAML file from the specified folder.

    Args:
        folder_path (str): Path to the folder containing YAML files.
        file_name (str, optional): Specific file name to read. If None, returns
                                   the first YAML file found.

    Returns:
        dict or None: The parsed YAML content, or None if no file found.
    """
    if file_name:
        file_path = os.path.join(folder_path, file_name)
        if os.path.exists(file_path):
            return read_yaml_file(file_path)
        return None

    # Get all YAML files
    yaml_files = list_yaml_files(folder_path)
    if not yaml_files:
        return None

    # Use the first file if no specific file requested
    file_path = os.path.join(folder_path, yaml_files[0])
    return read_yaml_file(file_path)


def get_yaml_files_dict(folder_path):
    """
    Get a dictionary of all YAML files in the folder.

    Args:
        folder_path (str): Path to the folder containing YAML files.

    Returns:
        dict: Dictionary with file names as keys and their full paths as values.
    """
    yaml_files = list_yaml_files(folder_path)
    return {name: os.path.join(folder_path, name) for name in yaml_files}


if __name__ == "__main__":
    folder_path = "../rules"
    yaml_dict = get_yaml_files_dict(folder_path)
    for name, path in yaml_dict.items():
        print(f"{name}: {path}")
