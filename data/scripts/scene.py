import pathlib


class Scene:
    # Abstract representation of scene

    def __init__(self, name: str, path: pathlib.Path):
        self.name = name
        self.path = path.resolve()

    def __str__(self):
        return f"Scene - name: {self.name}, path: {str(self.path)}"


def load_scenes_from_cfg(cfg_mod) -> list:
    scenes_dir_path = (pathlib.Path(__file__).parents[2] / "scenes").resolve()

    # Testing of requirements
    if not scenes_dir_path.is_dir():
        print(f'Scenes directory "{scenes_dir_path}" does not exist!')
        exit(1)
    if not hasattr(cfg_mod, "scenes"):
        print("There is no scenes element in the configuration file!")
        exit(1)
    if not isinstance(cfg_mod.scenes, list):
        print('"scenes" element of the configuration file must be a list: [].')
        exit(1)

    return load_scenes_from_list(scenes_dir_path, cfg_mod.scenes)


def load_scenes_from_directory(scenes_dir_path: pathlib.Path) -> list:
    # Takes each scenes_dir_path subfolder as a scene directory
    return load_scenes_from_list(
        scenes_dir_path,
        [sd.name for sd in scenes_dir_path.iterdir() if sd.is_dir()],
    )


def load_scenes_from_list(
    scenes_dir_path: pathlib.Path, scene_names: list
) -> list:
    # Loading of scenes while checking if any was defined multiple times
    scene_uq_names = set()
    scenes = []

    for scene_name in scene_names:
        if scene_name in scene_uq_names:
            print(f'Scene: "{scene_name}" is defined multiple times!')

        scene_uq_names.add(scene_name)

        scene_path = (scenes_dir_path / scene_name).resolve()
        scenes.append(Scene(scene_name, scene_path))

        if not scene_path.is_dir():
            print(
                f'Scene directory of scene: "{scene_name}" '
                f'at location "{scene_path}" does not exist!'
            )

    if len(scene_uq_names) != len(scene_names):
        print("Scene must not be defined multiple times! ")
        exit(1)

    return scenes
