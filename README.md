# Self Organized Criticality in Code Repositories
Project for the Complex System Simulation course in the UvA Master Computational Science.

## Why Power Laws? An Explanation from Fine-Grained Code Changes
The model is based on the model from Zhongpeng & Whitehead (2015).
Lin, Zhongpeng, and Jim Whitehead. "Why power laws? an explanation from fine-grained code changes." 2015 IEEE/ACM 12th Working Conference on Mining Software Repositories. IEEE, 2015.
Abstract Syntax Tree

Evolution of Software

Fitness of methods -> Uniform (random) distribution

### Creating

### Calling
Take two functions and link them

Question: how are these selected? Via something preferential?
Answer: method S is chosen as the caller with probability proportional to the size of its body (number of statements).

### Updating

### Deleting

#### Ideas
Code decay -> fitness decrease over time?
Question: why?

#### RUNNING the code:
<> optional arguments (and default values)
python run.py <iterations=1000> <gen_java_files=False>

#### Comments
\# Hoofdletter, geen punt

#### REMEMBER
PLYJ model.py van github halen, oude versie installed door pip is niet goed!


Folders:
- Analysis: contains the analysis notebooks and R files, and the scripts used for extracting statistics
- Codevo3-MSR2015: code from Zhongpeng & Whitehead (2015),  we added the saving of variables and run.py. Use codev0/run.py to run the model with the correct settings.
- Model: the model used in our experiments. Use run.py to run the model with the correct parameters.
- TODO
