import matplotlib.pyplot as plt
import pandas as pd
from pythondaq.arduino_device import ArduinoVISADevice, list_devices
import threading
import numpy as np

# deze class voert het experiment uit en geeft een plot en het .csv bestand van de meting.
class DiodeExperiment:
    """This class carries the experiment out. It may save the dataframe as a .csv file if asked for\n and shows a plot if asked for, the plot will also be saved if the dataframe is saved.
    """
    def __init__(self,port):
        """Sets up the Arduino and lists

        Args:
            port (string): name of the USB-port that the Arduino is connected to
        """
        # start the Arduino and shows the names of the USB-ports
        print(list_devices())
        self.device = ArduinoVISADevice(port=port)
        print(self.device.get_identification())
        
        # sets up the lists for the measurments
        self.U_LED = []
        self.I_LED = []
        self.U_err = []
        self.I_err = []

    def scan(self, start, stop, rep_num):
        """Takes a measurment with starting at the value given with start and ending with the value given by stop

        Args:
            start (integer): Starts the measurment at this value in ADC
            stop (integer): Stops the measurment at this value in ADC
            rep_num (integer): the amount of times that the measurment is repeated to ensure a better significance 
        """
        self.U_LED = []
        self.I_LED = []
        self.U_err = []
        self.I_err = []

        # makes the measurments between the start and stop values
        for ADC_IN in range(start, stop):
            # sets the output value as ADC_IN
            self.device.set_output_value(ADC_IN)

            # makes two clean voltage-in and -out lists
            U_IN = []
            U_OUT = []
            
            # takes [rep_num] number of measurments for the input and output values
            for n in range(rep_num):
                U_IN.append(float(self.device.get_output_voltage(channel = 1)))
                U_OUT.append(float(self.device.get_output_voltage(channel = 2)))
            
            # gives a expected value for the given ADC_IN for the voltage input and output based of the measurments just taken
            U_F_IN = 0
            U_F_OUT = 0
            for x in range(rep_num):
                U_F_OUT += U_OUT[x]/rep_num
                U_F_IN += U_IN[x]/rep_num 
            
            # gives the expected error values for the given ADC_IN for the voltage input and output based of the measurments just taken
            err_U_sqr = 0
            err_I_sqr = 0
            for i in range(rep_num):
                err_U_sqr += ((U_IN[i] - U_OUT[i]) - (U_F_IN - U_F_OUT))**2/rep_num
                err_I_sqr += ((U_IN[i] - U_F_IN)/220)**2/rep_num



            # The voltage, current and their errors are calculated and put into lists
            self.U_LED.append(U_F_IN - U_F_OUT)
            self.I_LED.append(U_F_OUT/220)
            self.U_err.append(np.sqrt(err_U_sqr))
            self.I_err.append(np.sqrt(err_I_sqr))


        # Turns the data into a dataframe and prints it
        dictionary = {"U LED": self.U_LED, "U ERR":self.U_err, "I LED": self.I_LED, "I ERR":self.I_err,}
        df = pd.DataFrame(dictionary)
        print(df)
        # turns the light off after the measurments are done

        self.device.close()

        return self.U_LED, self.I_LED, self.U_err, self.I_err

    def start_scan(self, start, stop, rep_num):
        """Starts the scan as a thread
        """
        self._scan_thread = threading.Thread(
            target=self.scan, args=(start, stop, rep_num)
        )
        self._scan_thread.start()

