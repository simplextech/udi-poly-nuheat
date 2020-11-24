'use strict';
const storage = require('node-persist');
storage.init({dir: './storage'});

const nodeDefId = 'CONTROLLER';

module.exports = function(Polyglot) {
  const logger = Polyglot.logger;

  const ThermostatNode_F = require('./ThermostatNode_F.js')(Polyglot);
  const ThermostatNode_C = require('./ThermostatNode_C.js')(Polyglot);

  class Controller extends Polyglot.Node {
    constructor(polyInterface, primary, address, name) {
      super(nodeDefId, polyInterface, primary, address, name);

      this.nuheat = require('../lib/nuheat.js')(Polyglot, polyInterface);

      this.commands = {
        DISCOVER: this.onDiscover,
        UPDATE_PROFILE: this.onUpdateProfile,
        REMOVE_NOTICES: this.onRemoveNotices,
        QUERY: this.query,
      };

      this.drivers = {
        ST: { value: '1', uom: 2 },
      };

      this.isController = true;
      this.sessionId = null;
    }

    async onDiscover() {
      let auth = await this.nuheat.authenticate();
      let tstats = null;
      
      logger.info('Getting Thermostats');
      tstats = await this.nuheat.thermostats();
      if (tstats == null) {
        logger.error('Not Authenticated... Sending Auth Request.');
        auth = await this.nuheat.authenticate();
        tstats = await this.nuheat.thermostats();
      }
      logger.info('Thermostat Data: ' + JSON.stringify(tstats));

      let groups = tstats.Groups;
      for (const group of groups) {
        logger.info('Group Name: ' + group.groupName);
        for (const stat of group.Thermostats) {
          const name = stat.Room;
          const address = stat.SerialNumber.toString();
          const scale = this.polyInterface.getCustomParam('Scale');

          if (scale == 'Fahrenheit') {
            try {
              const result = await this.polyInterface.addNode(
                new ThermostatNode_F(this.polyInterface, address, address, name)
              );
              logger.info('Add node worked: %s', result);
            } catch (err) {
              logger.errorStack(err, 'Add node failed:');
            }
          } else {
            try {
              const result = await this.polyInterface.addNode(
                new ThermostatNode_C(this.polyInterface, address, address, name)
              );
              logger.info('Add node worked: %s', result);
            } catch (err) {
              logger.errorStack(err, 'Add node failed:');
            }
          }
        }
      }
    }

    onUpdateProfile() {
      this.polyInterface.updateProfile();
    }

    onRemoveNotices() {
      this.polyInterface.removeNoticesAll();
    }

  };

  Controller.nodeDefId = nodeDefId;

  return Controller;
};
