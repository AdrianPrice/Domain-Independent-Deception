(define (problem test)
    (:domain logistics)
    (:objects 
        pos1 pos2 pos3 pos4 pos5 pos6 pos7 pos8 - location
        apt1 apt2 apt3 apt4 - airport
        tru1 tru2 tru3 tru4 - truck
        air1 air2 - airplane
        cit1 cit2 cit3 cit4 - city
        pac1 pac2 - package
    )
    (:init (at air1 apt1) (at air2 apt4) 
            (at tru1 pos1) (at tru2 pos2) (at tru3 pos3) (at tru4 pos4)
            (at pac1 pos1) (at pac2 pos2)
            (in-city pos1 cit1) (in-city pos2 cit2) (in-city pos3 cit3) (in-city pos4 cit4)
            (in-city pos5 cit1) (in-city pos6 cit2) (in-city pos7 cit3) (in-city pos8 cit4) 
            (in-city apt1 cit1) (in-city apt2 cit2) (in-city apt3 cit3) (in-city apt4 cit4)
    )
    (:goal <HYPOTHESIS>)
)
