#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This script runs stand-alone thermo estimation using RMG for a list of species in a
thermo input file.  It generates an output.txt file containing the chemkin format
thermochemistry as well as a ThermoLibrary file containing the enthalpy, entropy, and
heat capacity data in RMG-database format.
"""

import os.path
from rmgpy import settings
from rmgpy.data.rmg import RMGDatabase
from rmgpy.rmg.main import RMG
from rmgpy.data.thermo import ThermoLibrary
from rmgpy.chemkin import writeThermoEntry
from rmgpy.rmg.model import Species
from rmgpy.thermo.thermoengine import submit
                     
################################################################################

def runThermoEstimator(inputFile):
    """
    Estimate thermo for a list of species using RMG and the settings chosen inside a thermo input file.
    """
    
    rmg = RMG()
    rmg.loadThermoInput(inputFile)
    
    rmg.database = RMGDatabase()
    path = os.path.join(settings['database.directory'])

    # forbidden structure loading
    rmg.database.loadThermo(os.path.join(path, 'thermo'), rmg.thermoLibraries, depository=False)
   
    if rmg.solvent:
        rmg.database.loadSolvation(os.path.join(path, 'solvation'))
        Species.solventData = rmg.database.solvation.getSolventData(rmg.solvent)
        Species.solventName = rmg.solvent

    for species in rmg.initialSpecies:
        submit(species)

    library = ThermoLibrary(name='Thermo Estimation Library')
    for spc in rmg.initialSpecies:
        library.loadEntry(
            index = len(library.entries) + 1,
            label = species.label,
            molecule = species.molecule[0].toAdjacencyList(),
            thermo = species.getThermoData().toThermoData(),
            shortDesc = species.getThermoData().comment,
        )
    library.save(os.path.join(rmg.outputDirectory,'ThermoLibrary.py'))
    
    # Generate the thermo for all the species and write them to chemkin format as well as
    # ThermoLibrary format with values for H, S, and Cp's.
    with open(os.path.join(rmg.outputDirectory, 'output.txt'),'wb') as output:
        for spc in rmg.initialSpecies:
            output.write(writeThermoEntry(spc))
            output.write('\n')
        
    


################################################################################

if __name__ == '__main__':

    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('input', metavar='INPUT', type=str, nargs=1,
        help='Thermo input file')
    args = parser.parse_args()
    
    inputFile = os.path.abspath(args.input[0])
    
    runThermoEstimator(inputFile)