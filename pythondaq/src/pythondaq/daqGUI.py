import click
import sys
import numpy as np
import matplotlib.pyplot as plt
from pythondaq.pv_experiment import DiodeExperiment
from pythondaq.arduino_device import ArduinoVISADevice, list_devices
from PySide6 import QtWidgets,QtCore
from PySide6.QtCore import Slot
import pyqtgraph as pg

@click.group()
def app_group():
    """Starts the app
    """
    pass

@app_group.command()
def run():
    main()


class UserInterface(QtWidgets.QMainWindow):
    """Makes a user interface displaying a sin function, with adjustable start, stop and points
    """
    def __init__(self):
    # call the init off the parent class
        super().__init__()
    
        # black background, white text and function
        pg.setConfigOption("background", "w")
        pg.setConfigOption("foreground", "k")

        self.tab1_widget = QtWidgets.QTabWidget()
        self.tab2_widget = QtWidgets.QTabWidget()

        # makes the plot widget
        self.plot_widget = pg.PlotWidget()
        self.plot_R_V_widget = pg.PlotWidget()

        # makes the Min spinbox
        self.StartSpinBox = QtWidgets.QDoubleSpinBox()
        self.StartSpinBox.setSuffix("V  Start")
        self.StartSpinBox.setSingleStep(0.1)
        self.StartSpinBox.setMaximum(3.29)
        
        # makes the Max spinbox
        self.StopSpinBox = QtWidgets.QDoubleSpinBox()
        self.StopSpinBox.setSuffix("V  Stop")
        self.StopSpinBox.setSingleStep(0.1)
        self.StopSpinBox.setMaximum(3.3)
        self.StopSpinBox.setValue(3.3)
        
        # makes the Number of Points spinbox
        self.MeasSpinBox = QtWidgets.QSpinBox()
        self.MeasSpinBox.setSuffix("  Amount of measurements")
        self.MeasSpinBox.setMaximum(20)
        self.MeasSpinBox.setValue(5)

        # Makes the user interface
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)

        self.hbox = QtWidgets.QHBoxLayout(central_widget)
        self.vbox = QtWidgets.QVBoxLayout()

        self.vbox.addWidget(self.StartSpinBox)
        self.vbox.addWidget(self.StopSpinBox)
        self.vbox.addWidget(self.MeasSpinBox)
        
        # sets the ports for the user
        ports = list_devices()
        self.port_input = QtWidgets.QComboBox()
        for x in ports:
            self.port_input.addItem(x)
        self.vbox.addWidget(self.port_input)

        # runs the measurment with the specified values
        self.Run_button = QtWidgets.QPushButton("Run")
        self.vbox.addWidget(self.Run_button)

        self.END_button = QtWidgets.QPushButton("End measurement")
        self.vbox.addWidget(self.END_button)

        # prompts the user to save the file
        self.save_button = QtWidgets.QPushButton("Save")
        self.vbox.addWidget(self.save_button)

        # closes the program
        self.close_button = QtWidgets.QPushButton("Close")
        self.vbox.addWidget(self.close_button)

        self.tab1_widget.addTab(self.plot_widget,"U_pv tegen I_pv")
        self.tab1_widget.addTab(self.plot_R_V_widget,"U_0 tegen R")

        self.hbox.addWidget(self.tab1_widget)
        # self.hbox.widget(self.tab2_widget)

        self.hbox.addLayout(self.vbox)

        self.Run_button.clicked.connect(self.start_scan)
        self.END_button.clicked.connect(self.End)
        self.close_button.clicked.connect(self.close_program)
        self.save_button.clicked.connect(self.save)
        self.StartSpinBox.valueChanged.connect(self.hold_max)
        self.StopSpinBox.valueChanged.connect(self.hold_max)

        self.experiment = None

        self.plot_timer = QtCore.QTimer()
        # Roep iedere 100 ms de plotfunctie aan
        self.plot_timer.timeout.connect(self.plot_func)
        self.plot_timer.start(100)
    
    @Slot()
    def plot_func(self):
        """Plots the given function
        """

        if self.experiment != None:
            self.plot_widget.clear()

            self.plot_widget.plot(
            x = self.experiment.list_U_pv, 
            y = self.experiment.list_I_pv, 
            symbol='o', color = "darkviolet",
            pen=None)

            self.plot_R_V_widget.clear()

            self.plot_R_V_widget.plot(
            x = self.experiment.list_U_0, 
            y = self.experiment.list_R, 
            symbol=None, 
            pen={"color": "b", "width": 2})

            
            
            # Plots the errorbars
            self.error =pg.ErrorBarItem()
            self.error.setData(
                x = np.array(self.experiment.list_U_pv), y = np.array(self.experiment.list_I_pv),
                left = np.array(self.experiment.list_U_err), right = np.array(self.experiment.list_U_err),
                top = np.array(self.experiment.list_I_err), bottom = np.array(self.experiment.list_I_err)
            )
            self.plot_widget.addItem(self.error)

            # Gives the axes
            self.plot_widget.setLabel("bottom", "Voltage U_pv(V)", color = "k")
            self.plot_widget.setLabel("left", "Current I_pv(A)", color = "k")

            self.plot_R_V_widget.setLabel("bottom", "Voltage U_0(V)", color = "k")
            self.plot_R_V_widget.setLabel("left", "Resistance R(Ohm)", color = "k")

    @Slot()
    def save(self):
        """Saves the file
        """
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(filter="CSV files (*.csv)")

        # saves a plot with the same name
        if filename != "":
            fig, ax = plt.subplots()
            ax.errorbar(self.experiment.U_LED, self.experiment.I_LED,
                xerr=self.experiment.U_err,
                yerr=self.experiment.I_err,
                fmt='-',
                color='blue',
                ecolor='black')

            plt.xlabel("Voltage LED (V)")
            plt.ylabel("Current LED (A)")

            plt.savefig(f'{filename}.png')

    @Slot()
    def hold_max(self):
        """makes sure that the minimum value doesnt exceed the maximum
        """
        if self.StartSpinBox.value() >= self.StopSpinBox.value():
            New_Stop = self.StartSpinBox.value()+0.01 
            self.StopSpinBox.setValue(New_Stop)

    
    @Slot()
    def start_scan(self):
        """Initiates the scan
        """
        try:
            # Turns the device on
            device = self.port_input.currentText()
            self.experiment = DiodeExperiment(device)

            # Takes the given values
            rep_num = self.MeasSpinBox.value()
            start = round(self.StartSpinBox.value() *(1023/3.3))
            stop = round(self.StopSpinBox.value() *(1023/3.3)) + 1
            
            # Enters the values into the scan
            self.experiment.start_scan(start, stop, rep_num)

            # If a wrong port has been set it gives an error code back
        except:
            wrong_port_box = QtWidgets.QMessageBox()
            wrong_port_box.setWindowTitle("Error")
            wrong_port_box.setText(f"The Arduino isn't connected to the port {device}")
            wrong_port_box.exec()

    @Slot()
    def End(self):
        try:
            self.experiment.device.close()
        except: 
            wrong_port_box = QtWidgets.QMessageBox()
            wrong_port_box.setWindowTitle("Error")
            wrong_port_box.setText(f"No measurement is taking place")
            wrong_port_box.exec()

    @Slot()
    def close_program(self):
        """Closes the program
        """
        self.close()

def main():
    app = QtWidgets.QApplication(sys.argv)
    ui = UserInterface()
    ui.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()