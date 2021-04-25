;shui printer config

G21                     ;Units in mm
M414 S1      		    ;set language RU
M2000.0 X0 Y0 Z0        ;min axis value
M2000.1 X225 Y225 Z240  ;max axis value

M2001 X1 Y1 Z1 T0 E1    ;Axis inversion (1 - inverted)

;Sensors passive level (1 - vcc / 0 - gnd)
M2002 T0 E1
M2002 T1 E1
M2002.0 X1 Y1 Z1 P1
M2002.1 X1 Y1 Z1

;set manual leveling points
M2003 S0 X20 Y20
M2003 S1 X110 Y20
M2003 S2 X200 Y20

M2003 S3 X20 Y110
M2003 S4 X110 Y110
M2003 S5 X200 Y110

M2003 S6 X20 Y200
M2003 S7 X110 Y200
M2003 S8 X200 Y200
