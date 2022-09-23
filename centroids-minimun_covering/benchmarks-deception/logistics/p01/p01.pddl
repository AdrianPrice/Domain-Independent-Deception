(define (problem logistics-01)
(:domain logistics)
(:objects
apn1 - airplane
apt1 apt2 - airport
pos21 pos22 pos23 pos11 pos12 - location
cit2 cit1 - city
tru2 tru1 - truck
obj21 obj12 obj11 - package
)
(:init 
(at apn1 apt1)
(at tru1 pos12)
(at tru2 pos22)
(at obj11 pos11)
(at obj12 pos12)
(at obj21 pos11)
(in-city apt1 cit1)
(in-city pos11 cit1)
(in-city pos12 cit1)
(in-city apt2 cit2)
(in-city pos21 cit2)
(in-city pos22 cit2)
(in-city pos23 cit2)
)
(:goal (and
<HYPOTHESIS>
)
)
)