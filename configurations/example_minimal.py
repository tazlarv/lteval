# Example - minimal usable configuration file in practice.

# Everything possible is omitted with the exception
# of website generation and displaying.

configuration = {
    "webpage_generate": True,  # OPTIONAL, default: False
    "webpage_display": True,  # OPTIONAL, default : False
}

scenes = ["cbox_classic"]

renderers = {
    "mitsubaRenderer_0_5": {
        "type": "mitsuba_0_5",
        "path": "data/renderers/mitsuba_0_5/mitsuba.exe",
    },
}

# parameter_sets omitted

test_cases = [
    # No params, fallback on the default scene settings
    {"name": "mitsubaCase", "renderer": "mitsubaRenderer_0_5"},
]
