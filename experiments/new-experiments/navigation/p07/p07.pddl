(define (problem grid_07)
(:domain grid_navigation)
(:objects
p0 - player
c00 c01 c02 c03 c04 c05
c10 c11 c12 c13 c14 c15
c20 c21 c22 c23 c24 c25
c30 c31 c32 c33 c34 c35
c40 c41 c42 c43 c44 c45
c50 c51 c52 c53 c54 c55 - cell)

(:init
(free c00)
(free c01)
; (free c02)
(free c03)
(free c04)
(free c05)
(free c10)
(free c11)
(free c12)
(free c13)
(free c14)
(free c15)
(free c20)
(free c21)
(free c22)
(free c23)
(free c24)
(free c25)
(free c30)
(free c31)
(free c32)
(free c33)
(free c34)
(free c35)
(free c40)
(free c41)
(free c42)
(free c43)
(free c44)
(free c45)
(free c50)
(free c51)
(free c52)
(free c53)
(free c54)
(free c55)
(at p0 c02)
(connected c00 c01)
(connected c01 c00)
(connected c00 c10)
(connected c10 c00)
(connected c01 c02)
(connected c02 c01)
(connected c01 c11)
(connected c11 c01)
(connected c02 c12)
(connected c02 c03)
(connected c03 c02)
(connected c03 c04)
(connected c04 c03)
(connected c03 c13)
(connected c13 c03)
(connected c13 c23)
(connected c23 c13)
; (connected c23 c24)
; (connected c24 c23)
(connected c12 c02)
(connected c10 c11)
(connected c11 c10)
(connected c10 c20)
(connected c20 c10)
(connected c11 c12)
(connected c12 c11)
(connected c11 c21)
(connected c21 c11)
(connected c12 c22)
(connected c22 c12)
(connected c20 c21)
(connected c21 c20)
(connected c21 c22)
(connected c22 c21)
(connected c20 c30)
(connected c30 c20)
(connected c30 c40)
(connected c40 c30)
; (connected c40 c41)
; (connected c41 c40)
; (connected c41 c42)
; (connected c42 c41)
(connected c42 c43)
(connected c43 c42)
(connected c43 c44)
(connected c44 c43)
(connected c44 c34)
(connected c34 c44)
; (connected c34 c24)
; (connected c24 c34)
; (connected c24 c14)
; (connected c14 c24)
(connected c14 c04)
(connected c04 c14)
(connected c14 c13)
(connected c13 c14)
(connected c13 c12)
(connected c12 c13)

(connected c50 c40)
(connected c40 c50)
(connected c50 c51)
(connected c51 c50)

; (connected c51 c41)
; (connected c41 c51)
(connected c51 c52)
(connected c52 c51)

(connected c52 c42)
(connected c42 c52)
(connected c52 c53)
(connected c53 c52)

(connected c53 c43)
(connected c43 c53)
(connected c53 c54)
(connected c54 c53)

(connected c54 c44)
(connected c44 c54)
(connected c54 c55)
(connected c55 c54)

(connected c55 c45)
(connected c45 c55)

(connected c04 c05)
(connected c05 c04)

(connected c14 c15)
(connected c15 c14)

; (connected c24 c25)
; (connected c25 c24)

(connected c34 c35)
(connected c35 c34)

(connected c44 c45)
(connected c45 c44)

(connected c45 c35)
(connected c35 c45)
(connected c35 c25)
(connected c25 c35)
(connected c15 c25)
(connected c25 c15)
(connected c05 c15)
(connected c15 c05)
)

(:goal 
<HYPOTHESIS>
)
)
