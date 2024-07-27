"""
Collection of functions to parse GRIT HTML files.
"""

from pathlib import Path
from typing import Callable, Union

import pandas as pd
from lxml import etree

# column names expected when parsing HTML
EXPECTED_HEADER = [
    "Place",
    "Bib",
    "Name",
    "Gender",
    "City",
    "State",
    "Country",
    "Clock",  # NOTE: "<br>Time" dropped by lxml
    "Chip",  # NOTE: "<br>Time" dropped by lxml
    "Distance in Miles",
    "Progress",
    "Elevation Gain",
    "Pace",
    "Age",
    "Age",  # NOTE: "<br>Percentage" dropped by lxml
    "Run Crew Name",
]

# column names to use
REFORMATTED_HEADER = [
    "place",
    "bib",
    "name",
    "gender",
    "city",
    "state",
    "country",
    "clock_time",
    "chip_time",
    "distance_miles",
    "progress",
    "elevation_gain_ft",
    "pace",
    "age",
    "age_percentage",
    "run_crew_name",
]


def get_simple_value_handler(
    dtype: type,
) -> Callable[[etree._Element], Union[None, int, float, str]]:
    """
    Return value handler for the provided type (int, float, str)

    Args:
        dtype (type): int, float, str

    Raises:
        ValueError: if dtype is not recognized

    Returns:
        Callable[[etree._Element], Union[None, int, float, str]]: function that processes an
            etree._Element node and returns a value
    """
    if dtype not in (int, float, str):
        raise ValueError(f"dtype ({dtype}) must be int, float, or str")

    def simple_value_handler(node):
        if node.text is None:
            return None
        return dtype(node.text)

    return simple_value_handler


def participant_name_handler(node: etree._Element) -> str:
    """
    Process HTML for participant name

    Args:
        node (etree._Element): HTML node containing participantName__name node with top level
            node <td class="ta-left">

    Raises:
        ValueError: if structure is not as expected

    Returns:
        str: participant name in the format f"{first_name} {last_name}"
    """
    # Example node to process
    # <td class="ta-left">
    #     <div class="participantName">
    #         <div class="participantName__image">
    #             <div class="rsuCircleImg rsuCircleImg--xs rsuCircleImg--firstChar"><span>R</span></div>
    #         </div>
    #         <div class="participantName__name">
    #             <div class="participantName__name__firstName">Matthew</div>
    #             <div class="participantName__name__lastName">Perkett</div>
    #         </div>
    #     </div>
    # </td>

    # <td class="ta-left">
    if node.tag != "td":
        raise ValueError()
    if node.values() != ["ta-left"]:
        raise ValueError(f"Expected node value 'ta-left', but got {node.values()}")
    if len(node) != 1:
        raise ValueError(f"Expected node length == 1, but got {len(node)}")

    # <div class="participantName">
    pname_node = node[0]
    if pname_node.values() != ["participantName"]:
        raise ValueError(f"Expected node value 'participantName', but got {pname_node.values()}")
    if len(pname_node) != 2:
        raise ValueError(f"Expected node length == 2, but got {len(pname_node)}")

    # <div class="participantName__name">
    pname_name_node = pname_node[1]
    if pname_name_node.values() != ["participantName__name"]:
        raise ValueError(
            f"Expected node value 'participantName__name', but got {pname_name_node.values()}"
        )
    if len(pname_name_node) != 2:
        raise ValueError(f"Expected node length == 2, but got {len(pname_name_node)}")

    # <div class="participantName__name__firstName">Matthew</div>
    first_name_node = pname_name_node[0]
    if first_name_node.values() != ["participantName__name__firstName"]:
        raise ValueError(
            f"Expected node value 'participantName__name__firstName', but got {first_name_node.values()}"
        )
    first_name = first_name_node.text

    # <div class="participantName__name__lastName">Perkett</div>
    last_name_node = pname_name_node[1]
    if last_name_node.values() != ["participantName__name__lastName"]:
        raise ValueError(
            f"Expected node value 'participantName__name__lastName', but got {last_name_node.values()}"
        )
    last_name = last_name_node.text

    name = f"{first_name} {last_name}"
    return name


def elevation_gain_handler(node: etree._Element) -> float:
    """
    Process HTML node to get elevation gain in feet

    Args:
        node (etree._Element): HTML node with elevation (e.g. "<td>396ft (120.7m)</td>")

    Raises:
        ValueError: elevation gain text is not formatted as expected

    Returns:
        float: elevation_ft
    """
    # Example:
    # <td>396ft (120.7m)</td>
    s = node.text
    n = s.find("ft")
    m = s.find("(")
    p = s.find("m)")
    if n == -1 or m == -1 or p == -1:
        raise ValueError(f"elevation gain text is not formatted as expected ('{s}')")
    if not (n < m < p):
        raise ValueError(f"elevation gain text is not formatted as expected ('{s}')")

    elevation_ft = float(s[:n].replace(",", ""))
    # elevation_m = float(s[m + 1 : p].replace(",", ""))
    return elevation_ft


def get_handlers() -> list[Callable]:
    """
    Return a handler to process the data node from each column of the table

    Returns:
        list[Callable]: list of handlers (one for each column)
    """
    # TODO: parse clock_time, chip_time, pace into time or deltatime object
    # TODO: parse percent into a float instead of str

    handlers = [
        get_simple_value_handler(int),  # "place",
        get_simple_value_handler(int),  # "bib",
        participant_name_handler,  # "name",
        get_simple_value_handler(str),  # "gender",
        get_simple_value_handler(str),  # "city",
        get_simple_value_handler(str),  # "state",
        get_simple_value_handler(str),  # "country",
        get_simple_value_handler(str),  # "clock_time",
        get_simple_value_handler(str),  # "chip_time",
        get_simple_value_handler(float),  # "distance_miles",
        get_simple_value_handler(str),  # "progress",
        elevation_gain_handler,  # "elevation_gain_ft",
        get_simple_value_handler(str),  # "pace",
        get_simple_value_handler(int),  # "age",
        get_simple_value_handler(float),  # "age_percentage",
        get_simple_value_handler(str),  # "run_crew_name",
    ]

    return handlers


def parse_grit_table_header(table_header: Union[etree._Element, None]) -> list[str]:
    """
    Parse the table header to get all the column names

    Args:
        table_header (Union[etree._Element, None]): node to parse (with tag == 'thead')

    Raises:
        ValueError: node is not in expected format

    Returns:
        list[str]: header
    """
    if table_header is None:
        raise ValueError("table_header is None")
    if table_header.tag != "thead":
        raise ValueError("table_header tag is expected to be thead")
    if len(table_header) != 1 or table_header[0].tag != "tr":
        raise ValueError("Expected table_header to have a single child with tag 'tr'")
    header = [node.text for node in table_header[0]]
    return header


def parse_grit_table_body(
    table_body: Union[etree._Element, None], handlers
) -> list[list[Union[str, int, float]]]:
    """
    Parse the table body returning a list of lists with all of the data.

    Args:
        table_body (Union[etree._Element, None]): node to parse (with tag == 'tbody')
        handlers (_type_): list of functions equal to the number of columns that handle parsing each
            data node

    Raises:
        ValueError: node isn't formatted as expected

    Returns:
        list[list[str]]: data
    """
    if table_body is None:
        raise ValueError(f"table_body is None")
    if table_body.tag != "tbody":
        raise ValueError("table_body tag is expected to be 'tbody'")
    if len(table_body) < 1:
        raise ValueError("Expected table_body to have one or more children")

    data = []
    for row_node in table_body:
        if row_node.tag != "tr":
            raise ValueError("Expected table_body child node to have the tag 'tr'")
        if len(row_node) != len(handlers):
            raise ValueError(
                f"Expected the row to have the same length as number of handlers ({len(handlers)})"
            )

        row = []
        for data_node, handler in zip(row_node, handlers):
            if data_node.tag != "td":
                raise ValueError("Expected data_node to have the tag 'td'")
            row.append(handler(data_node))
        data.append(row)

    return data


def parse_grit_html(inp_file: Path) -> pd.DataFrame:
    """
    Parse the GRIT HTML table node and build a Pandas dataframe with the results

    Args:
        inp_file (Path): saved HTML input file path

    Raises:
        ValueError: header does not match what was expected (maybe format has changed?)

    Returns:
        pd.DataFrame: df
    """
    # read html file
    with open(inp_file, "r") as input_file:
        s = input_file.read()

    # parse table header to verify it matches what is expected
    table_header = etree.HTML(s).find("body/table/thead")
    table_column_names = parse_grit_table_header(table_header)
    if table_column_names != EXPECTED_HEADER:
        raise ValueError(
            "header does not match what was expected.  Are you parsing the correct file?"
        )

    column_names = REFORMATTED_HEADER
    handlers = get_handlers()

    # parse table body
    table_body = etree.HTML(s).find("body/table/tbody")
    data = parse_grit_table_body(table_body, handlers)

    df = pd.DataFrame(data, columns=column_names)

    return df
