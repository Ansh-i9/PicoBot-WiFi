import network
import socket
import time
from machine import Pin, PWM

# Wi-Fi Configuration
SSID = "YOUR_WIFI_NAME"
PASSWORD = "YOUR_WIFI_PASSWORD"

# - Motor Pin Setup
# Left Motor
in1 = Pin(2, Pin.OUT)
in2 = Pin(3, Pin.OUT)
ena = PWM(Pin(6))
# Right Motor
in3 = Pin(4, Pin.OUT)
in4 = Pin(5, Pin.OUT)
enb = PWM(Pin(7))

# Initialize PWM Frequency (1000Hz is standard for motor drivers)
ena.freq(1000)
enb.freq(1000)

# Default speed (approx 60%)
current_speed = 40000 

def move(a1, a2, b1, b2, speed):
    in1.value(a1)
    in2.value(a2)
    in3.value(b1)
    in4.value(b2)
    ena.duty_u16(speed)
    enb.duty_u16(speed)

def stop():
    move(0, 0, 0, 0, 0)

# Connect to Wi-Fi 
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, PASSWORD)

print("Connecting to Wi-Fi...")
while not wlan.isconnected():
    time.sleep(1)
    print(".", end="")

ip = wlan.ifconfig()[0]
print(f"\nConnected! IP Address: {ip}")

# Web UI Design
html = f"""<!DOCTYPE html>
<html>
<head><title>Pico 2W Robot PRO</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
    body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; text-align: center; background: #1a1a1a; color: white; padding-top: 20px; }}
    .container {{ max-width: 400px; margin: auto; background: #2d2d2d; padding: 20px; border-radius: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }}
    .btn {{ width: 80px; height: 80px; margin: 10px; font-size: 14px; border-radius: 20px; border: none; cursor: pointer; font-weight: bold; transition: 0.2s; box-shadow: 0 4px #999; }}
    .btn:active {{ box-shadow: 0 0 #666; transform: translateY(4px); opacity: 0.8; }}
    .fw {{ background: #4CAF50; color: white; }}
    .rev {{ background: #2196F3; color: white; }}
    .turn {{ background: #FF9800; color: white; }}
    .stop {{ background: #f44336; color: white; width: 100%; height: 60px; }}
    .slider-box {{ margin: 25px 0; padding: 15px; background: #3d3d3d; border-radius: 15px; }}
    .slider {{ width: 100%; height: 15px; border-radius: 5px; background: #555; outline: none; -webkit-appearance: none; }}
    .slider::-webkit-slider-thumb {{ -webkit-appearance: none; width: 25px; height: 25px; border-radius: 50%; background: #4CAF50; cursor: pointer; }}
</style>
</head>
<body>
    <div class="container">
        <h1>Robot Pro</h1>
        
        <div class="slider-box">
            <label>Power: <b id="perc">61</b>%</label><br><br>
            <input type="range" min="15000" max="65535" value="40000" class="slider" 
                oninput="document.getElementById('perc').innerText = Math.round((this.value/65535)*100)" 
                onchange="fetch('/set?s=' + this.value)">
        </div>

        <div><button class="btn fw" onclick="fetch('/f')">FORWARD</button></div>
        <div>
            <button class="btn turn" onclick="fetch('/l')">LEFT</button>
            <button class="btn turn" onclick="fetch('/r')">RIGHT</button>
        </div>
        <div><button class="btn rev" onclick="fetch('/b')">BACKWARD</button></div>
        <br>
        <button class="btn stop" onclick="fetch('/s')">EMERGENCY STOP</button>
        
        <p style="color: #666; font-size: 12px; margin-top: 20px;">IP: {ip}</p>
    </div>
</body>
</html>
"""

# Server Loop
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(addr)
s.listen(1)

print("Server is live!")

while True:
    try:
        cl, addr = s.accept()
        request = cl.recv(1024).decode()
        
        # Update Speed via Slider
        if '/set?s=' in request:
            try:
                current_speed = int(request.split('/set?s=')[1].split(' ')[0])
            except: pass

        # Movement Logic
        if '/f' in request: move(1, 0, 1, 0, current_speed)
        elif '/b' in request: move(0, 1, 0, 1, current_speed)
        elif '/l' in request: move(0, 1, 1, 0, current_speed) # Sharp turn
        elif '/r' in request: move(1, 0, 0, 1, current_speed) # Sharp turn
        elif '/s' in request: stop()

        cl.send('HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n' + html)
        cl.close()
    except Exception as e:
        print("Error:", e)
        cl.close()
