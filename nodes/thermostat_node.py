try:
    import polyinterface
except ImportError:
    import pgc_interface as polyinterface
    CLOUD = True


class ThermostatNode(polyinterface.Node):
    def __init__(self, controller, primary, address, name, nuheat):
        super(ThermostatNode, self).__init__(controller, primary, address, name)
        self.NuHeat = nuheat
        self.temperature_scale = None
        self.temp_uom = 0

    def start(self):
        account_info = self.NuHeat.get_account()
        if account_info is not None:
            self.temperature_scale = account_info['temperatureScale']

            if self.temperature_scale == "Fahrenheit":
                self.temp_uom = 17
            else:
                self.temp_uom = 4

            thermostats = self.NuHeat.get_thermostat()
            if thermostats is not None:
                for stat in thermostats:
                    if stat['serialNumber'] == self.address:
                        if self.temperature_scale == "Fahrenheit":
                            clitemp = self.NuHeat.nuheat_celsius_to_fahrenheit(stat['currentTemperature'])
                            clisph = self.NuHeat.nuheat_celsius_to_fahrenheit(stat['setPointTemp'])
                        else:
                            clitemp = self.NuHeat.nuheat_celsius_to_normal(stat['currentTemperature'])
                            clisph = self.NuHeat.nuheat_celsius_to_normal(stat['setPointTemp'])

                        climd = 0
                        if stat['operatingMode'] == 1:
                            climd = 3
                        elif stat['operatingMode'] == 2:
                            climd = 1

                        self.setDriver('ST', clitemp, uom=self.temp_uom)
                        self.setDriver('CLISPH', clisph, uom=self.temp_uom)
                        self.setDriver('CLIMD', climd, uom=67)
                    else:
                        polyinterface.LOGGER("Thermostat Serial Number not available")
            else:
                polyinterface.LOGGER("thermostat_node.Nuheat.get_thermostat: Returned None")
        else:
            polyinterface.LOGGER.error("thermostat_node.NuHeat.account_info: Unable to retrieve account information")

    def query(self, command=None):
        self.start()
        self.reportDrivers()

    def setpoint_heat(self, command):
        val = command['value']

        if self.temp_uom == 17:
            new_setpoint = self.NuHeat.nuheat_fahrenheit_to_celsius_json(val)
        else:
            new_setpoint = self.NuHeat.nuheat_celsius_to_json(val)

        _status = self.NuHeat.set_thermostat_setpoint(self.address, new_setpoint)
        if _status is not None:
            self.setDriver('CLISPH', val, uom=self.temp_uom)
        else:
            polyinterface.LOGGER.error("thermostat_node.setpoint_heat: " + str(_status))

    # "Hints See: https://github.com/UniversalDevicesInc/hints"
    # hint = [1,2,3,4]
    drivers = [
        {'driver': 'ST', 'value': 0, 'uom': 17},
        {'driver': 'CLISPH', 'value': 0, 'uom': 17},
        {'driver': 'CLIMD', 'value': 0, 'uom': 67}
    ]

    id = 'THERMOSTAT'

    commands = {
        'QUERY': query,
        'CLISPH': setpoint_heat
    }
