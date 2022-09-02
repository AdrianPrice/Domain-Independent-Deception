(define (problem p2)
(:domain blocks)
(:objects
p a t e r - block)

(:init
(HANDEMPTY)
(ONTABLE a)
(CLEAR e)
(ON e a)
(ONTABLE p)
(CLEAR r)
(ON t p)
(ON r t)
(= (total-cost) 0)
)

(:goal (and
<HYPOTHESIS>
)
)
(:metric minimize (total-cost))
)
