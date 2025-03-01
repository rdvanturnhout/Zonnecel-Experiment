# grafical user interface application

import sys
from PySide6 import QtWidgets
from PySide6.QtCore import Slot
from zonnecel.model import ZonnecelExperiment, show_devices
import pyqtgraph as pg
import pandas as pd
import numpy as np
from lmfit import models

pg.setConfigOption("background", "w")
pg.setConfigOption("foreground", "k")

class UserInterface(QtWidgets.QMainWindow):
    def __init__(self):
        """ Init function that builds the format of the graphical user interface and indicates what happens when buttons are clicked
        """        
        # roep de __init__() aan van de parent class
        super().__init__()

        # every QMainWindow needs a central widget
        # inside this widget you can add a layout and other widgets
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)

        # add plot widget
        self.plot_widget = pg.PlotWidget()
        self.setWindowTitle("Graphical user interface for solar cell measurements")

        # add layouts and widgets
        vbox = QtWidgets.QVBoxLayout(central_widget)
        vbox.addWidget(self.plot_widget)
        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)
        hbox2 = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox2)
        hbox3 = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox3)

        # buttons and text
        # first and second hbox and add min and max values
        self.startwlabel = QtWidgets.QLabel("Start:")
        hbox.addWidget(self.startwlabel) 
        self.startwaarde = QtWidgets.QDoubleSpinBox()
        hbox2.addWidget(self.startwaarde)
        self.startwaarde.setMinimum(0)
        self.startwaarde.setMaximum(3.3)
        self.stopwlabel = QtWidgets.QLabel("Stop:")
        hbox.addWidget(self.stopwlabel)
        self.stopwaarde = QtWidgets.QDoubleSpinBox()
        hbox2.addWidget(self.stopwaarde)
        self.stopwaarde.setMaximum(3.3)
        self.measurementslabel = QtWidgets.QLabel("Amount of measurements:")
        hbox.addWidget(self.measurementslabel) 
        self.measurements = QtWidgets.QSpinBox()
        hbox2.addWidget(self.measurements)
        self.measurements.setMinimum(1)
        self.portlabel = QtWidgets.QLabel("Add port you want to use:")
        hbox.addWidget(self.portlabel)
        self.add_port_choise = QtWidgets.QComboBox()
        self.add_port_choise.addItems(show_devices())
        hbox2.addWidget(self.add_port_choise)

        #third hbox
        add_start_button = QtWidgets.QPushButton("Do a measurement")
        hbox3.addWidget(add_start_button)
        add_UI_button = QtWidgets.QPushButton("voltage-current graph")
        hbox3.addWidget(add_UI_button)
        add_PR_button = QtWidgets.QPushButton("power-resistance curve")
        hbox3.addWidget(add_PR_button)
        add_save_button = QtWidgets.QPushButton("Save voltage-current Data")
        hbox3.addWidget(add_save_button)
        add_fit_button = QtWidgets.QPushButton("Fit IU Data")
        hbox3.addWidget(add_fit_button)


        # set initial values
        self.startwaarde.setValue(0)
        self.stopwaarde.setValue(3.3)
        self.measurements.setValue(2)
        self.add_port_choise.setCurrentIndex(3)

        #signals
        add_start_button.clicked.connect(self.scan_data)
        add_UI_button.clicked.connect(self.plot_UI)
        add_PR_button.clicked.connect(self.plot_PR)
        add_save_button.clicked.connect(self.save_data)
        add_fit_button.clicked.connect(self.fit)

        # intitial lists
        self.I = []
        self.U = []
        self.U_err = []
        self.I_err = []
        self.R = []
        self.P = []
        self.R_err = []
        self.P_err = []



    @Slot()
    def scan_data(self):
        """Get data from zonnecel experiment with the variables that are currently in the boxes/buttons
        """        
        self.plot_widget.clear()
        experiment = ZonnecelExperiment(port = self.add_port_choise.currentText())
        self.U, self.I, self.R, self.P, self.U_err, self.I_err, self.R_err, self.P_err = experiment.repeat_scan(int(self.startwaarde.value()/3.3*1024), int(self.stopwaarde.value()/3.3*1024), self.measurements.value())
        self.Rmax, self.Pmax = experiment.max_power(self.R, self.P)

    def plot_UI(self):
        # plotting U-I graph
        self.plot_widget.clear()
        error = pg.ErrorBarItem()
        error.setData(x = np.array(self.U), y = np.array(self.I), top = np.array(self.I_err), bottom = np.array(self.I_err), left = np.array(self.U_err), right = np.array(self.U_err))
        self.plot_widget.addItem(error)
        self.plot_widget.setXRange(0, 7)
        self.plot_widget.setYRange(0, .07)
        self.plot_widget.plot(self.U, self.I, symbol = "o", pen = None, symbolSize = 5, SymbolBrush = "b", symbolPen = "k")
        self.plot_widget.setLabel("left", "current (A)")
        self.plot_widget.setLabel("bottom", "voltage (V)")
        self.plot_widget.setTitle("Current against voltage graph")


    def plot_PR(self):
        # plotting P-R graph
        self.plot_widget.clear()
        error = pg.ErrorBarItem()
        error.setData(x = np.array(self.R), y = np.array(self.P), top = np.array(self.P_err), bottom = np.array(self.P_err), left = np.array(self.R_err), right = np.array(self.R_err))
        self.plot_widget.addItem(error)
        self.plot_widget.setXRange(0, 10000)
        self.plot_widget.setYRange(0, .25)
        self.plot_widget.plot(self.R, self.P, symbol = "o", pen = None, symbolSize = 5, SymbolBrush = "b", symbolPen = "k")
        self.plot_widget.plot(np.array([self.Rmax]), np.array([self.Pmax]), symbol = "o", pen = None, symbolSize = 8, SymbolBrush = "r", symbolPen = "r")
        self.plot_widget.setLabel("left", "power (W)")
        self.plot_widget.setLabel("bottom", "resistance (Ω)")
        self.plot_widget.setTitle("power-resistance graph")
    
    def save_data(self):
        """Saves data as a csv file that the user can name themselves
        """        
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(filter="CSV files (*.csv)")
        data_array = pd.DataFrame(np.column_stack([self.U, self.I, self.U_err, self.I_err]))
        data_array.to_csv(filename, index = False, header = False)

    def fit(self):
        # the function
        def intensity(U, I0, A):
            I = I0 * (np.exp(A * U) - 1)
            return I

        # make the fit to the selected data
        model = models.Model(intensity)
        fit = model.fit(np.array(self.I), U = np.array(self.U), weights = 1/(np.array(self.I_err) + 10**-9) , I0 = 0.04, A = 1)

        I0 = fit.params['I0'].value
        A = fit.params["A"].value

        print("I0 fit value =", I0)
        print("A fit value =", A)
        x = np.array(self.U)
        y = I0 * (np.exp(A*x) - 1)
        
        # give the results of the fit
        self.plot_widget.plot(x, y)
        


def main():
    """ Making instance of the QtWidgets.QApplication and our own class, call method show and making sure error is shown when something goes wrong
    """    
    app = QtWidgets.QApplication(sys.argv)
    ui = UserInterface()
    ui.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
 