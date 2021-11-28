import yaml
import os
import re
import sys
import logging
from shutil import copyfile
from pathlib import Path
import praw
import csv


def get_working_directory() -> str:
    """This functions gets the working directory path.

    Returns:
        working_directory (str): The directory where database and yaml are located.
    """
    userdir = os.path.expanduser("~")
    working_directory = os.path.join(userdir, "TelegramRedditScrapper")
    if not os.path.exists(working_directory):
        os.makedirs(working_directory)
    return working_directory


def get_file_location(filename: str) -> str:
    """This function gets the full path location of a file

    Args:
        filename (str): Filename that needs the full path location

    Returns:
        full_path_file_location (str): Full path location of the file
    """
    working_directory = get_working_directory()
    full_path_file_location = os.path.join(working_directory, filename)
    return full_path_file_location


logging.basicConfig(
    filename=get_file_location("Running.log"),
    level=logging.INFO,
    format="%(asctime)s:%(levelname)s:%(message)s",
)


def load_config_file(config_file_path: str) -> dict:
    """This function is for loading yaml config file

    Args:
        config_file_path (str): File path for the config file to be loaded

    Returns:
        file_config (dict): Dictionary with config keys.

    Raises:
        IOError
    """
    try:
        with open(get_file_location(config_file_path), "r") as config_yaml:
            file_config = yaml.safe_load(config_yaml)
            return file_config
    except IOError:
        logging.error("Archivo de configuración no encontrado, generando llaves")


def generate_bot_token_file(config_file_path: str):
    """This function generates a file template with the required parameters

    Args:
        config_file_path (str): Where the file should be stored
    """
    db_selector = {
        "token_bot": "",
        "reddit_id": "",
        "reddit_secret": "",
        "reddit_agent": "",
    }
    with open(config_file_path, "w") as f:
        f.write(yaml.safe_dump(db_selector, default_flow_style=False))


def generate_already_sended_submissions_csv_file(config_file_path: str):
    """This function generates a file template with the required parameters

    Args:
        config_file_path (str): Where the file should be stored
    """

    column_name = [
        "ID",
        "Postname",
        "Subreddit",
    ]  # The name of the columns

    with open(config_file_path, "w") as f:
        writer = csv.writer(f)  # this is the writer object
        writer.writerow(
            column_name
        )  # this will list out the names of the columns which are always the first entrries


def update_already_sended_submissions_csv_file(update: dict, config_file_path: str):
    """This function generates a file template with the required parameters

    Args:
        config_file_path (str): Where the file should be stored
    """

    field_names = [
        "ID",
        "Postname",
        "Subreddit",
    ]  # The name of the columns

    try:
        with open("config_file_path", "a") as csv_file:
            dict_object = csv.DictWriter(csv_file, fieldnames=field_names)
            dict_object.writerow(update)
    except IOError:
        print("Archivo de configuración no encontrado, generando archivo")
        generate_already_sended_submissions_csv_file(config_file_path)


def get_bot_token(config_file_path: str) -> str:
    """Returns the bot token stored in config_file_path

    Args:
        config_file_path (str): Where the file is stored

    Returns:
        str: Token to access to Telegram Bot
    """
    try:
        with open(get_file_location(config_file_path), "r") as config_yaml:
            file_config = yaml.safe_load(config_yaml)
            return file_config["token_bot"]
    except IOError:
        print("Archivo de configuración no encontrado, generando archivo")
        generate_bot_token_file(config_file_path)


def check_if_submission_was_sent(sumission_id: str, config_file_path: str) -> bool:
    try:
        with open(
            config_file_path, mode="r"
        ) as csv_file:  # "r" represents the read mode
            my_reader = csv.DictReader(csv_file)  # this is the reader object
            for item in my_reader:
                if sumission_id == item["ID"]:
                    return True
                else:
                    return False
    except IOError:
        print("Archivo de configuración no encontrado, generando archivo")
        generate_already_sended_submissions_csv_file(config_file_path)
        return False


def get_reddit(config_file_path: str) -> praw.Reddit:
    # Read-only instance

    file_config = None
    try:
        with open(get_file_location(config_file_path), "r") as config_yaml:
            file_config = yaml.safe_load(config_yaml)
    except IOError:
        print("Archivo de configuración no encontrado, generando archivo")
        generate_bot_token_file(config_file_path)

    reddit_read_only = praw.Reddit(
        client_id=file_config["reddit_id"],  # your client id
        client_secret=file_config["reddit_secret"],  # your client secret
        user_agent=file_config["reddit_agent"],  # your user agent
    )
    return reddit_read_only


def set_bot_token(config_file_path: str, data: dict):
    """Saves the telegram token for being used for the bot telegram

    Args:
        config_file_path (str): Where the file is stored
        token (str): A valid token to access to Telegram Bot

    """
    try:
        with open(get_file_location(config_file_path), "r") as config_yaml:
            file_config = yaml.safe_load(config_yaml)
    except IOError:
        print("Archivo de configuración no encontrado, generando archivo")
        generate_bot_token_file(config_file_path)
    with open(config_file_path, "w") as f:
        f.write(yaml.safe_dump(data, default_flow_style=False))
