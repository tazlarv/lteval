import pathlib
import subprocess
import shlex
import re

from data.scripts.renderers.abstractrenderer import AbstractRenderer
from data.scripts.scene import Scene
from data.scripts.tcase import TestCase


class Pbrt_3(AbstractRenderer):
    def __init__(
        self, executable_path: pathlib.Path = None, options: str = None
    ):
        self.scene_type = "pbrt_3"
        self.scene_suffix = ".pbrt"
        self.executable_path = executable_path
        self.options = options
        self._options_tokens = [] if options is None else shlex.split(options)
        self._test_cases = {}

    def scene_files_exist(self, scene: Scene) -> bool:
        # Check if all files for rendering of the scene exists
        dir_path = self._scene_dir_path(scene)
        return (
            (dir_path / ("scene" + self.scene_suffix)).exists()
            and (dir_path / ("settings" + self.scene_suffix)).exists()
            and (dir_path / ("description" + self.scene_suffix)).exists()
        )

    def prepare_scene_case(self, scene: Scene, test_case: TestCase):
        self._prepare_test_case(test_case)

        settings_path = self._scene_dir_path(scene) / (
            "settings" + self.scene_suffix
        )

        with open(settings_path, "r") as f:
            settings_str = f.read()

        # Remove comment strings which would confuse our parsing
        settings_no_comments_str = re.sub(r"#.*", "", settings_str)

        # Split the settings into tokens
        tokens = re.split(r"(\W+)", settings_no_comments_str)

        # Find indices of indetifier tokens
        identifier_indices = self._get_identifier_indices(tokens)

        # Generate content of new scene file
        case_content_string = self._get_case_content_string(
            tokens, identifier_indices, test_case
        )

        with open(self._scene_case_path(scene, test_case), "w") as f:
            f.write(case_content_string)

    def render_scene_case(
        self, scene: Scene, test_case: TestCase, output_dir_path: pathlib.Path
    ):
        scene_case_path = self._scene_case_path(scene, test_case)

        # Run the rendering, save the resulting file next to the scene file
        result_path = scene_case_path.with_suffix(".exr")

        process = subprocess.Popen(
            [str(self.executable_path)]
            + self._options_tokens
            + ["--outfile", str(result_path), str(scene_case_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

        # Redictects output of subprocess stdout to the sys.stdout via print()
        # sys.stdout can be changed to a customized object (e.g. log to a file)
        for line in iter(process.stdout.readline, ""):
            # Lines contain endline characters already
            print(line, end="")

        process.wait()

        # Move resulting HDR image to the provided output directory
        result_path.replace(output_dir_path / (test_case.name + ".exr"))

    def clear_scene_case(self, scene: Scene, test_case: TestCase):
        # Delete files which were generated for rendering
        # of a given combination of scene and test_case
        scene_case_path = self._scene_case_path(scene, test_case)
        if scene_case_path.exists():
            self._scene_case_path(scene, test_case).unlink()

    def clear_scene(self, scene: Scene):
        # Deletes all files from the scene folder
        # which are not necessary for future rendering.
        for file_path in self._scene_dir_path(scene).glob("*.pbrt"):
            file_name = file_path.stem
            if (
                file_name != "scene"
                and file_name != "settings"
                and file_name != "description"
            ):
                file_path.unlink()

        for file_path in self._scene_dir_path(scene).glob("*.exr"):
            if file_path.stem != "reference":
                file_path.unlink()

    def _scene_dir_path(self, scene: Scene) -> pathlib.Path:
        return scene.path / self.scene_type

    def _scene_case_path(
        self, scene: Scene, test_case: TestCase
    ) -> pathlib.Path:
        return self._scene_dir_path(scene) / (
            "__lteval_" + test_case.name + self.scene_suffix
        )

    def _prepare_test_case(self, test_case: TestCase):
        # Prepare test_case parameters for use in the native format

        # Do it only once for each test_case
        if test_case.name in self._test_cases:
            return

        # For each parameter set create corresponding pbrt statement
        # Statement: identifier "type" parameter-list
        # e.g. Integrator/Sampler/PixelFilter
        param_subsets = {}
        for name, params in test_case.parameter_set.parameters.items():
            statement = name
            for param in params:
                if param[1] == "":
                    # Parameter with no type is not parameter list
                    if param[0] == "type":
                        # Parameter named type is a "type" of the statement
                        statement += f' "{param[2]}"'
                    elif param[0] == "":
                        # Parameter with no name should be list of values
                        statement += f" {param[2]}"
                    else:
                        # Should not happen - such construct is not supported
                        print(
                            f'Tried to create pbrt parameter "{name}" '
                            f"without specified type! "
                            f'Make sure that ["type", "", "TODO: typename"] '
                            f"is specified in the element parameter list."
                        )
                else:
                    # Parameter with specified type is a pbrt parameter list
                    # Parameter list: "type name" [ value or values ]
                    statement += f' "{param[1]} {param[0]}"'
                    statement += (
                        f" {self._get_pbrt_parameter_value_str(param[2])}"
                    )

            param_subsets[name] = statement

        # Add these test case data to the dictionary of all prepared test cases
        self._test_cases[test_case.name] = param_subsets

    def _get_pbrt_parameter_value_str(self, param) -> str:
        if isinstance(param, str):
            # Value is a string - print it as a string with quotes
            return f'"{param}"'
        elif isinstance(param, bool):
            # Value is a boolean - print it as a pbrt bool string
            if param is True:
                return '"true"'
            else:
                return '"false"'
        elif isinstance(param, list):
            # Value is a List e.g. [X, Y, Z] (closing brackets needed)
            return str(param)
        else:
            # Value should be float (or integer)
            return f"[{param}]"

    def _get_identifier_indices(self, tokens: list) -> list:
        # Indetifier tokens are:
        # Unquoted sequences of characters starting with a letter
        identifier_indices = []
        re_alpha = re.compile(r"[a-zA-Z_]")
        quoted = False

        for token_idx, token in enumerate(tokens):
            quo_mark_count = token.count('"')
            if quo_mark_count != 0:
                if quo_mark_count % 2 == 1:
                    # If token contains odd number of quotation marks
                    # switch current quotation state
                    quoted = not quoted
                continue

            if not quoted and re_alpha.match(token):
                # Not quoted and starts with a letter = identifier
                identifier_indices.append(token_idx)

        return identifier_indices

    def _get_case_content_string(
        self, tokens: list, identifier_indices: list, test_case: TestCase
    ) -> str:
        test_case_native = self._test_cases[test_case.name]
        identifiers_handled = set()
        case_content_string = ""

        for identifier_idx, token_idx in enumerate(identifier_indices):
            identifier = tokens[token_idx]

            if identifier in test_case_native:
                # Write identifier definition from the test case
                identifiers_handled.add(identifier)
                case_content_string += f"{test_case_native[identifier]}\n"
            else:
                # Copy identifier from the source scene description
                cpy_start = identifier_indices[identifier_idx]
                if identifier_idx == len(identifier_indices) - 1:
                    cpy_end = len(tokens)
                else:
                    cpy_end = identifier_indices[identifier_idx + 1]

                case_content_string += f"{''.join(tokens[cpy_start:cpy_end])}"

        for identifier in test_case_native:
            # Add identifiers from the test which were not added yet
            if identifier in identifiers_handled:
                continue

            case_content_string += f"\n{test_case_native[identifier]}"

        # Include description of the scene
        case_content_string += '\nInclude "description.pbrt"'

        return case_content_string
