(define (problem p9)
(:domain blocks)
(:objects
p a t e r - block)

(:init
(HANDEMPTY)
(ONTABLE t)
(CLEAR r)
(ON p t)
(ON a p)
(ON e a)
(ON r e)
(= (total-cost) 0)
)

(:goal (and
<HYPOTHESIS>
)
)
(:metric minimize (total-cost))
)
