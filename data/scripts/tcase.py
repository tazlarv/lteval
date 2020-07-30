import copy
from copy import deepcopy


class ParameterSet:
    # Parameter set representation

    def __init__(self, params: dict = {}):
        self.base_unresolved = []
        self.parameters = copy.deepcopy(params)
        self._resolved = False

        if "base" in self.parameters:
            self.base_unresolved = self.parameters["base"]
            del self.parameters["base"]
        pass

    def __str__(self):
        return (
            f"Unresolved bases: {self.base_unresolved}\n"
            f"Parameters: {self.parameters}"
        )

    def is_ready(self) -> bool:
        # Parameter set is ready to be used if all of its bases were resolved
        return self._resolved and not self.base_unresolved

    def resolve_base(self, paramset_dictionary: dict):
        new_base_unresolved = []
        current = ParameterSet()

        # Iterate over unresolved bases, and merge them together in their order
        for base_name in self.base_unresolved:
            if base_name in paramset_dictionary:
                # paramset_dictionary should not have unresolved baseS
                assert paramset_dictionary[base_name].is_ready()
                current.merge_with(paramset_dictionary[base_name])
            else:
                new_base_unresolved.append(base_name)

        # Merge current with self (ParamSet object)
        # Current represents its resolved bases
        current.merge_with(self)

        # Update this ParamSet object with resolved bases
        self.base_unresolved = new_base_unresolved
        self.parameters = current.parameters
        self._resolved = True

    def merge_with(self, paramset: "ParameterSet"):
        self.base_unresolved.extend(paramset.base_unresolved)
        self._merge_parameters_with(paramset.parameters)

    def _merge_parameters_with(self, parameters: dict):
        # Copy other parameter set - we will delete keys from it
        parameters_cpy = copy.deepcopy(parameters)

        # Go over all keys of current parameter set
        for param_name, paramlist in self.parameters.items():
            if param_name not in parameters_cpy:
                continue

            # If other set has same key - merge it
            self.parameters[param_name] = self._merge_paramlists(
                paramlist, parameters_cpy[param_name]
            )
            del parameters_cpy[param_name]  # And delete it from the other

        # Resolve lists under other keys
        # (resolves duplicate params and sorts them)
        for param_name, paramlist in parameters_cpy.items():
            parameters_cpy[param_name] = self._resolve_paramlist(paramlist)

        # Update current parameter set with remaining keys
        self.parameters.update(parameters_cpy)

    def _merge_paramlists(self, a: list, b: list) -> list:
        return self._resolve_paramlist(a + b)

    def _resolve_paramlist(self, paramlist: list) -> list:
        dic = {}
        res = []

        # Last parameter of name & value should be saved
        for param in paramlist:
            key = tuple(param[0:2])
            dic[key] = param[2]

        # Convert dictionary back to a parameter list
        for key, val in dic.items():
            param = list(key)
            param.append(val)
            res.append(param)

        # Sort list based on the second (type) column
        res.sort(key=lambda x: x[1])

        return res


class TestCase:
    def __init__(self, data: dict):
        self.name = data["name"]
        self.description = data["description"] if "description" in data else ""
        self.renderer = data["renderer"]
        self.parameter_set = (
            ParameterSet(data["params"])
            if "params" in data
            else ParameterSet()
        )

    def __str__(self):
        return (
            f"Name: {self.name}\nDescription: {self.description}\n"
            f"Renderer: {self.renderer}\n{self.parameter_set}"
        )

    def is_ready(self) -> bool:
        return self.parameter_set.is_ready()


def load_test_cases(cfg_mod) -> list:
    # Mandatory attributes
    if not hasattr(cfg_mod, "test_cases"):
        print('There is no "test_cases" element in the configuration file!')
        exit(1)
    if not isinstance(cfg_mod.test_cases, list):
        print(
            '"test_cases" element of the configuration file '
            "must be a list: []."
        )
        exit(1)

    # Load parameter_sets
    param_sets = {}
    if hasattr(cfg_mod, "parameter_sets") and isinstance(
        cfg_mod.parameter_sets, dict
    ):
        # Their bases must be resolved before they are applied to test cases
        unresolved_param_sets = {}
        unresolved_names = set()

        # Create corresponding parameter sets (all unresolved)
        for set_name, set_data in cfg_mod.parameter_sets.items():
            unresolved_param_sets[set_name] = ParameterSet(set_data)
            unresolved_names.add(set_name)

        # Until there are no unresolved parameter sets
        while unresolved_names:
            any_resolved = False

            # Check every unresolved set
            for unresolved_name in list(unresolved_names):
                unresolved_set = unresolved_param_sets[unresolved_name]

                # If its bases are not resolved already
                if not unresolved_names.intersection(
                    set(unresolved_set.base_unresolved)
                ):
                    # If they are, resolve the set
                    unresolved_set.resolve_base(param_sets)
                    param_sets[unresolved_name] = unresolved_set
                    unresolved_names.remove(unresolved_name)
                    any_resolved = True

            # If no set was resolved, further iterations wont help
            # There is a dependency cycle on base clases
            if not any_resolved:
                print(
                    '"parameter_sets" could not be resolved '
                    ' because of cyclic "base" dependency.'
                )
                exit(1)

    # Load (and resolve) test cases
    test_cases = []
    for case_data in cfg_mod.test_cases:
        test_case = TestCase(case_data)
        test_case.parameter_set.resolve_base(param_sets)
        test_cases.append(test_case)

    # Check if all test cases are properly loaded and resolved
    # Print error messages for all test cases and end the execution
    _ready_check_test_cases(test_cases)

    return test_cases


def _ready_check_test_cases(test_cases: list):
    # Check if test cases have unique names
    # and if their parameter sets are ready.

    test_case_uq_names = set()
    test_failed = False

    for test_case in test_cases:
        if test_case.name in test_case_uq_names:
            print(f'Test case: "{test_case.name}" is defined multiple times!')

        test_case_uq_names.add(test_case.name)

        if not test_case.is_ready():
            test_failed = True

            print(
                f"Test case is not ready! "
                f"Check if there are not some unresolved bases:\n"
                f"{test_case}"
            )

    if len(test_case_uq_names) != len(test_cases):
        print("Test case names must be unique identifiers!")
        exit(1)

    if test_failed:
        exit(1)
