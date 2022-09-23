(define (problem logistics-problem)
(:domain logistics)
(:objects
 apn1 - airplane
 apt1 apt2 apt3 - airport
 pos31 pos21 pos22 pos23 pos11 pos12 pos13 - location
 cit3 cit2 cit1 - city
 tru3 tru2 tru1 - truck
 obj31 obj23 obj22 obj21 obj13 obj12 obj11 - package)

(:init 
  (at apn1 apt1)
  (at tru3 pos31) (at tru1 pos21) (at tru2 pos13) 
  (at obj11 pos11) (at obj12 pos12) (at obj13 pos13)
  (at obj21 pos21) (at obj22 pos22) (at obj23 pos23) 
  (at obj31 pos31) 
  (in-city apt1 cit1) (in-city pos11 cit1) (in-city pos12 cit1) (in-city pos13 cit1)
  (in-city apt2 cit2) (in-city pos21 cit2) (in-city pos22 cit2) (in-city pos23 cit2)
  (in-city apt3 cit3) (in-city pos31 cit3) 
)

(:goal (and
(achieved0)(achieved1)
)
)
)