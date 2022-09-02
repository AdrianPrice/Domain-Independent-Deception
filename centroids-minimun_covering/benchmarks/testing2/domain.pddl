(define (domain maze)
(:requirements :strips :typing)
(:types
cell - place
player - locatable
)

(:predicates
(at ?x1 - locatable ?x2 - cell)
(connected ?x1 - cell ?x2 - cell)
(free ?x1 - cell)
(volcano ?x1 - cell)
(safe-place ?x1 - cell)
)

(:functions
(total-cost)
)

(:action move
:parameters (?x1 - player ?x2 - cell ?x3 - cell)
:precondition (and
(at ?x1 ?x2)
(not (safe-place ?x2))
(free ?x3)
(connected ?x2 ?x3)
)
:effect (and
(not (at ?x1 ?x2))
(at ?x1 ?x3)
(free ?x2)
(not (free ?x3))
(increase (total-cost) 1)
)
)

(:action move-from-safe-place-to-volcano
:parameters (?x1 - player ?x2 - cell ?x3 - cell)
:precondition (and
(at ?x1 ?x2)
(safe-place ?x2)
(volcano ?x3)
(free ?x3)
(connected ?x2 ?x3)
)
:effect (and
(not (at ?x1 ?x2))
(at ?x1 ?x3)
(free ?x2)
(not (free ?x3))
(increase (total-cost) 10)
)
)

)