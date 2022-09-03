(define (domain police)
(:requirements :typing :action-costs)
(:types cell - location
car helicopter terrorist - movable
station
)

(:predicates
(at ?x1 - movable ?x2 - cell)
(at-terrorist ?x1 - cell)
(in ?x1 - cell ?x2 - station)
(connected ?x1 - cell ?x2 - cell)
(free ?x1 - cell)
(done)
)

(:functions
(total-cost)
)

(:action move-car
:parameters (?x1 - car ?x2 - cell ?x3 - cell)
:precondition (and
(at ?x1 ?x2)
(free ?x3)
(connected ?x2 ?x3)
)
:effect (and
(not (at ?x1 ?x2))
(at ?x1 ?x3)
(not (at terrorist ?x3))
(free ?x2)
(not (free ?x3))
(increase (total-cost) 1)
)
)

(:action move-helicopter
:parameters (?x1 - helicopter ?x2 - cell ?x3 - cell)
:precondition (and
(at ?x1 ?x2)
(free ?x3)
)
:effect (and
(not (at ?x1 ?x2))
(at ?x1 ?x3)
(not (at terrorist ?x3))
(free ?x2)
(not (free ?x3))
(increase (total-cost) 5)
)
)

)
