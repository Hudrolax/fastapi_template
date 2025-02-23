import os


def get_env_value(name: str) -> str:
    value = os.getenv(name)
    if value is None:
        raise ValueError(
            f'{name} environment variable should be filled in the OS.')
    return value


