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
M2003 B20

M2008 X20 Y20 Z20 E5 F1000	;Filament change point (X, Y, dZ, dE-retract feedrate)

;WiFi settings

M2009.1 S:HOME_NETWORK P:pleaseplease
M2009.2 S:SHUI P:pleaseplease
M2009 M1

; Power control
;F - flags. F=sum of:
;	1 - module exists,
;	2 - auto power off
;	4 - wait cooling hotend
;	8 - use fan
;S - delay before power off (0-255 sec)
;T - hotend temperature (0-255 celsius)
M2004 F15 S120 T60

; Units in mm (mm)
G21
;Steps per unit:
M92 X80.40 Y80.40 Z1600.00 E412.00

;Maximum feedrates (units/s):
M203 X400.00 Y400.00 Z10.00 E200.00

;Maximum Acceleration (units/s2):
M201 X1000.00 Y1000.00 Z100.00 E1000.00

;Acceleration (units/s2): P<print_accel> R<retract_accel> T<travel_accel>
M204 P1000.00 R1000.00 T1000.00

; Advanced: B<min_segment_time_us> S<min_feedrate> T<min_travel_feedrate> J<junc_dev>
M205 B20000.00 S0.00 T0.00 J0.01

; Home offset:
M206 X0.00 Y0.00 Z0.00

; Material heatup parameters:
M145 S0 B60 H200 ;Material preset
M145 S1 B90 H230
M145 S2 B70 H240
M145 S3 B110 H210

;PID Settings
M301 E0 P22.20 I1.08 D114.00
M301 E1 P22.20 I1.08 D114.00
M304 P10.00 I0.023 D305.4

;Filament load/unload config
M603 T0 L800 U850
M603 T1 L800 U850

;Cold Extrude
M302 S170 P0

M500
M0 S2 Configured
