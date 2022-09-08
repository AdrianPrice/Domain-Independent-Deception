import os
import optparse
import shutil
from operator import itemgetter
import time
from my_pddl import *
import signal

def signal_handler(signum, frame):
    raise Exception("Timed out!")

# We get the parameters
def parse_options():
    parser = optparse.OptionParser()
    parser.add_option('-s', '--state', action='store', dest='state',
                      help='state we want to compute: centroid (default), minimum-covering, medoid, minimum-covering-m, r-centroid, r-minimum-covering, r-medoid, r-minimum-covering-m',
                      default='centroid')
    parser.add_option('-e', '--estimation', action='store', dest='estimation',
                      help='method employed to estimate the cost of reaching a goal: heuristic (default), optimal-plan',
                      default='heuristic')
    parser.add_option('-a', '--exploration', action='store', dest='exploration',
                      help='mode in which the reachable state space is explored: greedy (default), greedy-restart, all-reachable-fast, all-reachable', default='greedy')
    parser.add_option('-P', '--plan-type', action='store', dest='plan_type', help='metric to minimize in the plan that reaches the state: shortest (default), metric-related',
                      default='shortest')
    parser.add_option('-r', '--search-paradigm', action='store', dest='search_paradigm',
                      help='search paradigm: forward,backward', default='forward')
    parser.add_option('-p', '--problem-file', action='store', dest='problem_file', help='problem file')
    parser.add_option('-d', '--domain-file', action='store', dest='domain_file', help='domain file')
    parser.add_option('-g', '--goals-file', action='store', dest='goals_file', help='goals file')

    options, args = parser.parse_args()
    return options

# Method to clean some auxiliary files that may be used during the search
def clean_files():
    rm_files = ['aux.pddl',
                'current-state.txt',
                'final_costs.txt',
                'header-file.txt',
                'initial_costs.txt',
                'new-domain.pddl',
                '*.pddl-original',
                'problemG.pddl',
                'resulting_states.txt',
                'salidaG.txt',
                'sas_plan',
                'search_output.txt',
                'state.txt',
                'static-predicates.txt',
                'fd-goals.txt',
                'domain.pddl',
                'test.pddl']

    os.system('rm ' + ' '.join(rm_files) + '> /dev/null 2>&1')


def generate_cmd(options,change_domain):
    domain_string = 'domain.pddl'
    base = "python fast-downward.py " + domain_string + ' ' + options.problem_file + ' --search '

    # These heuristics can be changed if we want some preferences, i.e., first minimize the avg and tiebreak by minmax
    heuristics_dictionary = {
        'centroid': '\"eager(tiebreaking([ff_avg()], unsafe_pruning=false),reopen_closed=true, f_eval=sum([ff_avg()]))\"',
        'minimum-covering': '\"eager(tiebreaking([ff_minmax()], unsafe_pruning=false),reopen_closed=true, f_eval=sum([ff_minmax()]))\"',
        'medoid': '\"eager(tiebreaking([weight(goalcount(),1000),ff_avg()], unsafe_pruning=false),reopen_closed=true, f_eval=sum([weight(goalcount(),1000),ff_avg()]))\"',
        'minimum-covering-m': '\"eager(tiebreaking([weight(goalcount(),1000),ff_minmax()], unsafe_pruning=false),reopen_closed=true, f_eval=sum([weight(goalcount(),1000),ff_minmax()]))\"',
        'r-centroid': '\"eager(tiebreaking([ff_avg()], unsafe_pruning=false),reopen_closed=true, f_eval=sum([ff_avg()]))\"',
        'r-minimum-covering': '\"eager(tiebreaking([ff_minmax()], unsafe_pruning=false),reopen_closed=true, f_eval=sum([ff_minmax()]))\"',
        'r-medoid': '\"eager(tiebreaking([weight(goalcount(),1000),ff_avg()], unsafe_pruning=false),reopen_closed=true, f_eval=sum([weight(goalcount(),1000),ff_avg()]))\"',
        'r-minimum-covering-m': '\"eager(tiebreaking([weight(goalcount(),1000),ff_minmax()], unsafe_pruning=false),reopen_closed=true, f_eval=sum([weight(goalcount(),1000),ff_minmax()]))\"'
    }

    rest_of_options = ' --state ' + options.state + ' --estimation ' + options.estimation + ' --exploration ' + options.exploration + ' --search-paradigm ' + options.search_paradigm + ' --plan-type ' + options.plan_type

    outfile = ' > search_output.txt'

    cmd = base + heuristics_dictionary[options.state] + rest_of_options + outfile

    return cmd




def main():
    # ....:::: CLEAN FILES ::::....
    #clean_files()

    start_time = time.time()
    print('**Computing initial state costs**')

    # ....:::: GET INITIAL STATE STATISTICS ::::....
    options = parse_options()

    shutil.copy(options.problem_file, options.problem_file+'-original')
    shutil.copy(options.domain_file,'domain.pddl')
    domain_name = options.domain_file.split('/')[1]
    goals, probabilities = get_goals(options.goals_file)
    change_domain = False
    if any(len(x) > 1 for x in goals):
        rewrite_domain_file(options.domain_file,goals)
        shutil.copy('new-domain.pddl','domain.pddl')
        change_domain = True

    # We compute the distance to each goal
    initial_costs = []
    cont = 0
    for g in goals:
        update_problem(options.problem_file, g, "aux.pddl")
        cmd = "python landmark-downward/fast-downward.py --alias seq-opt-lmcut " + options.domain_file + ' aux.pddl > initial_costs.txt'
        os.system(cmd)
        cost = get_fd_cost("initial_costs.txt")
        initial_costs.append([g, cost*float(probabilities[cont])])
        cont += 1

    new_goals = []
    contador = 0
    for g in goals:
        if len(g) > 1:
            new_goals.append('(achieved' + str(contador) + ')')
            contador += 1
        else:
            new_goals.append(g[0])

    rewrite_goals_file(new_goals,probabilities)

    update_problem(options.problem_file, new_goals, options.problem_file)
    header, initial_state = pddl_to_structures(options.problem_file)
    header_file = open("header-file.txt", 'w+')
    for h in header:
        header_file.write(h)
    header_file.close()

    # We compute some statistics about the initial state
    probabilities = [float(x) for x in probabilities]
    avg_initial_state = sum([x[1] for x in initial_costs]) / float(sum(probabilities))
    max_initial_state = max([x[1] for x in initial_costs])

    print('Done\n')
    print('**Performing the search**')



    
    # ....:::: DO THE SEARCH ::::....
    # We configure the call to the planner depending on the parameters
    cmd = generate_cmd(options,change_domain)
    # We launch the search
    initial_search_time = time.time()
    os.system(cmd)
    search_time = time.time() - initial_search_time

    print('Done (' + str(search_time) + 's)\n')




    # ....:::: GET FINAL STATES STATISTICS ::::....
    print('**Analyzing the output**')
    print('Retrieving the states..')

    # We compute some statistics about the final state as returned by the search
    infile = open('search_output.txt','r')
    os.remove(options.problem_file)
    os.rename(options.problem_file+'-original',options.problem_file)
    # [plan,cost,plan_value,state,realAvg,realMinmax,initialAvg,initialMinmax]
    set_of_results = []
    for line in infile:
        if 'Greedy stop' in line or 'Optimal stop' in line:
            line = next(infile)
            while 'There exist' not in line:
                if 'Solution found!' in line:
                    line = next(infile)
                    plan = []
                    state = []
                    cost = 0
                    while 'Solution found' not in line and 'There exist' not in line:
                        while 'Plan cost' not in line:
                            plan.append(line.strip())
                            line = next(infile)
                        cost = int(line.split(':')[1].strip())
                        line = next(infile)
                        plan_value = int(line.split(':')[1].strip())
                        while 'State reached' not in line:
                            line = next(infile)
                        line = next(infile)
                        while 'Solution found' not in line and 'There exist' not in line:
                            state.append(line.strip())
                            line = next(infile)
                        if [plan,cost,plan_value,clean_state(state)] not in set_of_results:
                            set_of_results.append([plan,cost,plan_value,clean_state(state)])
            break

    # Here we compute the statistics of the final state, launching optimal plans from each state
    print('Computing final state and plan statistics for ' + str(len(set_of_results)) + ' candidate solutions..')
    actions_effects = get_actions_effects('domain.pddl')
    actions_parameters_order = get_actions_parameters_order('domain.pddl')
    # print(actions_parameters_order)
    # First, we compute the optimal cost to the goals in G from the returned states
    for y in range(len(set_of_results)):
        state = set_of_results[y][3]
        infile = open("static-predicates.txt",'r')
        new_state = ["(:init\n"]
        for line in infile:
            new_state.append(line)
        for s in state:
            new_state.append(s + '\n')
        new_state.append(')\n')

        # We compute the cost from this state to each goal
        final_costs = []
        cont = 0
        for g in goals:
            new_state.append('\n(:goal (and\n')
            new_state.append(''.join(g) + '\n')
            new_state.append(')\n)(:metric minimize (total-cost))\n)')

            test_file = open("test.pddl", 'w+')
            for h in header:
                test_file.write(h)
            for s in new_state:
                test_file.write(s)
            test_file.close()
            cmd = "python landmark-downward/fast-downward.py --alias seq-opt-lmcut " + options.domain_file + ' test.pddl > final_costs.txt'
            os.system(cmd)
            cost = get_fd_cost("final_costs.txt")
            final_costs.append([g, cost * float(probabilities[cont])])
            new_state = new_state[:len(new_state) - 3]
            cont += 1

        avg_final_state = sum([x[1] for x in final_costs]) / float(sum(probabilities))
        if 'r-' in options.state:
            max_final_state = min([x[1] for x in final_costs])
        else:
            max_final_state = max([x[1] for x in final_costs])

        set_of_results[y].append(avg_final_state)
        set_of_results[y].append(max_final_state)
        set_of_results[y].append(avg_initial_state)
        set_of_results[y].append(max_initial_state)

        # Finally, we compute the plan value of the plan by traversing all the states in the plan
        # Here we treat it differently if try to escape from the goals (r-centroid, r-medoid etc)
        big_constant = 0
        total_plan_value = avg_initial_state
        this_state = list(initial_state)
        aux_cont = 0
        for a in set_of_results[y][0]:
            aux_cont += 1
            this_state = update_state(a,this_state,actions_effects,actions_parameters_order)
            this_state_cost = []
            cont = 0
            for g in goals:
                this_state.append(')\n(:goal (and\n')
                this_state.append(''.join(g) + '\n')
                this_state.append(')\n)(:metric minimize (total-cost))\n)')

                test_file = open("test.pddl", 'w+')
                for h in header:
                    test_file.write(h)
                for s in this_state:
                    test_file.write(s)
                test_file.close()
                cmd = "python landmark-downward/fast-downward.py --alias seq-opt-lmcut " + options.domain_file + ' test.pddl > final_costs.txt'
                os.system(cmd)
                cost = get_fd_cost("final_costs.txt")
                this_state_cost.append([g, cost*probabilities[cont]])
                this_state = this_state[:len(this_state) - 3]
                cont += 1

            avg_this_state = sum([x[1] for x in this_state_cost]) / float(sum(probabilities))
            total_plan_value = ((total_plan_value * aux_cont) + avg_this_state) / float(aux_cont + 1)

        if 'r-' in options.state: #in this case we want to approach the goals somehow
            total_plan_value = total_plan_value * -1
        set_of_results[y].append(total_plan_value)



    # IN THE CASE OF RISKS, WE ONLY WANT TO GET THE OPTIMAL RISK AVOIDANCE PLAN
    # [plan,cost,plan_value,state,realAvg,realMinmax,initialAvg,initialMinmax,real_plan_value]
    file_name = "statistics_" + domain_name + "_" + options.state + "_" + options.plan_type +".txt"
    print('\n**Writing the output to ' + file_name + ' and finishing**')
    if file_name not in os.listdir(os.getcwd()): # first time we write so we write the header
        outfile = open(file_name,'a+')
        outfile.write('Domain\t'
                      'Problem\t'
                      'Exploration\t'
                      'Estimation\t'
                      'Plan Type\t'
                      'State\t'
                      'Final State\t'
                      'Initial State Average\t'
                      'Initial State Minmax\t'
                      'Final State Average\t'
                      'Final State Minmax\t'
                      'Plan\t'
                      'Plan Cost\t'
                      'Plan Value\t'
                      'Number of States with Same Value\t'
                      'Search Time\n')
        outfile.close()
    outfile = open(file_name,"a+")
    gen = (x for x in set_of_results)
    # Here we are only getting one state, the best from all the computed ones
    # In case you want to output all the states with the same value, they can be retrieved
    if options.plan_type == 'metric-related':
        best = min(gen,key=itemgetter(4,8)) # The one with lower plan value
    else:
        best = min(gen,key=itemgetter(4,1,8)) # The one with shortest path

    outfile.write(options.domain_file + '\t'
                  + options.problem_file + '\t'
                  + options.exploration + '\t'
                  + options.estimation + '\t'
                  + options.plan_type + '\t'
                  + options.state + '\t'
                  + str(best[3]) + '\t'  #reached_state
                  + str(best[6]) + '\t'  # initial_state_average_distance_to_S
                  + str(best[7]) + '\t'  # initial_state_minmax_distance_to_S
                  + str(best[4]) + '\t'  # final_state_average_distance_to_S
                  + str(best[5]) + '\t'  # final_state_minmax_distance_to_S
                  + str(best[0]) + '\t'  # plan
                  + str(best[1]) + '\t'  # plan cost
                  + str(best[-1]) + '\t'  # plan value
                  + str(len(set_of_results)) + '\t'  # number_of_states_with_same_value_of_metric
                  + str(search_time) + '\n') #search time + instantiation of fd


    # Save the resulting state in a file along with the extraction time (in secods).
    path_to_save_output = options.domain_file.replace('/domain.pddl', '')
    pb_number = options.problem_file.split('/')[2]
    output_file_state_name = pb_number + '_' + domain_name + "_" + options.state + "_" + options.estimation + "_" + options.exploration + ".txt"
    output_file_state_name_runtime = pb_number + '_' + domain_name + "_" + options.state + "_" + options.estimation + "_" + options.exploration + "-runtime.txt"
    output_file_state = open(path_to_save_output + '/' + output_file_state_name, "w+")
    resulting_state = ''
    for f in best[3]:
        if 'achieved' not in f:
            resulting_state += str(f) + ' '

    output_file_state.write(resulting_state)

    print(path_to_save_output + '/' + output_file_state_name)

    # ....:::: CLEAN FILES ::::....
    clean_files()
    total_time = (time.time() - start_time)
    
    output_file_state = open(path_to_save_output + '/' + output_file_state_name_runtime, "w+")
    output_file_state.write(str(total_time))
    print(path_to_save_output + '/' + output_file_state_name_runtime)

    print("\n--- %s seconds ---" % total_time)

if __name__ == '__main__':
    # main()
    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(900)   # 15 minutes of timeout.
    try:
        main()
    except Exception, msg:
        print "Timed out!"
