
# Domain Independent Deception
This project is the work of [@ramonpereira](https://github.com/ramonpereira), [@adrianprice](https://github.com/https://github.com/adrianprice), Peta Masters and [@morVered](https://github.com/morVered) to create a deceptive planning algorithm that operates over any valid PDDL enviroment. 

### Usage
To run the code, ensure you have python 3 installed and run `python3 landmarkextraction.py` in the root of the project. Some example PDDL's can be found in `experiment-data/experiment-input` if you would like to add your own, delete the ones there and replace with your own PDDL. The files required for each enviroment are:
* domain.pddl: The domain PDDL
* template.pddl: The PDDL containing the initial and goal states
* hyps.dat: A file containing all potential goals (including the real goal)
* real_hyp.dat: A file containing just the real goal

Running the above code will just bring out the deceptive path. If you would like for information about whether each step is truthful or not run the above code with the `--deceptivestats` flag, and if you would like verbose printing run the above code with the `--verbose` flag.
