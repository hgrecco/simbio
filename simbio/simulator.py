import contextlib
from collections import abc
from typing import Collection, Iterable, Tuple, Union

import numpy as np
import pandas as pd
from scipy import integrate

from .compartments import Compartment, Universe


class Simulator:
    """Helper class to run a simulation.

    Parameters
    ----------
    model : Universe or Compartment
        Where reactions, reactants and parameters are define.
    observed_ndx : Collection of ints or None
        Indicates which variables (by position on the concentration vector) are recorded.
        None means record all.
    default_concentrations: dict
        Used to override the model concentrations.
        Concentrations not given in this dict, will be fetch from the model defaults.
    default_parameters:
        Used to override the model parameters.
        parameters not given in this dict, will be fetch from the model defaults.
    """

    def __init__(
        self,
        model: Union[Universe, Compartment],
        observed_ndx: Collection[int] = None,
        default_concentrations: dict = None,
        default_parameters: dict = None,
    ):
        self.model = model.copy()  # Else, the model might get modified outside.
        self.names = model.in_reaction_rectant_names
        self.solver = None
        self.__rhs = None
        self.observed_ndx = observed_ndx

        self.default_concentrations = default_concentrations
        self.default_parameters = default_parameters

    def _build_concentration_dict(self, concentrations: dict = None):
        if concentrations is None:
            return self.default_concentrations

        if self.default_concentrations is None:
            return concentrations

        return {**self.default_concentrations, **concentrations}

    def _build_parameters_dict(self, parameters: dict = None):
        if parameters is None:
            return self.default_parameters

        if self.default_parameters is None:
            return parameters

        return {**self.default_parameters, **parameters}

    @property
    def observed_names(self) -> Tuple[str, ...]:
        names = self.names
        if self.observed_ndx is None:
            return names

        return tuple(names[ndx] for ndx in self.observed_ndx)

    @observed_names.setter
    def observed_names(self, value):
        if value is None:
            self.observed_ndx = None
        else:
            self.observed_ndx = self.model.get_names_ndx(*value)

    def _reset_rhs(self, parameters: dict = None):
        parameters = self._build_parameters_dict(parameters)
        self.__rhs = self.model.build_ip_rhs(parameters)
        self.solver = None

    def _concentrations_to_y0(self, concentrations):
        if concentrations is None:
            return concentrations

        y0 = np.nan * np.ones(len(self.names))
        ndxs = self.model.get_names_ndx(*concentrations.keys())
        for ndx, value in zip(ndxs, concentrations.values()):
            y0[ndx] = value

        return y0

    def _start_solver(self, y0, t_bound):
        self.solver = integrate.RK45(self.__rhs, 0, y0, t_bound)

    def _resume_solver(self, new_y0, t_bound, relative_time):
        t0 = self.solver.t
        y0 = self.solver.y
        if relative_time:
            t_bound = t0 + t_bound

        if new_y0 is not None:
            y0 = np.copy(y0)
            sel = np.isfinite(new_y0)
            y0[sel] = new_y0[sel]

        self.solver = integrate.RK45(self.__rhs, t0, y0, t_bound)

    def run(
        self,
        time: Union[float, Iterable],
        concentrations: dict = None,
        parameters: dict = None,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Run the simulation

        Parameters
        ----------
        time : float or np.ndarray
            If a float is given, the time spacing is whatever the integrator steps are until that time.
            If an array is given, the time spacing is whatever given by this vector.
        concentrations : dict
            initial concentration value for each reactant.
            If not a reactant value is not given, the default value will be used.
        parameters : dict
            parameter value for each reactant.
            If not a parameter value is not given, the default value will be used.

        Returns
        -------
        np.ndarray, np.ndarray
            time vector (len N), concentrations matrix (shape N x M)
            where M is the number of observed variables
        """
        self._reset_rhs(parameters)

        return self.resume(time, concentrations)

    def resume(
        self, time: Union[float, Iterable], concentrations: dict = None
    ) -> (np.ndarray, np.ndarray):
        """Resume the simulationm from the last point the simulation

         Parameters
         ----------
         time : float or np.ndarray
             If a float is given, the time spacing is whatever the integrator steps are until that time.
             If an array is given, the time spacing is whatever given by this vector.
         concentrations : dict
             initial concentration value for each reactant.
             If not a reactant value is not given, the default value will be used.
         parameters : dict
             parameter value for each reactant.
             If not a parameter value is not given, the default value will be used.

         Returns
         -------
         np.ndarray, np.ndarray
            time vector (len N), concentrations matrix (shape N x M)
            where M is the number of observed variables
        """
        if isinstance(time, abc.Iterable):
            time = np.asarray(time)
            t_bound = time[-1]
        else:
            t_bound = time

        concentrations = self._build_concentration_dict(concentrations)

        if not isinstance(time, np.ndarray):

            if self.solver is None:
                self._start_solver(
                    self.model.build_concentration_vector(concentrations), t_bound
                )
            else:
                self._resume_solver(
                    self._concentrations_to_y0(concentrations), t_bound, False
                )

            return self._steps()

        t_values = np.empty(len(time))
        y_values = np.empty((len(time), len(self.observed_ndx or self.names)))

        for ndx, up_to in enumerate(time):
            t_values[ndx], y_values[ndx, :] = self.resume1(up_to, concentrations)
            concentrations = None

        return t_values, y_values

    def run1(
        self, time: float, concentrations: dict = None, parameters: dict = None
    ) -> (float, np.ndarray):
        """Run a simulation until a given time.

        Parameters
        ----------
        time : float
            finish simulation time.
        concentrations : dict
            initial concentration value for each reactant.
            If not a reactant value is not given, the default value will be used.
        parameters : dict
            parameter value for each reactant.
            If not a parameter value is not given, the default value will be used.

        Returns
        -------
        float, np.ndarray
            time, concentrations matrix (len M)
            where M is the number of observed variables
        """
        self._reset_rhs(parameters)

        return self.resume1(time, concentrations)

    def resume1(
        self, time: Union[float, np.ndarray], concentrations: dict = None
    ) -> (np.ndarray, np.ndarray):
        """Resume simulation.

        Parameters
        ----------
        time : float
            finish simulation time.
        concentrations : dict
            initial concentration value for each reactant.
            If not a reactant value is not given, the default value will be used.
        parameters : dict
            parameter value for each reactant.
            If not a parameter value is not given, the default value will be used.

        Returns
        -------
        float, np.ndarray
            time, concentrations matrix (len M)
            where M is the number of observed variables
        """
        concentrations = self._build_concentration_dict(concentrations)

        if self.solver is None:
            self._start_solver(
                self.model.build_concentration_vector(concentrations), time
            )
        else:
            self._resume_solver(self._concentrations_to_y0(concentrations), time, False)

        return self._steps1()

    def _steps(self) -> (np.ndarray, np.ndarray):

        solver = self.solver

        t_values = []
        y_values = []
        while solver.status == "running":
            # get solution step state
            solver.step()
            t_values.append(solver.t)
            if self.observed_ndx is None:
                y_values.append(solver.y)
            else:
                y_values.append(solver.y[self.observed_ndx])

        return np.asarray(t_values), np.asarray(y_values)

    def _steps1(self) -> (float, np.ndarray):

        solver = self.solver

        while solver.status == "running":
            # get solution step state
            solver.step()
            # break loop after modeling is finished

        if self.observed_ndx is None:
            return solver.t, solver.y
        else:
            return solver.t, solver.y[self.observed_ndx]

    @contextlib.contextmanager
    def observe_all(self):
        observed_ndx = self.observed_ndx
        yield observed_ndx
        self.observed_ndx = observed_ndx

    def _to_df(
        self, first: Union[float, np.ndarray], y: np.ndarray, first_name="time"
    ) -> pd.DataFrame:
        df = pd.DataFrame(y, columns=self.observed_names)
        df.insert(0, first_name, first)
        return df

    def _to_y_df(self, y: np.ndarray) -> pd.DataFrame:
        return pd.DataFrame(y, columns=self.observed_names)

    def df_run(
        self,
        time: Union[float, Iterable],
        concentrations: dict = None,
        parameters: dict = None,
    ) -> pd.DataFrame:
        t, y = self.run(time, concentrations, parameters)
        return self._to_df(t, y)

    def df_run1(
        self, time: float, concentrations: dict = None, parameters: dict = None
    ) -> pd.DataFrame:
        t, y = self.run1(time, concentrations, parameters)
        return self._to_df(t, y)

    def df_resume(
        self, time: Union[float, np.ndarray], concentrations: dict = None
    ) -> pd.DataFrame:
        t, y = self.resume(time, concentrations)
        return self._to_df(t, y)

    def df_resume1(
        self, t_bound: Union[float, np.ndarray], concentrations: dict = None
    ) -> pd.DataFrame:
        t, y = self.resume1(t_bound, concentrations)
        return self._to_df(t, y)
