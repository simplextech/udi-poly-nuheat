try:
    import polyinterface
except ImportError:
    import pgc_interface as polyinterface
    CLOUD = True

from nuheat import NuHeat

LOGGER = polyinterface.LOGGER


class ThermostatNode_F(polyinterface.Node):
    def __init__(self, controller, primary, address, name):
        super(ThermostatNode_F, self).__init__(controller, primary, address, name)
        self.access_token = None
        self.NuHeat = None
        self.temp_uom = controller.temp_uom

    def start(self):
        self.access_token = self.controller.polyConfig['customData']['access_token']
        self.NuHeat = NuHeat(self.access_token)
        thermostats = self.NuHeat.get_thermostat()
        if thermostats is not None:
            for stat in thermostats:
                if stat['serialNumber'] == self.address:
                    if self.temp_uom == 17:
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

                    if stat['isHeating']:
                        clihcs = 1
                    else:
                        clihcs = 0

                    # self.setDriver('ST', clitemp, uom=self.temp_uom)
                    # self.setDriver('CLISPH', clisph, uom=self.temp_uom)
                    # self.setDriver('CLIMD', climd, uom=67)
                    # self.setDriver('CLIHCS', clihcs, uom=66)
                    self.setDriver('ST', clitemp)
                    self.setDriver('CLISPH', clisph)
                    self.setDriver('CLIMD', climd)
                    self.setDriver('CLIHCS', clihcs)

                else:
                    LOGGER.error("Thermostat Serial Number not available")
        else:
            LOGGER.error("thermostat_node.Nuheat.get_thermostat: Returned None")

    def query(self, command=None):
        self.reportDrivers()

    def setpoint_heat(self, command):
        val = command['value']

        if self.temp_uom == 17:
            new_setpoint = self.NuHeat.nuheat_fahrenheit_to_celsius_json(val)
        else:
            new_setpoint = self.NuHeat.nuheat_celsius_to_json(val)

        _status = self.NuHeat.set_thermostat_setpoint(self.address, new_setpoint)
        if _status is not None:
            self.setDriver('CLISPH', val)
        else:
            print("thermostat_node.setpoint_heat: " + str(_status))

    # "Hints See: https://github.com/UniversalDevicesInc/hints"
    # hint = [1, 12, 1, 0]
    drivers = [
        {'driver': 'ST', 'value': 0, 'uom': 17},
        {'driver': 'CLISPH', 'value': 0, 'uom': 17},
        {'driver': 'CLIMD', 'value': 0, 'uom': 67},
        {'driver': 'CLIHCS', 'value': 0, 'uom': 66}
    ]

    id = 'THERMOSTAT_F'

    commands = {
        'QUERY': query,
        'CLISPH': setpoint_heat
    }


class ThermostatNode_C(polyinterface.Node):
    def __init__(self, controller, primary, address, name):
        super(ThermostatNode_C, self).__init__(controller, primary, address, name)
        self.access_token = None
        self.NuHeat = None
        self.temp_uom = controller.temp_uom

    def start(self):
        self.access_token = self.controller.polyConfig['customData']['access_token']
        self.NuHeat = NuHeat(self.access_token)
        thermostats = self.NuHeat.get_thermostat()
        if thermostats is not None:
            for stat in thermostats:
                if stat['serialNumber'] == self.address:
                    if self.temp_uom == 17:
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

                    if stat['isHeating']:
                        clihcs = 1
                    else:
                        clihcs = 0

                    self.setDriver('ST', clitemp)
                    self.setDriver('CLISPH', clisph)
                    self.setDriver('CLIMD', climd)
                    self.setDriver('CLIHCS', clihcs)

                else:
                    LOGGER.error("Thermostat Serial Number not available")
        else:
            LOGGER.error("thermostat_node.Nuheat.get_thermostat: Returned None")

    def query(self, command=None):
        self.reportDrivers()

    def setpoint_heat(self, command):
        val = command['value']

        if self.temp_uom == 17:
            new_setpoint = self.NuHeat.nuheat_fahrenheit_to_celsius_json(val)
        else:
            new_setpoint = self.NuHeat.nuheat_celsius_to_json(val)

        _status = self.NuHeat.set_thermostat_setpoint(self.address, new_setpoint)
        if _status is not None:
            self.setDriver('CLISPH', val)
        else:
            print("thermostat_node.setpoint_heat: " + str(_status))

    # "Hints See: https://github.com/UniversalDevicesInc/hints"
    # hint = [1, 12, 1, 0]
    drivers = [
        {'driver': 'ST', 'value': 0, 'uom': 4},
        {'driver': 'CLISPH', 'value': 0, 'uom': 4},
        {'driver': 'CLIMD', 'value': 0, 'uom': 67},
        {'driver': 'CLIHCS', 'value': 0, 'uom': 66}
    ]

    id = 'THERMOSTAT_C'

    commands = {
        'QUERY': query,
        'CLISPH': setpoint_heat
    }
