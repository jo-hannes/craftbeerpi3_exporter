# craftbeerpi3_exporter
[CraftBeerPi 3](https://github.com/Manuel83/craftbeerpi3) exporter for Prometheus

Based on Robust Perception's python exporter example: For more information see (https://www.robustperception.io/writing-json-exporters-in-python)

## Installation
On Debian systems just execute install.sh
```shell
sudo ./install.sh
```
This script should work on all Debian based systems but it is only tested on Debian.

## Configuration
**Note:** When running the craftbeerpi3_exporter on the same system as CraftBeerPi 3, no configuration is needed.

The following configuration options are available.
| Option  | Description              | Default   |
| ------- | ------------------------ | --------- |
| -l port | Listen port of exporter  | 9303      |
| -a addr | Address of CraftBeerPi 3 | 127.0.0.1 |
| -p port | Port of CraftBeerPi 3    | 5000      |

Just add the options to the service file.
