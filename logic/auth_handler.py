''' import network
import time
import ntptime
import machine
import socket
import ujson as json
import os
import hashlib

SECURITY_FILE = "/logging/security.json"
WHITELIST_FILE = "/logging/whitelist.json"

# Hash password or PIN with SHA-256
def hash_password(value):
    return hashlib.sha256(value.encode('utf-8')).hexdigest()

# Verify credentials against stored values
def verify_credentials(username, password, pin=None):
    with open(SECURITY_FILE, "r") as f:
        data = json.load(f)

    # Auto-hash plaintext password if needed
    if "password" in data:
        data["password_hash"] = hash_password(data["password"])
        del data["password"]
        print("[SECURITY] Plaintext password hashed and updated.")
        with open(SECURITY_FILE, "w") as f:
            json.dump(data, f)

    # Auto-hash plaintext PIN if needed
    if "pin" in data and not data["pin"].startswith("$2") and len(data["pin"]) < 12:
        data["pin_hash"] = hash_password(data["pin"])
        del data["pin"]
        print("[SECURITY] Plaintext PIN hashed and updated.")
        with open(SECURITY_FILE, "w") as f:
            json.dump(data, f)

    # Check PIN-based login first
    if pin:
        return hash_password(pin) == data.get("pin_hash")

    # Check username/password login
    hashed_input = hash_password(password)
    return data.get("username") == username and hashed_input == data.get("password_hash")

# Return MAC address of device
def get_device_mac():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    mac = wlan.config('mac')
    return ':'.join(['%02x' % b for b in mac])

# Check if MAC address is in whitelist
def is_mac_whitelisted():
    mac_address = get_device_mac()
    try:
        with open(WHITELIST_FILE, "r") as f:
            whitelist = json.load(f).get("whitelist", [])
            return mac_address in whitelist
    except Exception:
        return False

# Automatically authenticate if MAC is whitelisted
def auto_authenticate():
    return is_mac_whitelisted() '''

# Prototype Auth Handler. Not in use yet.