# Example - putting everything together

# Configuration file making use of most of the features:
# Multiple renderers
# Base parameter sets, extensions, modifications
# Example of Python code usage

# Default version of this configuration also nicely showcases that pool_simple
# is easily rendered by Bidiretional path tracer and that classical Path tracer
# is not going to render anything of use in reasonable time.

configuration = {"webpage_generate": True, "webpage_display": True}

# List of all available scenes for simple selection:
# "cbox_classic",
# "cbox_indirect",

# "cboxm_basic",
# "cboxm_diffuse_lsame",
# "cboxm_diffuse_lvar",
# "cboxm_glossy_lsame",
# "cboxm_glossy_lvar",

# "veach_mis",

# "pool_simple",
# "pool_classic",
# "ring",

scenes = ["pool_simple"]

renderers = {
    "mitsubaRenderer_0_5": {
        "type": "mitsuba_0_5",
        "path": "data/renderers/mitsuba_0_5/mitsuba.exe",
    },
    "pbrt3Renderer": {
        "type": "pbrt_3",
        "path": "data/renderers/pbrt_3/pbrt.exe",
    },
}

parameter_sets = {
    # Mitsuba - two base parameter sets,
    # modification of their values propagates into multiple test cases
    "mitsubaSampler": {
        "sampler": [
            ["type", "", "independent"],
            ["sampleCount", "integer", 2],
        ],
    },
    "mitsubaRfilter": {"rfilter": [["type", "", "box"]]},
    # Mitsuba - extension of the base sets.
    "mitsubaPtracer": {
        "base": ["mitsubaSampler", "mitsubaRfilter"],
        "integrator": [["type", "", "path"], ["maxDepth", "integer", 10]],
    },
    "mitsubaBidir": {
        "base": ["mitsubaSampler", "mitsubaRfilter"],
        "integrator": [["type", "", "bdpt"], ["maxDepth", "integer", 10]],
    },
    # PBRT - same as with Mitsuba
    "pbrtSampler": {
        "Sampler": [["type", "", "random"], ["pixelsamples", "integer", 2]],
        "PixelFilter": [["type", "", "box"]],
    },
    "pbrtFilter": {
        "Sampler": [["type", "", "random"], ["pixelsamples", "integer", 2]],
        "PixelFilter": [["type", "", "box"]],
    },
    "pbrtPtracer": {
        "base": ["pbrtSampler", "pbrtFilter"],
        "Integrator": [["type", "", "path"], ["maxdepth", "integer", 9]],
    },
    "pbrtBidir": {
        "base": ["pbrtSampler", "pbrtFilter"],
        "Integrator": [["type", "", "bdpt"], ["maxdepth", "integer", 9]],
    },
    # Note the differences:
    # "integrator" vs "Integrator"
    # "maxDepth" vs "maxdepth"
}

# Corresponding test cases
test_cases = [
    {
        "name": "mitsubaPtracer",
        "description": "Mitsuba - path tracer",
        "renderer": "mitsubaRenderer_0_5",
        "params": {"base": ["mitsubaPtracer"]},
    },
    {
        "name": "mitsubaBidir",
        "description": "Mitsuba - bidir",
        "renderer": "mitsubaRenderer_0_5",
        "params": {"base": ["mitsubaBidir"]},
    },
    {
        "name": "pbrtPtracer",
        "description": "PBRT - path tracer",
        "renderer": "pbrt3Renderer",
        "params": {"base": ["pbrtPtracer"]},
    },
    {
        "name": "pbrtBidir",
        "description": "PBRT - bidir",
        "renderer": "pbrt3Renderer",
        "params": {"base": ["pbrtBidir"]},
    },
]

# If we change name of the variable to test_case it will overwrite its
# previous definition (with 4 test cases), this way we can have multiple
# test_cases (or any other variables) inside of one configuration file
# and switch between them with simple adjustment to their names.
test_cases_ = [
    # Adjusted maxDepth/maxdepth
    {
        "name": "mitsubaBidir",
        "description": "Mitsuba - bidir",
        "renderer": "mitsubaRenderer_0_5",
        "params": {
            "base": ["mitsubaBidir"],
            "integrator": [["maxDepth", "integer", 5]],
        },
    },
    {
        "name": "pbrtBidir",
        "description": "PBRT - bidir",
        "renderer": "pbrt3Renderer",
        "params": {
            "base": ["pbrtBidir"],
            "Integrator": [["maxdepth", "integer", 4]],
        },
    },
]


# Because this is a python script we could do way more things...
# There is are no limitations to what can be done, as long as
# the required variables are available in the end.
def sophisticated_test_case_generator():
    return {
        "name": "mitsubaBidir",
        "description": "Mitsuba - bidir",
        "renderer": "mitsubaRenderer_0_5",
        "params": {"base": ["mitsubaBidir"]},
    }


test_cases_ = [
    sophisticated_test_case_generator(),
    {
        "name": "pbrtBidir",
        "description": "PBRT - bidir",
        "renderer": "pbrt3Renderer",
        "params": {"base": ["pbrtBidir"]},
    },
]
