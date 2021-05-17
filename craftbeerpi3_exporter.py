#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright 2020 Johannes Eigner <jo-hannes@dev-urandom.de>

import argparse
from prometheus_client import start_http_server, Metric, REGISTRY
import json
import requests
import time


def fahrenheit2celsius(temp):
  return ( temp - 32 ) / 1.8


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
    metric = Metric('cbp3_exporter_version_info',
        'Version of craftbeer pi 3 exporter', 'summary')
    metric.add_sample('cbp3_exporter_version_info', value=1, labels={})
    yield metric

    # Fetch the sensor data http://{addr}:{port}/api/sensor/
    url = 'http://{0}:{1}/api/sensor/'.format(self._addr, self._port)
    self.sensors = json.loads(requests.get(url).content.decode('UTF-8'))
    metric = Metric('cbp3_sensor_temp_celsius', 'craftbeer pi 3 temperature sensor', 'gauge')
    for sensorId in self.sensors:
      metric.add_sample(
        'cbp3_sensor_temp_celsius',
        value=self.getSensorTempCelsius(sensorId),
        labels={'name': self.sensors[sensorId]['name']} )
    yield metric

    # fetch the actor data http://{addr}:{port}/api/actor/
    url = 'http://{0}:{1}/api/actor/'.format(self._addr, self._port)
    self.actors = json.loads(requests.get(url).content.decode('UTF-8'))
    metric = Metric('cbp3_actor_power_ratio', 'craftbeer pi 3 actor power', 'gauge')
    for actorId in self.actors:
      metric.add_sample(
        'cbp3_actor_power_ratio',
        value=self.getActorPowerRation(actorId),
        labels={'name': self.actors[actorId]['name']})
    yield metric

    # Fetch the fermenter data http://{addr}:{port}/api/fermenter/
    url = 'http://{0}:{1}/api/fermenter/'.format(self._addr, self._port)
    fermenters = json.loads(requests.get(url).content.decode('UTF-8'))
    metric = Metric('cbp3_fermenter', 'craftbeer pi 3 fermenter metrics', 'gauge')
    for fermenterId in fermenters:
      name = fermenters[fermenterId]['name']
      # get operation state
      metric.add_sample(
        'cbp3_fermenter_state',
        value=fermenters[fermenterId]['state'],
        labels={'fermenter': name})
      # get target temperature
      metric.add_sample(
        'cbp3_fermenter_target_temp_celsius',
        value=fermenters[fermenterId]['target_temp'],
        labels={'fermenter': name})
      # get metrics of all temperature sensors
      for sensorName in ['sensor', 'sensor2', 'sensor3']:
        sensorId = fermenters[fermenterId][sensorName]
        if sensorId:
          metric.add_sample(
            'cbp3_fermenter_temp_celsius',
            value=self.getSensorTempCelsius(sensorId),
            labels={'fermenter': name, 'sensor': sensorName})
      # get cooler power ration
      coolerId = fermenters[fermenterId]['cooler']
      if coolerId:
        metric.add_sample(
          'cbp3_fermenter_cooler_power_ratio',
          value=self.getActorPowerRation(coolerId),
          labels={'fermenter': name})
      # get heater power ration
      heaterId = fermenters[fermenterId]['heater']
      if heaterId:
        metric.add_sample(
          'cbp3_fermenter_heater_power_ratio',
          value=self.getActorPowerRation(heaterId),
          labels={'fermenter': name})
    yield metric

    # Fetch the kettle data http://{addr}:{port}/api/kettle/
    url = 'http://{0}:{1}/api/kettle/'.format(self._addr, self._port)
    kettles = json.loads(requests.get(url).content.decode('UTF-8'))
    metric = Metric('cbp3_kettle', 'craftbeer pi 3 kettle metrics', 'gauge')
    for kettleId in kettles:
      name = kettles[kettleId]['name']
      # get operation state
      metric.add_sample(
        'cbp3_kettle_state',
        value=kettles[kettleId]['state'],
        labels={'kettle': name})
      # get target temperature
      metric.add_sample(
        'cbp3_kettle_target_temp_celsius',
        value=kettles[kettleId]['target_temp'],
        labels={'kettle': name})
      # get kettle temperature
      sensorId = kettles[kettleId]['sensor']
      if sensorId:
        metric.add_sample(
          'cbp3_kettle_temp_celsius',
          value=self.getSensorTempCelsius(sensorId),
          labels={'kettle': name})
      # get heater power ration
      heaterId = kettles[kettleId]['heater']
      if heaterId:
        metric.add_sample(
          'cbp3_kettle_heater_power_ratio',
          value=self.getActorPowerRation(heaterId),
          labels={'kettle': name})
      # get cooler power ration
      agitatorId = kettles[kettleId]['agitator']
      if agitatorId:
        metric.add_sample(
          'cbp3_kettle_agiator_power_ratio',
          value=self.getActorPowerRation(agitatorId),
          labels={'kettle': name})
    yield metric

def main():
  try:
    # parse arguments
    parser = argparse.ArgumentParser(description='Prometheus exporter for craftbeer pi 3')
    parser.add_argument('-l', metavar='port', default=9303, type=int, required=False, help='Listen port of exporter')
    parser.add_argument('-a', metavar='addr', default='127.0.0.1', required=False, help='Address of craftbeer pi 3')
    parser.add_argument('-p', metavar='port', default=5000, type=int, required=False, help='Port of craftbeer pi 3')
    args = parser.parse_args()
    # start server
    start_http_server(args.l)
    REGISTRY.register(Cbp3Collector(args.a, args.p))
    while True:
      time.sleep(1)

  except KeyboardInterrupt:
    print(" Interrupted")
    exit(0)


if __name__ == '__main__':
    main()
