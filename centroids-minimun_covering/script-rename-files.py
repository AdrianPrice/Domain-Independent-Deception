import os
import math
import argparse
import csv
import time
import subprocess
from os.path import exists

def main():
    DOMAINS = ['blocks-words', 'depots', 'driverlog', 'dwr', 'logistics', 'rovers', 'sokoban', 'zenotravel']
    # DOMAINS = ['blocks-words']
    NUMBER_OF_PROBLEMS = 10

    for domain in DOMAINS:
        for i in range(1,NUMBER_OF_PROBLEMS+1):
            pb = '0' + str(i) if i <= 9 else str(i)
            domain_problem_path = 'benchmarks-deception/' + domain + '/p' + pb
            
            domain_file = domain_problem_path + '/domain.pddl'
            template_file = domain_problem_path + '/template.pddl'
            goals_file = domain_problem_path + '/goals.txt'
            # goals_file = domain_problem_path + '/goals-no_real_hyp.txt'

            problem_n = '0' + str(i) if i <= 9 else str(i)

            new_p_name = 'p' + problem_n + '_' + domain + '_centroid_heuristic_greedy.txt'
            new_p_name_time = 'p' + problem_n + '_' + domain + '_centroid_heuristic_greedy-runtime.txt'

            p_name = 'p' + problem_n + '_' + domain + '_centroid_shortest.txt'
            p_name_time = 'p' + problem_n + '_' + domain + '_centroid_shortest-runtime.txt'

            print ('$> ' + domain_problem_path)

            if exists(domain_problem_path + '/' + p_name):
                print(domain_problem_path + '/' + p_name)
                os.rename(domain_problem_path + '/' + p_name, domain_problem_path + '/' + new_p_name)
            
            if exists(domain_problem_path + '/' + p_name_time):
                print(domain_problem_path + '/' + p_name_time)
                os.rename(domain_problem_path + '/' + p_name_time, domain_problem_path + '/' + new_p_name_time)

if __name__ == '__main__':
    main()
