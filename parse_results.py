import argparse
import os
from pathlib import Path

from parsing import parse_grit_html


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
        help="CSV output file path",
    )

    args = parser.parse_args()
    if not os.path.isfile(args.input_file_path):
        raise ValueError(f"input_file_path does not exist: {args.input_file_path}")

    return args


def main():
    args = parse_args()
    input_file_path = Path(args.input_file_path)
    output_file_path = Path(args.output_file_path)

    # read html file
    with open(input_file_path, "r") as input_file:
        html_text = input_file.read()

    df = parse_grit_html(html_text)

    # write output CSV file
    df.to_csv(output_file_path, header=True, index=False)


if __name__ == "__main__":
    main()
