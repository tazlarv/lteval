import pathlib
from abc import ABC, abstractmethod

from data.scripts.scene import Scene
from data.scripts.tcase import TestCase


class AbstractRenderer(ABC):
    @abstractmethod
    def __init__(
        self, executable_path: pathlib.Path = None, options: str = None
    ):
        pass

    @abstractmethod
    def scene_files_exist(self, scene: Scene) -> bool:
        # Check if all files for rendering of the scene exist.
        pass

    @abstractmethod
    def prepare_scene_case(self, scene: Scene, test_case: TestCase):
        # Prepare the scene for rendering of the test case.
        # This method is always called before render_scene_case.
        pass

    @abstractmethod
    def render_scene_case(
        self, scene: Scene, test_case: TestCase, output_dir_path: pathlib.Path
    ):
        # Render the scene with specific test case
        # and move the result to specified output.
        # prepare_scene_case is always called before this method.
        pass

    @abstractmethod
    def clear_scene_case(self, scene: Scene, test_case: TestCase):
        # Delete files which were generated for rendering
        # of a given combination of scene and test_case
        pass

    @abstractmethod
    def clear_scene(self, scene: Scene):
        # Deletes all generated files for rendering of a given scene.
        # Rendered images which were not moved to the proper ouput
        # directory because the scripts was interrupted should be deleted too.
        # (all generated files, includes even previous runs of lteval)
        pass
