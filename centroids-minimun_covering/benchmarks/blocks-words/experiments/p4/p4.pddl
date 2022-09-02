(define (problem p4)
(:domain blocks)
(:objects
p a t e r - block)

(:init
(HANDEMPTY)
(ONTABLE e)
(CLEAR e)
(ONTABLE p)
(CLEAR r)
(ON r p)
(ONTABLE t)
(CLEAR a)
(ON a t)
(= (total-cost) 0)
)

(:goal (and
<HYPOTHESIS>
)
)
(:metric minimize (total-cost))
)
