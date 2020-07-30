# Example - rendering of all evaluation scenes.

# Rendering of all scenes with just 1 sample per pixel with Mitsuba and PBRT.

# Integrator - Bidirectional path tracer, because ordinary Path tracer in PBRT
# is extremely slow (minutes for a single sample on cboxm scenes).
# Filter not defined - fallback on the one set up in the scene files (box).

# MANDATORY - Dictionary of settings
configuration = {
    "name": "cfg all_scenes",  # OPTIONAL
    "description": "Configuration file used for rendering of all scenes",
    # Fallback to defaults
    # "output_dir": "results",  # OPTIONAL, default: results
    # "output_dir_date": True,  # OPTIONAL, default: True
    "webpage_generate": True,  # OPTIONAL, default: False
    "webpage_display": True,  # OPTIONAL, default : False
}

# MANDATORY - List of scenes
scenes = [
    "cbox_classic",
    "cbox_indirect",
    "cboxm_diffuse_lsame",
    "cboxm_diffuse_lvar",
    "cboxm_glossy_lsame",
    "cboxm_glossy_lvar",
    "veach_mis",
    "pool_simple",
    "pool_classic",
    "ring",
]

# MANDATORY - Dictionary of renderers
renderers = {
    "mitsubaRenderer_0_5": {
        "type": "mitsuba_0_5",  # MANDATORY
        "path": "data/renderers/mitsuba_0_5/mitsuba.exe",  # MANDATORY
    },
    "pbrt3Renderer": {
        "type": "pbrt_3",
        "path": "data/renderers/pbrt_3/pbrt.exe",
    },
}

# OPTIONAL - Dictionary of re-used sets of parameters
parameter_sets = {
    # Different names and types of the setting are in truth the same thing:
    # maxDepth: Mitsuba - number of path segments, PBRT - number of bounces
    "mitsuba": {
        "integrator": [["type", "", "bdpt"], ["maxDepth", "integer", 10]],
        "sampler": [
            ["type", "", "independent"],
            ["sampleCount", "integer", 1],
        ],
    },
    "pbrt": {
        "Integrator": [["type", "", "bdpt"], ["maxdepth", "integer", 9]],
        "Sampler": [["type", "", "random"], ["pixelsamples", "integer", 1]],
    },
}

# MANDATORY - List of test cases
test_cases = [
    {
        "name": "mitsubaCase",  # MANDATORY
        "description": "Mitsuba rendering",  # OPTIONAL
        "renderer": "mitsubaRenderer_0_5",  # MANDATORY
        "params": {"base": ["mitsuba"]},  # OPTIONAL
    },
    {
        "name": "pbrtCase",
        "description": "PBRT rendering",
        "renderer": "pbrt3Renderer",
        "params": {"base": ["pbrt"]},
    },
]
