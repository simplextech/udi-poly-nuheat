'use strict';

const axios = require('axios');
const storage = require('node-persist');
storage.init({dir: './storage'});

const baseUrl = 'https://www.mynuheat.com';

const URL = {
  AUTH: '/api/authenticate/user',
  THERMOSTATS: '/api/thermostats',
  THERMOSTAT: '/api/thermostat',
  }

module.exports = function(Polyglot, polyInterface) {
  const logger = Polyglot.logger;

  class NuheatInterface {
    constructor(polyInterface) {
      this.polyInterface = polyInterface;
    }

    sleep(ms) {
      return new Promise(resolve => setTimeout(resolve, ms));
    }

    CtoF(celsius) {
      let _C = celsius / 100;
      let raw = (_C * 9/5) + 32;
      // logger.info('CtoF Raw: ' + raw);
      let F = Math.round(raw);
      // logger.info('CtoF Sending: ' + F);
      return F;
    }

    FtoC(fehrenheit) {
      let _F = parseInt(fehrenheit, 10);
      let C = (_F - 32) * 5/9;
      // logger.info('FtoC Raw: ' + C);
      return C;
    }

    JCtoC(json_celsius) {
      let _C = Math.round(json_celsius / 100, 10);
      return _C;
    }

    FtoJC(fehrenheit) {
      let _C = this.FtoC(fehrenheit);
      let _JC = Math.round(_C * 100);
      // logger.info('FtoJC Sending: ' + _JC);
      return _JC;
    }

    CtoJC(celsius) {
      let _JC = celsius * 100;
      return _JC;
    }

    async getReq(path, serialNumber) {
      let sessionId = await storage.getItem('sessionId');
      let data = null;

      const config = {
        method: 'get',
        url: baseUrl + path,
        headers: {
          'Content-Type': 'application/json'
        },
        params: {
          sessionid: sessionId,
          serialnumber: serialNumber
        }
      }
      // logger.info('Axios Config: ' + JSON.stringify(config));

      try {
        const res = await axios.request(config);
        data = res.data;
      }
      catch(err) {
        logger.error(err);
        data = null;
      }
      
      return data;
    }

    async postReq(path, serialNumber, setPoint) {
      let sessionId = await storage.getItem('sessionId');
      let data = null;

      const config = {
        method: 'post',
        url: baseUrl + path,
        headers: {
          'Content-Type': 'application/json'
        },
        params: {
          sessionid: sessionId,
          serialnumber: serialNumber
        },
        data: {
          ScheduleMode: 3,
          SetPointTemp: setPoint
        }
      }
      // logger.info('Axios Config: ' + JSON.stringify(config));

      try {
        const res = await axios.request(config);
        data = res.data;
      }
      catch(err) {
        logger.error(err);
        data = null
      }
      // logger.info('getReq data: ' + JSON.stringify(data));
      
      return data;
    }

    async authenticate() {
      let username = this.polyInterface.getCustomParam('Username');
      let password = this.polyInterface.getCustomParam('Password');

      const config = {
        method: 'post',
        url: baseUrl + URL['AUTH'],
        headers: {
          'Content-Type': 'application/json'
        },
        data: {
          Email: username,
          Password: password,
          Confirm: password,
        }
      }
      // logger.info('Axios Config: ' + JSON.stringify(config));

      let res = await axios.request(config);
      let data = res.data
      // logger.info(JSON.stringify(data));
      let _saved = await storage.setItem('sessionId', data.SessionId);

      return _saved;
    }
  
    async thermostats() {
      let data = this.getReq('/api/thermostats');
      return data;
    }

    async thermostat(serialNumber) {
      let data = this.getReq('/api/thermostat', serialNumber);
      return data;
    }

    async setPointHeat(serialNumber, setPoint) {
      let data = this.postReq('/api/thermostat', serialNumber, setPoint);
      return data;
    }
  }

 
  return new NuheatInterface(polyInterface);
};
