import pyvisa
import time



class ArduinoVISADevice:
    """this class turns the Arduino on and allows the user to perform action
    """
    # 
    def __init__(self,port):
        """tuns the Arduino on

        Args:
            port (string): fill in the USB-port to turn the Arduino on
        """
        self.rm = pyvisa.ResourceManager("@py")
        self.port = port
        self.device = self.rm.open_resource(
        self.port, read_termination="\r\n", write_termination="\n"
        )
        self.value = 0

    def get_identification(self):
        """gives the identification of the Arduino
        """
        return self.device.query("*IDN?")

    def set_output_value(self,value):
        """turns the light on at the given value and remembers that value in ADC and Volt

        Args:
            value (integer): the value in ADC that will be used to turn the light on and off
        """
        self.value = value
        self.voltage = float(value) * (3.3/1023)
        self.device.query(f"OUT:CH0 {self.value}")

    def get_output_value(self):
        """gives the ouput value in ADC
        """
        return self.device.query(f"MEAS:CH0?")

    def get_output_voltage(self, channel):
        """returns the ouput value in Volt in a given channel

        Args:
            channel (integer): the channel number to find the output value from
        """
        return float(self.device.query(f"MEAS:CH{channel}?")) * (3.3/1023)

    def get_input_value(self,channel):
        """returns the input value in ADC in a given channel

        Args:
            channel (integer): the channel number to find the input value from
        """	
        return self.device.query(f"MEAS:CH{channel}?")

    def get_input_voltage(self,channel):
        """returns the input value in Volt in a given channel

        Args:
            channel (integer): the channel number to find the input value from
        """	
        return float(self.device.query(f"MEAS:CH{channel}?")) * (3.3 / 1023)

    def close(self):
        "Turns off the device"
        self.device.query(f"OUT:CH0 0")
        self.device.close()

def list_devices():
    """"gives the USB-port in which the Arduino has been put

    Returns:
        string: the name of the USB-port(s) where the Arduino is in
    """
    rm = pyvisa.ResourceManager("@py")
    ports = rm.list_resources()
    return ports