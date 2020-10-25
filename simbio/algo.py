from __future__ import annotations

from typing import Tuple, Union

import numpy as np
import pyabc

from .compartments import Compartment
from .parameters import BaseParameter, Parameter
from .simulator import Simulator
from .solvers.core import BaseSolver
from .species import Species


def _find_steady_state(
    solver: BaseSolver, *, atol=1e-4, rtol=1e-4, max_iter=1000
) -> Tuple[float, np.ndarray]:
    for _ in range(max_iter):
        dy = np.abs(solver.rhs(solver.t, solver.y, solver.p))
        y = np.abs(solver.y)

        adiff = dy.max()
        cond = y > atol
        rdiff = (dy[cond] / y[cond]).max()

        if (adiff < atol) and (rdiff < rtol):
            return solver.t, solver.y
        else:
            solver.step()
    else:
        raise Exception(
            f"Maximum iterations ({max_iter}) reached at time {solver.t:.3f}."
        )


def find_steady_state(simulator: Simulator, **kwargs):
    t, y = _find_steady_state(simulator.create_solver(), **kwargs)
    return t, simulator._to_single_output(y, y_names=simulator.names)


def _dose_response(
    simulator: Simulator, name: Union[str, Species, Parameter], values, **kwargs
):
    values = np.asarray(values)
    response = []
    for solver in Scanner.from_single_value(simulator, name, values):
        _, y = _find_steady_state(solver, **kwargs)
        response.append(y)

    return values, np.asarray(response)


def dose_response(simulator, name: Union[str, Species, Parameter], values, **kwargs):
    return simulator._to_output(
        *_dose_response(simulator, name, values, **kwargs),
        t_name="dose",
        y_names=simulator.names,
    )


class Scanner:
    def __init__(self, simulator, scan_values):
        self.simulator = simulator
        self.scan_values = scan_values

    @classmethod
    def from_single_value(cls, simulator, name, values):
        if isinstance(name, str):
            name = simulator.model[name]
        elif not isinstance(name, BaseParameter):
            raise ValueError(f"{name.name} is neither a Species nor a Parameter.")

        return cls(simulator, ({name: value} for value in values))

    @classmethod
    def from_lhs(cls):
        # TODO:
        pass

    def __iter__(self):
        for scan_value in self.scan_values:
            yield self.simulator.create_solver(values=scan_value)


def infer_abc(
    model: Compartment,
    experiment_data: Tuple[np.ndarray, np.ndarray],
    db_path="sqlite:///test.db",
    debug=False,
):
    """
    pyABC inference of a model and the experimental data. The experimental data in a form of (t, y) tuple.
    You can provide the path of the sqlite DB to save the historical data of pyABC and if flag for debugging
    """

    # Get the running time and the experimenta data
    run_time, exp_data = experiment_data

    # Assuming will maintain the order!
    initial_values_per_specie = {}
    initial_value = exp_data[:, 0]  # First row of data

    # We get the relative name of the species (with the container) which is in use by the simulator
    cell_species = model._in_reaction_species_names
    for i, specie_nane in enumerate(cell_species):
        initial_values_per_specie[specie_nane] = initial_value[i]

    if debug:
        print("Initial values for species: {}".format(initial_values_per_specie))

    # We get the relative names (with the container name) for the model,
    # which is the name in use for the simulator
    cell_parameters = model._in_reaction_parameter_names

    prior_param_dict = {}
    for param in cell_parameters:
        prior_param_dict[param.name] = pyabc.RV("uniform", 0, 1)

    if debug:
        print("Parameters distribution: {}".format(prior_param_dict))

    def distance(exp_data, simulation):
        return np.absolute(exp_data["y"] - simulation["y"]).sum()

    def abc_model(params):
        values = {**initial_values_per_specie, **params}
        sim = Simulator(model, values=values)
        t, y = sim.run(run_time)
        return {"y": y}

    abc = pyabc.ABCSMC(
        models=abc_model,
        parameter_priors=pyabc.Distribution(**prior_param_dict),
        distance_function=distance,
        population_size=50,
        transitions=pyabc.LocalTransition(k_fraction=0.3),
        eps=pyabc.MedianEpsilon(500, median_multiplier=0.7),
    )

    # Where to save the history data
    h = abc.new(db_path, {"y": exp_data})

    h = abc.run(minimum_epsilon=0.5, max_nr_populations=10)

    return h
