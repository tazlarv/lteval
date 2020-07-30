import inspect
import sys
import importlib

from data.scripts.renderers.abstractrenderer import AbstractRenderer


def import_module_from_file(
    full_path_str: str, dont_write_bytecode: bool = False
):
    # Import module from file, don't create __pycache__
    dont_write_bytecode_old = sys.dont_write_bytecode
    sys.dont_write_bytecode = dont_write_bytecode

    # This approach to loading allows to load
    # even files that do not have .py suffix.
    try:
        loader = importlib.machinery.SourceFileLoader("", full_path_str)
        spec = importlib.util.spec_from_loader(loader.name, loader)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    except Exception:
        print(f'Importing of module at: "{full_path_str}" failed!\n')
        raise

    sys.dont_write_bytecode = dont_write_bytecode_old
    return mod


def get_renderer_class_from_file(
    full_path_str: str, dont_write_bytecode: bool = False
):
    # Import (potential) renderer module
    r_module = import_module_from_file(full_path_str, dont_write_bytecode)

    # Find renderer classes in the module
    # Must be derived from AbstractRenderer but
    # must not be an abstract class itself.
    r_module_renderers = [
        r[1]
        for r in inspect.getmembers(
            r_module,
            predicate=lambda x: inspect.isclass(x)
            and not inspect.isabstract(x),
        )
        if issubclass(r[1], AbstractRenderer)
    ]

    if len(r_module_renderers) == 1:
        # Exactly one = we found the renderer class
        return r_module_renderers[0]
    else:
        # More or less than one, something is wrong
        return None
