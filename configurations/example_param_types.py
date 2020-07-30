# Example - passing of different kinds of parameters to Mitsuba and PBRT

# Discussion about passing of different types of parameter values
# to Mitsuba and PBRT. Rendered images only illustrate that there
# was no issue with handling of parameters.

configuration = {"webpage_generate": True, "webpage_display": True}

scenes = ["pool_classic"]

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
    "mitsuba": {
        "integrator": [
            ["type", "", "pssmlt"],
            ["bidirectional", "boolean", True],  # Boolean
            ["maxDepth", "integer", 10],  # Integer
            ["twoStage", "boolean", "true"],  # Alternative for boolean
            ["pLarge", "float", 0.25],  # Float
            # String would be printed as is:
            # ["stringParamName", "string", "stringValue"]
            # Result: <string name="stringParamName" value="stringValue">
            # List of values "x, y, z" can be inputted as Python list:
            # ["listParamName", "rgb", [x, y, z]]
            # or as an equivalent Mitsuba string (will be copied as is):
            # ["listParamName", "rgb", "x, y, z"]
            # Result: <rgb name="listParamName" value="x, y, z">
        ],
        "sampler": [
            ["type", "", "independent"],
            ["sampleCount", "integer", 1],
        ],
    },
    "pbrt": {
        "Integrator": [
            ["type", "", "bdpt"],
            ["maxdepth", "integer", 9],  # Integer
            ["pixelbounds", "integer", [128, 384, 128, 384]],  # List
            ["lightsamplingstrategy", "string", "uniform"],  # String
            # Float is the same as integer
            # Boolean
            # ["booleanParamName", "bool", True]
            # or as an equivalent PBRT string:
            # ["booleanParamName", "bool", "true"]
            # Result: "bool booleanParamName" "true"
        ],
        "Sampler": [["type", "", "random"], ["pixelsamples", "integer", 1]],
    },
}

test_cases = [
    {
        "name": "mitsubaCase",
        "description": "Mitsuba rendering",
        "renderer": "mitsubaRenderer_0_5",
        "params": {"base": ["mitsuba"]},
    },
    {
        "name": "pbrtCase",
        "description": "PBRT rendering",
        "renderer": "pbrt3Renderer",
        "params": {"base": ["pbrt"]},
    },
]
