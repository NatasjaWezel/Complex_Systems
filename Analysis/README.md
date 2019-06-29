This directory contains:

analysis_multiple_sims_plot.ipynb
	- used the pickles files from the simulation results; output of statistics_pickle.py
	which can:
	- plot Mean minimal fitness per simulation
	- plot Mean minimal fitness of the commits per simulation
	- plot Mean value of max(insertions, deletions)\nof the commits per simulation
	- plot Mean lines changes in the commits per simulation
	- plot Mean changes in the commits per simulation
	- plot Proportion of the actions at commits per simulation

Merelo_analysis.R
	which can Create a log log and commits ordered on size plot as done by Merelo
	requires input form: analysis_multiple_sims.ipynb
	this file is copy pasted from: Merelo, J. J., Castillo, P. A., Mora, A. M., Garca-Valdez, M., Cotta, C., and Fernandes, C. (2017a). 		Self-organized criticality in code repositories. Proceedings of the European Conference on Artificial Life, pages 545–552.

KS_test.R
	which can powerlaw bootstrap to determine p_values_,xmin_values & alfa_values
	requires input form: analysis_multiple_sims.ipynb
	this file is copy pasted from: Ortiz, B., & Merelo-Guervós, J. J. (2019). Power laws in code repositories: A skeptical approach. 
	arXiv preprint arXiv:1905.11044.
	
results_plots.ipynb
	For a single simulation:
	plot Lowest fitness in repository per timestep
	plot Lowest fitness in a commit per step
	plot Number of steps per commit
	plot Number of steps per commit
	plot Proportions of last actions per commit
	plot Mean fitness of all methods
	Number of methods over time

Power_law_analysis.ipynb
	Uses the csv files of the commit sizes per simulation to investigate the power laws
	Per condition we create a synthetic data set by bootstrapping an equal number of simulations with the N commits (N= mean number of commits in the condition). From these data sets we fit the power law and save the exponent (gamma) to create a distribution of gamma values. These distributions are then analysed with stats.f_oneway ANOVA.
