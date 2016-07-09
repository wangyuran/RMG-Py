#!/bin/bash

export OMP_NUM_THREADS=1

# Run the thermo estimator on the given thermo input file
python -m scoop ../../scripts/thermoEstimator.py input_QM.py
