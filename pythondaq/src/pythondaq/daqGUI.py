import click
import sys
import numpy as np
import pandas as pd
import time
import matplotlib.pyplot as plt
from pythondaq.pv_experiment import DiodeExperiment
from pythondaq.arduino_device import ArduinoVISADevice, list_devices
from PySide6 import QtWidgets,QtCore, QtGui
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

        # gives the window an icon and title
        self.setWindowIcon(QtGui.QIcon("src/pythondaq/images/Icon.png"))
        self.setWindowTitle("They Love Coding Club: Zonnecel programma")

        # makes the tab widgets
        self.tab_widget = QtWidgets.QTabWidget()

        # makes the plot widget
        self.plot_widget = pg.PlotWidget()
        self.plot_R_V_widget = pg.PlotWidget()
        self.plot_P_R_widget = pg.PlotWidget()

        # makes the Min spinbox
        self.StartSpinBox = QtWidgets.QDoubleSpinBox()
        self.start_label = QtWidgets.QLabel("Start")
        self.StartSpinBox.setSuffix("V")
        self.StartSpinBox.setSingleStep(0.1)
        self.StartSpinBox.setMaximum(3.29)
        
        # makes the Max spinbox
        self.StopSpinBox = QtWidgets.QDoubleSpinBox()
        self.stop_label = QtWidgets.QLabel("Stop")
        self.StopSpinBox.setSuffix("V")
        self.StopSpinBox.setSingleStep(0.1)
        self.StopSpinBox.setMaximum(3.3)
        self.StopSpinBox.setValue(3.3)
        
        # makes the Number of Points spinbox
        self.MeasSpinBox = QtWidgets.QSpinBox()
        self.rep_label = QtWidgets.QLabel("accuracy measurement")
        self.MeasSpinBox.setMaximum(20)
        self.MeasSpinBox.setValue(5)

        # sets the logo up
        self.logo_box = QtWidgets.QLabel()
        self.logo = QtGui.QPixmap("src/pythondaq/images/Logo.png",)
        self.logo = self.logo.scaled(1000,50, QtCore.Qt.IgnoreAspectRatio,QtCore.Qt.FastTransformation )
        self.logo_box.setPixmap(self.logo)
        

        # Makes the user interface
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)

        self.total_box = QtWidgets.QVBoxLayout(central_widget)
        self.hbox = QtWidgets.QHBoxLayout()
        self.vbox = QtWidgets.QVBoxLayout()
        self.under_hbox = QtWidgets.QHBoxLayout()
        self.startbox = QtWidgets.QVBoxLayout()
        self.stopbox = QtWidgets.QVBoxLayout()
        self.repbox = QtWidgets.QVBoxLayout()


        self.startbox.addWidget(self.StartSpinBox)
        self.startbox.addWidget(self.start_label)
        self.under_hbox.addLayout(self.startbox)
        self.stopbox.addWidget(self.StopSpinBox)
        self.stopbox.addWidget(self.stop_label)
        self.under_hbox.addLayout(self.stopbox)
        self.repbox.addWidget(self.MeasSpinBox)
        self.repbox.addWidget(self.rep_label)
        self.under_hbox.addLayout(self.repbox)

        # sets the ports for the user
        ports = list_devices()
        self.port_input = QtWidgets.QComboBox()
        for x in ports:
            self.port_input.addItem(x)
        self.vbox.addWidget(self.port_input)

        # runs the measurment with the specified values
        self.Run_button = QtWidgets.QPushButton("Run")
        self.vbox.addWidget(self.Run_button)

        self.End_button = QtWidgets.QPushButton("End measurement")
        self.vbox.addWidget(self.End_button)

        # prompts the user to save the file
        self.save_button = QtWidgets.QPushButton("Save")
        self.vbox.addWidget(self.save_button)

        # closes the program
        self.close_button = QtWidgets.QPushButton("Close")
        self.vbox.addWidget(self.close_button)

        self.tab_widget.addTab(self.plot_widget,"U_pv tegen I_pv")
        self.tab_widget.addTab(self.plot_R_V_widget,"U_0 tegen R")
        self.tab_widget.addTab(self.plot_P_R_widget, "P tegen R")

        self.hbox.addWidget(self.tab_widget)
        self.hbox.addLayout(self.vbox)

        self.total_box.addWidget(self.logo_box)
        self.total_box.addLayout(self.hbox)
        self.total_box.addLayout(self.under_hbox)

        self.Run_button.clicked.connect(self.start_scan)
        self.End_button.clicked.connect(self.End)
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
            symbol='o', color = 'b', 
            pen=None)

            self.plot_P_R_widget.clear()

            self.plot_P_R_widget.plot(
            x = self.experiment.list_R, 
            y = self.experiment.list_P, 
            symbol='o', color = 'b', 
            pen=None)
            
            
            # Plots the errorbars
            self.error =pg.ErrorBarItem()
            self.error.setData(
                x = np.array(self.experiment.list_U_pv), y = np.array(self.experiment.list_I_pv),
                left = np.array(self.experiment.list_U_err), right = np.array(self.experiment.list_U_err),
                top = np.array(self.experiment.list_I_err), bottom = np.array(self.experiment.list_I_err)
            )
            self.plot_widget.addItem(self.error)


            self.error_R =pg.ErrorBarItem()
            self.error_R.setData(
                x = np.array(self.experiment.list_U_0), y = np.array(self.experiment.list_R),
                top = np.array(self.experiment.list_R_err), bottom = np.array(self.experiment.list_R_err)
            )
            self.plot_R_V_widget.addItem(self.error_R)
            
            self.error_P =pg.ErrorBarItem()
            self.error_P.setData(
                x = np.array(self.experiment.list_R), y = np.array(self.experiment.list_P),
                left = np.array(self.experiment.list_R_err), right = np.array(self.experiment.list_R_err),
                top = np.array(self.experiment.list_P_err), bottom = np.array(self.experiment.list_P_err)
            )
            self.plot_P_R_widget.addItem(self.error_P)

            # self.plot_P_R_widget.setXRange(0,8000)
            # self.plot_P_R_widget.setLimits(xMin=0, xMax=8000,disableAutoRange = True)
            # self.plot_P_R_widget.setLogMode(x=True)

            # Gives the axes
            self.plot_widget.setLabel("bottom", "Voltage U_pv(V)", color = "k")
            self.plot_widget.setLabel("left", "Current I_pv(A)", color = "k")

            self.plot_R_V_widget.setLabel("bottom", "Voltage U_0(V)", color = "k")
            self.plot_R_V_widget.setLabel("left", "Resistance R(Ohm)", color = "k")

            self.plot_P_R_widget.setLabel("bottom", "Resistance R(Ohm)", color = "k")
            self.plot_P_R_widget.setLabel("left", "Vermogen P(Watt)", color = "k")

    @Slot()
    def save(self):
        """Saves the file
        """
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(filter="CSV files (*.csv)", dir="src/pythondaq/Measurements")
        self.experiment.df.to_csv(path_or_buf=f"{filename}")
        # saves a plot with the same name

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
        """Ends the measurement, if no measurement is happening it gives an error to the user
        """
        try:
            if self.experiment.end_meas == None:
                self.experiment.end_meas = True

            else: 
                wrong_port_box = QtWidgets.QMessageBox()
                wrong_port_box.setWindowTitle("Error")
                wrong_port_box.setText(f"No measurement is taking place")
                wrong_port_box.exec()
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