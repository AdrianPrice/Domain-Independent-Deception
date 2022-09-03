#ifndef HEURISTICS_FF_AVG_H
#define HEURISTICS_FF_AVG_H

#include "additive_heuristic.h"

#include <vector>

namespace ff_heuristic {
    using relaxation_heuristic::PropID;
    using relaxation_heuristic::OpID;

    using relaxation_heuristic::NO_OP;

    using relaxation_heuristic::Proposition;
    using relaxation_heuristic::UnaryOperator;

/*
  TODO: In a better world, this should not derive from
        AdditiveHeuristic. Rather, the common parts should be
        implemented in a common base class. That refactoring could be
        made at the same time at which we also unify this with the
        other relaxation heuristics and the additional FF heuristic
        implementation in the landmark code.
*/
    class FFHeuristicAVG : public additive_heuristic::AdditiveHeuristic {
        // Relaxed plans are represented as a set of operators implemented
        // as a bit vector.
        using RelaxedPlan = std::vector<bool>;
        RelaxedPlan relaxed_plan;
        void mark_preferred_operators_and_relaxed_plan(
                const State &state, PropID goal_id);
    protected:
        virtual int compute_heuristic(const GlobalState &global_state) override;
        virtual int optimal_distance(State s, std::string goal);
    public:
        explicit FFHeuristicAVG(const options::Options &opts);
    };
}

#endif
