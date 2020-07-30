import copy
import pathlib
import subprocess
import shlex
from lxml import etree

from data.scripts.renderers.abstractrenderer import AbstractRenderer
from data.scripts.scene import Scene
from data.scripts.tcase import TestCase


class Mitsuba_0_5(AbstractRenderer):
    def __init__(
        self, executable_path: pathlib.Path = None, options: str = None
    ):
        self.scene_type = "mitsuba_0_5"
        self.scene_suffix = ".xml"
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

        parser = etree.XMLParser(remove_blank_text=True)
        case_content = etree.parse(str(settings_path), parser)

        tree = case_content.getroot()
        elem_film = tree.xpath("/scene/sensor/film")[-1]

        # Multiple definitions of the element in the source scene files
        # are not expected - scenes should be properly defined.
        # Nonetheless mitsuba applies the last definition and so
        # we save test_case elements in position of their last definitons.
        test_case_native = self._test_cases[test_case.name]
        for elem_name, elem_template in test_case_native.items():
            # Deepcopy of an element which is then inserted to the xml tree
            elem_native = copy.deepcopy(elem_template)

            if elem_name == "integrator":
                # All integrators deleted, new one inserted
                for elem in tree.xpath("/scene/integrator"):
                    elem.getparent().remove(elem)
                tree.insert(0, elem_native)
            elif elem_name == "sampler":
                # All samplers deleted, new inserted into last sensor element
                for elem in tree.xpath("/scene/sensor/sampler"):
                    elem.getparent().remove(elem)
                elem_film.addprevious(elem_native)
            elif elem_name == "rfilter":
                # All filters deleted, new inserted into last sensor element
                for elem in tree.xpath("/scene/sensor/film/rfilter"):
                    elem.getparent().remove(elem)
                elem_film.append(elem_native)
            else:
                # If there is other "unknown" element, append it at the end
                tree.append(elem_native)

        # Include description of the scene
        tree.append(
            etree.SubElement(tree, "include", {"filename": "description.xml"})
        )

        case_content_string = etree.tostring(
            case_content,
            encoding="utf-8",
            xml_declaration=True,
            pretty_print=True,
        )

        with open(self._scene_case_path(scene, test_case), "wb") as f:
            f.write(case_content_string)

    def render_scene_case(
        self, scene: Scene, test_case: TestCase, output_dir_path: pathlib.Path
    ):
        scene_case_path = self._scene_case_path(scene, test_case)

        process = subprocess.Popen(
            [str(self.executable_path)]
            + self._options_tokens
            + [str(scene_case_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )

        # Redictects output of subprocess stdout to the sys.stdout via print()
        # sys.stdout can be changed to a customized object (e.g. log to a file)
        for line in iter(process.stdout.readline, ""):
            # 2 backspace characters are at the end of rendering progress lines
            # These characters would otherwise be "printed" to the output file
            # Lines contain endline characters already
            print(line.replace("\b", ""), end="")

        process.wait()

        # Move resulting HDR image to the provided output directory
        # Mitsuba saves result image next to the input file
        result_path = scene_case_path.with_suffix(".exr")
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
        for file_path in self._scene_dir_path(scene).glob("*.xml"):
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
        # in mitsuba each parameter set represents one xml element

        # Do it only once for each test_case
        if test_case.name in self._test_cases:
            return

        # For each parameter set create corresponding xml element
        # e.g. integrator/sampler/rfilter
        param_subsets = {}
        for name, params in test_case.parameter_set.parameters.items():
            main_element = etree.Element(name)
            for param in params:
                if param[1] == "":
                    # Parameter with no type is an attribute
                    main_element.set(str(param[0]), str(param[2]))
                else:
                    # Parameter with type is a subelement,
                    # with attributes: "name" and "value"
                    if isinstance(param[2], bool):
                        value_str = "true" if param[2] is True else "false"
                    elif isinstance(param[2], list):
                        # List should not include square brackets
                        value_str = str(param[2])[1:-1]
                    else:
                        # Not in the Mitsuba input format specification
                        value_str = str(param[2])

                    etree.SubElement(
                        main_element,
                        param[1],
                        {"name": param[0], "value": value_str},
                    )

            param_subsets[name] = main_element

        # Add these test case data to the dictionary of all prepared test cases
        self._test_cases[test_case.name] = param_subsets
