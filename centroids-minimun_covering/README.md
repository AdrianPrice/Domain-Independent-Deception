**Goal Related States (GRS)** is a framework that allows the computation of states, and the plans to reach them, that keeps some relationship with respect to a set of other states. It is built on top of Fast Downward.

Some version of this code has been used in the following papers:

* **Finding Centroids and Minimum Covering States in Planning**. Pozanco, A; E-Martín, Y; Fernández, S; and Borrajo, D. In Proceedings of ICAPS’19, 348-352, Berkeley(USA), 2019. 

1. [Dependencies](#dependencies)
1. [Compilation](#compilation)
1. [Usage](#usage)
1. [Example](#example)

# <a name="dependencies"></a>Dependencies

To run the code, execute the following command , which installs Fast Downward's dependencies.

```bash
sudo apt install cmake g++ mercurial make python3
```

# <a name="compilation"></a>Compilation

Execute the following commands from the goal-related-states directory:
```bash
python build.py
python landmark-downward/build.py
```
The first line compiles the modified Fast Downward version where GRS runs. The second one compiles a plain Fast Downward used to compute the optimal plans in the optimal versions of GRS.

# <a name="usage"></a>Usage

To run GRS, execute the following command:

```bash
python goal-related-states.py -d DOMAIN_FILE -p PROBLEM_FILE -g GOALS_FILE -s STATE -e ESTIMATION -a EXPLORATION -P PLAN_TYPE
```

* DOMAIN_FILE: path to the domain file in PDDL. All the domains are required to consider a `total-cost` function. By now, in order to simplify the parsing, domain files must have an specific format, described in the file `pddl_formatting.txt`.

* PROBLEM_FILE: path to the problem file in PDDL. By now, in order to simplify the parsing, domain files must have an specific format, described in the file `pddl_formatting.txt`.

* GOALS_FILE: path to the goals file (*G* from now). Each line in the file contains a planning state with an associated weight we want to consider. For a planning state, each predicate is separated by '|'. The following example shows the content of a possible goals file *G* for the well-known blocksworld domain.
    ```
    (on A B)|(ontable C) - 1.0
    (on D E) - 0.58
    ```
* STATE: planning state we want to compute. By now, we allow the following state definitions given a specific metric:

    * *centroid (default)*: state that minimizes the weighted average cost to the states in *G*

    * *minimum-covering*: state that minimizes the maximum weighted cost to the states in *G*

    * *medoid*: state in *G* that minimizes the weighted average cost to the states in *G*

    * *minimum-covering-m*: state in *G* that minimizes the maximum weighted cost to the states in *G*

    * *r-centroid*: state that maximizes the weighted average cost to the states in *G*

    * *r-minimum-covering*: state that maximizes the minimum weighted cost to the states in *G*

    * *r-medoid*: state in *G* that maximizes the weighted average cost to the states in *G*

    * *r-minimum-covering-m*: state in *G* that maximizes the minimum weighted cost to the states in *G*

* ESTIMATION: method employed to estimate the cost between states:

    * *heuristic (default)*: FF heuristic 

    * *optimal-plan*: A* with lmcut heuristic

* EXPLORATION: way in which the state space is explored:

    * *greedy (default)*: greedy exploration that stops when there is no state in the open list with a best value than the best state visited so far

    * *greedy-restart*: greedy + random restart to escape from local minima

    * *all-reachable-fast*: explores all the reachable state space without reopening nodes when a better path is found

    * *all-reachable*: explores all the reachable state space and reopen nodes

* PLAN_TYPE: metric to minimize when computing the plan that reaches the state:

    * *shortest (default)*: least costly plan that leads to the returned state

    * *metric-related*: plan that minimizes the average of the STATE metric in across all the states that leads to the returned state


# <a name="example"></a>Example 

This would be the fastest (and also the furthest from optimum) way of computing centroids in a simple testing problem:

```bash
python goal-related-states.py -d benchmarks/testing/domain.pddl -p benchmarks/testing/p0.pddl -g benchmarks/testing/goals.txt
``` 

The output shows the execution of the program divided into three main steps:

* Extraction of initial state statistics

* Search procedure where the states and plans are computed

* Extraction of final state statistics, and writing the results to a file

The statistics of the task are automatically written to a file called "statistics_domainName.txt", where *domainName* stands for the name of the domain as it is specified in the PDDL file. It contains the following data in a csv-like format:

**Information about the task**

* Domain path

* Problem path

**Main parameters used in the computation**

* Exploration mode

* Estimation method used

* Plan type computed

**Data about the returned state**

* Final state reached, containing all the dynamic PDDL predicates

* Initial state average cost to the states in *G*

* Initial state minmax cost to the states in *G*

* Initial state average cost to the states in *G*

* Initial state minmax cost to the states in *G*

**Data about the returned plan**

* Plan, with all the actions as a list

* Plan cost

* Plan value given the employed metric. It consists on the sum of metric values of all the states traversed by the returned plan.

**Other statistics**

* Number of states with the same metric value

* Search time
