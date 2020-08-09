#!/usr/bin/python3

import sys

if sys.version_info[0] < 3:
    raise Exception("Must be using Python 3")

import http.server
if sys.version_info[1] < 7:
    # Can't use threaded HTTP server, which is new in 3.7
    server_class = http.server.HTTPServer
else:
    server_class = http.server.ThreadingHTTPServer
from http.server import BaseHTTPRequestHandler

import requests
from urllib.parse import urlparse, parse_qs
import urllib3
import os

# Settings
API_KEY = os.environ["UNMS_KEY"]
HEADERS = {"x-auth-token": API_KEY}
TIMEOUT = 5  # In seconds
SERVER_ADDRESS = ('', 8000)

if "UNMS_HOST" in os.environ:
    UNMS_HOST = os.environ["UNMS_HOST"]
else:
    UNMS_HOST = "unms.tomesh.net"


VERSION = "0.1.0"

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_devices_json():
    r = requests.get("https://" + UNMS_HOST + "/nms/api/v2.1/devices", verify=False, headers=HEADERS, timeout=TIMEOUT)
    r.raise_for_status()  # Error if not a 200 OK response
    return r.json()


def get_ifaces_json(device_id):
    """
    Returns interface JSON, for the device id provided.
    """

    r = requests.get("https://" + UNMS_HOST + "/nms/api/v2.1/devices/" + device_id + "/interfaces", verify=False, headers=HEADERS, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()


def find_device_id_by_name(name, devices):
    for dev in devices:
        if dev["identification"]["name"] == name:
            return dev["identification"]["id"]
    return ""

def find_device_id_by_ip(ip, devices):
    for dev in devices:
        if dev["ipAddress"].split('/')[0]  == ip:
            return dev["identification"]["id"]
    return ""


def write_prometheus_data(target_id, devices, ifaces, writer):
    """
    Writes a string of prometheus data, using the passed JSON.

    devices: devices JSON, in Python format
    ifaces: Interfaces JSON for the target (using the target's device id), in Python format.

    writer:
        Where data is written to. Any class with a write() method will work.
        sys.stdout can be used to print to stdout. This allows data to be streamed!
    """

    def write(string):
        writer.write(string.encode()+b"\n")

    write('unms_exporter_version{version="' + VERSION + '"} 1')
    
    for dev in devices:
        if dev["identification"]["id"] != target_id:
            continue

        write('node_uname_info{nodename="' + dev['identification']['name'] + '", sysname="' +  dev['identification']['model'] + '", release="' +  dev['identification']['firmwareVersion'] + '"} 1')
        write("ram " + str(dev['overview']['ram']))
        write("cpu " + str(dev['overview']['cpu']))
        write("uptime " + str(dev['overview']['uptime']))

        if dev['overview'].get('frequency') is not None:
            write("frequency " + str(dev['overview']['frequency']))

        if dev['overview'].get("signal") is not None:
            write("signal " + str(dev['overview']["signal"]))
        
        if dev['overview'].get("downlinkCapacity") is not None:
            write("downlinkCapacity " + str(dev['overview']['downlinkCapacity']))
            write("uplinkCapacity " + str(dev['overview']['uplinkCapacity']))

        for iface in ifaces:
            name = iface['identification']['name']

            if iface['status']['status'] == 'active':
                write('node_network_up{device="' + name + '"} 1')
            else:
                write('node_network_up{device="' + name + '"} 0')

            write('node_network_receive_bytes_total{device="' + name + '"} ' + str(iface['statistics']['rxbytes']))
            write('node_network_transmit_bytes_total{device="' + name + '"} ' + str(iface['statistics']['txbytes']))
            write('node_network_receive_rate{device="' + name + '"} ' + str(iface["statistics"]["rxrate"]))
            write('node_network_transmit_rate{device="' + name + '"} ' + str(iface["statistics"]["txrate"]))
            write('node_network_mtu_bytes{device="' + name + '"} ' + str(iface["mtu"]))
            write('node_network_dropped_total{device="' + name + '"} ' + str(iface["statistics"]["dropped"]))  # Not sure whether receive or transmit, or both
            
        # The target has been found and all data has been written
        break


class HTTPRequestHandler(BaseHTTPRequestHandler):

    server_version = "unms_exporter/" + VERSION
    error_content_type = "text/plain"
    error_message_format = "%(code)d %(message)s\n%(explain)s"

    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path != "/metrics":
            self.send_error(404)
            return

        # Verify target string
        params = parse_qs(parsed.query)
        if "target" in params:
            target = params["target"][-1]
            type = "ip"
        elif "targetName" in params:
            target= params["targetName"][-1]
            type = "name"
        else:
            self.send_error(400, explain="No target provided.")
            return

        print (target)
        try:
            devices = get_devices_json()
            if type == "ip":
               target_id = find_device_id_by_ip(target, devices)
            if type == "name":
               target_id = find_device_id_by_name(target, devices)

            if target_id == "":
                self.send_error(400, explain="Target name does not exist.")
                return

            ifaces = get_ifaces_json(target_id)

        except Exception as e:
            self.send_error(500, explain=e.__str__())
            return

        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        write_prometheus_data(target_id, devices, ifaces, self.wfile)


def main():
    httpd = server_class(SERVER_ADDRESS, HTTPRequestHandler)
    httpd.serve_forever()


if __name__ == "__main__":
    main()
