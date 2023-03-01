
'''
Messages contents
Control Message Ctl Iout & Vout reference value, control bits 
Values 1 Act1 Actual values measured from the OBC
Values 2 Act2 Actual values of power and AC current Limit 
Diagnostic Tst1 Real Time Diagnostic
Status Stat Status of OBC


Contactors Feedback Mask
    Bit 0 byte 0 negative contactor
    Bit 1 byte 0 positive contactor

Contactors Command Mask
    Bit 0 Byte 0 negative contanctor close/open (0 open/1 close)
    Bit 1 Byte 0 positive contactor close/open (0 open/1 close)

Voltages Mask
    byte 0 e 1 Battery Voltage
    byte 2 e 3 cell and cell max voltage

'''
# IDs Canbus
'''
CTL messages  (every 100ms)
example  Can_enable Ac_Max_current DC_Max_Voltage DC_Max_Current ->  (Vmax = Vout x 10) (Imax = Iout x 10) 80 00 A0 0E 10 00 AA 0x80 = Ctl.CanEnable enabled ; IacMaxset = 0x00A0 = 16A , Vout = 0x0E10 = 360V, Iout = 0x00AA = 17 A 

. Can Enable 80 Enable or 0 No enable
. AC MAX Current
. DC MAX Current
. DC MAX Voltages
'''
CTL_ID = 0X618

'''
ACT1 messages

. DC Output Current
. DC Output Voltage VOut DC Output Voltage
'''
ACT1_ID = 0x611

'''
STAT messages

. Charger Enable Status
. Charger Failure
'''
STAT_ID = 0x610

'''
TST1 messages

. hard-Failure
. Status
. AC ok status
. Temp Temperature over Power Stage
'''
TST1 = 0x615

'''
OBC Falts

. ltA Fault Active message
. Flt.codeerror
'''
OBC_FLTA = 0x61D

'''
ACT2 message

.AC Power

'''
ACT2_ID = 0x614

# BMS Contactors
CONTACTOR_FEEDBACK = 0x140  # comamand feedback
BMS_CON_COMMAND = 0x10  # command open and close

# BMS Faults
FAULT_BMS = 0x00

# BMS Status Battery
'''
State battery
. Battery Voltage
. Max Cell voltage
'''
STAT_BATTERY = 0x101

'''
State battery 
Min cell Voltage
'''
STAT_BATTERY2 = 0x102

'''
Temperature
'''
TEMPERATURES = 0x130