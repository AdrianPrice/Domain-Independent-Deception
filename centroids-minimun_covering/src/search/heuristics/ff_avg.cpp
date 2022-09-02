#include "ff_avg.h"
#include "ff_heuristic.h"

#include "../global_state.h"
#include "../option_parser.h"
#include "../plugin.h"

#include "../task_utils/task_properties.h"

#include <cassert>
#include <map>
#include <fstream>

using namespace std;
extern string state_to_compute;
extern string estimation;
extern vector<GP> goals_probabilities;
extern std::vector <std::string> header;
extern std::vector <std::string> static_predicates;
extern bool test;

namespace ff_heuristic {
// construction and destruction
    FFHeuristicAVG::FFHeuristicAVG(const Options &opts)
            : AdditiveHeuristic(opts),
              relaxed_plan(task_proxy.get_operators().size(), false) {
        cout << "Initializing FF AVG heuristic..." << endl;
    }


    int FFHeuristicAVG::optimal_distance(State s, string goal){
        int distancia = 0;
        std::vector <std::string> current_state = task_properties::return_pddl(s);

        if (header.size() == 0){
            return distancia;
        }


        std::ofstream outfile;
        outfile.open("problemG.pddl");

        // Write the header
        for (auto x: header){
            outfile << x;
        }

        // Write the static predicates
        outfile << "(:init\n";
        for (auto x: static_predicates){
            outfile << x;
        }

        // Write the dynamic predicates
        for (auto x: current_state){
            outfile << x + "\n";
        }

        // Write the goals
        outfile << ")\n";
        outfile << "(:goal (and\n";
        string delimiter = " ";
        string predicate = goal.substr(goal.find(delimiter)+1,goal.size());
        string toQuit = "()";
        std::string::size_type j = predicate.find(toQuit);
        if (j != string::npos){
            predicate.erase(j,toQuit.length());
            predicate.insert(0,"(");
            predicate.insert(predicate.size(),")");
        }
        else{
            replace(predicate.begin(),predicate.end(),'(',' ');
            string toQuit = ",";
            std::string::size_type j = predicate.find(toQuit);
            if (j != string::npos) {
                predicate.erase(j, toQuit.length());
            }
            predicate.insert(0,"(");
        }
        outfile << predicate;
        outfile << "\n))(:metric minimize (total-cost))\n)";
        outfile.close();


        // Execution of the planner for that goal
        int result = std::system("python landmark-downward/fast-downward.py --log-level warning --alias seq-opt-lmcut domain.pddl problemG.pddl > salidaG.txt");

        // Parse the solution
        if (result == 0){
            ifstream infile("salidaG.txt");
            while (infile.good()){
                string line;
                getline(infile,line);
                cout << line << endl;
                if (line.find("Plan cost: ") != string::npos){
                    string delim = ": ";
                    string cost = line.substr(line.find(delim)+1,line.size());
                    distancia = stoi(cost);
                }
            }
        }
        else{
            cout << "Could not solve the problem" << endl;
	    distancia = 1000;
        }



        return distancia;

    }







    void FFHeuristicAVG::mark_preferred_operators_and_relaxed_plan(
            const State &state, PropID goal_id) {
        Proposition *goal = get_proposition(goal_id);
        // Only consider each subgoal once.
        goal->marked = true;
        OpID op_id = goal->reached_by;
        if (op_id != NO_OP) { // We have not yet chained back to a start node.
            UnaryOperator *unary_op = get_operator(op_id);
            bool is_preferred = true;
            for (PropID precond : get_preconditions(op_id)) {
                mark_preferred_operators_and_relaxed_plan(
                        state, precond);
                if (get_proposition(precond)->reached_by != NO_OP) {
                    is_preferred = false;
                }
            }
            int operator_no = unary_op->operator_no;
            if (operator_no != -1) {
                // This is not an axiom.
                relaxed_plan[operator_no] = true;
                if (is_preferred) {
                    OperatorProxy op = task_proxy.get_operators()[operator_no];
                    assert(task_properties::is_applicable(op, state));
                    set_preferred(op);
                }
            }
        }

    }

    int FFHeuristicAVG::compute_heuristic(const GlobalState &global_state) {
        // For optimal heuristic evaluation h*
        if (estimation == "optimal-plan"){
            int h_ff = 0;
            double total_probabilidad = 0;
            State state = convert_global_state(global_state);
            for (size_t i = 0; i < goal_propositions.size(); i++){
                double partial_ff = 0;
                //Alberto Pozanco
                // This part weights each individual goal
                double probabilidad = 0;

                for (FactProxy goal: task_proxy.get_goals()){
                    PropID prop_id = get_prop_id(goal);

                    if (prop_id == goal_propositions[i]){
                        for (auto g: goals_probabilities){
                            for (auto t: g.atoms){
                                string nt = t.substr(0, t.size()-1);
                                if (nt == goal.get_name()){
                                    probabilidad = g.probability;
                                    total_probabilidad += probabilidad;
                                    partial_ff = optimal_distance(state,nt);
                                }
                            }
                        }

                    }
                }

                h_ff += (int)ceil((partial_ff*probabilidad)*10);

            }

            int h_value = int((h_ff/total_probabilidad));

            if (state_to_compute == "r-centroid" || state_to_compute == "r-minimum-covering"
                || state_to_compute == "r-medoid"
                || state_to_compute == "r-minimum-covering-m"){
                // A very large constant since we want to stay out of the goals
                h_value = 1000 - h_value;
            }

            return h_value;

        }




        // For normal heuristic evaluation


        State state = convert_global_state(global_state);
        int h_add = compute_add_and_ff(state);
        if (h_add == DEAD_END)
            return h_add;


        int h_ff = 0;
        double total_probabilidad = 0;


        for (size_t i = 0; i < goal_propositions.size(); i++){
            double partial_ff = 0;
            mark_preferred_operators_and_relaxed_plan(state, goal_propositions[i]);
            for (size_t op_no = 0; op_no < relaxed_plan.size(); ++op_no) {
                if (relaxed_plan[op_no]) {
                    relaxed_plan[op_no] = false; // Clean up for next computation.
                    partial_ff += task_proxy.get_operators()[op_no].get_cost();
                }
            }

            //Alberto Pozanco
            // This part weights each individual goal
            double probabilidad = 0;

            for (FactProxy goal: task_proxy.get_goals()){
                PropID prop_id = get_prop_id(goal);

                if (prop_id == goal_propositions[i]){
                    for (auto g: goals_probabilities){
                        for (auto t: g.atoms){
                            string nt = t.substr(0, t.size()-1);
                            if (nt == goal.get_name()){
                                probabilidad = g.probability;
                                total_probabilidad += probabilidad;
                            }
                        }
                    }

                }
            }

            h_ff += (int)ceil((partial_ff*probabilidad)*10); //we multiply to augment the precission of floats resulting from divisions
        }

        int h_value = int((h_ff/total_probabilidad));

        if (state_to_compute == "r-centroid" || state_to_compute == "r-minimum-covering"
                                                || state_to_compute == "r-medoid"
                                                   || state_to_compute == "r-minimum-covering-m"){
            // A very large constant since we want to stay out of the goals
            h_value = 1000 - h_value;
        }

        return h_value;
    }


    static shared_ptr<Heuristic> _parse(OptionParser &parser) {
        parser.document_synopsis("FF AVG heuristic", "");
        parser.document_language_support("action costs", "supported");
        parser.document_language_support("conditional effects", "supported");
        parser.document_language_support(
                "axioms",
                "supported (in the sense that the planner won't complain -- "
                "handling of axioms might be very stupid "
                "and even render the heuristic unsafe)");
        parser.document_property("admissible", "no");
        parser.document_property("consistent", "no");
        parser.document_property("safe", "yes for tasks without axioms");
        parser.document_property("preferred operators", "yes");

        Heuristic::add_options_to_parser(parser);
        Options opts = parser.parse();
        if (parser.dry_run())
            return nullptr;
        else
            return make_shared<FFHeuristicAVG>(opts);
    }

    static Plugin<Evaluator> _plugin("ff_avg", _parse);
}
