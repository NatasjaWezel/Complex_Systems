# Self Organized Criticality in Code Repositories
Project for the Complex System Simulation course in the UvA Master Computational Science.

A model has been created to run different experiments based on generating code files using four different actions each iteration and analysing when commits are made based on fitness values that are assigned to each method.

## Why Power Laws? An Explanation from Fine-Grained Code Changes
Abstract Syntax Tree

Evolution of Software

Fitness of methods -> Uniform (random) distribution

### Code base

#### Analysis

Contains the analysis scripts in R to reproduce plots and in python to run statistical tests against the data.

#### Model

Contains the full model code in python, everything written by us, except java_printer, which was taken from the original simulation model paper github repository.

- run.py

Runs the model

- model.py

Contains the model code

- visualize_graph, webFigures, create_commit_plot

Code containing transformation figures to create output based on the results from the model run

- AST.py

Code to manipulate internal representated code in AST format.

#### Scripts

Contains a python script replicating the paper that scrapes github repositories for absolute changes per commit

#### web_app

Contains web app code for the front end (Angular application) and backend (NodeJS server). This folder has a seperate README for installation.

#### literature

Contains literature used

### RUNNING the code:
python run.py

### NOTE
PLYJ model.py is outdated on pip, install newest version from their github repository.
