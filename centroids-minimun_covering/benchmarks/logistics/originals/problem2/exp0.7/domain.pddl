(define (domain logistics)
(:requirements :strips :typing)
(:types
city place physobj - object
package bomb vehicle - physobj
truck airplane enemytruck - vehicle
airport location - place
)

(:predicates
(in-city ?x1 - place ?x2 - city)
(at ?x1 - physobj ?x2 - place)
(in ?x1 - package ?x2 - vehicle)
(in-bomb ?x1 - bomb ?x2 - vehicle)
(achieved)
)

(:functions
(total-cost)
)

(:action LOAD-TRUCK
:parameters (?x1 - package ?x2 - truck ?x3 - place)
:precondition (and
(at ?x2 ?x3)
(at ?x1 ?x3)
)
:effect (and
(not (at ?x1 ?x3))
(in ?x1 ?x2)
(increase (total-cost) 1)
)
)

(:action LOAD-AIRPLANE
:parameters (?x1 - package ?x2 - airplane ?x3 - place)
:precondition (and
(at ?x1 ?x3)
(at ?x2 ?x3)
)
:effect (and
(not (at ?x1 ?x3))
(in ?x1 ?x2)
(increase (total-cost) 1)
)
)

(:action UNLOAD-TRUCK
:parameters (?x1 - package ?x2 - truck ?x3 - place)
:precondition (and
(at ?x2 ?x3)
(in ?x1 ?x2)
)
:effect (and
(not (in ?x1 ?x2))
(at ?x1 ?x3)
(increase (total-cost) 1)
)
)

(:action UNLOAD-AIRPLANE
:parameters (?x1 - package ?x2 - airplane ?x3 - place)
:precondition (and
(in ?x1 ?x2)
(at ?x2 ?x3)
)
:effect (and
(not (in ?x1 ?x2))
(at ?x1 ?x3)
(increase (total-cost) 1)
)
)

(:action DRIVE-TRUCK
:parameters (?x1 - truck ?x2 - place ?x3 - place ?x4 - city)
:precondition (and
(not (= ?x2 ?x3))
(at ?x1 ?x2)
(in-city ?x2 ?x4)
(in-city ?x3 ?x4)
)
:effect (and
(not (at ?x1 ?x2))
(at ?x1 ?x3)
(increase (total-cost) 3)
)
)

(:action FLY-AIRPLANE
:parameters (?x1 - airplane ?x2 - airport ?x3 - airport)
:precondition (and
(not (= ?x2 ?x3))
(at ?x1 ?x2)
)
:effect (and
(not (at ?x1 ?x2))
(at ?x1 ?x3)
(increase (total-cost) 2)
)
)
)
