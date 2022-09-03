(define (problem p6)
(:domain blocks)
(:objects
p a t e r - block)

(:init
(HANDEMPTY)
(ONTABLE a)
(CLEAR a)
(ONTABLE e)
(CLEAR p)
(ON p e)
(ONTABLE t)
(CLEAR r)
(ON r t)
(= (total-cost) 0)
)

(:goal (and
<HYPOTHESIS>
)
)
(:metric minimize (total-cost))
)
