from pythondaq.diode_experiment import DiodeExperiment

def measurement():
    """takes the measurment with given values
    """
    # port is automatically ASRL4::INSTR
    port = "ASRL4::INSTR"
    experiment = DiodeExperiment(port=port)

    # takes the measurment with ADC values as start and stop
    # repeats the measurments 10 times
    # doesnt save the dataframe or graph
    # graph is shown 
    experiment.scan(start=0, stop=1024, rep_num=10, ms_name="", graph=True)