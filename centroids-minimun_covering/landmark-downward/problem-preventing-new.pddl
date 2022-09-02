(define (problem police0)
(:domain police)
(:objects
s0 s1 s2 - station
carp - car
helicopterp - helicopter
terrorist - terrorist
c1 c2 c3 c4 c5 c6 c7 c8 - cell)
(:init
(at carp c5)
(free c2)
(free c4)
(free c6)
(free c7)
(free c8)
(connected c1 c2)
(connected c1 c3)
(connected c3 c4)
(connected c3 c5)
(connected c4 c6)
(connected c5 c6)
(connected c6 c8)
(connected c6 c7)
(= (total-cost) 0)
(at terrorist c3)
(free c1)
)
(:goal (and
(not (terrorist c6))
))
(:metric minimize (total-cost))
)
