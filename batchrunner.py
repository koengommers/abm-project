"""
The batchrunner class used in this project.

Core class: SobolBatchRunner
"""

import pandas as pd

from multiprocess import Pool, cpu_count
from mesa.batchrunner import BatchRunnerMP
from SALib.sample import saltelli


class SobolBatchRunner(BatchRunnerMP):
    """SobolBatchRunner: extend BatchRunnerMP to fix import and
    use saltelli sample as variable parameters. """

    def __init__(self, model_cls, problem, distinct_samples, **kwargs):
        """Create batchrunner with max amount of processors available.
        Initialize the different parameter value combinations used in runner."""
        super().__init__(model_cls, **kwargs)
        self.processes = cpu_count()
        self.pool = Pool(self.processes)

        param_values = saltelli.sample(problem, distinct_samples)
        self.parameters_list = [{name: val for name, val in zip(
            problem['names'], vals)} for vals in param_values]

    def _prepare_report_table(self, vars_dict, extra_cols=None):
        """
        Creates a dataframe from collected records and sorts it using 'Run'
        column as a key.

        Overwrites Mesa function to better work with sobol variable parameter input.
        """
        extra_cols = ["Run"] + (extra_cols or [])
        index_cols = []
        if self.parameters_list:
            index_cols = list(self.parameters_list[0].keys(
            )) + list(self.fixed_parameters.keys())
        index_cols += extra_cols

        records = []
        for param_key, values in vars_dict.items():
            record = dict(zip(index_cols, param_key))
            # print(record)
            record.update(values)
            records.append(record)

        df = pd.DataFrame(records)

        rest_cols = set(df.columns) - set(index_cols)
        ordered = df[index_cols + list(sorted(rest_cols))]
        ordered.sort_values(by="Run", inplace=True)
        if self._include_fixed:
            for param in self.fixed_parameters.keys():
                val = self.fixed_parameters[param]

                # avoid error when val is an iterable
                vallist = [val for i in range(ordered.shape[0])]
                ordered[param] = vallist
        return ordered

    def _make_model_args_mp(self):
        """Prepare all combinations of parameter values for `run_all`
        Due to multiprocessing requirements of @StaticMethod takes different input, hence the similar function
        Returns:
            List of list with the form:
            [[model_object, dictionary_of_kwargs, max_steps, iterations]]

        Overwrites Mesa function to better work with sobol variable parameter input.
        """
        total_iterations = self.iterations
        all_kwargs = []

        count = len(self.parameters_list)
        if count:
            for i, params in enumerate(self.parameters_list):
                kwargs = params.copy()
                kwargs.update(self.fixed_parameters)
                # run each iterations specific number of times
                for iter in range(self.iterations):
                    kwargs_repeated = kwargs.copy()
                    all_kwargs.append(
                        [self.model_cls, kwargs_repeated,
                            self.max_steps, iter * count + i]
                    )

        elif len(self.fixed_parameters):
            count = 1
            kwargs = self.fixed_parameters.copy()
            all_kwargs.append(kwargs)

        total_iterations *= count

        return all_kwargs, total_iterations
