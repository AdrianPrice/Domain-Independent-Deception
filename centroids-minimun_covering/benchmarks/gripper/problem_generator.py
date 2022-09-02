import os
import random
import shutil

try:
    os.mkdir('experiments2/')
except:
    print 'Directory exists'

original_problems = os.listdir('originals/')

for problem in original_problems:
    infile = open('originals/' + problem ,'r')

    new_problem = []
    goal_predicates = []

    daniel = []
    goals = []

    for line in infile:
        if not '(:goal' in line:
            if 'at ' in line:
                daniel.append(line.strip())
            new_problem.append(line.strip() + '\n')

        else:
            new_problem.append('(:goal (and\n')
            new_problem.append('<HYPOTHESIS>\n)\n)\n)')
            line = next(infile)
            while line.strip() != ')':
                goal_predicates.append(line.strip())
                line = next(infile)
            break

            """gs = []
            gs.append(line.split('(and ')[1].strip())
            line = next(infile)
            while not ')))' in line:
                gs.append(line)
                line =next(infile)

            for g in gs:
                this_g = []
                this_g.append('(' + g.strip().replace(')','').replace('(','') + ')')
                this_g.append(random.random())
                goals.append(this_g)"""

    """
    final_goals = []
    for x in range(2):
        this_goal = []
        for t in range(1):
            d = list(random.sample(goal_predicates,2))
            for h in d:
                if 'roomb' in h:
                    h.replace('roomb','rooma')
                else:
                    h.replace('rooma','roomb')
            this_goal=d
        final_goals.append(this_goal)
    """
    for x in daniel:
        goals.append([x, random.random()])


    n_path = 'experiments2/'+problem.replace('.pddl','')+'/'
    os.mkdir(n_path)
    problem_file = open(n_path +problem,'w+')
    for t in new_problem:
        problem_file.write(t)
    problem_file.close()

    goals_file = open(n_path+'/goals.txt','w+')
    for t in goals:
        goals_file.write(t[0] + ' - ' + str(t[1]) + '\n')
    goals_file.close()

    shutil.copyfile('domain.pddl',n_path + 'domain.pddl')
