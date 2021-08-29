# craftbeerpi_exporter
* [CraftBeerPi3](https://github.com/Manuel83/craftbeerpi3) exporter for Prometheus
* [CraftBeerPi4](https://github.com/Manuel83/craftbeerpi4) exporter for Prometheus

Based on Robust Perception's python exporter example: For more information see (https://www.robustperception.io/writing-json-exporters-in-python)

## Installation
On Debian systems just execute install.sh
```shell
sudo ./install.sh
```
This script should work on all Debian based systems but it is only tested on Debian.

## Configuration
**Note:** When running the craftbeerpi_exporter on the same system as CraftBeerPi 3, no configuration is needed.

The following configuration options are available.
| Option     | Description                     | Default   |
| ---------- | ------------------------------- | --------- |
| -l port    | Listen port of exporter         | 9826      |
| -a addr    | Address of CraftBeerPi          | 127.0.0.1 |
| -p port    | Port of CraftBeerPi             | 5000      |
| -c version | Version of CraftbeerPi [3|4]    | 3         |

Just add the options to the service file.
