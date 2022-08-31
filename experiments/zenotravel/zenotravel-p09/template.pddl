(define (problem zenotravelProblem)
(:domain zenotravel)
(:objects
    plane1
    plane2
    person1
    person2
    person3
    person4
    person5
    city0
    city1
    city2
    fl0
    fl1
    fl2
    fl3
    fl4
    fl5
    fl6
    )
(:init
    (at plane1 city2)
    (aircraft plane1)
    (fuellevel plane1 fl5)
    (at plane2 city0)
    (aircraft plane2)
    (fuellevel plane2 fl1)
    (at person1 city0)
    (person person1)
    (at person2 city0)
    (person person2)
    (at person3 city0)
    (person person3)
    (at person4 city0)
    (person person4)
    (at person5 city0)
    (person person5)
    (city city0)
    (city city1)
    (city city2)
    (next fl0 fl1)
    (next fl1 fl2)
    (next fl2 fl3)
    (next fl3 fl4)
    (next fl4 fl5)
    (next fl5 fl6)
    (next fl6 fl4)
    (flevel fl0)
    (flevel fl1)
    (flevel fl2)
    (flevel fl3)
    (flevel fl4)
    (flevel fl5)
    (flevel fl6)
)
(:goal  
    <HYPOTHESIS> 
))