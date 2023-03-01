import can
from parameter import *
from canID import *

class BMSClass:
    def __init__(self,canInterface,logging):
        self._canbus = canInterface
        self._logging = logging

    '''
    first byte: 
        bit 0 -> Contactor command -> 1 contactors close; 0 contactors open
        bit 1 -> Balancing -> 1 Balancing ON; 0 balancing OFF
        bit 2 -> Fun control -> 1 Fan ON, 0 Fan OFF
        bit 3 -> Manual Balacing ->  1 manual balancing ON, 0 manual balancing OFF
    '''

    #Closes the contactors and verifies their proper operation
    def openContactor(self):
        msg = can.Message(extended_id=False, arbitration_id=BMS_CON_COMMAND, data=[
                        0x04, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        try:
            self._canbus.send(msg)
        except Exception as e:
            print("Error no command", e)
            self._logging.error("Error no command" + e, exc_info=True) #passalo di la e metti il return per vedere cosa stampare
        try:
            msg_confirm = self._canbus.recv(timeout=5)
            resp = False
            while(resp == False):
                msg_confirm = self._canbus.recv(timeout=5)
                if msg_confirm.arbitration_id == CONTACTOR_FEEDBACK:
                    if(((msg_confirm.data[2] & 0xF0) >> 4) == 0):
                        if parameter.DEBUG:
                            print(msg_confirm.data, "-",
                                msg_confirm.arbitration_id)
                        self._logging.info("Contactors Close")
                        resp = True
                    else:
                        if parameter.DEBUG:
                            print("Error:contactors not close yet")
                            print("Precharge State : %d",
                                ((msg_confirm.data[2] & 0xF0) >> 4))
                        msg = can.Message(extended_id=False, arbitration_id=BMS_CON_COMMAND, data=[
                                        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
                        try:
                            self._canbus.send(msg)
                        except Exception as e:
                            print("Error no command", e)
                            self._logging.error("Error no command" + e, exc_info=True)

        except Exception as e:
            if parameter.DEBUG:
                print(e)
            self._logging.error("Error: contactors not close", exc_info=True)

    #Opens the contactors and verifies their proper operation
    def closeContactor(self):
            msg = can.Message(extended_id=False, arbitration_id=BMS_CON_COMMAND, data=[
                    0x05, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
            try:
                self._canbus.send(msg)
            
            except Exception as e:
                print("Error no command", e)
                self._logging.error("Error no command Negative Contactor" + e, exc_info=True)
            try:
                msg_confirm = self._canbus.recv(timeout=5)
                resp = False
                while(resp == False):
                    msg_confirm = self._canbus.recv(timeout=5)
                    if msg_confirm.arbitration_id == CONTACTOR_FEEDBACK:
                        if(((msg_confirm.data[2] & 0xF0) >> 4) == 6):
                            if DEBUG:
                                print(msg_confirm.data, "-",
                                        msg_confirm.arbitration_id)
                            self._logging.info("Contactors Close")
                            resp = True
                        else:
                            if DEBUG:
                                print("Error:contactors not close yet")
                            self._logging.warning("Precharge State : %d",((msg_confirm.data[2] & 0xF0) >> 4))
                            if DEBUG:
                                print("Precharge State : %d",
                                    ((msg_confirm.data[2] & 0xF0) >> 4))
                            msg = can.Message(extended_id=False, arbitration_id= BMS_CON_COMMAND, data=[
                                            0x05, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
                            try:
                                self._canbus.send(msg)
                            except Exception as e:
                                print("Error no command", e)
                                self._logging.error("Error no command" + e, exc_info=True)

            except Exception as e:
                print(e)
                self._logging.error("Error: contactors not close", exc_info=True)

    # Safety message for the BMS (within 600ms); this message mantain contacor close
    def send_bms_state_close(self):
        msg = can.Message(extended_id=False, arbitration_id= BMS_CON_COMMAND, data=[
                        0x05, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        try:    # send values to BMS
            self._canbus.send(msg)

        except Exception as e:
                print(e)

    # Safety message for the BMS (within 600ms); this message mantain contacor open
    def send_bms_state_open(self):
        msg = can.Message(extended_id=False, arbitration_id= BMS_CON_COMMAND, data=[
                        0x04, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        try:     # send values to BMS
            self._canbus.send(msg)

        except Exception as e:
            print(e)

