(define (problem dwrProblem)
  (:domain dwr)
  (:objects
   r1 - robot
   l1 l2 - location
   k1 k2 - crane
   p1 q1 p2 q2 - pile
   ca cb cc cd pallet - container)

  (:init
   (adjacent l1 l2)
   (adjacent l2 l1)

   (attached p1 l2)
   (attached q1 l2)
   (attached p2 l1)
   (attached q2 l1)

   (belong k1 l2)
   (belong k2 l1)

   (in ca p1)
   (in cb p1)
   (in cc p1)
   (in cd p1)

   (on cb pallet)
   (on ca cb)
   (on cc ca)
   (on cc cd)

   (top cc p1)
   (top pallet q1)
   (top pallet p2)
   (top pallet q2)

   (at r1 l2)
   (unloaded r1)
   (occupied l2)

   (empty k1)
   (empty k2))

(:goal (and
(achieved0)(achieved1)
)
))