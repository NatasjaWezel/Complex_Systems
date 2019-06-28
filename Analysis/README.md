This directory contains:

analysis_multiple_sims.ipynb
	which can:
	- determine the commit sizes from a datafile created by run.py which can be found in the model directory
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
	plot Lowest fitness in repository per timestep
	plot Lowest fitness in a commit per step
	plot Number of steps per commit
	plot Number of steps per commit
	plot Proportions of last actions per commit
	plot Mean fitness of all methods
Number of methods over time