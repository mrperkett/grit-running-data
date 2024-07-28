import random
from pathlib import Path

from lxml import etree

first_names = [
    "Aragorn",
    "Boromir",
    "Frodo",
    "Gandalf",
    "Galadriel",
    "Gimli",
    "Legolas",
    "Meriadoc",
    "Pippin",
    "Samwise",
    "Bilbo",
    "Eowyn",
    "Sauron",
    "Saruman",
    "Faramir",
    "Eomer",
    "Glorfindel",
]

last_names = [
    "Potter",
    "Granger",
    "Weasley",
    "Malfoy",
    "Hagrid",
    "Lovegood",
    "Dumbledore",
    "Snape",
    "McGonagall",
    "Diggory",
    "Longbottom",
    "Lupin",
    "Tonks",
    "Dursley",
    "Scamander",
]


def obfuscate_html_table(html_text: str, seed: int = 42) -> None:
    """
    Replace the first name and last names in the input HTML text.

    Args:
        html_text (str):
        seed (int, optional): value to seed random number generator. Defaults to 42.
    """
    random.seed(seed)
    root = etree.HTML(html_text)

    # replace all first names
    first_name_nodes = root.findall(".//div[@class='participantName__name__firstName']")
    for first_name_node in first_name_nodes:
        first_name_node.text = random.choice(first_names)

    # replace all last names
    last_name_nodes = root.findall(".//div[@class='participantName__name__lastName']")
    for last_name_node in last_name_nodes:
        last_name_node.text = random.choice(last_names)

    return etree.tostring(root)
