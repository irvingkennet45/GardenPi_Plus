# main.py, will be modularized later.
import network
import time
import ntptime
import machine
import socket
import ujson as json
import os
import hashlib

# File paths
SECURITY_FILE = "/logging/security.json"
WHITELIST_FILE = "/logging/whitelist.json"
CONFIG_FILE = "/logging/config.json"
WEATHER_LOG_FILE = "/logging/data.txt"

# Weather checking
last_weather_check = 0

# Relay pin (GPIO15) setup
RELAY_PIN = 15
relay = machine.Pin(RELAY_PIN, machine.Pin.OUT)
relay.value(0)

# Internal timers
last_ntp_sync = 0
schedule_state = {"last_trigger_min": -1, "relay_off_time": 0}

# --------- Utilities ---------
def hash_password(value):
    h = hashlib.sha256()
    h.update(value.encode("utf-8"))
    return h.digest().hex()

def generate_token():
    return hash_password(str(time.ticks_ms()))

def load_security():
    try:
        with open(SECURITY_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_security(data):
    with open(SECURITY_FILE, "w") as f:
        json.dump(data, f)

def parse_headers(req):
    headers = {}
    for line in req.split("\r\n")[1:]:
        if ": " in line:
            k, v = line.split(": ", 1)
            headers[k.lower()] = v
    return headers

def get_cookie(headers, name):
    cookies = headers.get("cookie", "")
    for pair in cookies.split(";"):
        if "=" in pair:
            k, v = pair.strip().split("=", 1)
            if k == name:
                return v
    return None

def verify_session(token):
    data = load_security()
    return token and token == data.get("session_token")

def get_mime_type(path):
    if path.endswith(".css"):
        return "text/css"
    elif path.endswith(".js"):
        return "application/javascript"
    elif path.endswith(".ico"):
        return "image/x-icon"
    elif path.endswith(".gif"):
        return "image/gif"
    elif path.endswith(".png"):
        return "image/png"
    elif path.endswith(".json"):
        return "application/json"
    return "text/html"

# --------- Auth ---------
def verify_credentials(username, password, pin=None):
    data = load_security()

    updated = False
    if "password" in data:
        data["password_hash"] = hash_password(data["password"])
        del data["password"]
        updated = True
    if "pin" in data and len(data["pin"]) < 12:
        data["pin_hash"] = hash_password(data["pin"])
        del data["pin"]
        updated = True
    if updated:
        save_security(data)

    if pin:
        return hash_password(pin) == data.get("pin_hash")
    return data.get("username") == username and hash_password(password) == data.get("password_hash")

def get_device_mac():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    return ":".join(["%02x" % b for b in wlan.config("mac")])

def is_mac_whitelisted():
    mac = get_device_mac()
    try:
        with open(WHITELIST_FILE, "r") as f:
            return mac in json.load(f).get("whitelist", [])
    except:
        return False

def auto_authenticate():
    return is_mac_whitelisted()

# --------- Network ---------
def load_wifi_config():
    try:
        with open(CONFIG_FILE, "r") as f:
            wifi = json.load(f).get("wifi", {})
            return wifi.get("ssid"), wifi.get("wifi_pass")
    except:
        return None, None

def network_config():
    ssid, password = load_wifi_config()
    if not ssid or not password:
        print("[ERROR] Missing WiFi credentials.")
        return
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    attempt = 0
    while not wlan.isconnected():
        if attempt and attempt % 10 == 0:
            print("[NETWORK] retrying in 5 minutes...")
            time.sleep(300)
        print(f"[NETWORK] Connecting to {ssid} (attempt {attempt + 1})")
        wlan.connect(ssid, password)
        for _ in range(10):
            if wlan.isconnected():
                break
            time.sleep(1)
        attempt += 1
    print("[NETWORK] Connected:", wlan.ifconfig())

# --------- NTP ---------
def ntp_config():
    global last_ntp_sync
    now = time.time()
    if now - last_ntp_sync < 21600:
        return time.localtime()
    try:
        ntptime.host = "time.google.com"
        ntptime.settime()
        last_ntp_sync = now
    except:
        print("[NTP] Sync failed.")
        return None

    UTC_OFFSET = -4
    t = time.localtime(time.time() + UTC_OFFSET * 3600)
    return t

# --------- JSON API ---------
def http_json(obj, extra_headers=None):
    body = json.dumps(obj)
    headers = ""
    if extra_headers:
        for k, v in extra_headers.items():
            headers += f"{k}: {v}\r\n"
    return f"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: {len(body)}\r\n{headers}\r\n{body}".encode()

# --------- Misting Control ---------
def update_misting_status(enabled, active):
    try:
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
        config["misting_feature"]["automation_enabled"] = enabled
        config["misting_feature"]["active"] = active
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f)
        relay.value(1 if active else 0)
        return True
    except Exception as e:
        print(f"[ERROR] Misting status update failed: {e}")
        return False

def update_schedule(new_schedule):
    try:
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
        parsed = {}
        for day, times in new_schedule.items():
            mins = []
            for t in times:
                if isinstance(t, str) and ":" in t:
                    h, m = map(int, t.split(":"))
                    mins.append(h * 60 + m)
            parsed[day] = mins
        config["schedule"] = parsed
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f)
        return True
    except Exception as e:
        print(f"[ERROR] Schedule update failed: {e}")
        return False

def log_weather(entry):
    try:
        with open(WEATHER_LOG_FILE, "r") as f:
            history = json.load(f)
    except:
        history = []

    history.append(entry)
    if len(history) > 21:
        history = history[-21:]

    try:
        with open(WEATHER_LOG_FILE, "w") as f:
            json.dump(history, f)
        return True
    except Exception as e:
        print(f"[ERROR] Weather log failed: {e}")
        return False

def fetch_forecast(lat, lon):
    try:
        import urequests
        r = urequests.get(f"https://api.weather.gov/points/{lat},{lon}")
        pt = r.json()
        r.close()
        url = pt["properties"]["forecast"]
        r = urequests.get(url)
        data = r.json()
        r.close()
        return data["properties"]["periods"]
    except Exception as e:
        print(f"[ERROR] Weather fetch failed: {e}")
        return []

def check_weather():
    global last_weather_check
    now = time.time()
    if now - last_weather_check < 21600:
        return
    last_weather_check = now
    try:
        with open(CONFIG_FILE, "r") as f:
            cfg = json.load(f)
        loc = cfg.get("location", {})
        lat = loc.get("lat")
        lon = loc.get("lon")
        if lat is None or lon is None:
            return
        periods = fetch_forecast(lat, lon)
        if not periods:
            return
        max_prob = 0
        for p in periods[:7]:
            v = p.get("probabilityOfPrecipitation", {}).get("value")
            if v is None:
                v = 0
            if v > max_prob:
                max_prob = v
        if max_prob >= 60:
            update_misting_status(False, False)
        log_weather({"timestamp": now, "periods": periods[:7]})
    except Exception as e:
        print(f"[ERROR] Weather check failed: {e}")

def handle_get_config():
    try:
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
        return http_json({
            "automation_enabled": config.get("misting_feature", {}).get("automation_enabled", False),
            "active": config.get("misting_feature", {}).get("active", False),
            "schedule": config.get("schedule", {}),
            "location": config.get("location", {})
        })
    except Exception as e:
        return http_json({"error": str(e)})

# --------- Schedule Runner ---------
def run_schedule():
    check_weather()
    t = time.localtime(time.time() - 14400)  # Adjust for UTC-4
    current_min = t[3] * 60 + t[4]
    today = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"][t[6]]

    try:
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
        auto_enabled = config.get("misting_feature", {}).get("automation_enabled", False)
        active_manual = config.get("misting_feature", {}).get("active", False)
        schedule = config.get("schedule", {}).get(today, [])

        now = time.time()

        if active_manual:
            relay.value(1)
            return

        if auto_enabled and current_min in schedule and current_min != schedule_state["last_trigger_min"]:
            relay.value(1)
            schedule_state["last_trigger_min"] = current_min
            schedule_state["relay_off_time"] = now + 480  # 8 minutes on

        elif now >= schedule_state.get("relay_off_time", 0):
            relay.value(0)

    except Exception as e:
        print(f"[ERROR] run_schedule failed: {e}")

# --------- Web Server ---------
def serve_file(path):
    try:
        if os.stat(path)[0] & 0x4000:
            path += "/index.html"
        with open(path, "rb") as f:
            content_type = get_mime_type(path)
            yield f"HTTP/1.1 200 OK\r\nContent-Type: {content_type}\r\n\r\n".encode()
            while True:
                chunk = f.read(512)
                if not chunk:
                    break
                yield chunk
    except Exception as e:
        print(f"[ERROR] serve_file: {e}")
        yield b"HTTP/1.1 404 Not Found\r\n\r\nFile Not Found"

def web_server():
    addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]
    s = socket.socket()
    s.bind(addr)
    s.listen(1)
    print("[WEB] Server running at http://" + network.WLAN(network.STA_IF).ifconfig()[0])

    while True:
        run_schedule()
        cl, addr = s.accept()
        req = cl.recv(1024).decode("utf-8")
        if not req:
            cl.close()
            continue

        headers = parse_headers(req)
        lines = req.split("\r\n")
        method, path = lines[0].split(" ")[:2]
        session = get_cookie(headers, "session")
        authenticated = verify_session(session) or auto_authenticate()

        if method == "POST" and path == "/api/auth":
            data = json.loads(req.split("\r\n\r\n", 1)[-1])
            if verify_credentials(data.get("username", ""), data.get("password", ""), data.get("pin")):
                token = generate_token()
                sec = load_security()
                sec["session_token"] = token
                save_security(sec)
                headers = {"Set-Cookie": f"session={token}; Path=/"}
                if data.get("remember"):
                    headers["Set-Cookie"] += "; Max-Age=604800"
                cl.send(http_json({"success": True, "token": token}, headers))
            else:
                cl.send(http_json({"success": False, "message": "Invalid credentials"}))

        elif method == "POST" and path == "/api/misting":
            data = req.split("\r\n\r\n", 1)[-1]
            cl.send(update_misting_status(**json.loads(data)) and http_json({"success": True}) or http_json({"success": False}))

    while True:
        run_schedule()
        cl, addr = s.accept()
        req = cl.recv(1024).decode("utf-8")
        if not req:
            cl.close()
            continue

        lines = req.split("\r\n")
        method, path = lines[0].split(" ")[:2]

        if method == "POST" and path == "/api/misting":
            data = req.split("\r\n\r\n", 1)[-1]
            cl.send(update_misting_status(**json.loads(data)) and http_json({"success": True}) or http_json({"success": False}))

        elif method == "POST" and path == "/api/schedule":
            data = req.split("\r\n\r\n", 1)[-1]
            cl.send(update_schedule(json.loads(data).get("schedule", {})) and http_json({"success": True}) or http_json({"success": False}))


        elif method == "GET" and path == "/api/config":
            cl.send(handle_get_config())

        else:
            if path != "/" and not authenticated and not path.startswith("/assets"):
                cl.send(b"HTTP/1.1 302 Found\r\nLocation: /\r\n\r\n")
                cl.close()
                continue
            path = "/portal/index.html" if path == "/" else "/portal" + path
            for chunk in serve_file(path):
                try:
                    cl.send(chunk)
                except:
                    break
        cl.close()

        elif method == "POST" and path == "/api/weather_log":
            data = req.split("\r\n\r\n", 1)[-1]
            cl.send(log_weather(json.loads(data)) and http_json({"success": True}) or http_json({"success": False}))

        elif method == "GET" and path == "/api/weather_log":
            try:
                with open(WEATHER_LOG_FILE, "r") as f:
                    log = json.load(f)
            except:
                log = []
            cl.send(http_json({"log": log}))

        elif method == "GET" and path == "/api/config":
            cl.send(handle_get_config())

        else:
            path = "/portal/index.html" if path == "/" else "/portal" + path
            for chunk in serve_file(path):
                try:
                    cl.send(chunk)
                except:
                    break
        cl.close()

# --------- Entry Point ---------
def main():
    network_config()
    t = ntp_config()
    if t:
        machine.RTC().datetime((t[0], t[1], t[2], t[6], t[3], t[4], t[5], 0))
    web_server()

main()