import can  # python-can
import logging
import time
from parameter import *
import datetime
from BMSClass import BMSClass as BMS
from ManagerClass import ManagerClass as Manager
from OBClass import OBClass as OBC

try:
    # logging page config
    logging.basicConfig(filename='/home/pi/charger/dashboard/Charger.log', filemode='w',
                        level=logging.INFO, format='[%(asctime)s] - %(levelname)s - %(message)s\n')
    logging.info("CANBUS init")

except Exception as e:
    print(str(e))

try:
    CanBus = can.interface.Bus(
        bustype='socketcan', channel='can0', receive_own_messages=True, bitrate=250000)
    logging.info("Initializing CANbus")
    if DEBUG:
        print('Initializing CANbus')

except Exception as e:
    print(str(e))
    if DEBUG:
        print("interfaccia can non inizializzata")

bms = BMS(CanBus,logging) #crea un istanza di BMS
manager = Manager(CanBus,logging) #crea classe per fare cose
obc = OBC(CanBus,logging)

def incremetTime():
    #timeMinute = timeMinute + 1
    pass

def printTime():
    return str(datetime.timedelta(seconds=timeMinute))
    # return str(0)