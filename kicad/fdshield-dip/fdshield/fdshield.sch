EESchema Schematic File Version 4
EELAYER 30 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 1 1
Title ""
Date "lun. 30 mars 2015"
Rev ""
Comp ""
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
Text Label 9400 2300 2    60   ~ 0
Vin
Text Label 9400 1700 2    60   ~ 0
IOREF
Text Label 8900 2500 0    60   ~ 0
A0
Text Label 8900 2600 0    60   ~ 0
A1
Text Label 8900 2700 0    60   ~ 0
A2
Text Label 8900 2800 0    60   ~ 0
A3
Text Label 8900 2900 0    60   ~ 0
A4
Text Label 8900 3000 0    60   ~ 0
A5
Text Label 10200 3000 0    60   ~ 0
0(Rx)
Text Label 10550 2800 0    60   ~ 0
2
Text Label 10200 2900 0    60   ~ 0
1(Tx)
Text Label 10550 2700 0    60   ~ 0
3(**)
Text Label 10550 2600 0    60   ~ 0
4
Text Label 10550 2500 0    60   ~ 0
5(**)
Text Label 10550 2400 0    60   ~ 0
6(**)
Text Label 10550 2300 0    60   ~ 0
7
Text Label 10550 2100 0    60   ~ 0
8
Text Label 10550 2000 0    60   ~ 0
9(**)
Text Label 10550 1900 0    60   ~ 0
10(**/SS)
Text Label 10550 1800 0    60   ~ 0
11(**/MOSI)
Text Label 10550 1700 0    60   ~ 0
12(MISO)
Text Label 10550 1600 0    60   ~ 0
13(SCK)
Text Label 10200 1400 0    60   ~ 0
AREF
NoConn ~ 9400 1600
Text Notes 8550 750  0    60   ~ 0
Shield for Arduino that uses\nthe same pin disposition\nlike "Uno" board Rev 3.
$Comp
L Connector_Generic:Conn_01x08 P1
U 1 1 56D70129
P 9600 1900
F 0 "P1" H 9600 2350 50  0000 C CNN
F 1 "Power" V 9700 1900 50  0000 C CNN
F 2 "Socket_Arduino_Uno:Socket_Strip_Arduino_1x08" V 9750 1900 20  0000 C CNN
F 3 "" H 9600 1900 50  0000 C CNN
	1    9600 1900
	1    0    0    -1  
$EndComp
Text Label 9400 1800 2    60   ~ 0
Reset
$Comp
L power:+3.3V #PWR01
U 1 1 56D70538
P 9100 1350
F 0 "#PWR01" H 9100 1200 50  0001 C CNN
F 1 "+3.3V" V 9100 1600 50  0000 C CNN
F 2 "" H 9100 1350 50  0000 C CNN
F 3 "" H 9100 1350 50  0000 C CNN
	1    9100 1350
	1    0    0    -1  
$EndComp
$Comp
L power:+5V #PWR02
U 1 1 56D707BB
P 8950 1350
F 0 "#PWR02" H 8950 1200 50  0001 C CNN
F 1 "+5V" V 8950 1550 50  0000 C CNN
F 2 "" H 8950 1350 50  0000 C CNN
F 3 "" H 8950 1350 50  0000 C CNN
	1    8950 1350
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR03
U 1 1 56D70CC2
P 9300 3150
F 0 "#PWR03" H 9300 2900 50  0001 C CNN
F 1 "GND" H 9300 3000 50  0000 C CNN
F 2 "" H 9300 3150 50  0000 C CNN
F 3 "" H 9300 3150 50  0000 C CNN
	1    9300 3150
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR04
U 1 1 56D70CFF
P 10300 3150
F 0 "#PWR04" H 10300 2900 50  0001 C CNN
F 1 "GND" H 10300 3000 50  0000 C CNN
F 2 "" H 10300 3150 50  0000 C CNN
F 3 "" H 10300 3150 50  0000 C CNN
	1    10300 3150
	1    0    0    -1  
$EndComp
$Comp
L Connector_Generic:Conn_01x06 P2
U 1 1 56D70DD8
P 9600 2700
F 0 "P2" H 9600 2300 50  0000 C CNN
F 1 "Analog" V 9700 2700 50  0000 C CNN
F 2 "Socket_Arduino_Uno:Socket_Strip_Arduino_1x06" V 9750 2750 20  0000 C CNN
F 3 "" H 9600 2700 50  0000 C CNN
	1    9600 2700
	1    0    0    -1  
$EndComp
$Comp
L Connector_Generic:Conn_01x08 P4
U 1 1 56D7164F
P 10000 2600
F 0 "P4" H 10000 2100 50  0000 C CNN
F 1 "Digital" V 10100 2600 50  0000 C CNN
F 2 "Socket_Arduino_Uno:Socket_Strip_Arduino_1x08" V 10150 2550 20  0000 C CNN
F 3 "" H 10000 2600 50  0000 C CNN
	1    10000 2600
	-1   0    0    -1  
$EndComp
Wire Notes Line
	8525 825  9925 825 
Wire Notes Line
	9925 825  9925 475 
Wire Wire Line
	9400 1900 9100 1900
Wire Wire Line
	9400 2000 8950 2000
Wire Wire Line
	9400 2100 9300 2100
Wire Wire Line
	9400 2200 9300 2200
Connection ~ 9300 2200
Wire Wire Line
	8950 2000 8950 1650
Wire Wire Line
	9100 1900 9100 1450
Wire Wire Line
	9400 2500 8900 2500
Wire Wire Line
	9400 2600 8900 2600
Wire Wire Line
	9400 2700 8900 2700
Wire Wire Line
	9400 2800 8900 2800
Wire Wire Line
	9400 2900 8900 2900
Wire Wire Line
	9400 3000 8900 3000
$Comp
L Connector_Generic:Conn_01x10 P3
U 1 1 56D721E0
P 10000 1600
F 0 "P3" H 10000 2150 50  0000 C CNN
F 1 "Digital" V 10100 1600 50  0000 C CNN
F 2 "Socket_Arduino_Uno:Socket_Strip_Arduino_1x10" V 10150 1600 20  0000 C CNN
F 3 "" H 10000 1600 50  0000 C CNN
	1    10000 1600
	-1   0    0    -1  
$EndComp
Wire Wire Line
	10200 2100 10550 2100
Wire Wire Line
	10200 2000 10550 2000
Wire Wire Line
	10200 1900 10550 1900
Wire Wire Line
	10200 1800 10550 1800
Wire Wire Line
	10200 1700 10550 1700
Wire Wire Line
	10200 1600 10550 1600
Wire Wire Line
	10200 2600 10550 2600
Wire Wire Line
	10200 2500 10550 2500
Wire Wire Line
	10200 2400 10550 2400
Wire Wire Line
	10200 2300 10550 2300
Wire Wire Line
	10200 1500 10300 1500
Wire Wire Line
	10300 1500 10300 3150
Wire Wire Line
	9300 2100 9300 2200
Wire Wire Line
	9300 2200 9300 3150
Wire Notes Line
	8500 500  8500 3450
Wire Notes Line
	8500 3450 11200 3450
Text Notes 9700 1600 0    60   ~ 0
1
$Comp
L fdshield:23LCxxx U5
U 1 1 5F06FFD6
P 7550 2650
F 0 "U5" H 7550 3131 50  0000 C CNN
F 1 "23LCxxx" H 7550 3040 50  0000 C CNN
F 2 "Package_DIP:DIP-8_W7.62mm" H 8400 2300 50  0001 C CNN
F 3 "http://ww1.microchip.com/downloads/en/DeviceDoc/20005155B.pdf" H 7550 2650 50  0001 C CNN
	1    7550 2650
	1    0    0    -1  
$EndComp
$Comp
L 74xx:74LS08 U3
U 1 1 5F071C25
P 5950 2100
F 0 "U3" H 5950 2425 50  0000 C CNN
F 1 "74LS08" H 5950 2334 50  0000 C CNN
F 2 "Package_DIP:DIP-14_W7.62mm" H 5950 2100 50  0001 C CNN
F 3 "http://www.ti.com/lit/gpn/sn74LS08" H 5950 2100 50  0001 C CNN
	1    5950 2100
	1    0    0    -1  
$EndComp
$Comp
L 74xx:74LS08 U3
U 2 1 5F076B93
P 5900 3100
F 0 "U3" H 5900 3425 50  0000 C CNN
F 1 "74LS08" H 5900 3334 50  0000 C CNN
F 2 "Package_DIP:DIP-14_W7.62mm" H 5900 3100 50  0001 C CNN
F 3 "http://www.ti.com/lit/gpn/sn74LS08" H 5900 3100 50  0001 C CNN
	2    5900 3100
	1    0    0    -1  
$EndComp
$Comp
L 74xx:74LS08 U3
U 3 1 5F077E6F
P 10600 5550
F 0 "U3" H 10850 5650 50  0000 C CNN
F 1 "74LS08" H 10900 5450 50  0000 C CNN
F 2 "Package_DIP:DIP-14_W7.62mm" H 10600 5550 50  0001 C CNN
F 3 "http://www.ti.com/lit/gpn/sn74LS08" H 10600 5550 50  0001 C CNN
	3    10600 5550
	1    0    0    -1  
$EndComp
$Comp
L 74xx:74LS08 U3
U 4 1 5F07A30D
P 10600 6050
F 0 "U3" H 10850 6150 50  0000 C CNN
F 1 "74LS08" H 10900 5950 50  0000 C CNN
F 2 "Package_DIP:DIP-14_W7.62mm" H 10600 6050 50  0001 C CNN
F 3 "http://www.ti.com/lit/gpn/sn74LS08" H 10600 6050 50  0001 C CNN
	4    10600 6050
	1    0    0    -1  
$EndComp
$Comp
L 74xx:74LS125 U4
U 1 1 5F07C912
P 6650 2100
F 0 "U4" H 6550 2300 50  0000 C CNN
F 1 "74LS125" H 6800 2300 50  0000 C CNN
F 2 "Package_DIP:DIP-14_W7.62mm" H 6650 2100 50  0001 C CNN
F 3 "http://www.ti.com/lit/gpn/sn74LS125" H 6650 2100 50  0001 C CNN
	1    6650 2100
	1    0    0    -1  
$EndComp
$Comp
L 74xx:74LS125 U4
U 2 1 5F07D910
P 6600 3100
F 0 "U4" H 6600 3417 50  0000 C CNN
F 1 "74LS125" H 6600 3326 50  0000 C CNN
F 2 "Package_DIP:DIP-14_W7.62mm" H 6600 3100 50  0001 C CNN
F 3 "http://www.ti.com/lit/gpn/sn74LS125" H 6600 3100 50  0001 C CNN
	2    6600 3100
	1    0    0    -1  
$EndComp
$Comp
L 74xx:74LS125 U4
U 4 1 5F07FC44
P 1850 6450
F 0 "U4" H 2000 6550 50  0000 C CNN
F 1 "74LS125" H 2100 6350 50  0000 C CNN
F 2 "Package_DIP:DIP-14_W7.62mm" H 1850 6450 50  0001 C CNN
F 3 "http://www.ti.com/lit/gpn/sn74LS125" H 1850 6450 50  0001 C CNN
	4    1850 6450
	1    0    0    -1  
$EndComp
$Comp
L 74xx:74LS125 U4
U 5 1 5F0806C9
P 8800 5700
F 0 "U4" H 8850 5350 50  0000 L CNN
F 1 "74LS125" H 8850 6050 50  0000 L CNN
F 2 "Package_DIP:DIP-14_W7.62mm" H 8800 5700 50  0001 C CNN
F 3 "http://www.ti.com/lit/gpn/sn74LS125" H 8800 5700 50  0001 C CNN
	5    8800 5700
	1    0    0    -1  
$EndComp
$Comp
L 74xx:74LS08 U3
U 5 1 5F0819FC
P 9250 5700
F 0 "U3" H 9300 5350 50  0000 L CNN
F 1 "74LS08" H 9300 6050 50  0000 L CNN
F 2 "Package_DIP:DIP-14_W7.62mm" H 9250 5700 50  0001 C CNN
F 3 "http://www.ti.com/lit/gpn/sn74LS08" H 9250 5700 50  0001 C CNN
	5    9250 5700
	1    0    0    -1  
$EndComp
$Comp
L 74xx:74LS74 U1
U 3 1 5F086330
P 7900 5700
F 0 "U1" H 7950 5350 50  0000 L CNN
F 1 "74LS74" H 7950 6050 50  0000 L CNN
F 2 "Package_DIP:DIP-14_W7.62mm" H 7900 5700 50  0001 C CNN
F 3 "74xx/74hc_hct74.pdf" H 7900 5700 50  0001 C CNN
	3    7900 5700
	1    0    0    -1  
$EndComp
$Comp
L 74xx:74LS74 U1
U 2 1 5F086D5C
P 4200 3100
F 0 "U1" H 4000 3350 50  0000 C CNN
F 1 "74LS74" H 4400 3350 50  0000 C CNN
F 2 "Package_DIP:DIP-14_W7.62mm" H 4200 3100 50  0001 C CNN
F 3 "74xx/74hc_hct74.pdf" H 4200 3100 50  0001 C CNN
	2    4200 3100
	1    0    0    -1  
$EndComp
Wire Wire Line
	4500 3200 4600 3200
Wire Wire Line
	4600 3200 4600 2700
Wire Wire Line
	4600 2700 3800 2700
Wire Wire Line
	3800 2700 3800 3000
Wire Wire Line
	3800 3000 3900 3000
Wire Wire Line
	4500 3000 4700 3000
Wire Wire Line
	4200 3400 4200 3500
Wire Wire Line
	4200 3500 5000 3500
Wire Wire Line
	5000 3400 5000 3500
Connection ~ 4200 3500
Wire Wire Line
	4700 3100 4700 3600
$Comp
L Connector_Generic:Conn_02x17_Odd_Even J1
U 1 1 5F0A2B8A
P 1450 5050
F 0 "J1" H 1500 6067 50  0000 C CNN
F 1 "Conn_02x17_Odd_Even" H 1500 5976 50  0000 C CNN
F 2 "Connector_PinHeader_2.54mm:PinHeader_2x17_P2.54mm_Vertical" H 1450 5050 50  0001 C CNN
F 3 "~" H 1450 5050 50  0001 C CNN
	1    1450 5050
	1    0    0    -1  
$EndComp
Wire Wire Line
	1250 4250 1150 4250
Wire Wire Line
	1150 4250 1150 4450
Wire Wire Line
	1250 5850 1150 5850
Connection ~ 1150 5850
Wire Wire Line
	1150 5850 1150 5950
Wire Wire Line
	1150 5750 1250 5750
Connection ~ 1150 5750
Wire Wire Line
	1150 5750 1150 5850
Wire Wire Line
	1250 5650 1150 5650
Connection ~ 1150 5650
Wire Wire Line
	1150 5650 1150 5750
Wire Wire Line
	1150 5550 1250 5550
Connection ~ 1150 5550
Wire Wire Line
	1150 5550 1150 5650
Wire Wire Line
	1250 5450 1150 5450
Connection ~ 1150 5450
Wire Wire Line
	1150 5450 1150 5550
Wire Wire Line
	1250 4450 1150 4450
Connection ~ 1150 4450
Wire Wire Line
	1150 4450 1150 4550
Wire Wire Line
	1150 4550 1250 4550
Connection ~ 1150 4550
Wire Wire Line
	1150 4550 1150 4650
Wire Wire Line
	1250 4650 1150 4650
Connection ~ 1150 4650
Wire Wire Line
	1150 4650 1150 4750
Wire Wire Line
	1150 4750 1250 4750
Connection ~ 1150 4750
Wire Wire Line
	1150 4750 1150 4850
Wire Wire Line
	1250 4850 1150 4850
Connection ~ 1150 4850
Wire Wire Line
	1150 4850 1150 4950
Wire Wire Line
	1150 4950 1250 4950
Connection ~ 1150 4950
Wire Wire Line
	1150 4950 1150 5050
Wire Wire Line
	1250 5050 1150 5050
Connection ~ 1150 5050
Wire Wire Line
	1150 5050 1150 5150
Wire Wire Line
	1150 5150 1250 5150
Connection ~ 1150 5150
Wire Wire Line
	1150 5150 1150 5250
Wire Wire Line
	1250 5250 1150 5250
Connection ~ 1150 5250
Wire Wire Line
	1150 5250 1150 5350
Wire Wire Line
	1150 5350 1250 5350
Connection ~ 1150 5350
Wire Wire Line
	1150 5350 1150 5450
NoConn ~ 1250 4350
NoConn ~ 1750 4250
Text Label 1800 4350 0    50   ~ 0
HEAD_LOAD
Text Label 1800 4450 0    50   ~ 0
DS3
Text Label 1800 4550 0    50   ~ 0
INDEX
Text Label 1800 4650 0    50   ~ 0
DS0
Text Label 1800 4750 0    50   ~ 0
DS1
Text Label 1800 4850 0    50   ~ 0
DS2
Text Label 1800 4950 0    50   ~ 0
M_ON
Text Label 1800 5050 0    50   ~ 0
DIR
Text Label 1800 5150 0    50   ~ 0
STEP
Text Label 1800 5250 0    50   ~ 0
WD
Text Label 1800 5350 0    50   ~ 0
WG
Text Label 1800 5450 0    50   ~ 0
TRK00
Text Label 1800 5550 0    50   ~ 0
WP
Text Label 1800 5650 0    50   ~ 0
RD
Text Label 1800 5750 0    50   ~ 0
SIDE1
Text Label 1800 5850 0    50   ~ 0
READY
$Comp
L Device:R R1
U 1 1 5F0DE3EB
P 2800 4550
F 0 "R1" V 2750 4750 50  0000 C CNN
F 1 "150" V 2800 4550 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0204_L3.6mm_D1.6mm_P7.62mm_Horizontal" V 2730 4550 50  0001 C CNN
F 3 "~" H 2800 4550 50  0001 C CNN
	1    2800 4550
	0    1    1    0   
$EndComp
Wire Wire Line
	3150 5650 3150 5450
Connection ~ 3150 5250
Connection ~ 3150 5350
Wire Wire Line
	3150 5350 3150 5250
Connection ~ 3150 5450
Wire Wire Line
	3150 5450 3150 5350
Wire Wire Line
	3150 4550 3150 5250
$Comp
L power:GND #PWR0101
U 1 1 5F1168A4
P 3250 5950
F 0 "#PWR0101" H 3250 5700 50  0001 C CNN
F 1 "GND" H 3255 5777 50  0000 C CNN
F 2 "" H 3250 5950 50  0001 C CNN
F 3 "" H 3250 5950 50  0001 C CNN
	1    3250 5950
	1    0    0    -1  
$EndComp
$Comp
L power:VCC #PWR0102
U 1 1 5F1171C8
P 3150 4350
F 0 "#PWR0102" H 3150 4200 50  0001 C CNN
F 1 "VCC" H 3165 4523 50  0000 C CNN
F 2 "" H 3150 4350 50  0001 C CNN
F 3 "" H 3150 4350 50  0001 C CNN
	1    3150 4350
	1    0    0    -1  
$EndComp
Wire Wire Line
	3150 4350 3150 4550
Connection ~ 3150 4550
$Comp
L Jumper:SolderJumper_2_Bridged JP2
U 1 1 5F11CFCC
P 2800 4650
F 0 "JP2" H 3000 4700 50  0000 C CNN
F 1 "SolderJumper_2_Bridged" H 3400 4600 50  0001 C CNN
F 2 "Jumper:SolderJumper-2_P1.3mm_Bridged_Pad1.0x1.5mm" H 2800 4650 50  0001 C CNN
F 3 "~" H 2800 4650 50  0001 C CNN
	1    2800 4650
	1    0    0    -1  
$EndComp
Wire Wire Line
	3250 4450 3250 4650
Connection ~ 3250 4750
Wire Wire Line
	3250 4750 3250 4850
Connection ~ 3250 4650
Wire Wire Line
	3250 4650 3250 4750
Wire Wire Line
	3250 4850 3250 5950
Connection ~ 3250 4850
Wire Wire Line
	2950 5650 3150 5650
Wire Wire Line
	2950 5450 3150 5450
Wire Wire Line
	2950 5350 3150 5350
Wire Wire Line
	2950 5250 3150 5250
Wire Wire Line
	2950 4450 3250 4450
Wire Wire Line
	2950 4550 3150 4550
Wire Wire Line
	2950 4650 3250 4650
Wire Wire Line
	2950 4750 3250 4750
Wire Wire Line
	2950 4850 3250 4850
$Comp
L power:GND #PWR0103
U 1 1 5F1897E2
P 1150 5950
F 0 "#PWR0103" H 1150 5700 50  0001 C CNN
F 1 "GND" H 1155 5777 50  0000 C CNN
F 2 "" H 1150 5950 50  0001 C CNN
F 3 "" H 1150 5950 50  0001 C CNN
	1    1150 5950
	1    0    0    -1  
$EndComp
Wire Wire Line
	2300 5650 2300 3900
Wire Wire Line
	2300 5650 1750 5650
Wire Wire Line
	5600 3200 5600 3000
Wire Wire Line
	6250 2100 6350 2100
Wire Wire Line
	6200 3100 6300 3100
Wire Wire Line
	6650 2350 6650 2450
Wire Wire Line
	6650 2450 6250 2450
Wire Wire Line
	6250 2450 6250 3450
Wire Wire Line
	6600 3350 6600 3450
Wire Wire Line
	6600 3450 6250 3450
Connection ~ 6250 3450
Wire Wire Line
	6250 3450 6250 3700
Text Label 3500 3700 0    50   ~ 0
CAP_EN
Wire Wire Line
	3250 3600 4700 3600
Wire Wire Line
	3250 2500 3250 3600
Wire Wire Line
	5550 2500 5550 2200
Wire Wire Line
	5550 2200 5650 2200
Wire Wire Line
	4200 2800 4750 2800
$Comp
L power:VCC #PWR0106
U 1 1 5F228AC5
P 4750 2750
F 0 "#PWR0106" H 4750 2600 50  0001 C CNN
F 1 "VCC" H 4765 2923 50  0000 C CNN
F 2 "" H 4750 2750 50  0001 C CNN
F 3 "" H 4750 2750 50  0001 C CNN
	1    4750 2750
	1    0    0    -1  
$EndComp
Wire Wire Line
	4750 2750 4750 2800
Connection ~ 4750 2800
$Comp
L Device:R R2
U 1 1 5F23E320
P 2800 5250
F 0 "R2" V 2750 5450 50  0000 C CNN
F 1 "150" V 2800 5250 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0204_L3.6mm_D1.6mm_P7.62mm_Horizontal" V 2730 5250 50  0001 C CNN
F 3 "~" H 2800 5250 50  0001 C CNN
	1    2800 5250
	0    1    1    0   
$EndComp
$Comp
L Device:R R3
U 1 1 5F23E741
P 2800 5350
F 0 "R3" V 2750 5550 50  0000 C CNN
F 1 "150" V 2800 5350 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0204_L3.6mm_D1.6mm_P7.62mm_Horizontal" V 2730 5350 50  0001 C CNN
F 3 "~" H 2800 5350 50  0001 C CNN
	1    2800 5350
	0    1    1    0   
$EndComp
$Comp
L Device:R R4
U 1 1 5F23E917
P 2800 5450
F 0 "R4" V 2750 5650 50  0000 C CNN
F 1 "150" V 2800 5450 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0204_L3.6mm_D1.6mm_P7.62mm_Horizontal" V 2730 5450 50  0001 C CNN
F 3 "~" H 2800 5450 50  0001 C CNN
	1    2800 5450
	0    1    1    0   
$EndComp
$Comp
L Device:R R5
U 1 1 5F23EBA7
P 2800 5650
F 0 "R5" V 2750 5850 50  0000 C CNN
F 1 "150" V 2800 5650 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0204_L3.6mm_D1.6mm_P7.62mm_Horizontal" V 2730 5650 50  0001 C CNN
F 3 "~" H 2800 5650 50  0001 C CNN
	1    2800 5650
	0    1    1    0   
$EndComp
$Comp
L Device:LED D1
U 1 1 5F23FA46
P 6750 1300
F 0 "D1" V 6789 1182 50  0000 R CNN
F 1 "LED" V 6698 1182 50  0000 R CNN
F 2 "LED_THT:LED_D3.0mm" H 6750 1300 50  0001 C CNN
F 3 "~" H 6750 1300 50  0001 C CNN
	1    6750 1300
	0    -1   -1   0   
$EndComp
$Comp
L power:VCC #PWR0108
U 1 1 5F24086A
P 6750 1050
F 0 "#PWR0108" H 6750 900 50  0001 C CNN
F 1 "VCC" H 6765 1223 50  0000 C CNN
F 2 "" H 6750 1050 50  0001 C CNN
F 3 "" H 6750 1050 50  0001 C CNN
	1    6750 1050
	1    0    0    -1  
$EndComp
$Comp
L Device:R R6
U 1 1 5F240D85
P 6500 1550
F 0 "R6" V 6450 1750 50  0000 C CNN
F 1 "470" V 6500 1550 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0204_L3.6mm_D1.6mm_P7.62mm_Horizontal" V 6430 1550 50  0001 C CNN
F 3 "~" H 6500 1550 50  0001 C CNN
	1    6500 1550
	0    1    1    0   
$EndComp
Wire Wire Line
	6750 1050 6750 1150
Wire Wire Line
	6750 1450 6750 1550
Wire Wire Line
	6750 1550 6650 1550
Wire Wire Line
	6350 1550 6250 1550
Wire Wire Line
	5450 1550 5650 1550
Connection ~ 5450 2000
Wire Wire Line
	5450 2000 5650 2000
Wire Wire Line
	7950 2650 8150 2650
Wire Wire Line
	8150 2650 8150 3100
Wire Wire Line
	8150 3100 7050 3100
Wire Wire Line
	7950 2550 8150 2550
Wire Wire Line
	8150 2550 8150 2100
Wire Wire Line
	8150 2100 6950 2100
Text Label 10200 1900 0    50   ~ 0
SS
Text Label 6750 2750 0    50   ~ 0
SS
$Comp
L power:VCC #PWR0109
U 1 1 5F2A19A6
P 7100 2000
F 0 "#PWR0109" H 7100 1850 50  0001 C CNN
F 1 "VCC" H 7115 2173 50  0000 C CNN
F 2 "" H 7100 2000 50  0001 C CNN
F 3 "" H 7100 2000 50  0001 C CNN
	1    7100 2000
	1    0    0    -1  
$EndComp
Wire Wire Line
	7100 2000 7100 2350
Wire Wire Line
	7150 2550 7100 2550
Wire Wire Line
	7550 2350 7100 2350
Connection ~ 7100 2350
Wire Wire Line
	7100 2350 7100 2550
Text Label 8250 2750 0    50   ~ 0
MISO
Text Label 10200 1700 0    50   ~ 0
MISO
Text Label 10200 1800 0    50   ~ 0
MOSI
Wire Wire Line
	7050 3100 7050 3000
Wire Wire Line
	7050 3000 7300 3000
Connection ~ 7050 3100
Wire Wire Line
	7050 3100 6900 3100
Text Label 7100 3000 0    50   ~ 0
MOSI
$Comp
L Device:C C1
U 1 1 5F32153A
P 6700 5700
F 0 "C1" H 6750 5800 50  0000 L CNN
F 1 "0.1u" H 6750 5600 50  0000 L CNN
F 2 "Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm" H 6738 5550 50  0001 C CNN
F 3 "~" H 6700 5700 50  0001 C CNN
	1    6700 5700
	1    0    0    -1  
$EndComp
$Comp
L Device:C C2
U 1 1 5F32F044
P 6950 5700
F 0 "C2" H 7000 5800 50  0000 L CNN
F 1 "0.1u" H 7000 5600 50  0000 L CNN
F 2 "Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm" H 6988 5550 50  0001 C CNN
F 3 "~" H 6950 5700 50  0001 C CNN
	1    6950 5700
	1    0    0    -1  
$EndComp
$Comp
L Device:C C3
U 1 1 5F32F240
P 7200 5700
F 0 "C3" H 7250 5800 50  0000 L CNN
F 1 "0.1u" H 7250 5600 50  0000 L CNN
F 2 "Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm" H 7238 5550 50  0001 C CNN
F 3 "~" H 7200 5700 50  0001 C CNN
	1    7200 5700
	1    0    0    -1  
$EndComp
$Comp
L Device:C C4
U 1 1 5F32F43D
P 7450 5700
F 0 "C4" H 7500 5800 50  0000 L CNN
F 1 "0.1u" H 7500 5600 50  0000 L CNN
F 2 "Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm" H 7488 5550 50  0001 C CNN
F 3 "~" H 7450 5700 50  0001 C CNN
	1    7450 5700
	1    0    0    -1  
$EndComp
$Comp
L power:VCC #PWR0112
U 1 1 5F33A5C5
P 8300 5150
F 0 "#PWR0112" H 8300 5000 50  0001 C CNN
F 1 "VCC" H 8315 5323 50  0000 C CNN
F 2 "" H 8300 5150 50  0001 C CNN
F 3 "" H 8300 5150 50  0001 C CNN
	1    8300 5150
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR0113
U 1 1 5F33AE9E
P 8250 6250
F 0 "#PWR0113" H 8250 6000 50  0001 C CNN
F 1 "GND" H 8255 6077 50  0000 C CNN
F 2 "" H 8250 6250 50  0001 C CNN
F 3 "" H 8250 6250 50  0001 C CNN
	1    8250 6250
	1    0    0    -1  
$EndComp
Wire Wire Line
	9250 6200 8800 6200
Connection ~ 8800 6200
Wire Wire Line
	8250 6250 8250 6200
Wire Wire Line
	8250 6200 7900 6200
Wire Wire Line
	7900 6200 7900 6100
Connection ~ 8250 6200
Wire Wire Line
	7900 6200 7450 6200
Wire Wire Line
	6700 6200 6700 5850
Connection ~ 7900 6200
Wire Wire Line
	6950 5850 6950 6200
Connection ~ 6950 6200
Wire Wire Line
	6950 6200 6700 6200
Wire Wire Line
	7200 5850 7200 6200
Connection ~ 7200 6200
Wire Wire Line
	7200 6200 6950 6200
Wire Wire Line
	7450 5850 7450 6200
Connection ~ 7450 6200
Wire Wire Line
	7450 6200 7200 6200
Wire Wire Line
	8300 5150 8300 5200
Connection ~ 8800 5200
Wire Wire Line
	8800 5200 9250 5200
Wire Wire Line
	7900 5200 7900 5300
Wire Wire Line
	6700 5200 6700 5550
Connection ~ 7900 5200
Wire Wire Line
	6950 5550 6950 5200
Wire Wire Line
	6700 5200 6950 5200
Connection ~ 6950 5200
Wire Wire Line
	6950 5200 7200 5200
Wire Wire Line
	7200 5200 7200 5550
Connection ~ 7200 5200
Wire Wire Line
	7200 5200 7300 5200
Wire Wire Line
	7450 5550 7450 5200
Connection ~ 7450 5200
Wire Wire Line
	7450 5200 7900 5200
Wire Wire Line
	7900 5200 8300 5200
Connection ~ 8300 5200
Wire Wire Line
	10300 6150 10300 5950
Connection ~ 10300 5950
Connection ~ 10300 5650
Wire Wire Line
	10300 5650 10300 5950
Connection ~ 10300 5450
Wire Wire Line
	10300 5450 10300 5650
Connection ~ 9250 5200
NoConn ~ 10900 5550
NoConn ~ 10900 6050
Text Label 10200 2400 0    50   ~ 0
HEAD_LOAD
Text Label 9050 2500 0    50   ~ 0
INDEX
Text Label 4750 2000 0    50   ~ 0
CAP_ACTIVE
Text Label 9050 2600 0    50   ~ 0
CAP_ACTIVE
Text Label 9050 2700 0    50   ~ 0
READY
Text Label 9050 2800 0    50   ~ 0
TRK00
Text Label 10200 2800 0    50   ~ 0
WP
Text Label 10200 2600 0    50   ~ 0
CAP_RST
Text Label 10200 2700 0    50   ~ 0
CAP_EN
Wire Wire Line
	3350 3700 6250 3700
Text Label 10200 2000 0    50   ~ 0
STEP
Text Label 10200 2100 0    50   ~ 0
DIR
Text Label 10200 2300 0    50   ~ 0
M_ON
Text Label 10200 2500 0    50   ~ 0
SIDE1
Wire Wire Line
	1750 4350 2150 4350
Wire Wire Line
	1750 4950 2150 4950
Wire Wire Line
	1750 5050 2150 5050
Wire Wire Line
	1750 5150 2150 5150
Wire Wire Line
	1750 5550 2150 5550
Wire Wire Line
	1750 5750 2150 5750
Wire Wire Line
	1750 5850 2150 5850
NoConn ~ 5300 3200
$Comp
L power:PWR_FLAG #FLG0101
U 1 1 5F603339
P 7300 5100
F 0 "#FLG0101" H 7300 5175 50  0001 C CNN
F 1 "PWR_FLAG" H 7300 5273 50  0000 C CNN
F 2 "" H 7300 5100 50  0001 C CNN
F 3 "~" H 7300 5100 50  0001 C CNN
	1    7300 5100
	1    0    0    -1  
$EndComp
Wire Wire Line
	7300 5100 7300 5200
Connection ~ 7300 5200
Wire Wire Line
	7300 5200 7450 5200
$Comp
L power:VCC #PWR0114
U 1 1 5F613858
P 8800 1350
F 0 "#PWR0114" H 8800 1200 50  0001 C CNN
F 1 "VCC" V 8815 1523 50  0000 C CNN
F 2 "" H 8800 1350 50  0001 C CNN
F 3 "" H 8800 1350 50  0001 C CNN
	1    8800 1350
	1    0    0    -1  
$EndComp
Wire Wire Line
	8800 1350 8800 1650
Wire Wire Line
	8800 1650 8950 1650
Connection ~ 8950 1650
Wire Wire Line
	8950 1650 8950 1350
Wire Wire Line
	7550 2950 7550 3150
$Comp
L power:PWR_FLAG #FLG0102
U 1 1 5F654F0A
P 6450 6150
F 0 "#FLG0102" H 6450 6225 50  0001 C CNN
F 1 "PWR_FLAG" H 6450 6323 50  0000 C CNN
F 2 "" H 6450 6150 50  0001 C CNN
F 3 "~" H 6450 6150 50  0001 C CNN
	1    6450 6150
	1    0    0    -1  
$EndComp
Wire Wire Line
	6450 6150 6450 6200
Wire Wire Line
	6450 6200 6700 6200
Connection ~ 6700 6200
NoConn ~ 10200 1400
NoConn ~ 10200 2900
NoConn ~ 10200 3000
Text Label 10200 1600 0    50   ~ 0
SCK
NoConn ~ 9400 2300
NoConn ~ 9400 1800
NoConn ~ 9400 1700
$Comp
L power:PWR_FLAG #FLG0103
U 1 1 5F7611CC
P 9250 1350
F 0 "#FLG0103" H 9250 1425 50  0001 C CNN
F 1 "PWR_FLAG" V 9250 1650 50  0000 C CNN
F 2 "" H 9250 1350 50  0001 C CNN
F 3 "~" H 9250 1350 50  0001 C CNN
	1    9250 1350
	1    0    0    -1  
$EndComp
Wire Wire Line
	9250 1350 9250 1450
Wire Wire Line
	9250 1450 9100 1450
Connection ~ 9100 1450
Wire Wire Line
	9100 1450 9100 1350
Wire Wire Line
	8150 2100 8150 1850
Wire Wire Line
	8150 1850 7700 1850
Connection ~ 8150 2100
Text Label 7700 1850 0    50   ~ 0
SCK
Wire Wire Line
	10200 2700 10550 2700
Wire Wire Line
	10200 2800 10550 2800
NoConn ~ 10200 1200
NoConn ~ 10200 1300
Text Label 9050 2900 0    50   ~ 0
CAP_HOLD
Text Label 6750 2650 0    50   ~ 0
CAP_HOLD
Wire Wire Line
	6750 2650 7150 2650
Wire Wire Line
	6750 2750 7150 2750
$Comp
L power:GND #PWR0111
U 1 1 5F2CA4B8
P 7550 3150
F 0 "#PWR0111" H 7550 2900 50  0001 C CNN
F 1 "GND" H 7555 2977 50  0000 C CNN
F 2 "" H 7550 3150 50  0001 C CNN
F 3 "" H 7550 3150 50  0001 C CNN
	1    7550 3150
	1    0    0    -1  
$EndComp
$Comp
L 74xx:74HC04 U6
U 4 1 5F195538
P 5950 1550
F 0 "U6" H 5950 1867 50  0000 C CNN
F 1 "74HCU04" H 6150 1650 50  0000 C CNN
F 2 "Package_DIP:DIP-14_W7.62mm" H 5950 1550 50  0001 C CNN
F 3 "https://assets.nexperia.com/documents/data-sheet/74HC_HCT04.pdf" H 5950 1550 50  0001 C CNN
	4    5950 1550
	1    0    0    -1  
$EndComp
$Comp
L 74xx:74HC04 U6
U 5 1 5F1961F8
P 2050 2500
F 0 "U6" H 2050 2817 50  0000 C CNN
F 1 "74HCU04" H 2250 2600 50  0000 C CNN
F 2 "Package_DIP:DIP-14_W7.62mm" H 2050 2500 50  0001 C CNN
F 3 "https://assets.nexperia.com/documents/data-sheet/74HC_HCT04.pdf" H 2050 2500 50  0001 C CNN
	5    2050 2500
	1    0    0    -1  
$EndComp
$Comp
L 74xx:74HC04 U6
U 6 1 5F198307
P 1350 2500
F 0 "U6" H 1350 2817 50  0000 C CNN
F 1 "74HCU04" H 1550 2600 50  0000 C CNN
F 2 "Package_DIP:DIP-14_W7.62mm" H 1350 2500 50  0001 C CNN
F 3 "https://assets.nexperia.com/documents/data-sheet/74HC_HCT04.pdf" H 1350 2500 50  0001 C CNN
	6    1350 2500
	1    0    0    -1  
$EndComp
$Comp
L 74xx:74HC04 U6
U 7 1 5F198CAC
P 9700 5700
F 0 "U6" H 9750 5350 50  0000 L CNN
F 1 "74HCU04" H 9750 6050 50  0000 L CNN
F 2 "Package_DIP:DIP-14_W7.62mm" H 9700 5700 50  0001 C CNN
F 3 "https://assets.nexperia.com/documents/data-sheet/74HC_HCT04.pdf" H 9700 5700 50  0001 C CNN
	7    9700 5700
	1    0    0    -1  
$EndComp
Connection ~ 9700 5200
Wire Wire Line
	9700 5200 10300 5200
Wire Wire Line
	9250 6200 9700 6200
Connection ~ 9250 6200
Text Label 2800 2500 0    50   ~ 0
CAP_CLK
$Comp
L 74xx:74HC04 U6
U 1 1 5F18FCB3
P 2750 3900
F 0 "U6" H 2200 4050 50  0000 C CNN
F 1 "74HCU04" H 2300 3950 50  0000 C CNN
F 2 "Package_DIP:DIP-14_W7.62mm" H 2750 3900 50  0001 C CNN
F 3 "https://assets.nexperia.com/documents/data-sheet/74HC_HCT04.pdf" H 2750 3900 50  0001 C CNN
	1    2750 3900
	1    0    0    -1  
$EndComp
$Comp
L 74xx:74LS125 U4
U 3 1 5F07EB64
P 9700 4650
F 0 "U4" H 9700 4967 50  0000 C CNN
F 1 "74LS125" H 9700 4876 50  0000 C CNN
F 2 "Package_DIP:DIP-14_W7.62mm" H 9700 4650 50  0001 C CNN
F 3 "http://www.ti.com/lit/gpn/sn74LS125" H 9700 4650 50  0001 C CNN
	3    9700 4650
	1    0    0    -1  
$EndComp
Wire Wire Line
	3350 3500 4200 3500
Wire Wire Line
	4750 2000 5450 2000
Wire Wire Line
	9250 5200 9400 5200
Connection ~ 9400 5200
Wire Wire Line
	9400 5200 9700 5200
Wire Wire Line
	4750 2800 5000 2800
$Comp
L 74xx:74LS74 U1
U 1 1 5F137465
P 5000 3100
F 0 "U1" H 4750 3350 50  0000 C CNN
F 1 "74LS74" H 5200 3350 50  0000 C CNN
F 2 "Package_DIP:DIP-14_W7.62mm" H 5000 3100 50  0001 C CNN
F 3 "74xx/74hc_hct74.pdf" H 5000 3100 50  0001 C CNN
	1    5000 3100
	1    0    0    -1  
$EndComp
Wire Wire Line
	5300 3000 5600 3000
Connection ~ 5600 3000
Connection ~ 3250 2500
Wire Wire Line
	3250 2500 5550 2500
Wire Wire Line
	8300 5200 8800 5200
Wire Wire Line
	8250 6200 8800 6200
Text Label 3500 3500 0    50   ~ 0
CAP_RST
Text Label 4300 3500 0    50   ~ 0
CAP_RST
Wire Wire Line
	1650 3550 1650 3450
Wire Wire Line
	1050 3450 1050 3550
Wire Wire Line
	1650 2500 1750 2500
Wire Wire Line
	1650 2750 1450 2750
Connection ~ 1650 2750
Wire Wire Line
	1650 2500 1650 2750
Wire Wire Line
	1650 2750 1650 3000
Wire Wire Line
	1650 3000 1650 3150
Connection ~ 1650 3000
Wire Wire Line
	1450 3000 1650 3000
Wire Wire Line
	1150 3000 1050 3000
Wire Wire Line
	1050 3000 1050 2750
Wire Wire Line
	1050 2750 1050 2500
Connection ~ 1050 2750
Wire Wire Line
	1050 2750 1150 2750
Connection ~ 1050 3000
Wire Wire Line
	1050 3150 1050 3000
$Comp
L power:GND #PWR06
U 1 1 5F26E889
P 1650 3550
F 0 "#PWR06" H 1650 3300 50  0001 C CNN
F 1 "GND" H 1850 3500 50  0000 C CNN
F 2 "" H 1650 3550 50  0001 C CNN
F 3 "" H 1650 3550 50  0001 C CNN
	1    1650 3550
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR05
U 1 1 5F26E389
P 1050 3550
F 0 "#PWR05" H 1050 3300 50  0001 C CNN
F 1 "GND" H 1200 3500 50  0000 C CNN
F 2 "" H 1050 3550 50  0001 C CNN
F 3 "" H 1050 3550 50  0001 C CNN
	1    1050 3550
	1    0    0    -1  
$EndComp
$Comp
L Device:C C6
U 1 1 5F26E048
P 1650 3300
F 0 "C6" H 1800 3300 50  0000 L CNN
F 1 "22p" H 1700 3200 50  0000 L CNN
F 2 "Capacitor_THT:C_Disc_D3.0mm_W1.6mm_P2.50mm" H 1688 3150 50  0001 C CNN
F 3 "~" H 1650 3300 50  0001 C CNN
	1    1650 3300
	1    0    0    -1  
$EndComp
$Comp
L Device:C C5
U 1 1 5F26D99B
P 1050 3300
F 0 "C5" H 1200 3300 50  0000 L CNN
F 1 "22p" H 1100 3200 50  0000 L CNN
F 2 "Capacitor_THT:C_Disc_D3.0mm_W1.6mm_P2.50mm" H 1088 3150 50  0001 C CNN
F 3 "~" H 1050 3300 50  0001 C CNN
	1    1050 3300
	1    0    0    -1  
$EndComp
$Comp
L Device:R R7
U 1 1 5F26D3F4
P 1300 2750
F 0 "R7" V 1250 2950 50  0000 C CNN
F 1 "1M" V 1300 2750 50  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0204_L3.6mm_D1.6mm_P7.62mm_Horizontal" V 1230 2750 50  0001 C CNN
F 3 "~" H 1300 2750 50  0001 C CNN
	1    1300 2750
	0    1    1    0   
$EndComp
$Comp
L Device:Crystal Y1
U 1 1 5F26CE1A
P 1300 3000
F 0 "Y1" H 1450 2950 50  0000 C CNN
F 1 "Crystal" H 1300 2850 50  0000 C CNN
F 2 "Crystal:Crystal_HC49-U_Vertical" H 1300 3000 50  0001 C CNN
F 3 "~" H 1300 3000 50  0001 C CNN
	1    1300 3000
	1    0    0    -1  
$EndComp
$Comp
L 74xx:74HC04 U6
U 3 1 5F193548
P 2750 3100
F 0 "U6" H 2200 3250 50  0000 C CNN
F 1 "74HCU04" H 2300 3150 50  0000 C CNN
F 2 "Package_DIP:DIP-14_W7.62mm" H 2750 3100 50  0001 C CNN
F 3 "https://assets.nexperia.com/documents/data-sheet/74HC_HCT04.pdf" H 2750 3100 50  0001 C CNN
	3    2750 3100
	1    0    0    -1  
$EndComp
Connection ~ 1650 2500
$Comp
L 74xx:74HC04 U6
U 2 1 5F19285B
P 2750 3500
F 0 "U6" H 2200 3650 50  0000 C CNN
F 1 "74HCU04" H 2300 3550 50  0000 C CNN
F 2 "Package_DIP:DIP-14_W7.62mm" H 2750 3500 50  0001 C CNN
F 3 "https://assets.nexperia.com/documents/data-sheet/74HC_HCT04.pdf" H 2750 3500 50  0001 C CNN
	2    2750 3500
	1    0    0    -1  
$EndComp
$Comp
L Jumper:SolderJumper_2_Bridged JP1
U 1 1 5F31DA36
P 2800 4450
F 0 "JP1" H 3000 4500 50  0000 C CNN
F 1 "SolderJumper_2_Bridged" H 3400 4400 50  0001 C CNN
F 2 "Jumper:SolderJumper-2_P1.3mm_Bridged_Pad1.0x1.5mm" H 2800 4450 50  0001 C CNN
F 3 "~" H 2800 4450 50  0001 C CNN
	1    2800 4450
	1    0    0    -1  
$EndComp
$Comp
L Jumper:SolderJumper_2_Bridged JP3
U 1 1 5F31E1DE
P 2800 4750
F 0 "JP3" H 3000 4800 50  0000 C CNN
F 1 "SolderJumper_2_Bridged" H 3400 4700 50  0001 C CNN
F 2 "Jumper:SolderJumper-2_P1.3mm_Bridged_Pad1.0x1.5mm" H 2800 4750 50  0001 C CNN
F 3 "~" H 2800 4750 50  0001 C CNN
	1    2800 4750
	1    0    0    -1  
$EndComp
$Comp
L Jumper:SolderJumper_2_Bridged JP4
U 1 1 5F31E80F
P 2800 4850
F 0 "JP4" H 3000 4900 50  0000 C CNN
F 1 "SolderJumper_2_Bridged" H 3400 4800 50  0001 C CNN
F 2 "Jumper:SolderJumper-2_P1.3mm_Bridged_Pad1.0x1.5mm" H 2800 4850 50  0001 C CNN
F 3 "~" H 2800 4850 50  0001 C CNN
	1    2800 4850
	1    0    0    -1  
$EndComp
Wire Wire Line
	2600 6800 2600 5350
Wire Wire Line
	2600 5350 1750 5350
Wire Wire Line
	1750 4450 2650 4450
Wire Wire Line
	1750 4550 2650 4550
Wire Wire Line
	1750 4650 2650 4650
Wire Wire Line
	1750 4750 2650 4750
Wire Wire Line
	1750 4850 2650 4850
Wire Wire Line
	1750 5450 2650 5450
Wire Wire Line
	2600 5350 2650 5350
Connection ~ 2600 5350
Wire Wire Line
	2300 5650 2650 5650
Connection ~ 2300 5650
Wire Wire Line
	1850 6700 1850 6800
Wire Wire Line
	7950 2750 8450 2750
Text Label 1250 6450 0    50   ~ 0
MISO
Wire Wire Line
	1250 6450 1550 6450
Wire Wire Line
	1250 6800 1850 6800
Text Label 1250 6800 0    50   ~ 0
WG_
Text Label 9050 3000 0    50   ~ 0
WG_
$Comp
L Jumper:SolderJumper_2_Open JP5
U 1 1 5F465A9C
P 2350 6800
F 0 "JP5" H 2350 6913 50  0000 C CNN
F 1 "SolderJumper_2_Open" H 2350 6914 50  0001 C CNN
F 2 "Jumper:SolderJumper-2_P1.3mm_Open_Pad1.0x1.5mm" H 2350 6800 50  0001 C CNN
F 3 "~" H 2350 6800 50  0001 C CNN
	1    2350 6800
	1    0    0    -1  
$EndComp
Wire Wire Line
	1750 5250 2500 5250
Wire Wire Line
	2500 6450 2500 5250
Connection ~ 2500 5250
Wire Wire Line
	2500 5250 2650 5250
Wire Wire Line
	2150 6450 2500 6450
Wire Wire Line
	2500 6800 2600 6800
Wire Wire Line
	10300 5200 10300 5450
Text Notes 7650 6900 0    98   ~ 0
2D/2DD FLOPPY DISK CAPTURE SHIELD
Text Notes 10600 7650 0    79   ~ 0
G
Wire Wire Line
	1850 6800 2200 6800
Connection ~ 1850 6800
Wire Wire Line
	2350 2500 3250 2500
Wire Wire Line
	9400 4650 9400 4900
Wire Wire Line
	9700 4900 9400 4900
Connection ~ 9400 4900
Wire Wire Line
	9400 4900 9400 5200
NoConn ~ 10000 4650
Wire Wire Line
	2450 3900 2300 3900
Wire Wire Line
	3050 3700 2300 3700
Wire Wire Line
	2300 3700 2300 3500
Wire Wire Line
	2300 3500 2450 3500
Wire Wire Line
	3050 3300 2300 3300
Wire Wire Line
	2300 3300 2300 3100
Wire Wire Line
	2300 3100 2450 3100
Wire Wire Line
	5450 2000 5450 1550
Wire Wire Line
	3050 3300 3050 3500
Wire Wire Line
	3050 3700 3050 3900
Wire Wire Line
	3050 3100 3900 3100
$EndSCHEMATC
