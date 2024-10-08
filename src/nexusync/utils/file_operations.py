# src/utils/file_operations.py

import os
from typing import List, Tuple
import hashlib


def get_all_files(directory: str, recursive: bool = True) -> List[str]:
    """
    Get all file paths in the given directory.

    Args:
        directory (str): The directory to search for files.
        recursive (bool): If True, search subdirectories as well. Defaults to True.

    Returns:
        List[str]: A list of file paths.
    """
    file_paths = []
    if recursive:
        for root, _, files in os.walk(directory):
            for file in files:
                file_paths.append(os.path.join(root, file))
    else:
        file_paths = [
            os.path.join(directory, f)
            for f in os.listdir(directory)
            if os.path.isfile(os.path.join(directory, f))
        ]
    return file_paths


def get_file_hash(file_path: str) -> str:
    """
    Compute the MD5 hash of a file.

    Args:
        file_path (str): The path to the file.

    Returns:
        str: The MD5 hash of the file.
    """
    hasher = hashlib.md5()
    with open(file_path, "rb") as file:
        buf = file.read()
        hasher.update(buf)
    return hasher.hexdigest()


def get_changed_files(
    directory: str, old_hashes: dict
) -> Tuple[List[str], List[str], List[str]]:
    """
    Determine which files in the directory have been added, modified, or deleted.

    Args:
        directory (str): The directory to check for changes.
        old_hashes (dict): A dictionary of file paths and their previous hashes.

    Returns:
        Tuple[List[str], List[str], List[str]]: Lists of added, modified, and deleted file paths.
    """
    current_files = get_all_files(directory)
    current_hashes = {file: get_file_hash(file) for file in current_files}

    added = [file for file in current_files if file not in old_hashes]
    modified = [
        file
        for file in current_files
        if file in old_hashes and current_hashes[file] != old_hashes[file]
    ]
    deleted = [file for file in old_hashes if file not in current_files]

    return added, modified, deleted
