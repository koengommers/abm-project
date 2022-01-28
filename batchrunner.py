from SALib.sample import saltelli
from multiprocess import Pool, cpu_count
from mesa.batchrunner import BatchRunnerMP

class SobolBatchRunner(BatchRunnerMP):
    def __init__(self, model_cls, problem, distinct_samples, **kwargs):
        super().__init__(model_cls, **kwargs)
        self.processes = cpu_count()
        self.pool = Pool(self.processes)

        param_values = saltelli.sample(problem, distinct_samples)
        self.parameters_list = [{name: val for name, val in zip(problem['names'], vals)} for vals in param_values]

