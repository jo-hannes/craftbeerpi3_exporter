#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright 2020 Johannes Eigner <jo-hannes@dev-urandom.de>

import argparse
from prometheus_client import start_http_server, Metric, REGISTRY
import json
import requests
import time

class Cbp4Collector(object):
  def __init__(self, addr, port):
    self._addr = addr
    self._port = port

  def collect(self):
    # Add version of this SW to metrics
    # This also helps in case no sensor, actor, fermenter oe kettle is defined.
    metric = Metric('cbpi_exporter_version_info', 'Version of craftbeer pi 4 exporter', 'summary')
    metric.add_sample('cbpi_exporter_version_info', value=1, labels={})
    yield metric

    # Fetch sensor config http://{addr}:{port}/sensor/ and then iterate over /sensor/id
    sensor_config_url = 'http://{0}:{1}/sensor/'.format(self._addr, self._port)
    sensor_configs = json.loads(requests.get(sensor_config_url).content.decode('UTF-8'))
    metric = Metric('cbpi_sensor_temp_celsius', 'craftbeer pi 4 temperature sensor', 'gauge')
    for sensor_config in sensor_configs["data"]:
      sensor_value_url = 'http://{0}:{1}/sensor/{2}'.format(self._addr, self._port, sensor_config["id"])
      sensor_value = json.loads(requests.get(sensor_value_url).content.decode('UTF-8'))["value"]

      metric.add_sample( 'cbpi_sensor_temp_celsius', value=sensor_value, labels={'name': sensor_config['name'], 'type': sensor_config["type"]} )
    yield metric

    # Fetch kettle data http://{addr}:{port}/kettle/
    url = 'http://{0}:{1}/kettle/'.format(self._addr, self._port)
    kettles = json.loads(requests.get(url).content.decode('UTF-8'))["data"]
    metric = Metric('cbpi_kettle', 'craftbeer pi 4 kettle metrics', 'gauge')
    for kettle in kettles:
      # get target temperature
      metric.add_sample('cbpi_kettle_temp_celsius', value=kettle['target_temp'], labels={'kettle': kettle["name"], 'sensor': 'target'})
    yield metric


class Cbp3Collector(object):
  def __init__(self, addr, port):
    self._addr = addr
    self._port = port

  def getSensorTempCelsius(self, sensorId):
    if self.sensors[sensorId]['instance']['unit'] == '°F':
      return (self.sensors[sensorId]['instance']['value'] - 32 ) / 1.8
    else:
      return self.sensors[sensorId]['instance']['value']

  def getActorPowerRation(self, actorId):
    return self.actors[actorId]['state'] * self.actors[actorId]['power'] / 100

  def collect(self):
    # Add version of this SW to metrics
    # This also helps in case no sensor, actor, fermenter oe kettle is defined.
    metric = Metric('cbpi_exporter_version_info',
        'Version of craftbeer pi 3 exporter', 'summary')
    metric.add_sample('cbpi_exporter_version_info', value=2, labels={})
    yield metric

    # Fetch the sensor data http://{addr}:{port}/api/sensor/
    url = 'http://{0}:{1}/api/sensor/'.format(self._addr, self._port)
    self.sensors = json.loads(requests.get(url).content.decode('UTF-8'))
    metric = Metric('cbpi_sensor_temp_celsius', 'craftbeer pi 3 temperature sensor', 'gauge')
    for sensorId in self.sensors:
      metric.add_sample(
        'cbpi_sensor_temp_celsius',
        value=self.getSensorTempCelsius(sensorId),
        labels={'name': self.sensors[sensorId]['name']} )
    yield metric

    # fetch the actor data http://{addr}:{port}/api/actor/
    url = 'http://{0}:{1}/api/actor/'.format(self._addr, self._port)
    self.actors = json.loads(requests.get(url).content.decode('UTF-8'))
    metric = Metric('cbpi_actor_power_ratio', 'craftbeer pi 3 actor power', 'gauge')
    for actorId in self.actors:
      metric.add_sample(
        'cbpi_actor_power_ratio',
        value=self.getActorPowerRation(actorId),
        labels={'name': self.actors[actorId]['name']})
    yield metric

    # Fetch the fermenter data http://{addr}:{port}/api/fermenter/
    url = 'http://{0}:{1}/api/fermenter/'.format(self._addr, self._port)
    fermenters = json.loads(requests.get(url).content.decode('UTF-8'))
    metric = Metric('cbpi_fermenter', 'craftbeer pi 3 fermenter metrics', 'gauge')
    for fermenterId in fermenters:
      name = fermenters[fermenterId]['name']
      # get operation state
      metric.add_sample(
        'cbpi_fermenter_state',
        value=fermenters[fermenterId]['state'],
        labels={'fermenter': name})
      # get target temperature
      metric.add_sample(
        'cbpi_fermenter_temp_celsius',
        value=fermenters[fermenterId]['target_temp'],
        labels={'fermenter': name, 'sensor': 'target'})
      # get metrics of all temperature sensors
      for sensorName in ['sensor', 'sensor2', 'sensor3']:
        sensorId = fermenters[fermenterId][sensorName]
        if sensorId:
          metric.add_sample(
            'cbpi_fermenter_temp_celsius',
            value=self.getSensorTempCelsius(sensorId),
            labels={'fermenter': name, 'sensor': sensorName})
      # get cooler power ration
      coolerId = fermenters[fermenterId]['cooler']
      if coolerId:
        metric.add_sample(
          'cbpi_fermenter_actor_power_ratio',
          value=self.getActorPowerRation(coolerId),
          labels={'fermenter': name, 'type': 'cooler'})
      # get heater power ration
      heaterId = fermenters[fermenterId]['heater']
      if heaterId:
        metric.add_sample(
          'cbpi_fermenter_actor_power_ratio',
          value=self.getActorPowerRation(heaterId),
          labels={'fermenter': name, 'type': 'heater'})
    yield metric

    # Fetch the kettle data http://{addr}:{port}/api/kettle/
    url = 'http://{0}:{1}/api/kettle/'.format(self._addr, self._port)
    kettles = json.loads(requests.get(url).content.decode('UTF-8'))
    metric = Metric('cbpi_kettle', 'craftbeer pi 3 kettle metrics', 'gauge')
    for kettleId in kettles:
      name = kettles[kettleId]['name']
      # get operation state
      metric.add_sample(
        'cbpi_kettle_state',
        value=kettles[kettleId]['state'],
        labels={'kettle': name})
      # get target temperature
      metric.add_sample(
        'cbpi_kettle_temp_celsius',
        value=kettles[kettleId]['target_temp'],
        labels={'kettle': name, 'sensor': 'target'})
      # get kettle temperature
      sensorId = kettles[kettleId]['sensor']
      if sensorId:
        metric.add_sample(
          'cbpi_kettle_temp_celsius',
          value=self.getSensorTempCelsius(sensorId),
          labels={'kettle': name, 'sensor': 'sensor'})
      # get heater power ration
      heaterId = kettles[kettleId]['heater']
      if heaterId:
        metric.add_sample(
          'cbpi_kettle_actor_power_ratio',
          value=self.getActorPowerRation(heaterId),
          labels={'kettle': name, 'type': 'heater'})
      # get cooler power ration
      agitatorId = kettles[kettleId]['agitator']
      if agitatorId:
        metric.add_sample(
          'cbpi_kettle_actor_power_ratio',
          value=self.getActorPowerRation(agitatorId),
          labels={'kettle': name, 'type': 'agitator'})
    yield metric


def main():
  try:
    # parse arguments
    parser = argparse.ArgumentParser(description='Prometheus exporter for craftbeer pi 3 and pi 4')
    parser.add_argument('-l', metavar='port', default=9826, type=int, required=False, help='Listen port of exporter')
    parser.add_argument('-a', metavar='addr', default='127.0.0.1', required=False, help='Address of craftbeer pi')
    parser.add_argument('-p', metavar='port', default=5000, type=int, required=False, help='Port of craftbeer pi')
    parser.add_argument('-c', metavar='cbpi-version', default='3', required=False, help='Version of craftbeerpi [3|4]')
    args = parser.parse_args()

    # start server
    start_http_server(args.l)
    if args.c == "3":
      REGISTRY.register(Cbp3Collector(args.a, args.p))
    if args.c == "4":
      REGISTRY.register(Cbp4Collector(args.a, args.p))


    while True:
      time.sleep(1)

  except KeyboardInterrupt:
    print(" Interrupted")
    exit(0)


if __name__ == '__main__':
    main()
