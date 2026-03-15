import network
import socket
import time
from machine import Pin, PWM

# Wi-Fi Configuration
SSID = "YOUR_WIFI_NAME"
PASSWORD = "YOUR_WIFI_PASSWORD"

# Motor Pin Setup
# Left Motor (A)
in1 = Pin(2, Pin.OUT)
in2 = Pin(3, Pin.OUT)
ena = PWM(Pin(6))

# Right Motor (B)
in3 = Pin(4, Pin.OUT)
in4 = Pin(5, Pin.OUT)
enb = PWM(Pin(7))

# Initialize PWM
ena.freq(1000)
enb.freq(1000)

# Speed (0 to 65535)
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

# Simple Web UI with corrected labels and layout
html = f"""<!DOCTYPE html>
<html>
<head><title>Pico 2W Robot</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
    body {{ font-family: Arial; text-align: center; background: #222; color: white; padding-top: 50px; }}
    .btn {{ width: 90px; height: 90px; margin: 10px; font-size: 16px; border-radius: 15px; border: none; cursor: pointer; font-weight: bold; transition: 0.2s; }}
    .btn:active {{ opacity: 0.7; transform: scale(0.95); }}
    .fw {{ background: #4CAF50; color: white; }}
    .rev {{ background: #2196F3; color: white; }}
    .turn {{ background: #FF9800; color: white; }}
    .stop {{ background: #f44336; color: white; }}
    .row {{ display: block; margin-bottom: 10px; }}
</style>
</head>
<body>
    <h1>Pico 2W Robot Control</h1>
    <p>Status: Connected to {SSID}</p>
    
    <div class="row">
        <button class="btn fw" onclick="fetch('/f')">FORWARD</button>
    </div>
    
    <div class="row">
        <button class="btn turn" onclick="fetch('/l')">LEFT</button>
        <button class="btn stop" onclick="fetch('/s')">STOP</button>
        <button class="btn turn" onclick="fetch('/r')">RIGHT</button>
    </div>
    
    <div class="row">
        <button class="btn rev" onclick="fetch('/b')">BACKWARD</button>
    </div>

    <script>
        // Optional: Prevents the page from reloading/flickering on mobile
        function sendCmd(cmd) {{
            fetch(cmd).catch(err => console.log(err));
        }}
    </script>
</body>
</html>
"""

# Start Server
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(addr)
s.listen(1)

print("Listening on port 80...")

while True:
    try:
        cl, addr = s.accept()
        request = cl.recv(1024).decode()
        
        # Parse Commands and match to functions
        if '/f' in request:
            move(1, 0, 1, 0, current_speed)  # Forward
        elif '/b' in request:
            move(0, 1, 0, 1, current_speed)  # Backward
        elif '/l' in request:
            move(0, 1, 1, 0, current_speed)  # Sharp Left
        elif '/r' in request:
            move(1, 0, 0, 1, current_speed)  # Sharp Right
        elif '/s' in request:
            stop()                           # Stop

        # Send response
        cl.send('HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n' + html)
        cl.close()
        
    except Exception as e:
        print("Error:", e)
        try:
            cl.close()
        except:
            pass  
