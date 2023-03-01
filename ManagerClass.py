import can 
from canID import *

class ManagerClass:


    def __init__(self,_canbus,logging):
        self.canbus = _canbus
        self._logging = logging
        self._batteryCellVoltage = 0.0
        self._voltageOut = 0.0
        self._batteryVoltage = 0.0
        self._currentOut = 0.0
        self._temperatureOBC = 0.0
        self._actualPowerIn = 0.0
        self._batteryCellVoltageMin = 0.0
        self._batteryTemperature = 0.0
        self._batteryTemperatureMiddle = 0.0
        self._Soc = 0.0
        self._error = 0.0
        
        self._noError = False  # no Failed error True = Ok False = Failed
        self._startButton = True  # Button Start charger True = OK,Start False = not Start
        self._noErrorLatch = False  # failure or a soft failure flag True = OK False = Failed
        self._finishCharge = False  # this variable go to True if charge is finish
        self._PrechargeFinish = False  # True = Precharge finish esle False = Not Finish
        self._acOk = False  # Ac status True = Ok False = Failed
        self._bulkOk = False

    # Manager message ad elaboration
    def manage_message(self):   
        
        for msg in self.canbus:
            #get BMS parameter
            if msg.arbitration_id == STAT_BATTERY:
                self._batteryVoltage = ((int(msg.data[1])*256) + int(msg.data[0])) * 0.1
                self._batteryCellVoltage = (int(msg.data[3])*256) + int(msg.data[2])
                self._batteryTemperature = ((int(msg.data[5])*256) + int(msg.data[4])) * 0.1
                self._batteryTemperatureMiddle = (
                    (int(msg.data[7])*256) + int(msg.data[6])) * 0.1

            #get BMS state
            if msg.arbitration_id == CONTACTOR_FEEDBACK:
                if(((msg.data[2] & 0xF0) >> 4) < 6):
                    return (9, 'BMS status != OK')
                
            ...

            #get BMS parameter
            if msg.arbitration_id == STAT_BATTERY2:  # get battery voltages cell min
                self._batteryCellVoltageMin = ((int(msg.data[1])*256) + int(msg.data[0]))
                self._Soc = ((int(msg.data[3])*256) + int(msg.data[2])) * 0.01

            #get OBC errors
            if msg.arbitration_id == OBC_FLTA:
                self._error = str(hex(msg.data[2]))

                if(msg.data[0] & 0xFF) == False:
                    # errore grave -> esci subito
                    if hex(msg.data[2]) == 0xAA or hex(msg.data[2]) == 0xA3 or hex(msg.data[2]) == 0xA9 or hex(msg.data[2]) == 0xAD:
                        return (3, str(msg.data[2]))
                    # warming: scrivilo in loggin ma  non fare nulla
                    elif hex(msg.data[2]) == 0xA4 or hex(msg.data[2]) == 0xA7:
                        self._logging.warning('Warning: OBC code warning:   ' + str(hex(msg.data[2])))
                    else:  # c'e' da uscire
                        self._logging.warning('Soft Error: OBC code soft error:  ' + str(hex(msg.data[2])))
                        return -1

            #get OBC parameter
            if msg.arbitration_id == ACT1_ID:
                self._voltageOut = (((int(msg.data[4])*256) + int(msg.data[5])) * 0.1)
                self._currentOut = (((int(msg.data[6])*256) + int(msg.data[7])) * 0.1)
                self._temperatureOBC = (
                    ((int(msg.data[2])*256) + int(msg.data[3]))*0.005188-40)

            #get OBC parameter
            if msg.arbitration_id == ACT2_ID:
                self._actualPowerIn = ((int(msg.data[2])*256) + int(msg.data[3])) * 0.01

            # checks Ac status & precharge OBC status
            if msg.arbitration_id == TST1:
                if(((msg.data[0] >> 7) & 1)):
                    self._acOk = True
                else:
                    self._acOk = False

                if(((msg.data[0] >> 6) & 1)):
                    self._PrechargeFinish = True
                else:
                    self._PrechargeFinish = False

            # checks if exist error
            if msg.arbitration_id == OBC_FLTA:  # if frame is FF FF FF FF FF FF FF FF is OK not error
                if((msg.data[1] & 0xFF) and (msg.data[2] & 0xFF) and (msg.data[3] & 0xFF) and (msg.data[4] & 0xFF) and (msg.data[5] & 0xFF) and (msg.data[6] & 0xFF) and (msg.data[7] & 0xFF)):
                    self._noError = True
                else:
                    self._noError = False
                    # print code error
                    self._logging.error("Code Error: " + str(hex(msg.data[2])) + ", page 31 manual\n")

            # checks Error Latch
            if msg.arbitration_id == STAT_ID:
                if((msg.data[0] >> 6) & 1) == False:
                    self._noErrorLatch = True
                else:
                    self._noErrorLatch = False

                if((msg.data[0]) & 1) == False:
                    self._bulkOk = True
                else:
                    self._bulkOk = False
            return 100

    def BatteryVoltage(self):  # return battery voltage
        return self._batteryVoltage


    def CellVoltage(self):  # return cells max voltage
        return self._batteryCellVoltage


    def BatteryTemperature(self):  # return max cells temperature
        return self._batteryTemperature


    def BatteryTemperatureMiddle(self):  # return middle cells temperature
        return self._batteryTemperatureMiddle


    def VoltageOutOBC(self):  # return Voltage out OBC
        return self._voltageOut


    def CurrentOutOBC(self):  # return Current out OBC
        return self._currentOut


    def CellVoltageMin(self):  # return min cells voltage
        return self._batteryCellVoltageMin


    def Soc(self):  # return SOC
        return self._Soc


    def OBCTemperature(self): #return OBC Temperature
        return self._temperatureOBC


    def PowerIn(self):    #return Power input 
        return self._actualPowerIn


    def Error(self):  #return Error
        return self._error


    def ACok(self):   #return state of AC
        return self._acOk


    def BulkOk(self): #return bulk status
        return self._bulkOk


    def NoError(self):    #return state of generic error
        return self._noError


    def NoErrorLatch(self):   #return state of persistent error
        return self._noErrorLatch


    def PrechargeFinish(self):    #return state of OBC precharge
        return self._PrechargeFinish
