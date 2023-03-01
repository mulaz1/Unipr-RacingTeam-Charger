TIMEOUT = 2 #timeout oltre il quale il caricatore va in errore

'''
parametri target di carica

'''
VOLTAGE_CELL_REF =  4150    # Ref voltage cells to change state [mV]
COSTANT_CURRENT = 12  #current stage CC [A]

#error parameter
MAX_TEMPERATURE_BAT = 60    #Max temperature battery Error [°C]
VOLTAGE_MAX = 600   # max voltage of battery Error [V]
VOLTAGE_MAX_CELL = 4200 # max voltage cells Error [mV] 

COUNTERROR = 20 #Maximum number of errors before going in error

BATTERY_STAGE_1 = False #fase di CC o VC (costante voltage and costante current)

K = 0.1 #current reduction coefficent

DEBUG = True   #Se TRUE tutti i messasggi e parametri vengono stampati su terminale
