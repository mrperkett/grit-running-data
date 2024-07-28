import argparse
import os
from pathlib import Path

from utils import obfuscate_html_table


def parse_args() -> argparse.Namespace:
    """
    Parse command line arguments.

    Raises:
        ValueError: if input file does not exist

    Returns:
        argparse.Namespace: args contains input_file_path and output_file_path
    """
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--input",
        "-i",
        dest="input_file_path",
        type=str,
        required=True,
        help="HTML input file path",
    )
    parser.add_argument(
        "--output",
        "-o",
        dest="output_file_path",
        type=str,
        required=True,
        help="obfuscated HTML output file path",
    )

    args = parser.parse_args()
    if not os.path.isfile(args.input_file_path):
        raise ValueError(f"input_file_path does not exist: {args.input_file_path}")

    return args


def main():
    # parse command line arguments
    args = parse_args()
    input_file_path = Path(args.input_file_path)
    output_file_path = Path(args.output_file_path)

    # read html file
    with open(input_file_path, "r") as input_file:
        html_text = input_file.read()

    obfuscated_html_text = obfuscate_html_table(html_text, seed=42)

    # write output file
    with open(output_file_path, "wb") as out_file:
        out_file.write(obfuscated_html_text)


if __name__ == "__main__":
    main()
