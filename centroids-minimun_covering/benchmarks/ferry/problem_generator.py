import os
import random
import shutil

os.mkdir('experiments2/')

original_problems = os.listdir('originals/')

for problem in original_problems:
    infile = open('originals/' + problem,'r')

    new_problem = []
    goals = []

    daniel = []

    for line in infile:
        if not '(:goal' in line:
            if 'at ' in line:
                daniel.append(line.strip())
            new_problem.append(line)

        else:
            new_problem.append('(:goal (and\n')
            new_problem.append('<HYPOTHESIS>\n)\n)\n)')
            break

    gs = random.sample(daniel, 5)
    for x in gs:
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
