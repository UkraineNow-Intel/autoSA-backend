import configparser


def read_config(file_name):
    config = configparser.ConfigParser()
    config.read(file_name)
    return config
