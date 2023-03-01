import time
import datetime
import csv
import os.path
import os
import signal
from gpiozero import Button
from parameter import *
from data import *

# def button_callback():
#     if DEBUG:
#         print("button clicked!")
#     os.kill(os.getpid(), signal.SIGINT)

def SecondsToDatatime(sec): 
    return str(datetime.timedelta(seconds=sec))

def ChargingAlgorithm():
    
    if DEBUG:
        print("Charging start")
    logging.info("Charging start")
    timenow = time.time() * 1000  # set millisecond now
    maintime = time.time() * 1000  # set millisecond to send value
    sendtime = time.time() * 1000  # set millisecond
    safetytime = time.time() * 1000  # set millisecond to security

    countMaxVoltage = 0  # counter max error cells voltage
    countMaxCell = 0  # counter max error cells voltage
    countMaxTemperature = 0  # counter max error temperature value
    countCurrentLow = 0  # counter current low

    BATTERY_STAGE_1 = True

    actualCurrent = COSTANT_CURRENT

    while 1:
        if (timenow % 10) == 0:
            # funzione che riceve e spacchetta tutti i messaggi sul can
            returnDataMessage = manager.manage_message()
            if returnDataMessage[0] != 0:
                return(returnDataMessage[0], str(returnDataMessage[1]))

            # controllo lo stato del bottone
            if buttonStateSwitch.is_pressed == False:  # In qualsiasi momento della carica quando l'interruttore va in posizione di off --> la carica si ferma e i contattori si aprono
                return(10, 'Stop charger')

            # if charge current is down of 0,1 A for more that 1s exit to charge with error
            if(((time.time() * 1000) - safetytime) >= 1000):
                if (actualCurrent - manager.CurrentOutOBC()) >= 0.5:
                    if(countCurrentLow > COUNTERROR):
                        return(5, 'Corrente troppo bassa')
                    else:
                        countCurrentLow = countCurrentLow + 1

            # controllo che la carica non vada oltre il tempo limite
            if(((time.time() * 1000) - safetytime) >= (TIMEOUT*3600000)):
                return(7, 'Charge Timeout')

            # controllo che la tensione di partenza non sia maggiore di 4050 perche' altrimenti diventerebbe pericoloso
            # if manager.CellVoltage() > 4050 and ((time.time() * 1000) - safetytime) <= 1000:
            #     actualCurrent = 2

            # send param and fault error request every 100 ms
            if(((time.time() * 1000) - maintime) >= 100):
                obc.Charger_parameters(VOLTAGE_MAX, actualCurrent)
                bms.send_bms_state_close()
                maintime = time.time() * 1000

            # controllo la tensione totale della batteria
            if manager.BatteryVoltage() > VOLTAGE_MAX:
                countMaxVoltage = countMaxVoltage + 1
                if(countMaxVoltage > COUNTERROR):
                    logging.error("Voltage over max value")
                    return (1, str(manager.BatteryVoltage()))

            # controllo la tensione della cella massima
            if(manager.CellVoltage() > VOLTAGE_MAX_CELL):
                countMaxCell = countMaxCell + 1
                if(countMaxCell > COUNTERROR):
                    logging.error("cells voltage over max value")
                    return (2, str(manager.CellVoltage()))

            # controllo la temperatura della cella massima
            if manager.BatteryTemperature() > MAX_TEMPERATURE_BAT:
                if manager.BatteryTemperatureMiddle() > MAX_TEMPERATURE_BAT:
                    countMaxTemperature = countMaxTemperature + 1
                    if(countMaxTemperature > COUNTERROR):
                        logging.error(
                            "Temperature battery over max value")
                        return (8, str(manager.BatteryTemperature()))

            # se la cella e' arrivata al valore di targer allora inizia la fase CV
            if manager.CellVoltage() > VOLTAGE_CELL_REF:
                if(BATTERY_STAGE_1 == True):
                    BATTERY_STAGE_1 = False

            # CV stage in this phase the current is decremented by 0.1A when the maximum cell voltage reaches the target voltage
            if(BATTERY_STAGE_1 == False):
                if(((time.time()*1000) - timenow) >= 100):  # every 100ms
                    if manager.CellVoltage() > VOLTAGE_CELL_REF:
                        actualCurrent = actualCurrent - K
                        if actualCurrent > 0.1 or manager.CurrentOutOBC() > 0.1:
                            if DEBUG:
                                print("ACTUAL CURRENT:  " + str(actualCurrent))
                            obc.Charger_parameters(VOLTAGE_MAX, actualCurrent)
                        else:
                            if DEBUG:
                                print('charge finish')
                            obc.stop_Charger()
                            return (0, 'finish charge')
                    timenow = time.time() * 1000


            if ((time.time()*1000) - sendtime) >= 1000:  # every 1s

                timeMinute = timeMinute + 1    #increment seconds to stamp and timer 
                if DEBUG:  # for debug
                    print("\n")
                    print("Voltage:     " + str(manager.BatteryVoltage()))
                    print("Max cells Voltage:   " +
                        str(manager.CellVoltage()))
                    print("Min cells Voltage:   " +
                        str(manager.CellVoltageMin()))
                    print("Batery Temperature:   " +
                        str(manager.BatteryTemperature()))
                    print("Battery Temperature Middle" +
                        str(manager.BatteryTemperatureMiddle()))
                    print("VoltageOut :     " + str(manager.VoltageOutOBC()))
                    print("CurrentOut :     " + str(manager.CurrentOutOBC()))
                    print("OBC Temperature:     " +
                        str(manager.OBCTemperature()))
                    print("AC Power:    " + str(manager.PowerIn()))
                    print("time:    " + SecondsToDatatime(timeMinute))

                # Aggiungo ai file CSV i nuovi parametri da utilizzare per la GUI

                with open("/home/pi/charger/dashboard/voltages.csv", "a", newline='') as voltages_file:
                    fields = ['battery_voltage', 'cells_voltage',
                            'VoltageOut', 'time', 'min_cells_voltage', 'end']
                    dashboard = csv.DictWriter(
                        voltages_file, fieldnames=fields)
                    if(os.path.getsize("/home/pi/charger/dashboard/voltages.csv") == 0):
                        dashboard.writeheader()
                    dashboard.writerow({'battery_voltage': str(manager.BatteryVoltage()), 'cells_voltage':  str(manager.CellVoltage()), 'VoltageOut': str(
                        manager.VoltageOutOBC()), 'time': SecondsToDatatime(timeMinute), 'min_cells_voltage': str(manager.CellVoltageMin()), 'end': str(0)})
                    voltages_file.close()

                with open('/home/pi/charger/dashboard/current.csv', 'a', newline='') as current_file:
                    fields = ['currentOut', 'time', 'end']
                    dashboard = csv.DictWriter(current_file, fieldnames=fields)
                    if(os.path.getsize("/home/pi/charger/dashboard/current.csv") == 0):
                        dashboard.writeheader()
                    dashboard.writerow({'currentOut': str(manager.CurrentOutOBC()), 'time':SecondsToDatatime(timeMinute), 'end': str(0)})
                    current_file.close()

                with open('/home/pi/charger/dashboard/parameter.csv', 'w', newline='') as parameter_file:
                    fields = ['Acstatus', 'OBC_temperature', 'AC_Power', 'Error',
                            'batteryTemperature', 'batteryTemperatureMiddle', 'bulk', 'time', 'SOC', 'end']
                    dashboard = csv.DictWriter(
                        parameter_file, fieldnames=fields)
                    dashboard.writeheader()
                    dashboard.writerow({'Acstatus': str(manager.ACok()), 'OBC_temperature': str(manager.OBCTemperature()), 'AC_Power': str(manager.PowerIn()), 'Error': str(manager.Error()), 'batteryTemperature': str(
                        manager.BatteryTemperature()), 'batteryTemperatureMddle': str(manager.BatteryTemperatureMiddle()), 'bulk': str(manager.BulkOk()), 'time': SecondsToDatatime(timeMinute), 'SOC': str(manager.Soc()), 'end': str(0)})
                    parameter_file.close()
                sendtime = time.time() * 1000
    return 0

buttonStateSwitch = Button(17)  # button GPIO mwnaging
buttonState = False
buttonStateok = False

timeMinute = 0

def main():
    try:
        try:
            # inizializza CSV file for voltages parameters
            if os.path.isfile('/home/pi/charger/dashboard/voltages.csv'):
                # cancella il file precedente e lo sostituisce con uno nuovo vuoto
                os.remove('/home/pi/charger/dashboard/voltages.csv')
            open('/home/pi/charger/dashboard/voltages.csv', 'w').close()
        except Exception as e:
            print(str(e))

        try:
            # inizializza CSV file for current param
            if os.path.isfile('/home/pi/charger/dashboard/current.csv'):
                os.remove('/home/pi/charger/dashboard/current.csv')
            open('/home/pi/charger/dashboard/current.csv', 'w').close()
        except Exception as e:
            print(str(e))

        try:
            # inizializza CSV file for general parameters
            if os.path.isfile('/home/pi/charger/dashboard/parameter.csv'):
                os.remove("/home/pi/charger/dashboard/parameter.csv")
            open('/home/pi/charger/dashboard/parameter.csv', 'w').close()
        except Exception as e:
            print(str(e))

        times = time.time() * 1000

        while(1):

            manager.manage_message()

            if buttonStateSwitch.is_pressed == False:  # se il bottone e' sullo stato off posso controllare lo stato altrimenti aspetto che vada in stato off; per ragione di sicurezza
                buttonStateok = True
                startButton = False

            if buttonStateSwitch.is_pressed == True and buttonStateok == True:  # leggo il bottone
                startButton = True
            else:
                startButton = False

            if((time.time() * 1000) - times) >= 100:  # ogni 100ms
                #Sends the command to prevent the OBC from going to standby, all parameters to 0
                obc.stop_Charger()
                obc.send_request_error()  #requests the errors of the OBC
                #Sends the command to prevent the BMS from going to standby, drive the bms with open contactors and fan on
                bms.send_bms_state_open()
                #reset timer
                times = time.time() * 1000

                with open("/home/pi/charger/dashboard/voltages.csv", "a", newline='') as voltages_file:
                    fields = ['battery_voltage', 'cells_voltage',
                            'VoltageOut', 'time', 'min_cells_voltage', 'end']
                    dashboard = csv.DictWriter(voltages_file, fieldnames=fields)
                    if(os.path.getsize("/home/pi/charger/dashboard/voltages.csv") == 0):
                        dashboard.writeheader()
                    dashboard.writerow({'battery_voltage': str(manager.BatteryVoltage()), 'cells_voltage':  str(manager.CellVoltage()), 'VoltageOut': str(
                        manager.VoltageOutOBC()), 'time': str(0), 'min_cells_voltage': str(manager.CellVoltageMin()), 'end': str(0)})
                    voltages_file.close()

                with open('/home/pi/charger/dashboard/parameter.csv', 'w', newline='') as parameter_file:
                    fields = ['Acstatus', 'OBC_temperature', 'AC_Power', 'Error',
                            'batteryTemperature', 'batteryTemperatureMiddle', 'bulk', 'time', 'SOC', 'end']
                    dashboard = csv.DictWriter(parameter_file, fieldnames=fields)
                    if(os.path.getsize("/home/pi/charger/dashboard/parameter.csv") == 0):
                        dashboard.writeheader()
                    dashboard.writerow({'Acstatus': str(manager.ACok()), 'OBC_temperature': str(manager.OBCTemperature()), 'AC_Power': str(manager.PowerIn()), 'Error': str(manager.Error()), 'batteryTemperature': str(
                        manager.BatteryTemperature()), 'batteryTemperatureMiddle': str(manager.BatteryTemperatureMiddle()), 'bulk': str(manager.BulkOk()), 'time': SecondsToDatatime(timeMinute), 'end': str(0)})
                    parameter_file.close()
                    timeBattery = time.time() * 1000

            # Se noErrorLatch e' in fault potrebbe essere un problema di bulk per cui controllare i collegamenti delle fasi e del neutro della trifase
            if DEBUG:
                print("ACok: " + str(manager.ACok()) + " startButton:  " + str(startButton) + " Errori:  " + str(manager.NoError()) + " ErrorLatch:  " + str(manager.NoErrorLatch()) + " PrechargeOBCFinish:  " + str(manager.PrechargeFinish()))
            
            if manager.ACok() and manager.NoError() and manager.NoErrorLatch() and manager.PrechargeFinish():
                if startButton:
                    bms.closeContactor()
                    if DEBUG:
                        print('START CHARGING')
                    state = ChargingAlgorithm()

                    if DEBUG:
                        print("Exit with:" + str(state[0]) + " value: " + str(state[1]))
                    if state[0] == 0:
                        if DEBUG:
                            logging.info("Succesfully: Charge finish")
                    if state[0] == 1: 
                        logging.critical("Error: Battery voltage over max:  " + str(state[1]))

                    if state[0] == 2:
                        logging.critical("Error: Max Cells voltage over max:    " + str(state[1]))

                    if state[0] == 3:
                        logging.critical("Error: OBC Active Error, code error: " + str(state[1]) + 'page 31 manual')

                    if state[0] == 4: 
                        logging.critical("Error: Ac Plug error")

                    if state[0] == 5:
                        logging.critical('Error: Charge Current Low')

                    if state[0] == 7: 
                        logging.warning('Warning: Duration of the charge beyond the time limit')
                    
                    if state[0] == 8: 
                        logging.critical('Temperature Over 60°C')

                    if state[0] == 9:
                        logging.critical("Error in BMS")
                    
                    if state[0] == 10:
                        logging.info("Stop charge")
                    break

    except Exception as e:
        print("\nAn exception occurred...")
        print(e)
        obc.stop_Charger()
        time.sleep(1)
        bms.openContactor()

if __name__ == "__main__":
    main()


