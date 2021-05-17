#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-3-Clause
# Copyright 2020 Johannes Eigner <jo-hannes@dev-urandom.de>

import argparse
from prometheus_client import start_http_server, Metric, REGISTRY
import json
import requests
import time


def metricsName(name):
  '''Create sane names for prometheus metrics'''
  # regex allowed: [a-zA-Z_:][a-zA-Z0-9_:]*
  # TODO check for regex and replace other chars
  # - is not allowed in metrics names!
  saneName = name.replace('-', '_')
  # Replace special german characters
  saneName = saneName.replace('ä', 'ae').replace('ö', 'oe').replace('ü', 'ue').replace('ß', 'ss')
  return saneName


def fahrenheit2celsius(temp):
  return ( temp - 32 ) / 1.8


class Cbp3Collector(object):
  def __init__(self, addr, port):
    self._addr = addr
    self._port = port
  def collect(self):
    # Add version of this SW to metrics
    # This also helps in case no sensor, actor, fermenter oe kettle is defined.
    metric = Metric('cbp3_exporter_version_info',
        'Version of craftbeer pi 3 exporter', 'summary')
    metric.add_sample('cbp3_exporter_version_info', value=1, labels={})
    yield metric

    # Fetch the sensor data http://{addr}:{port}/api/sensor/
    url = 'http://{0}:{1}/api/sensor/'.format(self._addr, self._port)
    sensors = json.loads(requests.get(url).content.decode('UTF-8'))
    metric = Metric('cbp3_sensor_temp_celsius', 'craftbeer pi 3 temperature sensor', 'gauge')
    for sensor in sensors:
      if sensors[sensor]['instance']['unit'] == '°F':
        temp = fahrenheit2celsius(sensors[sensor]['instance']['value'])
      else:
        temp = sensors[sensor]['instance']['value']
      metric.add_sample(
        'cbp3_sensor_temp_celsius',
        value=temp,
        labels={'name': sensors[sensor]['name']} )
    yield metric

    # fetch the actor data http://{addr}:{port}/api/actor/
    url = 'http://{0}:{1}/api/actor/'.format(self._addr, self._port)
    actors = json.loads(requests.get(url).content.decode('UTF-8'))
    metric = Metric('cbp3_actor_power_ratio', 'craftbeer pi 3 actor power', 'gauge')
    for actor in actors:
      metric.add_sample(
        'cbp3_actor_power_ratio',
        value=actors[actor]['state'] * actors[actor]['power'] / 100,
        labels={'name': actors[actor]['name']})
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
