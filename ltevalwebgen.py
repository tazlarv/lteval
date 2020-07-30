import argparse
import pathlib

import data.scripts.webgen as webgen
import data.scripts.webdisplay as webdisplay


def _create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser("lteval webpage generation tool.")
    parser.add_argument(
        "dir",
        type=str,
        help=(
            "lteval configuration output directory. "
            "If lteval configuration file (cfg.py) is present in this "
            "directory, information in it will be used to enhance "
            "generation of the webpage. "
            "Any additional scenes and test cases not defined in the "
            "configuration file will be added to the generated webpage."
        ),
    )
    parser.add_argument(
        "-d",
        "--d",
        action="store_true",
        dest="display",
        help=(
            "Display the generated webpage with "
            "the default webdisplay.py settings."
        ),
    )

    return parser


if __name__ == "__main__":
    args = _create_parser().parse_args()

    dir_path = pathlib.Path(args.dir).resolve()
    if not dir_path.is_dir():
        print(f'"{str(dir_path)}" is not a directory or does not exist!')
        exit(1)

    webgen.WebGenerator(dir_path).generate_webpage()

    if args.display:
        webdisplay.display_webpage(dir_path)
