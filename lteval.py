import pathlib
import shutil

import data.scripts.lteutils as lteutils
import data.scripts.outputconst as out
import data.scripts.scene as scene
import data.scripts.tcase as tcase
import data.scripts.webgen as webgen
import data.scripts.webdisplay as webdisplay

if __name__ == "__main__":
    # Parse arguments
    args = lteutils.create_parser().parse_args()

    # Clear scenes directory instead of following configuration file
    if args.force_clear:
        lteutils.clear_scenes_directory()
        exit(0)

    # Load configuration
    cfg_path = pathlib.Path(args.cfg).resolve()
    cfg_mod = lteutils.load_configuration_module(cfg_path)

    # Output directory name - use name specified in the configuration
    # or fallback to the name of the configuration file.
    output_dir_path = lteutils.create_output_dir(cfg_mod, cfg_path)

    # Copy configuration file to the output directory
    shutil.copy(str(cfg_path), str(output_dir_path / out.cfg_file))

    # Create logger (future print() statements are handled by it)
    # Sends print to the stdout and logging file
    logger = lteutils.create_logger(output_dir_path)

    # Load renderers
    renderers = lteutils.load_renderers(cfg_mod)

    # Load scenes
    scenes = scene.load_scenes_from_cfg(cfg_mod)

    # Load test cases
    test_cases = tcase.load_test_cases(cfg_mod)

    # Check if scene files of the defined renderers exist
    lteutils.check_renderers_scene_files(scenes, renderers)

    # Render test cases
    lteutils.render_scene_cases(
        scenes,
        renderers,
        test_cases,
        output_dir_path / out.scenes_dir,
        args.eof,
        args.clear,
    )

    # Webpage generation
    if (
        "webpage_generate" in cfg_mod.configuration
        and cfg_mod.configuration["webpage_generate"]
    ):
        webgen.WebGenerator(output_dir_path).generate_webpage()

        # And its display
        if (
            "webpage_display" in cfg_mod.configuration
            and cfg_mod.configuration["webpage_display"]
        ):
            webdisplay.display_webpage(output_dir_path)
