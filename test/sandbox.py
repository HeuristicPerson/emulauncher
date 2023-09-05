"""
File to do quick and manual python tests when needed.
"""

import os
import shutil
import subprocess

import libs.cons as cons


def list_files_with_positions(root_dir):
    file_positions = []

    def traverse_directory(path, level=0):
        nonlocal file_positions

        # Add the current directory to the list
        file_positions.append((path, level))

        # Iterate through the contents of the directory
        for item in os.listdir(path):
            item_path = os.path.join(path, item)

            # Check if the item is a directory
            if os.path.isdir(item_path):
                traverse_directory(item_path, level + 1)
            else:
                # Add the file to the list
                file_positions.append((item_path, level + 1))

    traverse_directory(root_dir)

    return file_positions

# Specify the root directory
root_directory = os.path.join(cons.s_TEST_DATA_DIR, 'libs_install', 'function_patch_dir', 'multi_rom')

file_positions = list_files_with_positions(root_directory)

# Print the list of files and their positions
for position, (file_path, level) in enumerate(file_positions, start=1):
    indentation = "    " * level
    print(f"{position}. {indentation}{file_path}")
