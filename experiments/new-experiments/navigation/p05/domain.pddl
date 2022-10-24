(define (domain grid_navigation)
(:requirements :strips :typing)
(:types
cell
player
)

(:predicates
(at ?x1 - player ?x2 - cell)
(connected ?x1 - cell ?x2 - cell)
(free ?x1 - cell)
)

(:action move
:parameters (?x1 - player ?x2 - cell ?x3 - cell)
:precondition (and
(at ?x1 ?x2)
(free ?x3)
(connected ?x2 ?x3)
)
:effect (and
(not (at ?x1 ?x2))
(at ?x1 ?x3)
(free ?x2)
(not (free ?x3))
)
)
)
