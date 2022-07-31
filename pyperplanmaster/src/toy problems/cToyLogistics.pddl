(define (problem TOY-LOGISTICS) (:domain logistics)
(:objects 
P - airplane 
T - truck 
cit1 cit2 - city
pkg1 pkg2 pkg3 pkg4 - package
loc1 loc2 - location
arp1 arp2 - airport
)

(:init
(in-city loc1 cit1) (in-city loc2 cit1) (in-city arp1 cit1) (in-city arp2 cit2)
(at pkg3 loc1) (at pkg2 arp1) (at pkg4 loc2) (at pkg1 arp2) 
(at T loc2) (at P arp2)
)

(:goal (and
(at pkg2 loc1) (at pkg1 loc2) (at pkg4 loc2) (at pkg3 arp2)
))

;un-comment the following line if metric is needed
;(:metric minimize (???))
)

