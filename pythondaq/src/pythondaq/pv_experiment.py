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
        self.U_pv = []
        self.I_pv = []
        self.R = []
        self.U_err = []
        self.I_err = []

    def scan(self, start, stop, rep_num):
        """Takes a measurment with starting at the value given with start and ending with the value given by stop

        Args:
            start (integer): Starts the measurment at this value in ADC
            stop (integer): Stops the measurment at this value in ADC
            rep_num (integer): the amount of times that the measurment is repeated to ensure a better significance 
        """
        self.list_U_pv = []
        self.list_U_0 = []
        self.list_I_pv = []
        self.list_R = []
        self.list_P = []
        self.list_U_err = []
        self.list_I_err = []
        self.list_R_err = []
        self.list_P_err = []
        self.end_meas = None

        # makes the measurments between the start and stop values
        for ADC_IN in range(start, stop):
            if self.end_meas == None:
                # sets the output value as ADC_IN
                self.device.set_output_value(ADC_IN)
                
                # makes two clean voltage-in and -out lists
                U_1 = []
                U_2 = []
                R_n = []
                P_n = []
                # takes [rep_num] number of measurments for the input and output values
                for n in range(rep_num):
                    U_n_1 = float(self.device.get_output_voltage(channel = 1))
                    U_1.append(U_n_1)
                    U_n_2 = float(self.device.get_output_voltage(channel = 2))
                    U_2.append(U_n_2)
                    P_n.append(U_n_1*U_n_2)

                    try:
                        R_n.append((U_n_1 * 14.1)/U_n_2)
                    except:
                        R_n.append(5000)
                

                # gives average of repeated measurement of each inputvalues 
                U_1_avg = np.mean(U_1)
                U_2_avg = np.mean(U_2)

                # gives a expected value for the given ADC_IN for the voltage input and output based of the measurments just taken
                # U_F_IN = 0
                # U_F_OUT = 0
                # for x in range(rep_num):
                #     U_F_OUT += U_OUT[x]/rep_num
                #     U_F_IN += U_IN[x]/rep_num 
                
                # voltage on channel 1 (U_1) is a third of voltage over photocell
                U_pv = 3 * U_1_avg
                U_1_std =np.std(U_1)
                U_err = 3 * U_1_std

                # current over resistor of 4.7 Ohm with voltage of channel 2 (U_2)
                I_pv = U_2_avg / 4.7
                U_2_std = np.std(U_2)
                I_err  = U_2_std / 4.7

                # resistance over photocell effectively same as resistance of transistor
                R = np.mean(R_n)
                R_err = np.std(P_n)

                P = np.mean(P_n)
                P_err = np.std(P_n)
                # gives the expected error values for the given ADC_IN for the voltage input and output based of the measurments just taken
                # err_U_sqr = 0
                # err_I_sqr = 0
                # for i in range(rep_num):
                #     err_U_sqr += ((U_IN[i] - U_OUT[i]) - (U_F_IN - U_F_OUT))**2/rep_num
                #     err_I_sqr += ((U_IN[i] - U_F_IN)/220)**2/rep_num

                U_0 = ADC_IN *3.3 / 1023

                # The voltage, current and their errors are calculated and put into lists
                self.list_U_pv.append(U_pv)
                self.list_U_0.append(U_0)
                self.list_I_pv.append(I_pv)
                self.list_R.append(R)
                self.list_P.append(P)
                self.list_U_err.append(U_err)
                self.list_I_err.append(I_err)
                self.list_R_err.append(R_err)
                self.list_P_err.append(P_err)
        
        # calculates fill factor from
        P_max = max(self.list_P)
        I_oc = self.list_I_pv[-1]
        U_oc = self.list_U_pv[0]
        P_tmax = I_oc * U_oc
        self.FF = P_max / P_tmax
        # Turns the data into a dataframe and prints it
        dictionary = {"U pv": self.list_U_pv, "U ERR":self.list_U_err, "I pv": self.list_I_pv, "I ERR":self.list_I_err, "R":self.list_R}
        self.df = pd.DataFrame(dictionary)
        print(self.df)

        # turns the light off after the measurments are done
        self.device.close()

        return self.list_U_pv, self.list_U_0, self.list_I_pv, self.list_R, self.list_P, self.list_U_err, self.list_I_err, self.list_R_err, self.list_P_err, self.FF

    def start_scan(self, start, stop, rep_num):
        """Starts the scan as a thread
        """
        self._scan_thread = threading.Thread(
            target=self.scan, args=(start, stop, rep_num)
        )
        self._scan_thread.start()

