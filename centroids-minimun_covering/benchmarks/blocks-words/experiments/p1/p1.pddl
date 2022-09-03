(define (problem p1)
(:domain blocks)
(:objects
p a t e r - block)

(:init
(HANDEMPTY)
(ONTABLE r)
(CLEAR t)
(ON t r)
(ONTABLE p)
(CLEAR e)
(ON a p)
(ON e a)
(= (total-cost) 0)
)

(:goal (and
<HYPOTHESIS>
)
)
(:metric minimize (total-cost))
)
