(define (problem blocks-4-1)
(:domain blocks)
(:objects a c d b - block)
(:init (clear b) (ontable d) (on b c) (on c a) (on a d) (handempty))
(:goal (and (ontable d) (on c d) (on a b)))
)