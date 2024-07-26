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
    input_file = Path(args.input_file_path)
    output_file = Path(args.output_file_path)
    df = parse_grit_html(input_file)
    df.to_csv(output_file, header=True, index=False)


if __name__ == "__main__":
    main()
