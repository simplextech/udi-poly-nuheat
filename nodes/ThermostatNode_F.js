'use strict';

const nodeDefId = 'THERMOSTAT_F';

module.exports = function(Polyglot) {
  const logger = Polyglot.logger;

  class ThermostatNode_F extends Polyglot.Node {
    constructor(polyInterface, primary, address, name) {
      super(nodeDefId, polyInterface, primary, address, name);

      this.nuheat = require('../lib/nuheat.js')(Polyglot, polyInterface);

      this.commands = {
        QUERY: this.query,
        CLISPH: this.setPointHeat,
      };

      this.drivers = {
        ST: {value: '0', uom: 17},
        CLISPH: {value: '0', uom: 17},
        CLIMD: {value: '0', uom: 25},
        CLIHCS: {value: '0', uom: 66},
      };

      this.query();
      
    }

    async query() {
      let statInfo = await this.nuheat.thermostat(this.address);

      if (statInfo == null) {
        logger.error('Not Authenticated... Re-Authenticating...');
        this.nuheat.authenticate();
      } else {
        let temp = this.nuheat.CtoF(statInfo.Temperature);
        let setPoint = this.nuheat.CtoF(statInfo.SetPointTemp);
        let isHeating = 0;

        if (statInfo.Heating) {
          isHeating = 1;
        } else {
          isHeating = 0
        }

        this.setDriver('ST', temp, true);
        this.setDriver('CLISPH', setPoint, true);
        this.setDriver('CLIMD', statInfo.OperatingMode, true);
        this.setDriver('CLIHCS', isHeating, true);
      }
    }

    setPointHeat(message) {
      let setPoint = this.nuheat.FtoJC(message.value);

      this.nuheat.setPointHeat(this.address, setPoint);
      this.setDriver('CLISPH', message.value, true);
    }
    
  };

  ThermostatNode_F.nodeDefId = nodeDefId;

  return ThermostatNode_F;
};
