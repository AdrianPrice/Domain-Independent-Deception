# This file contains some methods used to manipulate the PDDL files
# TODO: improve this by using the FD translator, although it is necessary to modify it

# Method to get the goals from the goals.txt file
def get_goals(file):
    goal_file = open(file, 'r')
    goals = []
    probs = []
    for line in goal_file:
        data = line.split(' - ')
        goal = data[0].split('|')
        probs.append(data[1].strip())
        goals.append(goal)
    goal_file.close()
    return goals, probs

# Method that updates the goals to make them look like FD Atoms
def rewrite_goals_file(goals,probs):
    new_goal_file = open("fd-goals.txt", 'w+')
    contador = 0
    for x in goals:
        if 'not ' in goals:
            print('This is not implemented yet!')
        else:
            new_goal = 'Atom '
            separated = x.split(' ')
            if len(separated) > 1:
                first = separated[0].replace('(', '')
                new_goal += first
                new_goal += '('
                new_goal += ', '.join(separated[1:])
                new_goal += ' - ' + probs[contador]
                new_goal_file.write(new_goal + '\n')
            else:
                aux = separated[0]
                first = aux.replace('(','').replace(')','')
                new_goal += first + '()'
                new_goal += ' - ' + probs[contador]
                new_goal_file.write(new_goal + '\n')
        contador += 1
    new_goal_file.close()


# Method that updates the domain in the case of goal statements with multiple predicates
def rewrite_domain_file(file,goals):
    domain_file = open(file,'r')
    domain_content = []
    for line in domain_file:
        if '(:action ' in line:
            line = '\n' + line;
            domain_content.append(line.replace('  (:action ', '(:action '))
        else: domain_content.append(line.lstrip())
    domain_content.pop()
    domain_file.close()

    num_comp_goals = 0
    for g in goals:
        if len(g) > 1:
            new_action = generate_action(g,num_comp_goals)
            num_comp_goals += 1
            domain_content.append('\n')
            for x in new_action:
                domain_content.append(x)
    domain_content.append(')')

    index = domain_content.index("(:predicates\n")
    to_write = ''
    for x in range(num_comp_goals):
        to_write += '(achieved' + str(x) + ')\n'
    domain_content.insert(index+1,to_write)

    outfile = open('new-domain.pddl','w+')
    for nl in domain_content:
        outfile.write(nl)
    outfile.close()
    return num_comp_goals

# Method that generates a fake action that achieves multiple goals
def generate_action(goal,num):
    to_return = []
    action_name = '-'.join(goal).replace(')','').replace('(','').replace(' ','')
    to_return.append('(:action ' + action_name + '\n')
    to_return.append(':parameters ()\n')
    to_return.append(':precondition (and\n')
    for p in goal:
        to_return.append(p + '\n')
    to_return.append(')\n')
    to_return.append(':effect (and\n')
    to_return.append('(achieved' + str(num) +')\n')
    to_return.append(')\n')
    to_return.append(')\n')

    return to_return


# Method that gets the costs from the Fast Downward's output
def get_fd_cost(file):
    heuristic_value = 0
    infile = open(file, 'r')
    num_of_actions = 0
    for line in infile:
        if 'Initial heuristic value for' in line:
            try:
                heuristic_value = int(line.split(': ')[1].replace('\n', ''))
            except:
                # Infinity
                heuristic_value = 1000
        if 'Just heuristic value, no search' in line:
            infile.close()
            return heuristic_value
        if 'Plan length' in line:
            num_of_actions = int(line.split(' ')[2])
        if 'Plan cost' in line:
            real_value = int(line.split(': ')[1].replace('\n', ''))
            if real_value == 0 and num_of_actions > 0: #can assume unitary action costs
                real_value = num_of_actions
            infile.close()
            return real_value
    return 1000

# Method that divides a pddl problem into structures
def pddl_to_structures(path):
    infile = open(path,'r')
    header = []
    initial_state = []
    for line in infile:
        while '(:init' not in line:
            header.append(line)
            line = next(infile)
        while line != ')\n' and line != ')':
            initial_state.append(line)
            line = next(infile)
        break

    return header, initial_state


# Method that updates the problem with the goals
def update_problem(file, goals, new_file):
    # Get the problem
    problem_file = open(file, 'r')
    problem = []
    header = []
    aux = False
    for line in problem_file:
        if ':init' in line:
            aux = True
        if not aux:
            header.append(line)
        if line != '<HYPOTHESIS>\n':
            problem.append(line)
        else:
            problem.append(''.join(goals) + '\n')

    problem_file.close()
    # Write it
    new_problem_file = open(new_file, 'w')
    for p in problem:
        new_problem_file.write(p)
    new_problem_file.close()
    return header

# Method that instantiate the effects of an action
def instantiate_effects_2(o,actions_effects,parameters_order):
    # Instantiate the effects of each action
    o = o.split('(')[0].strip()
    to_delete_facts = []
    to_append_facts = []

    aux = o.replace('(', '').replace(')', '')
    action = aux.split(' ')[0]
    parameters = parameters_order[action]
    facts_in_parameters = aux.split(' ')[1:]
    #instantiated_new_facts = []
    effects_of_actions = actions_effects[action]
    for element in effects_of_actions:
        if not 'increase' in element:
            if not '?' in element:
                if 'not' in element:
                    aux = element.replace('(not ','').replace('))',')')
                    to_delete_facts.append(aux)
                else:
                    to_append_facts.append(element)
            else:
                sol = element.split(' ')
                sol_def = []
                for m in sol:
                    if not '?' in m:
                        sol_def.append(m)
                    else:
                        m = m.replace(')','').replace('(','')
                        sol_def.append(facts_in_parameters[parameters.index(m)])

                if '(not' in sol_def:
                    to_delete_facts.append(' '.join(sol_def[1:]) + ')')
                else:
                    to_append_facts.append(' '.join(sol_def) + ')')

    return to_delete_facts,to_append_facts

# Method that receives a planning state and an action and returns an updated planning state
def update_state(obs,state,actions_effects,actions_parameters_order):
    delete,add = instantiate_effects_2(obs,actions_effects,actions_parameters_order)
    for dfact in delete:
        if dfact+'\n' in state:
            state.remove(dfact+'\n')
    for afact in add:
        state.append(afact+'\n')

    return state

# This method receives the execution's path and returns a dictionary with the effects of each action
def get_actions_effects(path):
    domain_file = open(path,'r')
    actions_effects_dict = {}
    for line in domain_file:
        if '(:action' in line:
            action_name = line.strip().split(' ')[1].replace('\n','').lower()
            effects = []
            while ':effect (and' not in line:
                line = next(domain_file)
            line = next(domain_file)
            while line.strip() != ')':
                effects.append(line.strip())
                line = next(domain_file)
            actions_effects_dict[action_name] = effects
    return actions_effects_dict

# This method receives a domain file and returns a dictionary containing the order of the parameters of each action
def get_actions_parameters_order(path):
    domain_file = open(path, 'r')
    actions_parameters_dict = {}
    for line in domain_file:
        if '(:action' in line:
            action_name = line.strip().split(' ')[1].replace('\n', '').lower()
            line = next(domain_file)
            new_line = line.strip().replace('  ',' ').replace(':parameters (', '').replace(')', '')
            data = new_line.strip().split(' ')
            if action_name not in actions_parameters_dict:
                actions_parameters_dict[action_name] = []
            if not '-' in data:
                actions_parameters_dict[action_name] = data
            else:
                for x in range(0, len(data) - 2, 3):
                    actions_parameters_dict[action_name].append(data[x])

    return actions_parameters_dict

# Method that cleans the state as it is returned by FD
def clean_state(aux_state):
    state = []
    for x in aux_state:
        if not 'those' in x:
            if not 'NegatedAtom' in x:
                data = x.split('Atom')[1].strip()
                aux = data.split('(')
                predicate = '(' + aux[0] + ' '+ aux[1].replace(',','')
                state.append(predicate)
            else:
                data = x.split('Atom')[1].strip()
                aux = data.split('(')
                predicate = '(not (' + aux[0] + ' ' + aux[1].replace(',', '') + ')'
                state.append(predicate)
    return state