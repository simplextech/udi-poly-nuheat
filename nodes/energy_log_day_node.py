try:
    import polyinterface
except ImportError:
    import pgc_interface as polyinterface
    CLOUD = True

import pytz
from datetime import datetime
from nuheat import NuHeat

LOGGER = polyinterface.LOGGER


class EnergyLogDayNode(polyinterface.Node):
    def __init__(self, controller, primary, address, name):
        super(EnergyLogDayNode, self).__init__(controller, primary, address, name)
        self.access_token = None
        self.NuHeat = None
        self.tz = controller.polyConfig['customParams']['tz']
        self.date = datetime.now(pytz.timezone(self.tz)).strftime('%Y-%m-%d')

    def start(self):
        self.access_token = self.controller.polyConfig['customData']['access_token']
        self.NuHeat = NuHeat(self.access_token)
        energy_used = self.NuHeat.get_energy_log_day(self.primary, self.date)
        if energy_used is not None:
            self.setDriver('GV0', energy_used[0], uom=45)
            self.setDriver('ST', energy_used[1], uom=33)
            self.setDriver('GV1', energy_used[2], uom=103)
        else:
            LOGGER.error("Energy Log Day Returned: None")

    def query(self, command=None):
        self.start()
        self.reportDrivers()

    # "Hints See: https://github.com/UniversalDevicesInc/hints"
    # hint = [1,2,3,4]
    drivers = [
        # {'driver': 'ST', 'value': 0, 'uom': 2},
        {'driver': 'GV0', 'value': 0, 'uom': 45},
        {'driver': 'ST', 'value': 0, 'uom': 33},
        {'driver': 'GV1', 'value': 0, 'uom': 104}
    ]

    id = 'ENERGYLOG'

    commands = {'QUERY': query}
