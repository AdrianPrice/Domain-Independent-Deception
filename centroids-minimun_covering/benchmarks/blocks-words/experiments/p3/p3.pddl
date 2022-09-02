(define (problem p3)
(:domain blocks)
(:objects
p a t e r - block)

(:init
(HANDEMPTY)
(ONTABLE e)
(CLEAR e)
(ONTABLE a)
(CLEAR t)
(ON t a)
(ONTABLE r)
(CLEAR p)
(ON p r)
(= (total-cost) 0)
)

(:goal (and
<HYPOTHESIS>
)
)
(:metric minimize (total-cost))
)
