import json
import pathlib
import dominate
from dominate.tags import *
from distutils.dir_util import copy_tree

import data.scripts.outputconst as out
import data.scripts.futils as futils


class WebGenerator:
    def __init__(self, dir_path: pathlib.Path):
        self.dir_path = dir_path.resolve()
        self.scenes_dir_path = (dir_path / out.scenes_dir).resolve()
        self.web_dir_path = (dir_path / out.web_dir).resolve()

        if not self.scenes_dir_path.is_dir():
            print(
                f'"{str(self.scenes_dir_path)}" '
                f' - "scenes" directory does not exist!'
            )
            exit(1)

        self._cfg_description = None

        self._found_scene_cases = []
        self._cfg_scene_cases = []
        self._additional_scene_cases = []

        self._cfg_test_cases = []

        # Cfg file is parsed for additional information (e.g. descriptions)
        cfg_path = dir_path / out.cfg_file
        self._cfg_mod = (
            futils.import_module_from_file(str(cfg_path), True)
            if cfg_path.exists()
            else None
        )

    def generate_webpage(self):
        self._get_scene_cases()
        self._apply_cfg_file()
        self._create_web_directory()
        self._create_index_file()
        self._create_scene_files()

    def _get_scene_cases(self):
        # Scene dirs (names) are sorted by name
        scene_dir_paths = sorted(
            [sd for sd in self.scenes_dir_path.iterdir() if sd.is_dir()]
        )

        for scene_dir_path in scene_dir_paths:
            # Derived from .exr file names excluding reference .exrs
            # Test cases are sorted by name
            self._found_scene_cases.append(
                {
                    "scene_name": scene_dir_path.name,
                    "case_names": [
                        p.stem
                        for p in sorted(scene_dir_path.glob("*.exr"))
                        if not p.stem.endswith(out.refimg_stem_suffix)
                    ],
                }
            )

    def _apply_cfg_file(self):
        if not self._cfg_mod:
            return

        # Configuration description
        cfg_config = self._cfg_mod.configuration
        if "description" in cfg_config:
            self._cfg_description = cfg_config["description"]

        # Test cases and their description
        self._cfg_test_cases = [
            {
                "name": tc["name"],
                "description": tc["description"]
                if "description" in tc
                else "",
            }
            for tc in self._cfg_mod.test_cases
        ]

        # Reordering of found test cases
        # Currently does not matter because JERI takes scenes
        # not as an ordered list but as an dictionary
        for sc in self._cfg_scene_cases:
            cases_cfg_ordered = []

            # All found cases for a given scene (non reference exr names)
            cases_found = set(sc["case_names"])

            # Put cases defined in the cfg file first in their correct order
            for case_name in [tc["name"] for tc in self._cfg_test_cases]:
                if case_name in cases_found:
                    cases_cfg_ordered.append(case_name)
                    cases_found.remove(case_name)

            # Put any additional test cases at the end of the list
            cases_cfg_ordered.extend(
                [tc for tc in sc["case_names"] if tc in cases_found]
            )

            sc["case_names"] = cases_cfg_ordered

        # Reordering of scenes based on the cfg order:
        # All found scenes
        scenes_found = {s["scene_name"]: s for s in self._found_scene_cases}

        # Scene (cases) defined in the cfg file in their correct order
        for scene_name in self._cfg_mod.scenes:
            if scene_name in scenes_found:
                self._cfg_scene_cases.append(scenes_found[scene_name])
                del scenes_found[scene_name]

        # Additional scene (cases) not defined in the cfg file
        self._additional_scene_cases.extend(
            [
                sc
                for sc in self._found_scene_cases
                if sc["scene_name"] in scenes_found
            ]
        )

    def _create_web_directory(self):
        # Create web directory and copy JERI files into its subdirectory
        jeri_web_dir_path = self.web_dir_path / "jeri"
        jeri_web_dir_path.mkdir(parents=True, exist_ok=True)

        copy_tree(
            str(pathlib.Path(__file__).parent / "../jeri"),
            str(jeri_web_dir_path),
        )

    def _create_index_file(self):
        doc = dominate.document(title="lteval")

        with doc.head:
            meta(charset="utf-8")
            style(
                "body { font-family: sans-serif; } "
                "a:link, a:visited { color: #55bada; }"
            )

        with doc:
            h2("Light transport evaluation visualization")

            if self._cfg_description:
                h4(self._cfg_description)

            if self._cfg_test_cases:
                h3("Test cases:")

                with ul():
                    for test_case in self._cfg_test_cases:
                        li(
                            test_case["name"]
                            + ": "
                            + (
                                test_case["description"]
                                if test_case["description"]
                                else ""
                            )
                        )

            h3("Scenes:")
            if self._found_scene_cases:
                with ul():
                    li(a("all scenes", href=f"{out.web_dir}/all_scenes.html"))

                if self._cfg_scene_cases:
                    h4("Defined scenes:")
                    with ul():
                        for sc in self._cfg_scene_cases:
                            li(
                                a(
                                    sc["scene_name"],
                                    href=f"{out.web_dir}/"
                                    f"{sc['scene_name']}.html",
                                )
                            )

                if self._additional_scene_cases:
                    h4("Additional scenes:")
                    with ul():
                        for sc in self._additional_scene_cases:
                            li(
                                a(
                                    sc["scene_name"],
                                    href=f"{out.web_dir}/"
                                    f"{sc['scene_name']}.html",
                                )
                            )

        with (self.dir_path / "index.html").open("w") as f:
            f.write(doc.render())

    def _create_scene_files(self):
        jeri_scenes_data = []

        for scene in self._found_scene_cases:
            scene_name = scene["scene_name"]
            case_names = scene["case_names"]

            # Create html page with a single scene
            self._create_scene_html_file(scene_name)

            # Create JERI data file script for the webpage
            jeri_data = self._create_jeri_scene_data(scene_name, case_names)
            jeri_scenes_data.append({"name": scene_name, "data": jeri_data})
            self._create_jeri_data_file(scene_name, jeri_data)

        # Create html page with all scenes
        self._create_scene_html_file("all_scenes")
        self._create_jeri_data_file(
            "all_scenes", self._create_jeri_all_scenes_data(jeri_scenes_data)
        )

    def _create_scene_html_file(self, name):
        doc = dominate.document(title=name)

        with doc.head:
            meta(charset="utf-8")
            meta(name="viewport", content="width=device-width")

            style(
                ".stretch {"
                " width: 100%;"
                " height: 100%;"
                " position: absolute;"
                " left:0; right: 0; top:0; bottom: 0;"
                "} "
                ".image-wrapper {"
                " width: 400px;"
                " height: 300px;"
                " position: relative;"
                " border: 1px solid #ccc;"
                " display: inline-block;"
                "}"
            )

        with doc:
            div(id="root", cls="stretch")

            script(
                src=(
                    "https://cdnjs.cloudflare.com/"
                    "ajax/libs/react/15.6.1/react.js"
                )
            )
            script(
                src=(
                    "https://cdnjs.cloudflare.com/"
                    "ajax/libs/react/15.6.1/react-dom.js"
                )
            )
            script(src="jeri/jeri.js")

            # This script will contain JERI viewer data specification
            script(src=name + "_jeri_data.js")

        with (self.web_dir_path / (name + ".html")).open("w") as f:
            f.write(doc.render())

    def _create_jeri_all_scenes_data(self, jeri_scenes_data: list) -> dict:
        jeri_all_data = {"title": "root", "children": []}

        for scene_data in jeri_scenes_data:
            jeri_data = scene_data["data"]
            jeri_data["title"] = scene_data["name"]
            jeri_all_data["children"].append(jeri_data)

        return jeri_all_data

    def _create_jeri_scene_data(
        self, scene_name: str, case_names: list
    ) -> dict:
        case_exr = {
            cn: "../scenes/" + scene_name + "/" + cn + ".exr"
            for cn in case_names
        }
        case_ref_exr = {
            cn: "../scenes/"
            + scene_name
            + "/"
            + cn
            + out.refimg_stem_suffix
            + ".exr"
            for cn in case_names
        }

        # Create JERI data description file
        jeri_data = {"title": "root", "children": []}

        # Images
        images = {
            "title": "Img",
            "children": [
                {"title": cn, "image": case_exr[cn]} for cn in case_names
            ],
        }
        jeri_data["children"].append(images)

        # References
        references = {
            "title": "Reference",
            "children": [
                {"title": cn, "image": case_ref_exr[cn]} for cn in case_names
            ],
        }
        jeri_data["children"].append(references)

        # Error metrics
        jeri_data["children"].extend(
            self._create_jeri_error_images(case_names, case_exr, case_ref_exr)
        )

        return jeri_data

    def _create_jeri_error_images(
        self, case_names: list, case_exr: dict, case_ref_exr: dict
    ) -> list:
        error_metrics = [
            "Diff",
            "DiffRelative",
            "L1",
            "L2",
            "MAPE",
            "SMAPE",
            "SSIM",
        ]

        errors = []

        for error_metric in error_metrics:
            error = {"title": error_metric, "children": []}

            for case_name_a in case_names:
                case_data_a = {"title": case_name_a, "children": []}
                case_data_a_ref = {
                    "title": case_name_a + "-ref",
                    "children": [],
                }

                for case_name_b in case_names:
                    # a - img, b - img
                    case_data_a["children"].append(
                        self._create_jeri_error_image(
                            case_name_b,
                            case_exr[case_name_a],
                            case_exr[case_name_b],
                            error_metric,
                        )
                    )
                    # a - img, b - ref
                    case_data_a["children"].append(
                        self._create_jeri_error_image(
                            case_name_b + "-ref",
                            case_exr[case_name_a],
                            case_ref_exr[case_name_b],
                            error_metric,
                        )
                    )
                    # a - ref, b - img
                    case_data_a_ref["children"].append(
                        self._create_jeri_error_image(
                            case_name_b,
                            case_ref_exr[case_name_a],
                            case_exr[case_name_b],
                            error_metric,
                        )
                    )
                    # a - ref, b - ref
                    case_data_a_ref["children"].append(
                        self._create_jeri_error_image(
                            case_name_b + "-ref",
                            case_ref_exr[case_name_a],
                            case_ref_exr[case_name_b],
                            error_metric,
                        )
                    )

                error["children"].append(case_data_a)
                error["children"].append(case_data_a_ref)
            errors.append(error)
        return errors

    def _create_jeri_error_image(
        self, title: str, img_a: str, img_b: str, function: str
    ) -> dict:
        return {
            "title": title,
            "lossMap": {
                "function": function,
                "imageA": img_a,
                "imageB": img_b,
            },
        }

    def _create_jeri_data_file(self, name: str, jeri_data: dict):
        jeri_data_content = (
            f"const data = {json.dumps(jeri_data, indent=4)}"
            f"\nJeri.renderViewer(document.getElementById('root'), data);"
        )

        jeri_data_path = self.web_dir_path / (name + "_jeri_data.js")
        with (jeri_data_path).open("w") as f:
            f.write(jeri_data_content)
