import sys
import requests


class NuHeat:
    def __init__(self, access_token):
        self.api_url = "https://api.mynuheat.com/api/v1"
        self.headers = {'Authorization': 'Bearer ' + access_token}

    def nuheat_celsius_to_fahrenheit(self, json_celsius):
        celsius = json_celsius / 100
        fahrenheit = round((celsius * 9/5) + 32, 0)
        return fahrenheit

    def nuheat_fahrenheit_to_celsius_json(self, fahrenheit):
        celsius = (int(fahrenheit) - 32) * 5/9
        json_celsius = round(celsius * 100)
        return json_celsius

    def nuheat_celsius_to_json(self, celsius):
        json_celsius = int(celsius) * 100
        return json_celsius

    def nuheat_celsius_to_normal(self, json_celsius):
        celsius = round(json_celsius / 100, 0)
        return celsius

    def nuheat_cents_to_dollars(self, cents):
        usd = round(cents / 100, 2)
        return usd

    def get_account(self):
        try:
            r = requests.get(self.api_url + "/account", headers=self.headers)
            if r.status_code == requests.codes.ok:
                resp = r.json()
                return resp
            else:
                return None
        except requests.exceptions.RequestException as e:
            print("NuHeat.get_account Error: " + str(e))

    def get_thermostat(self):
        try:
            r = requests.get(self.api_url + "/Thermostat", headers=self.headers)
            if r.status_code == requests.codes.ok:
                resp = r.json()
                return resp
            else:
                return None
        except requests.exceptions.RequestException as e:
            print("NuHeat.get_thermostat Error: " + str(e))

    def set_thermostat_setpoint(self, serial_number, setpoint):
        put_headers = self.headers
        put_headers.update({'Content-Type': 'application/json'})

        payload = {'serialNumber': serial_number,
                    'scheduleMode': 2,
                    'setPointTemp': setpoint}

        try:
            r = requests.put(self.api_url + "/Thermostat", headers=put_headers, json=payload)
            print(r.content)
            if r.status_code == requests.codes.ok:
                resp = r.json()
                return resp
            else:
                return None
        except requests.exceptions.RequestException as e:
            print("NuHeat.set_thermostat_setpoint Error: " + str(e))

    def get_energy_log_day(self, serial_number, date):
        energy_log_url = self.api_url + "/EnergyLog/Day/" + serial_number + "/" + date
        try:
            r = requests.get(energy_log_url, headers=self.headers)
            if r.status_code == requests.codes.ok:
                resp = r.json()
                monday_is_first_day = resp['mondayIsFirstDay']
                minutes = 0
                raw_energy_kw_hour = 0
                raw_charge_kw_hour = 0
                for entry in resp['energyUsage']:
                    minutes += entry['minutes']
                    raw_energy_kw_hour += entry['energyKWattHour']
                    raw_charge_kw_hour += entry['chargeKWattHour']

                energy_kw_hour = round(raw_energy_kw_hour, 2)
                cents_charge_kw_hour = round(raw_charge_kw_hour, 2)
                usd_charge_kw_hour = self.nuheat_cents_to_dollars(cents_charge_kw_hour)
                energy = [minutes, energy_kw_hour, usd_charge_kw_hour]
                return energy
            else:
                return None
        except requests.exceptions.RequestException as e:
            print("NuHeat.get_energy_log_day Error: " + str(e))

    def get_energy_log_week(self, serial_number, date):
        energy_log_url = self.api_url + "/EnergyLog/Week/" + serial_number + "/" + date
        try:
            r = requests.get(energy_log_url, headers=self.headers)
            if r.status_code == requests.codes.ok:
                resp = r.json()
                monday_is_first_day = resp['mondayIsFirstDay']
                minutes = 0
                raw_energy_kw_hour = 0
                raw_charge_kw_hour = 0
                for entry in resp['energyUsage']:
                    minutes += entry['minutes']
                    raw_energy_kw_hour += entry['energyKWattHour']
                    raw_charge_kw_hour += entry['chargeKWattHour']

                energy_kw_hour = round(raw_energy_kw_hour, 2)
                cents_charge_kw_hour = round(raw_charge_kw_hour, 2)
                usd_charge_kw_hour = self.nuheat_cents_to_dollars(cents_charge_kw_hour)
                energy = [minutes, energy_kw_hour, usd_charge_kw_hour]
                return energy
            else:
                return None
        except requests.exceptions.RequestException as e:
            print("NuHeat.get_energy_log_day Error: " + str(e))
