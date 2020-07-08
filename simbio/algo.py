from typing import Tuple

import numpy as np
import pandas as pd

from .simulator import Simulator


def _to_df(
    first, y: np.ndarray, columns: Tuple[str, ...], first_name="time"
) -> pd.DataFrame:
    df = pd.DataFrame(y, columns=columns)
    df.insert(0, first_name, first)
    return df


def _to_y_df(y: np.ndarray, columns: Tuple[str, ...]) -> pd.DataFrame:
    return pd.DataFrame(y, columns=columns)


def find_steady_state(
    sim: Simulator, t_window: float, r_tol: float = 0.1, rounds=None
) -> (np.ndarray, np.ndarray):
    # TODO: better param names
    t_0, y_0 = sim.resume1(t_window / 10)

    rounds = rounds or 5

    diff = 0
    with sim.observe_all() as ndx:
        for _ in range(rounds):
            t_end, y_end = sim.resume1(t_0 + t_window)
            diff = np.abs((y_end - y_0) / (y_end + y_0))
            if np.any(diff > r_tol):
                t_0 = t_end
                y_0 = y_end
                t_window *= 2
            else:
                if ndx is None:
                    return t_end, y_end
                return t_end, y_end[ndx]

    raise Exception(
        f"Steady state not found after {rounds} rounds."
        f"(time: {t_end}, window: {t_window}, max. dif. {np.max(diff):.2f}). "
    )


def df_find_steady_state(
    sim: Simulator, t_window: float, r_tol: float = 0.1, rounds=None
) -> pd.DataFrame:
    t, y = find_steady_state(sim, t_window, r_tol, rounds)
    return _to_df(t, y, sim.observed_names)


def dose_response(
    sim: Simulator, name: str, values, find_ss_kwargs=None
) -> (np.ndarray, np.ndarray):

    if find_ss_kwargs is None:
        find_ss_kwargs = dict(t_window=100)

    out = []
    values = np.asarray(values)
    for sim in Scanner.from_single(name, values, sim.model):
        _, y = sim.find_steady_state(**find_ss_kwargs)
        out.append(y)

    return values, np.asarray(out)


def df_dose_response(
    sim: Simulator, name: str, values, find_ss_kwargs=None
) -> pd.DataFrame:

    values, y = dose_response(sim, name, values, find_ss_kwargs)
    return _to_df(values, y, sim.observed_names, name)


def going_up_and_down(
    sim, name, values, find_ss_kwargs=None
) -> (np.ndarray, np.ndarray):

    ups = list(values)
    downs = reversed(ups[:-1])
    values_up, y_up = sim.dose_response(name, ups, find_ss_kwargs)
    values_down, y_down = sim.dose_response(name, downs, find_ss_kwargs)

    return np.stack((values_up, values_down)), np.stack((y_up, y_down))


def df_going_up_and_down(sim, name, values, find_ss_kwargs=None) -> pd.DataFrame:

    values, y = going_up_and_down(sim, name, values, find_ss_kwargs)
    return _to_df(values, y, sim.observed_names, name)


class Scanner:
    def __init__(self, scan_values, model):
        self.scan_values = scan_values
        self.model = model

    @classmethod
    def from_single(cls, name, values, model):
        if True:  # TODO: check if name is reactant or parater
            return cls.from_single_concentration(name, values, model)
        else:
            return cls.from_single_parameter(name, values, model)

    @classmethod
    def from_single_concentration(cls, name, values, model):
        return cls((({name: value}, None) for value in values), model)

    @classmethod
    def from_single_parameter(cls, name, values, model):
        return cls(((None, {name: value}) for value in values), model)

    @classmethod
    def from_lhs(cls):
        # TODO:
        pass

    def __iter__(self):
        def fun():
            for c, p in self.scan_values:
                sim = Simulator(
                    self.model, default_concentrations=c, default_parameters=p
                )
                yield sim

        return fun
