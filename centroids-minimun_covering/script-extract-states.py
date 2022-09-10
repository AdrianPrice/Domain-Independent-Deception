import os
import math
import argparse
import csv
import time
import subprocess

def main():
    # DOMAINS = ['blocks-words', 'depots', 'driverlog', 'dwr', 'logistics', 'rovers', 'sokoban', 'zenotravel']
    DOMAINS = ['blocks-words']
    NUMBER_OF_PROBLEMS = 10

    for domain in DOMAINS:
        for i in range(1,NUMBER_OF_PROBLEMS+1):
            pb = '0' + str(i) if i <= 9 else str(i)
            domain_problem_path = 'benchmarks-deception/' + domain + '/p' + pb
            
            domain_file = domain_problem_path + '/domain.pddl'
            template_file = domain_problem_path + '/template.pddl'
            goals_file = domain_problem_path + '/goals.txt'
            # goals_file = domain_problem_path + '/goals-no_real_hyp.txt'

            print ('$> ' + domain_problem_path)

            # cmd = 'python goal-related-states.py -d ' + domain_file + ' -p ' + template_file + ' -g ' + goals_file + ' -s centroid'
            cmd = 'python goal-related-states.py -d ' + domain_file + ' -p ' + template_file + ' -g ' + goals_file + ' -s minimum-covering'
            print(cmd)
            os.system(cmd)
            print('\n')

if __name__ == '__main__':
    main()
