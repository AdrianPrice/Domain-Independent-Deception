(define (problem p8)
(:domain blocks)
(:objects
p a t e r - block)

(:init
(HANDEMPTY)
(ONTABLE a)
(CLEAR a)
(ONTABLE p)
(CLEAR t)
(ON t p)
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
