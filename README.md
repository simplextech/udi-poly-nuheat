# NuHeat Signature Nodeserver

#### Installation

Install from the Polyglot Cloud store.

#### Requirements

- ISY994i
- Polyglot Cloud
- NuHeat Signature Thermostat(s)
- [My NuHeat](https://mynuheat.com) Portal account

#### Usage
- On start a notice will be created with a link to step through the NuHeat OAuth process
- After successful authentication a Nuheat Controller node is created
  - Open the Admin Console
  - Select the Nuheat Controller
  - Click Discover
  - This will connect to the NuHeat API and discover your connected thermostats
  - Two nodes should be created.  One for the Thermostat and One for daily energy information
  - If the energy node is not created click discover again as there is sometimes a timing issue with cloud services
 
- Energy Use information depends on what you have configured for each thermostat within the NuHeat configuration.
This can be done through the NuHeat web interface.
  - [My NuHeat](https://mynuheat.com) Portal

- Timezone configuration is used to get the correct data for Energy Log retrieval.  Enter
your timezone in the Polyglot configuration based upon your location or close enough
to be in the same Day.  A list of acceptable timezones is available here
  - [List of tz database time zones](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones)

#### Features
- Creates Thermostat nodes
- Creates Energy Log node for the daily usage

#### Limitations
- Scheduling is not configurable through the Nodeserver
- Mode setting (away) is not yet configurable
- Tested against a single NuHeat Signature Thermostat.
