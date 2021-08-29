#!/bin/bash
# SPDX-License-Identifier: MIT
# Copyright 2020 Johannes Eigner <jo-hannes@dev-urandom.de>

# Install craftbeerpi_exporter on your system

set -e

# main
function main
{
    readonly destPath="/usr/bin/"
    readonly systemdUnitDir="/etc/systemd/system/"

    # check if we have root rights
    if [[ $EUID -ne 0 ]]; then
        echo "Error: This script must be run as root" 
        exit 1
    fi
    # check if destination path exists
    if [[ ! -d "${destPath}" ]]; then
        echo "Error: Target directory '${destPath}' does not exist"
        echo "  You may need to create it first with:"
        echo "  mkdir -p ${destPath}"
        exit 1
    fi

    # install required packages
    # shellcheck disable=SC2046
    apt install $(grep -v '#' requirementsDebian.txt)

    # install the exporter
    install -o root -g root -m 0755 craftbeerpi_exporter.py "${destPath}/craftbeerpi_exporter"
    # install systemd service file
    install -o root -g root -m 0755 craftbeerpi_exporter.service "${systemdUnitDir}/craftbeerpi_exporter.service"
    # enable and install craftbeerpi_exporter.service
    systemctl daemon-reload
    systemctl enable craftbeerpi_exporter.service
    systemctl start craftbeerpi_exporter.service

    echo "craftbeerpi_exporter successfully installed"

    exit 0
}

main "$@"
