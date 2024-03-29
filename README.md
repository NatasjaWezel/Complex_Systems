# Self Organized Criticality in Code Repositories
Project for the Complex System Simulation course in the UvA Master Computational Science.

The model is based on the model fro Lin, Zhongpeng, and Jim Whitehead. "Why power laws? an explanation from fine-grained code changes." 2015 IEEE/ACM 12th Working Conference on Mining Software Repositories. IEEE, 2015.

The evolution of software is simulated by starting with a small piece of Java code, parsing that into an abstract syntax tree and creating, deleting, updating and calling methods for a number of timesteps. Each method has a uniform random fitness.

![Simulation scheme](figures/simu.png "Simulation")

## Prerequisites
For the videos: install the newest version from gource: https://gource.io

Install R

## Installing
Install the dependencies of Python and R in requirements.txt
For the PLYJ installation you should get the newest 'model.py' from github: https://github.com/musiKk/plyj/tree/master/plyj

For further instructions on how to install the web application, see the web application folder.

## RUNNING the code:
Navigate to the model directory and run:
```python run.py ```
The standard settings are set. You can change their values in run.py.

### Folders:
- Analysis: contains the analysis notebooks and R files, and the scripts used for extracting statistics
- Codevo3-MSR2015: code from Zhongpeng & Whitehead (2015),  we added the saving of variables and run.py. Use codev0/run.py to run the model with the correct settings.
- Model: the model used in our experiments. Use run.py to run the model with the correct parameters.

### Data:
https://we.tl/t-K28O0wZ3qp

### Sneak preview for the results
The models give power-law like behavior in the code repositories. While trying to simplify the model, we got rid of the preferential attachment criteria for calling methods. We see differences in the behavior of the model, but we don't see statistical significant differences between the powerlaws of these simulations.
![Network Graphs](figures/pref_attachment_BOTH.png "Network graphs")
On the right we see the network without preferential attachment, on the left with. Edges are method calls, nodes are methods.

## Authors
* Mathijs Maijer
* Esra Solak
* Linda Wouters
* Koen Greuell
* Natasja Wezel
