import click
from pythondaq.diode_experiment import DiodeExperiment
from pythondaq.arduino_device import ArduinoVISADevice,list_devices

@click.group()
def diode_group():
    """takes measurments from a given Arduino
    """
    pass

@diode_group.command()
@click.option("-d", "--device", default="ASRL4::INSTR", help="Input the USB-port that the device is in, if you dont know it, use the list command")
@click.option("-s" "--start", default=0, help="Input the start value in Volt for the measurment")
@click.option("-e" "--stop", default=3.3, help="Input the stop value in Volt for the measurment")
@click.option("-r", "--rep_num", default=5, help="The amount of times that the measurement is repeated for a better significance")
@click.option("-o","--output", default="", help="if you want to save the dataframe and graph(if asked for with -g or --graph) fill in the name that you want the saved file to have")
@click.option("-g/-no-g","--graph/--no-graph", default=False, help="use -g or  --graph to show the graph, saves it if a name was given with -o or --output")
def scan(device, start, stop, rep_num, output, graph):
    """takes the measurment and saves a dataframe if asked for. Also shows a graph if asked for,
    the graph is saved under the same name as the dataframe if the dataframe is saved

    Args:
        device (string): takes the USB-port in which the Arduino is placed in
        start (integer): Starts the measurment at this value in Volt
        stop (integer): Stops the measurment at this value in Volt
        rep_num (integer): the amount of times that the measurment is repeated to ensure a better significance 
        ms_name (integer): if filled will save the dataframe as a .csv file and name the file [ms_name]
        graph (True/False): returns a graph if True, also names and saves that graph if [ms_name] is filled
    """
    # sets up the Arduino
    experiment = DiodeExperiment(device)
    
    #changes the start and stop values to ADC in order for easier communication with the Arduino
    start = round(start*(1023/3.3)) + 1
    stop = round(stop*(1023/3.3)) + 1

    # does the experiment
    experiment.scan(start, stop, rep_num, ms_name=output, graph = graph)

@diode_group.command()
def list():
    """gives the USB-port that the Arduino is connected to
    """
    print(list_devices())

@diode_group.command()
@click.option("-d", "--device", default="ASRL4::INSTR")
def info(device):
    """gives the identification of the Arduino
    """
    ArduinoDevice = ArduinoVISADevice(device)

    print(ArduinoDevice.get_identification())

# if the programme is called allows acces to the commands
if __name__ == "__main__":
    diode_group()

