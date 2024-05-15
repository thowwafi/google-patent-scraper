import os


def make_dir_if_not_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
