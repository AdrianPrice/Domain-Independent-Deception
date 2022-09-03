(define (domain driverlog)
(:requirements :strips) 
(:predicates
(achieved0)
(achieved1)
(achieved2)
(achieved3)
(achieved4)
(achieved5)
(achieved6)
(achieved7)
(OBJ ?obj)
(TRUCK ?truck)
(LOCATION ?loc)
(driver ?d)
(at ?obj ?loc)
(in ?obj1 ?obj)
(driving ?d ?v)
(link ?x ?y) (path ?x ?y)
(empty ?v)
)

(:action LOAD-TRUCK
:parameters (?obj ?truck ?loc)
:precondition
(and (OBJ ?obj) (TRUCK ?truck) (LOCATION ?loc)
(at ?truck ?loc) (at ?obj ?loc))
:effect (and 
(not (at ?obj ?loc)) 
(in ?obj ?truck)
)
)

(:action UNLOAD-TRUCK
:parameters (?obj ?truck ?loc)
:precondition
(and (OBJ ?obj) (TRUCK ?truck) (LOCATION ?loc)
(at ?truck ?loc) (in ?obj ?truck))
:effect (and 
(not (in ?obj ?truck)) 
(at ?obj ?loc)
)
)

(:action BOARD-TRUCK
:parameters (?driver ?truck ?loc)
:precondition
(and (DRIVER ?driver) (TRUCK ?truck) (LOCATION ?loc)
(at ?truck ?loc) (at ?driver ?loc) (empty ?truck))
:effect (and 
(not (at ?driver ?loc)) 
(driving ?driver ?truck) 
(not (empty ?truck))
)
)

(:action DISEMBARK-TRUCK
:parameters (?driver ?truck ?loc)
:precondition
(and (DRIVER ?driver) (TRUCK ?truck) (LOCATION ?loc)
(at ?truck ?loc) (driving ?driver ?truck))
:effect (and 
(not (driving ?driver ?truck)) 
(at ?driver ?loc) 
(empty ?truck)
)
)

(:action DRIVE-TRUCK
:parameters (?truck ?loc-from ?loc-to ?driver)
:precondition
(and (TRUCK ?truck) (LOCATION ?loc-from) (LOCATION ?loc-to) (DRIVER ?driver) 
(at ?truck ?loc-from)
(driving ?driver ?truck) (link ?loc-from ?loc-to))
:effect (and 
(not (at ?truck ?loc-from))
(at ?truck ?loc-to)
)
)

(:action WALK
:parameters (?driver ?loc-from ?loc-to)
:precondition
(and (DRIVER ?driver) (LOCATION ?loc-from) (LOCATION ?loc-to)
(at ?driver ?loc-from) (path ?loc-from ?loc-to))
:effect (and 
(not (at ?driver ?loc-from))
(at ?driver ?loc-to)
)
)

(:action atdriver1s2-attruck1s0-atpackage1s1-atpackage2s0
:parameters ()
:precondition (and
(at driver1 s2)
(at truck1 s0)
(at package1 s1)
(at package2 s0)
)
:effect (and
(achieved0)
)
)

(:action atdriver1s1-attruck1s2-atpackage1s2-atpackage2s1
:parameters ()
:precondition (and
(at driver1 s1)
(at truck1 s2)
(at package1 s2)
(at package2 s1)
)
:effect (and
(achieved1)
)
)

(:action atdriver1s0-attruck1s0-atpackage1s0-atpackage2s2
:parameters ()
:precondition (and
(at driver1 s0)
(at truck1 s0)
(at package1 s0)
(at package2 s2)
)
:effect (and
(achieved2)
)
)

(:action atdriver1s2-attruck1s1-atpackage1s1-atpackage2s0
:parameters ()
:precondition (and
(at driver1 s2)
(at truck1 s1)
(at package1 s1)
(at package2 s0)
)
:effect (and
(achieved3)
)
)

(:action atdriver1s1-attruck1s0-atpackage1s2-atpackage2s1
:parameters ()
:precondition (and
(at driver1 s1)
(at truck1 s0)
(at package1 s2)
(at package2 s1)
)
:effect (and
(achieved4)
)
)

(:action atdriver1s0-attruck1s2-atpackage1s0-atpackage2s2
:parameters ()
:precondition (and
(at driver1 s0)
(at truck1 s2)
(at package1 s0)
(at package2 s2)
)
:effect (and
(achieved5)
)
)

(:action atdriver1s2-attruck1s2-atpackage1s1-atpackage2s0
:parameters ()
:precondition (and
(at driver1 s2)
(at truck1 s2)
(at package1 s1)
(at package2 s0)
)
:effect (and
(achieved6)
)
)

(:action atdriver1s1-attruck1s1-atpackage1s0-atpackage2s1
:parameters ()
:precondition (and
(at driver1 s1)
(at truck1 s1)
(at package1 s0)
(at package2 s1)
)
:effect (and
(achieved7)
)
)
)