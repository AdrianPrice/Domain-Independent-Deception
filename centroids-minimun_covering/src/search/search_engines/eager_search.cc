#include "eager_search.h"

#include "../evaluation_context.h"
#include "../evaluator.h"
#include "../open_list_factory.h"
#include "../option_parser.h"
#include "../pruning_method.h"

#include "../algorithms/ordered_set.h"
#include "../task_utils/successor_generator.h"
#include "../task_utils/task_properties.h"
#include "../heuristics/ff_avg.h"

#include <cassert>
#include <cstdlib>
#include <memory>
#include <optional.hh>
#include <set>
#include <fstream>
#include <map>

#include <random>

using namespace std;

extern string state_to_compute;
extern string estimation;
extern string type_of_exploration;
extern string search_paradigm;
extern string goals_file;
extern string plan_type;
extern vector <string> header;
extern vector <string> static_predicates;
extern vector <int> global_contador_fmin;
extern vector <GlobalState> best_states;
extern int best_f;
extern std::vector<GP> goals_probabilities;
extern bool test;

namespace eager_search {
EagerSearch::EagerSearch(const Options &opts)
    : SearchEngine(opts),
      reopen_closed_nodes(opts.get<bool>("reopen_closed")),
      open_list(opts.get<shared_ptr<OpenListFactory>>("open")->
                create_state_open_list()),
      f_evaluator(opts.get<shared_ptr<Evaluator>>("f_eval", nullptr)),
      preferred_operator_evaluators(opts.get_list<shared_ptr<Evaluator>>("preferred")),
      lazy_evaluator(opts.get<shared_ptr<Evaluator>>("lazy_evaluator", nullptr)),
      pruning_method(opts.get<shared_ptr<PruningMethod>>("pruning")) {
    if (lazy_evaluator && !lazy_evaluator->does_cache_estimates()) {
        cerr << "lazy_evaluator must cache its estimates" << endl;
        utils::exit_with(utils::ExitCode::SEARCH_INPUT_ERROR);
    }
}

void EagerSearch::initialize() {
    cout << "Conducting best first search"
         << (reopen_closed_nodes ? " with" : " without")
         << " reopening closed nodes, (real) bound = " << bound
         << endl;
    assert(open_list);

    //ALBERTO POZANCO
    // Initialize structures
    // Read the header
    string line2;
    //vector<string> header;
    ifstream headerFile("header-file.txt");
    if (headerFile.is_open()) {
        while (getline(headerFile, line2)) {
            header.push_back(line2 + "\n");
        }
        headerFile.close();
    }

    // Read static predicates
    string line3;
    ifstream staticFile("static-predicates.txt");
    if (staticFile.is_open()) {
        while (getline(staticFile, line3)) {
            static_predicates.push_back(line3 + "\n");
        }
        staticFile.close();
    }

    set<Evaluator *> evals;
    open_list->get_path_dependent_evaluators(evals);

    // Get the goals and print them
    for (auto g: task_proxy.get_goals()){
        cout << g.get_name() << endl;
    }


    //Alberto Pozanco
    // Assigning each goal its probability
    string line;
    ifstream goals ("fd-goals.txt");

    while (getline(goals,line)){
        string delimiter = "-";
        string aux_probability = line.substr(line.find(delimiter)+1,line.size());
        string goal = line.substr(0,line.find(delimiter));


        string sub_delimiter = "|";
        vector <string> complete_goal;
        complete_goal.clear();
        string token;
        size_t pos = 0;
        while ((pos = goal.find(sub_delimiter)) != string::npos){
            token = goal.substr(0,pos);

            complete_goal.push_back(token);
            goal.erase(0,pos+sub_delimiter.length());
        }
        complete_goal.push_back(goal);


        double probability = stod(aux_probability);
        GP this_goal;
        this_goal.atoms = complete_goal;
        this_goal.probability = probability;
        goals_probabilities.push_back(this_goal);

    }
    goals.close();



    /*
      Collect path-dependent evaluators that are used for preferred operators
      (in case they are not also used in the open list).
    */
    for (const shared_ptr<Evaluator> &evaluator : preferred_operator_evaluators) {
        evaluator->get_path_dependent_evaluators(evals);
    }

    /*
      Collect path-dependent evaluators that are used in the f_evaluator.
      They are usually also used in the open list and will hence already be
      included, but we want to be sure.
    */
    if (f_evaluator) {
        f_evaluator->get_path_dependent_evaluators(evals);
    }

    /*
      Collect path-dependent evaluators that are used in the lazy_evaluator
      (in case they are not already included).
    */
    if (lazy_evaluator) {
        lazy_evaluator->get_path_dependent_evaluators(evals);
    }

    path_dependent_evaluators.assign(evals.begin(), evals.end());

    const GlobalState &initial_state = state_registry.get_initial_state();
    for (Evaluator *evaluator : path_dependent_evaluators) {
        evaluator->notify_initial_state(initial_state);
    }

    /*
      Note: we consider the initial state as reached by a preferred
      operator.
    */

    EvaluationContext eval_context(initial_state, 0, true, &statistics);

    int min_f_value = f_evaluator->compute_result(eval_context).get_evaluator_value();
    global_contador_fmin[min_f_value]++;

    statistics.inc_evaluated_states();

    if (open_list->is_dead_end(eval_context)) {
        cout << "Initial state is a dead end." << endl;
    } else {
        if (search_progress.check_progress(eval_context))
            print_checkpoint_line(0);
        start_f_value_statistics(eval_context);
        SearchNode node = search_space.get_node(initial_state);
        if (plan_type == "metric-related"){ // In this case the g of the initial state is its distance to the goals
            node.open_initialB(min_f_value);
        }
        else {
            node.open_initial();
        }


        open_list->insert(eval_context, initial_state.get_id());
    }

    print_initial_evaluator_values(eval_context);


    pruning_method->initialize(task);
}

void EagerSearch::print_checkpoint_line(int g) const {
    cout << "[g=" << g << ", ";
    statistics.print_basic_statistics();
    cout << "]" << endl;
}

void EagerSearch::print_statistics() const {
    statistics.print_detailed_statistics();
    search_space.print_statistics();
    pruning_method->print_statistics();
}

SearchStatus EagerSearch::step() {
    tl::optional<SearchNode> node;
    while (true) {
        if (open_list->empty()) {
            cout << "Completely explored state space -- no solution!" << endl;
            cout << "Optimal stop " << endl;
            test = true;
            for (auto const g: best_states){
                cout << "Solution found!" << endl;
                Plan plan;
                search_space.trace_path(g, plan);
                set_plan(plan);
                OperatorsProxy operators = task_proxy.get_operators();
                for (OperatorID op_id : plan) {
                    cout << operators[op_id].get_name() << " (" << operators[op_id].get_cost() << ")" << endl;
                }
                cout << "Plan cost: " << calculate_plan_cost(plan,task_proxy) << endl;
                cout << "Plan risk: " << search_space.get_node(g).get_g() << endl;
                cout << "State reached:" << endl;
                g.dump_pddl();
            }
            cout << "There exist " << best_states.size() << " states with the same value!" << endl;
            cout << "Returned state h* to every goal" << endl;

            return SOLVED;
        }
        StateID id = open_list->remove_min();
        // TODO is there a way we can avoid creating the state here and then
        //      recreate it outside of this function with node.get_state()?
        //      One way would be to store GlobalState objects inside SearchNodes
        //      instead of StateIDs
        GlobalState s = state_registry.lookup_state(id);
        node.emplace(search_space.get_node(s));

        if (node->is_closed())
            continue;

        /*
          We can pass calculate_preferred=false here since preferred
          operators are computed when the state is expanded.
        */
        EvaluationContext eval_context(s, node->get_g(), false, &statistics);

        if (lazy_evaluator) {
            /*
              With lazy evaluators (and only with these) we can have dead nodes
              in the open list.

              For example, consider a state s that is reached twice before it is expanded.
              The first time we insert it into the open list, we compute a finite
              heuristic value. The second time we insert it, the cached value is reused.

              During first expansion, the heuristic value is recomputed and might become
              infinite, for example because the reevaluation uses a stronger heuristic or
              because the heuristic is path-dependent and we have accumulated more
              information in the meantime. Then upon second expansion we have a dead-end
              node which we must ignore.
            */
            if (node->is_dead_end())
                continue;

            if (lazy_evaluator->is_estimate_cached(s)) {
                int old_h = lazy_evaluator->get_cached_estimate(s);
                int new_h = eval_context.get_evaluator_value_or_infinity(lazy_evaluator.get());
                if (open_list->is_dead_end(eval_context)) {
                    node->mark_as_dead_end();
                    statistics.inc_dead_ends();
                    continue;
                }
                if (new_h != old_h) {
                    open_list->insert(eval_context, id);
                    continue;
                }
            }
        }

        node->close();
        assert(!node->is_dead_end());
        update_f_value_statistics(eval_context);
        statistics.inc_expanded();
        break;
    }
    GlobalState s = node->get_state();
    s.dump_pddl(); // I changed the dump to write the state to a file
    //cout << "\n\n\nEstado que expando " << endl;
    //for (auto x: s.return_pddl()){
    //    cout << x << endl;
    //}
    //cout << "G del nodo que expando " << node->get_g() << endl;

    vector<OperatorID> applicable_ops;
    successor_generator.generate_applicable_ops(s, applicable_ops);

    /*
      TODO: When preferred operators are in use, a preferred operator will be
      considered by the preferred operator queues even when it is pruned.
    */
    pruning_method->prune_operators(s, applicable_ops);

    // This evaluates the expanded state (again) to get preferred ops
    //EvaluationContext eval_context(s, node->get_g(), false, &statistics, true);
    EvaluationContext eval_context(s, node->get_g(), false, &statistics, true);
    ordered_set::OrderedSet<OperatorID> preferred_operators;

    //ALBERTO POZANCO
    int min_f_value = f_evaluator->compute_result(eval_context).get_evaluator_value();
    //cout << "G del nodo que expando = " << node->get_g() << endl;
    //cout << "F del nodo que expando = " << min_f_value << endl;
    global_contador_fmin[min_f_value]--;
    if (min_f_value < best_f){
        best_states.clear();
        best_states.push_back(s);
        best_f = min_f_value;
    }
    else if (min_f_value == best_f){
        best_states.push_back(s);
    }


    for (const shared_ptr<Evaluator> &preferred_operator_evaluator : preferred_operator_evaluators) {
        collect_preferred_operators(eval_context,
                                    preferred_operator_evaluator.get(),
                                    preferred_operators);
    }


    for (OperatorID op_id : applicable_ops) {
        OperatorProxy op = task_proxy.get_operators()[op_id];
        //cout << "\nGenero un hijo " << op.get_name() << endl;
        if ((node->get_real_g() + op.get_cost()) >= bound){
            continue;
        }


        GlobalState succ_state = state_registry.get_successor_state(s, op);
        statistics.inc_generated();
        bool is_preferred = preferred_operators.contains(op_id);

        SearchNode succ_node = search_space.get_node(succ_state);

        for (Evaluator *evaluator : path_dependent_evaluators) {
            evaluator->notify_state_transition(s, op_id, succ_state);
        }

        // Previously encountered dead end. Don't re-evaluate.
        if (succ_node.is_dead_end()){
            cout << "Dead end "<< endl;
            continue;
        }

        //EvaluationContext succ_eval_context(
         //       succ_state, node->get_g(), is_preferred, &statistics);

        EvaluationContext succ_eval_context(
                succ_state, node->get_g(), is_preferred, &statistics);
        statistics.inc_evaluated_states();

        int succ_g;
        if (plan_type == "metric-related"){
            Plan auxplan;
            search_space.trace_path(s, auxplan);
            int longitud_plan_previo = auxplan.size() + 1;
            int numerador = (node->get_g()*longitud_plan_previo) + (f_evaluator->compute_result(succ_eval_context).get_evaluator_value());
            int denominador = longitud_plan_previo + 1;

            succ_g = int(numerador/denominador);
            //cout << "G almacenada para ese nodo " << succ_node.get_g() << endl;
            //cout << "Calculo de la g del hijo " << endl;
            //cout << "Numerador " << numerador << endl;
            //cout << "Denominador " << denominador << endl;
            //cout << "G del hijo " << succ_g << endl;

        }
        else {
            succ_g = node->get_g() + get_adjusted_cost(op);
            //cout << "G almacenada para ese nodo " << succ_node.get_g() << endl;
            //cout << "Calculo de la g del hijo " << endl;
            //cout << "G del padre = " << node->get_g() << " + Coste accion = " << get_adjusted_cost(op) << " = " << succ_g << endl;


        }


        if (succ_node.is_new()) {
            //cout << "El hijo es nuevo " << endl;
            // We have not seen this state before.
            // Evaluate and create a new node.

            // Careful: succ_node.get_g() is not available here yet,
            // hence the stupid computation of succ_g.
            // TODO: Make this less fragile.





            if (open_list->is_dead_end(succ_eval_context)) {
                if (state_to_compute == "medoid"){
                    //cout << "Dead end" << endl;
                    succ_node.mark_as_dead_end();
                    statistics.inc_dead_ends();
                    continue;
                }
                else {
                    //cout << "Dead end" << endl;
                    succ_node.mark_as_dead_end();
                    statistics.inc_dead_ends();
                    continue;
                }

            }
            if (plan_type == "metric-related"){
                succ_node.open(*node, op, succ_g);
            }
            else {
                succ_node.open(*node, op, get_adjusted_cost(op));
            }

            //ALBERTO POZANCO
            int f_value = f_evaluator->compute_result(succ_eval_context).get_evaluator_value();
            //cout << "La f del hijo es " << f_value << endl;
            global_contador_fmin[f_value]++;

            if (plan_type == "metric-related"){
                succ_node.openB(*node, op, succ_g);
            }
            else {
                succ_node.open(*node, op, get_adjusted_cost(op));
            }

            open_list->insert(succ_eval_context, succ_state.get_id());
            if (search_progress.check_progress(succ_eval_context)) {
                print_checkpoint_line(succ_node.get_g());
                reward_progress();
            }
        }

        else if ((succ_node.get_g() > (node->get_g() + get_adjusted_cost(op))) &
                 (type_of_exploration != "all-reachable-fast") & (plan_type != "metric-related")) {
            // We found a new cheapest path to an open or closed state.
            //cout << "Ya hemos visto este estado y hay un camino mas corto " << endl;
            if (reopen_closed_nodes) {
                //cout << "BP-reopen closed nodes" << endl;
                if (succ_node.is_closed()) {
                    /*
                      TODO: It would be nice if we had a way to test
                      that reopening is expected behaviour, i.e., exit
                      with an error when this is something where
                      reopening should not occur (e.g. A* with a
                      consistent heuristic).
                    */
                    statistics.inc_reopened();
                }
                //succ_g = f_evaluator->compute_result(succ_eval_context).get_evaluator_value();
                succ_node.reopen(*node, op, get_adjusted_cost(op));

                /*
                  Note: our old code used to retrieve the h value from
                  the search node here. Our new code recomputes it as
                  necessary, thus avoiding the incredible ugliness of
                  the old "set_evaluator_value" approach, which also
                  did not generalize properly to settings with more
                  than one evaluator.

                  Reopening should not happen all that frequently, so
                  the performance impact of this is hopefully not that
                  large. In the medium term, we want the evaluators to
                  remember evaluator values for states themselves if
                  desired by the user, so that such recomputations
                  will just involve a look-up by the Evaluator object
                  rather than a recomputation of the evaluator value
                  from scratch.
                */
                open_list->insert(succ_eval_context, succ_state.get_id());
            } else {
                //cout << "BP-We do not reopen closed nodes " << endl;
                // If we do not reopen closed nodes, we just update the parent pointers.
                // Note that this could cause an incompatibility between
                // the g-value and the actual path that is traced back.
                succ_node.update_parent(*node, op, get_adjusted_cost(op));
            }
        }


        else if ((type_of_exploration != "all-reachable-fast") & (plan_type == "metric-related")){
            //cout << "Ya hemos visto este estado y puede que haya un plan con menos metric acumulado" << endl;
            Plan auxplan;
            search_space.trace_path(s, auxplan);
            int longitud_plan_previo = auxplan.size() + 1;
            int numerador = (node->get_g()*longitud_plan_previo) + (f_evaluator->compute_result(succ_eval_context).get_evaluator_value());
            int denominador = longitud_plan_previo + 1;
            succ_g = int(numerador/denominador) + (10*longitud_plan_previo); //Alberto: anyado esta suma para que no vaya infinito de un sitio a otro
            //cout << "Paso estos calculos " << endl;
            //cout << "succ_node " << succ_node.get_g() << endl;
            //cout << "succ_g" << succ_g << endl;
            if (succ_node.get_g() > succ_g){
                if (reopen_closed_nodes){
                    if (succ_node.is_closed()) {
                        /*
                          TODO: It would be nice if we had a way to test
                          that reopening is expected behaviour, i.e., exit
                          with an error when this is something where
                          reopening should not occur (e.g. A* with a
                          consistent heuristic).
                        */
                        statistics.inc_reopened();
                    }
                    //cout << "Por aqui" << endl;
                    succ_node.reopen(*node, op, succ_g);
                    open_list->insert(succ_eval_context, succ_state.get_id());
                    //cout << "Inserto" << endl;
                }
                else {
                    //cout << "We do not reopen closed nodes " << endl;
                    // If we do not reopen closed nodes, we just update the parent pointers.
                    // Note that this could cause an incompatibility between
                    // the g-value and the actual path that is traced back.
                    succ_node.update_parent(*node, op, get_adjusted_cost(op));
                }
            }

        }

        else{
            continue;
        }
    }
    //cout << "Hago los checks " << endl;
    //ALBERTO POZANCO
    // New goal condition in the case of greedy centroids
    if ((type_of_exploration == "greedy") | (type_of_exploration == "greedy-restart")){
        for (int i = 0; i <= best_f; i++){
            if (global_contador_fmin[i] > 0){
                return IN_PROGRESS;
            }
        }

        if (type_of_exploration == "greedy-restart"){
            cout << "Performing greedy restart " << endl;
            int max_jumps = 50;
            vector <GlobalState> jumps;
            jumps.push_back(best_states[0]);
            std::random_device rd;
            std::mt19937_64 gen(rd());

            while (max_jumps > 0){
                GlobalState restart = jumps[0];
                node.emplace(search_space.get_node(restart));
                vector<OperatorID> applicable_ops_restart;
                successor_generator.generate_applicable_ops(restart, applicable_ops_restart);
                std::uniform_int_distribution<> dis (0,applicable_ops_restart.size()-1);

                // select a randm successor
                int randomIndex = dis(gen);
                OperatorProxy op = task_proxy.get_operators()[applicable_ops_restart[randomIndex]];
                GlobalState succ_state = state_registry.get_successor_state(restart, op);
                SearchNode succ_node = search_space.get_node(succ_state);
                EvaluationContext succ_eval_context(
                        succ_state, node->get_g(), false, &statistics);

                open_list->insert(succ_eval_context,succ_state.get_id());

                if (succ_node.is_new()){
                    cout << "We found a new state " << endl;
                    int f_value = f_evaluator->compute_result(succ_eval_context).get_evaluator_value();
                    if (f_value < best_f){
                        cout << "We found a better state performing greedy restart" << endl;
                        best_states.clear();
                        best_states.push_back(succ_state);
                        best_f = f_value;
                    }
                    succ_node.open(*node, op, f_value);
                }
                else{
                    cout << "We have seen this node before" << endl;
                }


                jumps.clear();
                jumps.push_back(succ_state);
                max_jumps--;
            }


        }

        // If not, there is no better state in the open list so we finish
        cout << "Greedy stop " << endl;
        test = true;
        for (auto const tr: best_states){
            cout << "Solution found!" << endl;
            Plan plan;
            search_space.trace_path(tr, plan);
            set_plan(plan);
            OperatorsProxy operators = task_proxy.get_operators();
            for (OperatorID op_id : plan) {
                cout << operators[op_id].get_name() << " (" << operators[op_id].get_cost() << ")" << endl;
            }
            cout << "Plan cost: " << calculate_plan_cost(plan,task_proxy) << endl;

            cout << "Plan risk: " << search_space.get_node(tr).get_g() << endl;
            EvaluationContext eval_context_final(s);
            int f_value_final = f_evaluator->compute_result(eval_context_final).get_evaluator_value();
            cout << "Final f value returned by the algorithm " <<f_value_final << endl;
            cout << "State reached:" << endl;
            tr.dump_pddl();
        }
        cout << "There exist " << best_states.size() << " states with the same value!" << endl;
        cout << "Returned state h* to every goal" << endl;

        return SOLVED;
    }

    else{

        while (!open_list->empty()){
            return IN_PROGRESS;
        }

        cout << "Optimal stop " << endl;
        test = true;
        for (auto const g: best_states){
            cout << "Solution found!" << endl;
            Plan plan;
            search_space.trace_path(g, plan);
            set_plan(plan);
            OperatorsProxy operators = task_proxy.get_operators();
            for (OperatorID op_id : plan) {
                cout << operators[op_id].get_name() << " (" << operators[op_id].get_cost() << ")" << endl;
            }
            cout << "Plan cost: " << calculate_plan_cost(plan,task_proxy) << endl;
            cout << "Plan risk: " << search_space.get_node(g).get_g() << endl;
            EvaluationContext eval_context_final(s);
            int f_value_final = f_evaluator->compute_result(eval_context_final).get_evaluator_value();
            cout << "Final f value returned by the algorithm " <<f_value_final << endl;
            cout << "State reached:" << endl;
            g.dump_pddl();
        }
        cout << "There exist " << best_states.size() << " states with the same value!" << endl;
        cout << "Returned state h* to every goal" << endl;

        return SOLVED;
    }




    //return IN_PROGRESS;
}

void EagerSearch::reward_progress() {
    // Boost the "preferred operator" open lists somewhat whenever
    // one of the heuristics finds a state with a new best h value.
    open_list->boost_preferred();
}

void EagerSearch::dump_search_space() const {
    search_space.dump(task_proxy);
}

void EagerSearch::start_f_value_statistics(EvaluationContext &eval_context) {
    if (f_evaluator) {
        int f_value = eval_context.get_evaluator_value(f_evaluator.get());
        statistics.report_f_value_progress(f_value);
    }
}

/* TODO: HACK! This is very inefficient for simply looking up an h value.
   Also, if h values are not saved it would recompute h for each and every state. */
void EagerSearch::update_f_value_statistics(EvaluationContext &eval_context) {
    if (f_evaluator) {
        int f_value = eval_context.get_evaluator_value(f_evaluator.get());
        statistics.report_f_value_progress(f_value);
    }
}
}
