(define (domain zenotravel)
(:requirements :strips)
(:predicates
	(at ?x ?c)
	(in ?p ?a)
	(next ?l1 ?l2)
	(aircraft ?p)
	(person ?x)
	(city ?x)
	(flevel ?x)
	(fuellevel ?a ?l)
)
(:action board
 :parameters (?p ?a ?c)
 :precondition
	(and (person ?p) (aircraft ?a) (city ?c)  (at ?p ?c) (at ?a ?c))
 :effect
	(and (in ?p ?a) (not (at ?p ?c))))

(:action debark
 :parameters ( ?p ?a ?c)
 :precondition
	(and (person ?p) (aircraft ?a) (city ?c)  (in ?p ?a) (at ?a ?c))
 :effect
	(and (at ?p ?c) (not (in ?p ?a))))

(:action fly
 :parameters ( ?a ?c1 ?c2 ?l1 ?l2)
 :precondition
	(and (aircraft ?a) (city ?c1) (city ?c2) (flevel ?l1) (flevel ?l2)  (at ?a ?c1) (fuellevel ?a ?l1) (next ?l2 ?l1))
 :effect
	(and (at ?a ?c2) (fuellevel ?a ?l2) (not (at ?a ?c1)) (not (fuellevel ?a ?l1))))

(:action zoom
 :parameters ( ?a ?c1 ?c2 ?l1 ?l2 ?l3)
 :precondition
	(and (aircraft ?a) (city ?c1) (city ?c2) (flevel ?l1) (flevel ?l2) (flevel ?l3)  (at ?a ?c1) (fuellevel ?a ?l1) (next ?l2 ?l1) (next ?l3 ?l2))
 :effect
	(and (at ?a ?c2) (fuellevel ?a ?l3) (not (at ?a ?c1)) (not (fuellevel ?a ?l1))))

(:action refuel
 :parameters ( ?a ?c ?l ?l1)
 :precondition
	(and (aircraft?a) (city ?c) (flevel ?l) (flevel ?l1)  (fuellevel ?a ?l) (next ?l ?l1) (at ?a ?c))
 :effect
	(and (fuellevel ?a ?l1) (not (fuellevel ?a ?l))))
)