(define (problem p7)
(:domain blocks)
(:objects
p a t e r - block)

(:init
(HANDEMPTY)
(ONTABLE p)
(CLEAR p)
(ONTABLE t)
(CLEAR a)
(ON a t)
(ONTABLE r)
(CLEAR e)
(ON e r)
(= (total-cost) 0)
)

(:goal (and
<HYPOTHESIS>
)
)
(:metric minimize (total-cost))
)
