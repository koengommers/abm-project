# Prey-Predator Model

This repository contains the code for a project during the Agent-Based Modelling course at the University of Amsterdam

* Koen Gommers
* Stijn Henckens
* Sigo van der Linde
* Jesse Pronk
* Pieter de Regt

## Setup

Please use pipenv to install the required packages. If you don't have pipenv, [installation instructions can be found here](https://pipenv.pypa.io/en/latest/).

    pipenv shell

    pipenv install

(We use the same environment as given in the course.)

## Running the visualization

To run the model with GUI, do:

    mesa runserver

It will launch the server and it can be viewed at http://127.0.0.1:8521/

## Running simulations for Sobol sensitivity analysis

In order to do Sobol sensitivity analysis, data of the simulations with different parameters are needed. We look at 3 parameters (`prey_cohere_factor`, `prey_separate_factor`, `prey_separate_pred_factor`). The bounds and the values of other fixed parameters can be viewed and set in the `config.json` file.

We use multithreading to optimize this. To run the full experiment, do:

    python runner.py

This will take a long time, to test if it works the number of samples and iterationsn can be decreased:

    python runner.py --distinct_samples 1 --iterations 1

Additional arguments can be found by:

    python runner.py --help

## Analyzing results

The previous step results in a .csv file. This file can be read and analyzed in the `Analyze.ipynb` notebook. For further instructions, see the notebook.
