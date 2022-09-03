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

    for line in infile:
        if not '(:goal' in line:
            if 'on ' in line:
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

    #final_goals = goal_predicates[1:]


    n_path = 'experiments2/'+problem.replace('.pddl','')+'/'
    os.mkdir(n_path)
    problem_file = open(n_path +problem,'w+')
    for t in new_problem:
        problem_file.write(t)
    problem_file.close()

    goals_file = open(n_path+'/goals.txt','w+')
    goals_file.write('|'.join(daniel) + ' - ' + str(random.random()) + '\n')
    goals_file.close()

    shutil.copyfile('domain.pddl',n_path + 'domain.pddl')
