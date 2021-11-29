M2005 E ;Erase snippets
;* - снипет может быть не задан. Будет выполнен типовой код

M2005 S10|G28 X0|M0 S2 Homed            ;* HOME_X 10
M2005 S11|G28 Y0|M0 S2 Homed            ;* HOME_Y 11
M2005 S12|G28 Z0|M0 S2 Homed            ;* HOME_Z 12
M2005 S13|G28|M0 S2 Homed               ;* HOME_ALL 13

M2005 S14|G28 O|G1 Z200 F2000|M0 S2 Ok  ;* HOME_B 14
M2005 S15|G28 O|G91|G1 Z20 F2000|G90|G1 X20 Y20|M0 S2 Ok ;* HOME_T 15

M2005 S16|M190S0|M81C                   ;* POWER_OFF UI BUTTON
M2005 S19|M84|M300                      ;* STEPPERS OFF 19
M2005 S20|M81 C                         ;* POWER_OFF HARDWARE BUTTON
M2005 S21|M117 Prepare for power off    ;* PRE_POWER_OFF HARDWARE BUTTON

M2005 S22|M25|G60|G91|G1Z20T0E-10|G90|G1X20Y20|M2006N2      ;* PAUSE
M2005 S23|G91|G1E10|G61|G90|M24                             ;* RESUME
M2005 S24|G61XY|M24|M2097                                   ;* RESUME AND SKIP ITEM
M2005 S25|G28XY|M300                                        ;* AFTER PRINT TERMINATE ACTION



M2005 S30|G91|G1%sF1500|G90             ;* MOVE X or Y relative
M2005 S31|G90|G1X%sY%sF1500             ;* MOVE X and Y absolute
M2005 S32|G91|G1Z%sF1000|G90            ;* MOVE Z relative
M2005 S33|G90|G1Z%sF1000                ;* MOVE Z absolute
M2005 S34|G91|G1E%sF1000|G90            ;* MOVE E relative
M2005 S35|G91|G1X%sY%sF1500|G90         ;* MOVE XY relative

;M2005 S40|M0 S2 snippet 40             ;Home UI snippets
;M2005 S41|M0 S2 snippet 41
;M2005 S42|M0 S2 snippet 42
;M2005 S43|M0 S2 snippet 43

;M2005 S44|M0 S2 snippet 44             ;Filament UI snippets
;M2005 S45|M0 S2 snippet 45
;M2005 S46|M0 S2 snippet 46
;M2005 S47|M0 S2 snippet 47

M2005 S48|M105                          ;GCODE UI snippets
M2005 S49|M114
M2005 S50|M118 E1 SHUI


M2005 S51|M303E0S200C5U|M303E-1S90C5U|M500|M300|M0 S2 Done  ;PID
;M2005 S51|M2006N13|M303E0S200C5U|M303E-1S90C5U|M500|M300

M2005 S52|M401                          ;DEBUG UI snippets
M2005 S53|M402
;M2005 S54|M118 E1 SHUI
;M2005 S55|M2006 W2

M2005 S56#M810 M117 Hello#M2018S10A3R810                          ;TIMER UI snippets
M2005 S57#M810 M300#M2018S10A3R810
M2005 S58#M810 M300#M2018S2A3R810
M2005 S59#M810 M300#M2018S5A1R810
M2005 S60|M140S0|M300|M117 Yougurt completted               ;* YOGURT DEFAULT SNIPPET

M0 S2 Snippets updated
