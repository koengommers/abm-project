import argparse
from datetime import datetime
import json
import pickle
from batchrunner import SobolBatchRunner
from model import PreyPredatorModel

def main(args):
    with open(args.config) as config_file:
        params = json.load(config_file)

    problem = {
        'num_vars': len(params['variable_params']),
        'names': params['variable_params'].keys(),
        'bounds': list(params['variable_params'].values())
    }

    model_reporters = {
        'Predator': lambda m: m.schedule_Predator.get_agent_count(),
        'Prey': lambda m: m.schedule_Prey.get_agent_count(),
        'Time': lambda m: m.schedule.steps
    }

    params['fixed_params'].update({ 'collect_data': False })

    batch = SobolBatchRunner(PreyPredatorModel,
            problem,
            args.distinct_samples,
            max_steps=args.max_steps,
            iterations=args.iterations,
            fixed_parameters=params['fixed_params'],
            model_reporters=model_reporters)

    batch.run_all()

    results = batch.get_model_vars_dataframe()

    out = args.out
    if not out:
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        out = f'results_{timestamp}'

    params.update({
        'iterations': args.iterations,
        'max_steps': args.max_steps,
        'distinct_samples': args.distinct_samples
    })
    with open(out, 'wb') as out_file:
        pickle.dump((params, results), out_file)

    return problem, results
 
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', default='config.json', type=str)
    parser.add_argument('--iterations', default=10, type=int)
    parser.add_argument('--max_steps', default=1000, type=int)
    parser.add_argument('--distinct_samples', default=512, type=int)
    parser.add_argument('--out', type=str)
    args = parser.parse_args()

    main(args)
