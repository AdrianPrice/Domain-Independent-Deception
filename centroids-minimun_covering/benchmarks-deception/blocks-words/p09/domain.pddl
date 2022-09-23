;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;; 4 Op-blocks world
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(define (domain BLOCKS)
  (:requirements :strips :typing :equality)
  (:types block)
  (:predicates
  (achieved0)
  (achieved1)
  (achieved2)
  (on ?x1 - block ?x2 - block)
	       (ontable ?x1 - block)
	       (clear ?x1 - block)
	       (handempty)
	       (holding ?x1 - block)
	       (achieved0)
	       (achieved1)
	       (achieved2)
	       )

(:functions
(total-cost)
)

(:action pick-up
:parameters (?x1 - block)
:precondition (and
(clear ?x1)
(ontable ?x1)
(handempty)
)
:effect (and
(not (achieved0))
(not (achieved1))
(not (achieved2))
(not (ontable ?x1))
(not (clear ?x1))
(not (handempty))
(holding ?x1)
(increase (total-cost) 1)
)
)

(:action put-down
:parameters (?x1 - block)
:precondition (and
(holding ?x1)
)
:effect (and
(not (achieved0))
(not (achieved1))
(not (achieved2))
(not (holding ?x1))
(clear ?x1)
(handempty)
(ontable ?x1)
(increase (total-cost) 1)
)
)

(:action stack
:parameters (?x1 - block ?x2 - block)
:precondition (and
(holding ?x1)
(clear ?x2)
)
:effect (and
(not (achieved0))
(not (achieved1))
(not (achieved2))
(not (holding ?x1))
(not (clear ?x2))
(clear ?x1)
(handempty)
(on ?x1 ?x2)
(increase (total-cost) 1)
)
)

(:action unstack
:parameters (?x1 - block ?x2 - block)
:precondition (and
(on ?x1 ?x2)
(clear ?x1)
(handempty)
)
:effect (and
(not (achieved0))
(not (achieved1))
(not (achieved2))
(holding ?x1)
(clear ?x2)
(not (clear ?x1))
(not (handempty))
(not (on ?x1 ?x2))
(increase (total-cost) 1)
)
)
)
