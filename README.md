
# Domain Independent Deception
This project is the work of [@ramonpereira](https://github.com/ramonpereira), [@adrianprice](https://github.com/https://github.com/adrianprice) and Mor Vered to create a deceptive planning algorithm that operates over any valid PDDL enviroment. 

### Usage
To run the code, ensure you have python 3 installed and run `python3 landmarkextraction.py` in the root of the project. Some example PDDL's can be found in `experiment-data/experiment-input` if you would like to add your own, delete the ones there and replace with your own PDDL. The files required for each enviroment are:
* domain.pddl: The domain PDDL
* template.pddl: The PDDL containing the initial and goal states
* hyps.dat: A file containing all potential goals (including the real goal)
* real_hyp.dat: A file containing just the real goal