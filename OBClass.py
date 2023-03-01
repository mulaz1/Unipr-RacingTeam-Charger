import can
from canID import *

class OBClass:
    
    def __init__(self,CanBus,logging):
        self._canbus = CanBus
        self._logging = logging
    
    # Request to OBC Errors list
    def send_request_error(self):
        msg = can.Message(extended_id=False, arbitration_id=0x61B, data=[
                        0x80, 0x00, 0x06, 0x1D, 0x00, 0x00, 0x00, 0x00])
        try:     # send values to OBC
            self._canbus.send(msg)
        except Exception as e:
            print(e)

    # Sends message to seting charging parameter
    def Charger_parameters(self,volt, _current):
        voltage = 0
        current = 0
        voltage = int(volt * 10)
        current = int(_current * 10)

        # voltage mask
        VoltageUint81 = hex((voltage >> 8) & 0xFF)
        VoltageUint82 = hex(voltage & 0xFF)

        # current mask
        CurrentUint81 = hex((int(current) >> 8) & 0xFF)
        CurrentUint82 = hex(current & 0xFF)

        msg = can.Message(extended_id=False, arbitration_id=CTL_ID, data=[0x88, 0x00, 0xA4, int(
            VoltageUint81, 16), int(VoltageUint82, 16), int(CurrentUint81, 16), int(CurrentUint82, 16)])
        try:     # send values to OBC
            self._canbus.send(msg)
        except Exception as e:
            print(e)

    # Sends message to stop charging and disable OBC
    def stop_Charger(self):
        msg = can.Message(extended_id=False, arbitration_id=CTL_ID, data=[
                        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])  # enable and led off
        try:     # send values to BMS
            self._canbus.send(msg)
        except Exception as e:
            print(e)
