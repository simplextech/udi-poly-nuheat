#!/usr/bin/env python

try:
    import polyinterface
except ImportError:
    import pgc_interface as polyinterface
import sys
import time
import requests
from nodes import ThermostatNode
from nodes import EnergyLogDayNode
from nodes import EnergyLogWeekNode
from nuheat import NuHeat

LOGGER = polyinterface.LOGGER


class Controller(polyinterface.Controller):
    def __init__(self, polyglot):
        super(Controller, self).__init__(polyglot)
        self.name = 'NuHeat'
        # self.poly.onConfig(self.process_config)
        self.server_data = {}
        self.temperature_scale = None
        self.NuHeat = None
        self.tz = None
        self.disco = 0

    def start(self):
        if self.get_credentials():
            self.check_params()
            if self.refresh_token():
                self.discover()
            else:
                self.auth_prompt()
        # self.poly.add_custom_config_docs("<b>And this is some custom config data</b>")

    def get_credentials(self):
        LOGGER.info('---- Environment: ' + self.poly.stage + ' ----')
        if self.poly.stage == 'test':
            if 'clientId' in self.poly.init['oauth']['test']:
                self.server_data['clientId'] = self.poly.init['oauth']['test']['clientId']
            else:
                LOGGER.error('Unable to find Client ID in the init data')
                return False
            if 'secret' in self.poly.init['oauth']['test']:
                self.server_data['clientSecret'] = self.poly.init['oauth']['test']['secret']
            else:
                LOGGER.error('Unable to find Client Secret in the init data')
                return False
            if 'redirectUrl' in self.poly.init['oauth']['test']:
                self.server_data['url'] = self.poly.init['oauth']['test']['redirectUrl']
            else:
                LOGGER.error('Unable to find URL in the init data')
                return False
            if self.poly.init['worker']:
                self.server_data['worker'] = self.poly.init['worker']
            else:
                return False
            return True
        elif self.poly.stage == 'prod':
            if 'clientId' in self.poly.init['oauth']['prod']:
                self.server_data['clientId'] = self.poly.init['oauth']['prod']['clientId']
            else:
                LOGGER.error('Unable to find Client ID in the init data')
                return False
            if 'secret' in self.poly.init['oauth']['test']:
                self.server_data['clientSecret'] = self.poly.init['oauth']['prod']['secret']
            else:
                LOGGER.error('Unable to find Client Secret in the init data')
                return False
            if 'redirectUrl' in self.poly.init['oauth']['test']:
                self.server_data['url'] = self.poly.init['oauth']['prod']['redirectUrl']
            else:
                LOGGER.error('Unable to find URL in the init data')
                return False
            if self.poly.init['worker']:
                self.server_data['worker'] = self.poly.init['worker']
            else:
                return False
            return True

    def auth_prompt(self):
        _auth_url = "https://identity.mynuheat.com/connect/authorize"
        _response_type = "code"
        _scope = "openapi openid profile offline_access"

        _user_auth_url = _auth_url + \
                        "?client_id=" + self.server_data['clientId'] + \
                        "&response_type=" + _response_type + \
                        "&scope=" + _scope + \
                        "&redirect_uri=" + self.server_data['url'] + \
                        "&state=" + self.server_data['worker']

        self.addNotice(
            {'myNotice': 'Click <a href="' + _user_auth_url + '">here</a> to link your NuHeat account'})

    def oauth(self, oauth):
        LOGGER.info('OAUTH Received: {}'.format(oauth))
        if 'code' in oauth:
            self.get_token(oauth['code'])

    def get_token(self, code):
        _token_url = "https://identity.mynuheat.com/connect/token"
        _response_type = "token"
        _scope = "openapi openid profile offline_access"

        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        payload = {"grant_type": "authorization_code",
                   "code": code,
                   "client_id": self.server_data['clientId'],
                   "response_type": _response_type,
                   "client_secret": self.server_data['clientSecret'],
                   "scope": _scope,
                   "redirect_uri": self.server_data['url']}

        try:
            r = requests.post(_token_url, headers=headers, data=payload)
            if r.status_code == requests.codes.ok:
                try:
                    resp = r.json()
                    id_token = resp['id_token']
                    access_token = resp['access_token']
                    refresh_token = resp['refresh_token']
                    expires_in = resp['expires_in']

                    cust_data = {'id_token': id_token,
                                 'access_token': access_token,
                                 'refresh_token': refresh_token,
                                 'expires_in': expires_in}

                    self.saveCustomData(cust_data)
                    self.NuHeat = NuHeat(access_token)
                    self.remove_notices_all()
                    return True
                except KeyError as ex:
                    LOGGER.error("get_token Error: " + str(ex))
            else:
                return False
        except requests.exceptions.RequestException as e:
            LOGGER.error("NuHeat.set_thermostat_setpoint Error: " + str(e))

    def refresh_token(self):
        token_url = "https://identity.mynuheat.com/connect/token"

        if 'refresh_token' in self.polyConfig['customData']:
            refresh_token = self.polyConfig['customData']['refresh_token']

            _response_type = "token"
            _scope = "openapi openid profile offline_access"

            headers = {'Content-Type': 'application/x-www-form-urlencoded'}

            payload = {"grant_type": "refresh_token",
                       "client_id": self.server_data['clientId'],
                       "response_type": _response_type,
                       "client_secret": self.server_data['clientSecret'],
                       "scope": _scope,
                       "redirect_uri": self.server_data['url'],
                       "refresh_token": refresh_token}

            try:
                r = requests.post(token_url, headers=headers, data=payload)
                if r.status_code == requests.codes.ok:
                    try:
                        resp = r.json()
                        id_token = resp['id_token']
                        access_token = resp['access_token']
                        refresh_token = resp['refresh_token']
                        expires_in = resp['expires_in']

                        cust_data = {'id_token': id_token,
                                     'access_token': access_token,
                                     'refresh_token': refresh_token,
                                     'expires_in': expires_in}

                        self.saveCustomData(cust_data)
                        self.NuHeat = NuHeat(access_token)
                        return True
                    except KeyError as ex:
                        LOGGER.error("get_token Error: " + str(ex))
                else:
                    return False
            except requests.exceptions.RequestException as e:
                LOGGER.error("NuHeat.set_thermostat_setpoint Error: " + str(e))
        else:
            return False

    def shortPoll(self):
        if self.disco == 1:
            for node in self.nodes:
                self.nodes[node].query()

    def longPoll(self):
        """
        The token expires every 1 hour (3600 seconds).  The long Poll is set to 30 minutes by default
        and refreshes on Nodeserver start.
        :return:
        """
        self.refresh_token()

    def query(self, command=None):
        self.check_params()
        for node in self.nodes:
            self.nodes[node].reportDrivers()

    def discover(self, *args, **kwargs):
        thermostats = self.NuHeat.get_thermostat()
        for stat in thermostats:
            name = stat['name']
            stat_address = stat['serialNumber']
            energy_log_day_address = "eld" + str(stat_address)
            energy_log_week_address = "elw" + str(stat_address)
            self.addNode(ThermostatNode(self, stat_address, stat_address, name, self.NuHeat))
            time.sleep(2)
            self.addNode(EnergyLogDayNode(self, stat_address, energy_log_day_address, "Energy-Day", self.NuHeat))
            time.sleep(2)
            self.addNode(EnergyLogWeekNode(self, stat_address, energy_log_week_address, "Energy-Week", self.NuHeat))
            time.sleep(2)

        self.disco = 1

    def delete(self):
        LOGGER.info('Removing Nuheat Nodeserver')

    def stop(self):
        LOGGER.debug('NodeServer stopped.')

    def process_config(self, config):
        # this seems to get called twice for every change, why?
        # What does config represent?
        LOGGER.info("process_config: Enter config={}".format(config));
        LOGGER.info("process_config: Exit");

    def check_params(self):
        """
        This is an example if using custom Params for user and password and an example with a Dictionary
        """
        self.removeNoticesAll()
        default_tz = "America/New_York"

        if 'tz' in self.polyConfig['customParams']:
            self.tz = self.polyConfig['customParams']['tz']
        else:
            self.tz = default_tz
            LOGGER.info("Change the TimeZone to match your location and restart")
            self.addNotice("Change the TimeZone to match your location and restart")

        self.addCustomParam({'tz': default_tz})

    def remove_notice_test(self, command):
        LOGGER.info('remove_notice_test: notices={}'.format(self.poly.config['notices']))
        # Remove all existing notices
        self.removeNotice('test')

    def remove_notices_all(self):
        LOGGER.info('remove_notices_all: notices={}'.format(self.poly.config['notices']))
        # Remove all existing notices
        self.removeNoticesAll()

    def update_profile(self, command):
        LOGGER.info('update_profile:')
        st = self.poly.installprofile()
        return st

    id = 'controller'
    commands = {
        'QUERY': query,
        'DISCOVER': discover,
        'UPDATE_PROFILE': update_profile
        # 'REMOVE_NOTICES_ALL': remove_notices_all,
        # 'REMOVE_NOTICE_TEST': remove_notice_test
    }
    drivers = [{'driver': 'ST', 'value': 1, 'uom': 2}]


if __name__ == "__main__":
    try:
        polyglot = polyinterface.Interface('NuHeat')
        polyglot.start()
        control = Controller(polyglot)
        control.runForever()
    except (KeyboardInterrupt, SystemExit):
        polyglot.stop()
        sys.exit(0)