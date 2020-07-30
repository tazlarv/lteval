# Example - configuration file described in the documentation/thesis.

# Showcasing all main features on a simple rendering
# of two scenes with two test cases:
# LQ_test_case - 2 samples per pixel
# HQ_test_case - 8 samples per pixel

# MANDATORY - Dictionary of settings
configuration = {
    "name": "cfg example",  # OPTIONAL, default: name of the configuration file
    "description": "Configuration file basic example",  # OPTIONAL
    "output_dir": "results",  # OPTIONAL, default: results
    "output_dir_date": True,  # OPTIONAL, default: True
    "webpage_generate": True,  # OPTIONAL, default: False
    "webpage_display": True,  # OPTIONAL, default : False
}

# MANDATORY - List of scenes
scenes = ["cbox_classic", "cbox_indirect"]

# MANDATORY - Dictionary of renderers
renderers = {
    "mitsubaRenderer_0_5": {
        "type": "mitsuba_0_5",  # MANDATORY
        "path": "data/renderers/mitsuba_0_5/mitsuba.exe",  # MANDATORY
        "options": "",  # OPTIONAL
    },
}

# OPTIONAL - Dictionary of re-used sets of parameters
parameter_sets = {
    "mitsubaLQ": {
        "integrator": [["type", "", "bdpt"], ["maxDepth", "integer", 10]],
        "sampler": [
            ["type", "", "independent"],
            ["sampleCount", "integer", 2],
        ],
        "rfilter": [["type", "", "box"]],
    },
    "mitsubaHQ": {
        "base": ["mitsubaLQ"],
        "sampler": [["sampleCount", "integer", 8]],
    },
}

# MANDATORY - List of test cases
test_cases = [
    {
        "name": "LQ_test_case",  # MANDATORY
        "description": "Fast preview rendering",  # OPTIONAL
        "renderer": "mitsubaRenderer_0_5",  # MANDATORY
        "params": {"base": ["mitsubaLQ"]},  # OPTIONAL
    },
    {
        "name": "HQ_test_case",
        "description": "High quality rendering",
        "renderer": "mitsubaRenderer_0_5",
        "params": {"base": ["mitsubaHQ"]},
    },
]
