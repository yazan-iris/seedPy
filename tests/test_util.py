import os


def path(file: str) -> str:
    return f'{os.getcwd()}/{file}'


def current_directory() -> str:
    return os.getcwd()
