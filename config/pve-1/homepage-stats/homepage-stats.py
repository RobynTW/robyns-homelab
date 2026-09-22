#!/usr/bin/env python3

import json
import subprocess
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer


GLANCES = "http://127.0.0.1:61208"


def get_json(path):
    with urllib.request.urlopen(GLANCES + path, timeout=3) as response:
        return json.loads(response.read())


def get_stats():
    cpu = get_json("/api/4/cpu")
    mem = get_json("/api/4/mem")
    sensors = get_json("/api/4/sensors")
    fs = get_json("/api/4/fs")

    temperature = None

    for sensor in sensors:
        if sensor.get("label") == "Package id 0":
            temperature = sensor.get("value")
            break

    if temperature is None:
        for sensor in sensors:
            if sensor.get("label") == "Composite":
                temperature = sensor.get("value")
                break

    root = None

    for filesystem in fs:
        if filesystem.get("mnt_point") == "/":
            root = filesystem
            break

    swap = subprocess.check_output(
        ["free", "-b"],
        text=True
    )

    swap_line = next(
        line for line in swap.splitlines()
        if line.startswith("Swap:")
    )

    swap_parts = swap_line.split()

    swap_total = int(swap_parts[1])
    swap_used = int(swap_parts[2])

    swap_percent = (
        round((swap_used / swap_total) * 100, 1)
        if swap_total > 0
        else 0
    )

    uptime = subprocess.check_output(
        ["uptime", "-p"],
        text=True
    ).strip()

    return {
        "cpu": cpu.get("total"),
        "memory": mem.get("percent"),
        "swap": swap_percent,
        "temperature": temperature,
        "uptime": uptime,
        "root": root.get("percent") if root else None,
        "root_used": root.get("used") if root else None,
        "root_size": root.get("size") if root else None,
    }


class Handler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path != "/stats":
            self.send_response(404)
            self.end_headers()
            return

        try:
            data = get_stats()

            payload = json.dumps(data).encode()

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()

            self.wfile.write(payload)

        except Exception as error:
            payload = json.dumps({
                "error": str(error)
            }).encode()

            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()

            self.wfile.write(payload)

    def log_message(self, format, *args):
        return


HTTPServer(("0.0.0.0", 61209), Handler).serve_forever()
