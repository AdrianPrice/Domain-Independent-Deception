import os
import random
import shutil

os.mkdir('experiments2/')

original_problems = os.listdir('originals/')

for problem in original_problems:
    infile = open('originals/' + problem + '/template.pddl','r')

    new_problem = []
    goals = []

    daniel = []

    for line in infile:
        if not '(:goal' in line:
            if 'bomb' in line or 'total-cost' in line or 'enemy' in line:
                continue
            else:
                if 'at ' in line:
                    daniel.append(line.strip())
                new_problem.append(line)
        else:
            new_problem.append('(:goal (and\n')
            new_problem.append('<HYPOTHESIS>\n)\n)\n)')
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
    gs = []
    goal_file = open('originals/' + problem + '/hyps.dat','r')
    for line in goal_file:
        g = line.split(' (')[0]
        gs.append([g,random.random()])
    """

    gs = random.sample(daniel,4)
    for x in gs:
        goals.append([x,random.random()])


    n_path = 'experiments2/'+problem.replace('.pddl','')+'/'
    os.mkdir(n_path)
    problem_file = open(n_path +problem+'.pddl','w+')
    for t in new_problem:
        problem_file.write(t)
    problem_file.close()

    goals_file = open(n_path+'/goals.txt','w+')
    for t in goals:
        goals_file.write(t[0] + ' - ' + str(t[1]) + '\n')
    goals_file.close()

    shutil.copyfile('domain.pddl',n_path + 'domain.pddl')
