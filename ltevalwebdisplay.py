import argparse
import pathlib

import data.scripts.webdisplay as webdisplay


def _create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser("lteval webpage displaying tool.")
    parser.add_argument(
        "dir",
        type=str,
        help=("index.html file of the lteval webpage or its directory."),
    )
    parser.add_argument(
        "--p",
        "-p",
        dest="port",
        type=int,
        default=8000,
        help="Port of the local web server.",
    )

    return parser


if __name__ == "__main__":
    args = _create_parser().parse_args()

    args_path = pathlib.Path(args.dir).resolve()
    if not args_path.exists():
        print(
            f'Path of index file: "{args_path}" '
            f"does not point to an existing file or directory!"
        )
        exit(1)

    server_dir_path = args_path if args_path.is_dir() else args_path.parent
    webdisplay.display_webpage(server_dir_path, args.port)
