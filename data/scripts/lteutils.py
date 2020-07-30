import argparse
import pathlib
import shutil
import sys
from datetime import datetime

import data.scripts.outputconst as out
import data.scripts.futils as futils
from data.scripts.scene import load_scenes_from_directory


class Logger(object):
    # Redirecting of print() into both stdout and logging file

    def __init__(self, file_path: pathlib.Path):
        # One line buffered file
        self.file = file_path.open("w", buffering=1)
        self.stdout = sys.stdout
        sys.stdout = self

    def close(self):
        if self.stdout is not None:
            sys.stdout = self.stdout
            self.stdout = None
        if self.file is not None:
            self.file.close()
            self.file = None

    def write(self, data):
        self.file.write(data)
        self.stdout.write(data)

    def flush(self):
        self.file.flush()
        self.stdout.flush()

    def __del__(self):
        self.close()


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser("Light transport evaluation framework.")

    parser.add_argument(
        "cfg", type=str, default="", help="Evaluation configuration file."
    )

    parser.add_argument(
        "-c",
        "--c",
        dest="clear",
        type=str,
        choices=["n", "y", "fy"],
        default="y",
        help=(
            "Clear - whenever scene files generated for rendering "
            "of individual cases should be deleted. "
            "n (no) - files are not deleted. "
            "y (yes - default) - files are deleted after the rendering, "
            "in the case of failure generated scene file is preserved."
            "fy (forced yes) - files are deleted after the rendering "
            "(even in the case of failure)."
        ),
    )

    parser.add_argument(
        "-fc",
        "--fc",
        dest="force_clear",
        action="store_true",
        help=(
            "Force clear - deletes all files which are not original "
            " scene files e.g. generated files from previous runs). "
            "If set, cfg file is ignored (and can be empty string): "
            'python lteval.py "" -fc'
        ),
    )

    eof_parser = parser.add_mutually_exclusive_group(required=False)
    eof_parser.add_argument(
        "--eof",
        dest="eof",
        action="store_true",
        help="(default) End on failure - whenever execution of the evaluation "
        "script should be stopped if rendering of the scene fails.",
    )
    eof_parser.add_argument("--no-eof", dest="cache", action="store_false")
    parser.set_defaults(eof=True)

    return parser


def create_logger(output_dir_path: pathlib.Path) -> Logger:
    return Logger(output_dir_path / out.log_file)


def load_configuration_module(cfg_path: pathlib.Path):
    if not cfg_path.exists():
        print(f'Configuration file at "{cfg_path}" does not exist!')
        exit(1)

    cfg_mod = futils.import_module_from_file(str(cfg_path))

    return cfg_mod


def create_output_dir(cfg_mod, cfg_path: pathlib.Path) -> pathlib.Path:
    cfg_config = cfg_mod.configuration

    # Use name if specified, otherwise fallback
    # to the name of the configuration file
    if "name" not in cfg_config or cfg_config["name"] == "":
        cfg_name = cfg_path.stem
    else:
        cfg_name = cfg_config["name"]

    # Include date and time in the output directory name
    # If not explicitly disabled
    if "output_dir_date" not in cfg_config or cfg_config["output_dir_date"]:
        cfg_name += "-" + datetime.now().strftime("%Y-%m-%d-%H%M%S")

    # Create output directory in the specified output_dir,
    # or fallback to the ./results folder of the lteval framework.
    lteval_dir_path = pathlib.Path(__file__).parents[2]
    if "output_dir" in cfg_config:
        output_dir_path = (
            lteval_dir_path / cfg_config["output_dir"] / cfg_name
        ).resolve()
    else:
        output_dir_path = (lteval_dir_path / "results" / cfg_name).resolve()

    # Create the directory and any other necessary parent directories
    output_dir_path.mkdir(parents=True, exist_ok=True)
    return output_dir_path


def load_renderers(cfg_mod) -> dict:
    lteval_dir_path = pathlib.Path(__file__).parents[2].absolute()
    renderer_scripts_dir_path = lteval_dir_path / "data/scripts/renderers"

    # Mandatory attributes
    if not hasattr(cfg_mod, "renderers"):
        print('There is no "renderers" element in the configuration file!')
        exit(1)
    if not isinstance(cfg_mod.renderers, dict):
        print(
            '"renderers" element of the configuration file '
            "must be a dictionary: {}."
        )
        exit(1)

    renderers = {}

    # For every renderer specified in the configuration file
    for r_name, r_data in cfg_mod.renderers.items():
        r_options = None if "options" not in r_data else r_data["options"]

        # Resolve its executable path
        r_exec_path = (lteval_dir_path / r_data["path"]).resolve()
        if not r_exec_path.is_file():
            print(
                f'Executable of the renderer: "{r_name}" '
                f'at the location: "{r_exec_path}" '
                f"does not exist or path is not a file!"
            )
            print("Continuing on to test rest of the configuration...")
            continue

        # Load script supporting its type - rendering framework
        r_module_path = renderer_scripts_dir_path / (r_data["type"] + ".py")
        r_class = futils.get_renderer_class_from_file(str(r_module_path))
        if r_class:
            renderers[r_name] = r_class(r_exec_path, r_options)
        else:
            print(
                f'Renderer module at: "{r_module_path}" does not contain '
                f"exactly one renderer class. "
            )
            print("Continuing on to test rest of the configuration...")

    return renderers


def check_renderers_scene_files(scenes: list, renderers: dict):
    # Check if scene files of the defined renderers exist
    for scene in scenes:
        for r_name, r_module in renderers.items():
            if not r_module.scene_files_exist(scene):
                print(
                    f'Scene files of scene: "{scene.name}" '
                    f'for renderer: "{r_name}" do not exist!'
                )


def render_scene_cases(
    scenes: list,
    renderers: dict,
    test_cases: list,
    output_dir_path: pathlib.Path,
    eof: bool,
    clear: str,
):
    for scene in scenes:
        output_scene_dir_path = output_dir_path / scene.name
        output_scene_dir_path.mkdir(parents=True, exist_ok=True)

        for test_case in test_cases:
            renderer = renderers[test_case.renderer]

            # Generate scene file and render the scene
            renderer.prepare_scene_case(scene, test_case)

            try:
                renderer.render_scene_case(
                    scene, test_case, output_scene_dir_path
                )

                # Delete generated scene file
                if clear == "y":
                    renderer.clear_scene_case(scene, test_case)
            except Exception:
                # Renderering failed (no result image was generated and
                # as such it could not be copied to the output directory)
                print(
                    f'Rendering of scene: "{scene.name}", '
                    f'for test case: "{test_case.name}" failed!\n'
                )
                if clear == "fy":
                    renderer.clear_scene_case(scene, test_case)
                if eof:
                    # Stop script on failure (with exception)
                    raise

            # Copy reference image (if it exists) next to the rendered image
            reference_path = scene.path / renderer.scene_type / "reference.exr"

            if reference_path.is_file():
                shutil.copy(
                    reference_path,
                    output_scene_dir_path
                    / (
                        test_case.name
                        + out.refimg_stem_suffix
                        + reference_path.suffix
                    ),
                )


def clear_scenes_directory():
    scenes_dir_path = pathlib.Path(__file__).parents[2].absolute() / "scenes"

    # All scenes in the scenes directory
    scenes = load_scenes_from_directory(scenes_dir_path)

    # All renderer class implementations found in the renderers directory
    renderers = [
        rc()
        for rc in [
            futils.get_renderer_class_from_file(str(rf))
            for rf in (
                pathlib.Path(__file__).parent.absolute() / "renderers"
            ).glob("*.py")
        ]
        if rc
    ]

    # Clear all found scenes with all found renderers
    for scene in scenes:
        for renderer in renderers:
            renderer.clear_scene(scene)
