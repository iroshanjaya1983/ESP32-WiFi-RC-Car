import network
import socket
import time
from machine import Pin, PWM, reset

# ═══════════════════════════════════════
#           MOTOR PIN SETUP
# ═══════════════════════════════════════

# Left Motor
IN1 = Pin(5,  Pin.OUT)   # D1
IN2 = Pin(4,  Pin.OUT)   # D2

# Right Motor
IN3 = Pin(0,  Pin.OUT)   # D3
IN4 = Pin(2,  Pin.OUT)   # D4

# Speed Control (PWM)
ENA = PWM(Pin(14), freq=1000)  # D5
ENB = PWM(Pin(12), freq=1000)  # D6

DEFAULT_SPEED = 800
TURN_SPEED    = 600

# ═══════════════════════════════════════
#           MOTOR FUNCTIONS
# ═══════════════════════════════════════

def set_speed(left, right):
    ENA.duty(int(left))
    ENB.duty(int(right))

def stop():
    IN1.off(); IN2.off()
    IN3.off(); IN4.off()
    ENA.duty(0)
    ENB.duty(0)
    print("STOP")

def forward(speed=DEFAULT_SPEED):
    set_speed(speed, speed)
    IN1.on();  IN2.off()
    IN3.on();  IN4.off()
    print(f"FORWARD {speed}")

def backward(speed=DEFAULT_SPEED):
    set_speed(speed, speed)
    IN1.off(); IN2.on()
    IN3.off(); IN4.on()
    print(f"BACKWARD {speed}")

def turn_left(speed=TURN_SPEED):
    set_speed(speed, speed)
    IN1.off(); IN2.on()
    IN3.on();  IN4.off()
    print(f"LEFT {speed}")

def turn_right(speed=TURN_SPEED):
    set_speed(speed, speed)
    IN1.on();  IN2.off()
    IN3.off(); IN4.on()
    print(f"RIGHT {speed}")

def forward_left(speed=DEFAULT_SPEED):
    set_speed(speed//2, speed)
    IN1.on();  IN2.off()
    IN3.on();  IN4.off()
    print("FORWARD LEFT")

def forward_right(speed=DEFAULT_SPEED):
    set_speed(speed, speed//2)
    IN1.on();  IN2.off()
    IN3.on();  IN4.off()
    print("FORWARD RIGHT")

def backward_left(speed=DEFAULT_SPEED):
    set_speed(speed//2, speed)
    IN1.off(); IN2.on()
    IN3.off(); IN4.on()
    print("BACKWARD LEFT")

def backward_right(speed=DEFAULT_SPEED):
    set_speed(speed, speed//2)
    IN1.off(); IN2.on()
    IN3.off(); IN4.on()
    print("BACKWARD RIGHT")

def spin_left(speed=DEFAULT_SPEED):
    set_speed(speed, speed)
    IN1.off(); IN2.on()
    IN3.on();  IN4.off()
    print("SPIN LEFT")

def spin_right(speed=DEFAULT_SPEED):
    set_speed(speed, speed)
    IN1.on();  IN2.off()
    IN3.off(); IN4.on()
    print("SPIN RIGHT")

# ═══════════════════════════════════════
#      WIFI SETUP
# ═══════════════════════════════════════

def setup_wifi():
    # Disable STA mode first
    sta = network.WLAN(network.STA_IF)
    sta.active(False)
    time.sleep(0.5)

    # Setup AP
    ap = network.WLAN(network.AP_IF)
    ap.active(False)   # Reset AP first
    time.sleep(1)      # Wait before restart
    ap.active(True)

    ap.config(
        essid    = 'RC-Car-ESP32',
        password = '12345678',
        channel  = 6,
        authmode = network.AUTH_WPA_WPA2_PSK
    )

    # Wait until AP is ready
    timeout = 0
    while not ap.active():
        time.sleep(0.5)
        timeout += 1
        if timeout > 20:
            print("AP Failed! Restarting...")
            time.sleep(2)
            reset()

    ip = ap.ifconfig()[0]
    print("="*40)
    print("RC Car Ready!")
    print(f"SSID     : RC-Car-ESP8266")
    print(f"Password : 12345678")
    print(f"IP       : {ip}")
    print(f"URL      : http://{ip}")
    print("="*40)
    return ip

# ═══════════════════════════════════════
#           HTML PAGE
# ═══════════════════════════════════════

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>RC Car</title>
    <style>
        * {
            margin: 0; padding: 0;
            box-sizing: border-box;
            -webkit-tap-highlight-color: transparent;
            user-select: none;
        }
        body {
            background: linear-gradient(135deg, #0f0f23, #1a1a3e);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            font-family: Arial, sans-serif;
            color: white;
            overflow: hidden;
        }
        .header {
            text-align: center;
            padding: 15px;
            width: 100%;
            background: rgba(0,212,255,0.1);
            border-bottom: 2px solid rgba(0,212,255,0.3);
        }
        .header h1 { font-size: 1.4em; color: #00d4ff; }
        .status-bar {
            display: flex;
            justify-content: space-around;
            width: 100%;
            padding: 8px;
            background: rgba(0,0,0,0.4);
            font-size: 0.8em;
        }
        .status-value { color: #00ff88; font-weight: bold; }
        .speed-wrap {
            width: 90%;
            max-width: 400px;
            margin: 12px auto;
            text-align: center;
        }
        .speed-wrap label {
            display: block;
            margin-bottom: 6px;
            color: #00d4ff;
            font-size: 0.9em;
        }
        input[type=range] {
            width: 100%; height: 8px;
            -webkit-appearance: none;
            border-radius: 4px;
            background: linear-gradient(to right,#00d4ff,#ff6b6b);
            outline: none;
        }
        input[type=range]::-webkit-slider-thumb {
            -webkit-appearance: none;
            width: 26px; height: 26px;
            border-radius: 50%;
            background: white;
            cursor: pointer;
            box-shadow: 0 0 8px #00d4ff;
        }
        .action-display {
            font-size: 1.1em;
            color: #00d4ff;
            letter-spacing: 2px;
            padding: 8px;
            min-height: 36px;
            text-align: center;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(3,1fr);
            gap: 10px;
            padding: 10px 15px;
            width: 100%;
            max-width: 360px;
        }
        .grid2 {
            display: grid;
            grid-template-columns: repeat(2,1fr);
            gap: 10px;
            padding: 5px 15px;
            width: 100%;
            max-width: 260px;
        }
        .btn {
            height: 75px;
            border: none;
            border-radius: 14px;
            font-size: 1.7em;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-direction: column;
            box-shadow: 0 4px 12px rgba(0,0,0,0.4);
            transition: transform 0.1s;
            touch-action: none;
        }
        .btn small {
            font-size: 0.32em;
            margin-top: 3px;
            letter-spacing: 1px;
        }
        .btn:active { transform: scale(0.91); }

        .c-fwd  { background: linear-gradient(135deg,#00d4ff,#0099cc); color:#fff; }
        .c-bwd  { background: linear-gradient(135deg,#ff6b6b,#cc3333); color:#fff; }
        .c-lr   { background: linear-gradient(135deg,#ffd700,#cc9900); color:#1a1a1a; }
        .c-diag { background: linear-gradient(135deg,#7b68ee,#5533cc); color:#fff; }
        .c-dbwd { background: linear-gradient(135deg,#ff8c00,#cc6600); color:#fff; }
        .c-spin { background: linear-gradient(135deg,#00ff88,#00aa55); color:#1a1a1a; }
        .c-stop {
            background: linear-gradient(135deg,#ff2244,#aa0022);
            color: #fff;
            border: 2px solid #ff4466;
            animation: glow 1.5s infinite;
        }
        @keyframes glow {
            0%,100% { box-shadow: 0 0 8px rgba(255,34,68,0.5); }
            50%      { box-shadow: 0 0 20px rgba(255,34,68,1); }
        }
        .dot {
            position: fixed; top: 10px; right: 10px;
            width: 12px; height: 12px;
            border-radius: 50%;
            background: #ff4444;
            box-shadow: 0 0 6px #ff4444;
        }
        .dot.on { background:#00ff88; box-shadow:0 0 6px #00ff88; }
        .sec-title {
            font-size: 0.65em;
            color: rgba(255,255,255,0.4);
            letter-spacing: 2px;
            margin: 4px 0 0 0;
        }
        .empty { visibility: hidden; }
    </style>
</head>
<body>
<div class="dot" id="dot"></div>

<div class="header">
    <h1>&#x1F697; WiFi RC Car Controller</h1>
</div>

<div class="status-bar">
    <div>Speed<br><span class="status-value" id="spd">80%</span></div>
    <div>Action<br><span class="status-value" id="act">READY</span></div>
    <div>WiFi<br><span class="status-value" id="sig">--</span></div>
</div>

<div class="speed-wrap">
    <label>Speed: <span id="spdLbl">80%</span></label>
    <input type="range" id="slider" min="20" max="100" value="80"
           oninput="setSpd(this.value)">
</div>

<div class="action-display" id="actDisp">&#9679; STANDBY &#9679;</div>

<p class="sec-title">&#9472;&#9472; DRIVE &#9472;&#9472;</p>
<div class="grid">

    <!-- Row 1 -->
    <button class="btn c-diag"
        ontouchstart="go('forward_left')"  ontouchend="go('stop')"
        onmousedown="go('forward_left')"   onmouseup="go('stop')">
        &#x2196;&#xFE0F;<small>FWD-L</small>
    </button>
    <button class="btn c-fwd"
        ontouchstart="go('forward')"       ontouchend="go('stop')"
        onmousedown="go('forward')"        onmouseup="go('stop')">
        &#x2B06;&#xFE0F;<small>FORWARD</small>
    </button>
    <button class="btn c-diag"
        ontouchstart="go('forward_right')" ontouchend="go('stop')"
        onmousedown="go('forward_right')"  onmouseup="go('stop')">
        &#x2197;&#xFE0F;<small>FWD-R</small>
    </button>

    <!-- Row 2 -->
    <button class="btn c-lr"
        ontouchstart="go('left')"          ontouchend="go('stop')"
        onmousedown="go('left')"           onmouseup="go('stop')">
        &#x2B05;&#xFE0F;<small>LEFT</small>
    </button>
    <button class="btn c-stop"
        ontouchstart="go('stop')"          ontouchend="go('stop')"
        onmousedown="go('stop')"           onmouseup="go('stop')">
        &#x23F9;&#xFE0F;<small>STOP</small>
    </button>
    <button class="btn c-lr"
        ontouchstart="go('right')"         ontouchend="go('stop')"
        onmousedown="go('right')"          onmouseup="go('stop')">
        &#x27A1;&#xFE0F;<small>RIGHT</small>
    </button>

    <!-- Row 3 -->
    <button class="btn c-dbwd"
        ontouchstart="go('backward_left')" ontouchend="go('stop')"
        onmousedown="go('backward_left')"  onmouseup="go('stop')">
        &#x2199;&#xFE0F;<small>BWD-L</small>
    </button>
    <button class="btn c-bwd"
        ontouchstart="go('backward')"      ontouchend="go('stop')"
        onmousedown="go('backward')"       onmouseup="go('stop')">
        &#x2B07;&#xFE0F;<small>BACKWARD</small>
    </button>
    <button class="btn c-dbwd"
        ontouchstart="go('backward_right')"ontouchend="go('stop')"
        onmousedown="go('backward_right')" onmouseup="go('stop')">
        &#x2198;&#xFE0F;<small>BWD-R</small>
    </button>
</div>

<p class="sec-title">&#9472;&#9472; SPIN &#9472;&#9472;</p>
<div class="grid2">
    <button class="btn c-spin"
        ontouchstart="go('spin_left')"     ontouchend="go('stop')"
        onmousedown="go('spin_left')"      onmouseup="go('stop')">
        &#x1F504;<small>SPIN L</small>
    </button>
    <button class="btn c-spin"
        ontouchstart="go('spin_right')"    ontouchend="go('stop')"
        onmousedown="go('spin_right')"     onmouseup="go('stop')">
        &#x1F503;<small>SPIN R</small>
    </button>
</div>

<script>
var spd = 80;
var names = {
    forward:'FORWARD', backward:'BACKWARD',
    left:'TURN LEFT',  right:'TURN RIGHT',
    forward_left:'FWD-LEFT',   forward_right:'FWD-RIGHT',
    backward_left:'BWD-LEFT',  backward_right:'BWD-RIGHT',
    spin_left:'SPIN LEFT',     spin_right:'SPIN RIGHT',
    stop:'STOPPED'
};

function setSpd(v){
    spd = v;
    document.getElementById('spdLbl').textContent = v+'%';
    document.getElementById('spd').textContent    = v+'%';
}

function go(cmd){
    document.getElementById('actDisp').textContent = names[cmd]||cmd;
    document.getElementById('act').textContent     = cmd==='stop'?'STOP':'MOVE';
    var x = new XMLHttpRequest();
    x.open('GET','/cmd?action='+cmd+'&speed='+spd,true);
    x.timeout = 1500;
    x.onload = function(){ if(x.status==200) setConn(true); }
    x.onerror = x.ontimeout = function(){ setConn(false); }
    x.send();
}

function setConn(ok){
    var d = document.getElementById('dot');
    var s = document.getElementById('sig');
    if(ok){ d.className='dot on'; s.textContent='GOOD'; }
    else  { d.className='dot';    s.textContent='LOST'; }
}

// Keyboard support
var km = {
    ArrowUp:'forward', ArrowDown:'backward',
    ArrowLeft:'left',  ArrowRight:'right',
    ' ':'stop', a:'spin_left', d:'spin_right'
};
var held = {};
document.addEventListener('keydown',function(e){
    if(km[e.key] && !held[e.key]){
        held[e.key]=1; go(km[e.key]); e.preventDefault();
    }
});
document.addEventListener('keyup',function(e){
    if(km[e.key]){ delete held[e.key]; go('stop'); }
});

// Ping every 3s
setInterval(function(){
    var x=new XMLHttpRequest();
    x.open('GET','/ping',true);
    x.timeout=2000;
    x.onload=function(){ setConn(true); }
    x.onerror=x.ontimeout=function(){ setConn(false); }
    x.send();
},3000);
</script>
</body>
</html>"""

# ═══════════════════════════════════════
#      COMMAND HANDLER
# ═══════════════════════════════════════

def handle(path):
    if '/ping' in path:
        return b'HTTP/1.0 200 OK\r\nContent-Type: text/plain\r\n\r\nOK'

    if path == '/' or 'index' in path:
        return (
            b'HTTP/1.0 200 OK\r\nContent-Type: text/html\r\n\r\n'
            + HTML.encode()
        )

    if '/cmd' in path:
        try:
            params = {}
            if '?' in path:
                for p in path.split('?')[1].split('&'):
                    k,v = p.split('=')
                    params[k] = v

            action = params.get('action','stop')
            speed  = int(params.get('speed','80'))
            pwm    = int((speed/100)*1023)
            tpwm   = int((speed/100)*700)

            cmd_map = {
                'forward'        : lambda: forward(pwm),
                'backward'       : lambda: backward(pwm),
                'left'           : lambda: turn_left(tpwm),
                'right'          : lambda: turn_right(tpwm),
                'forward_left'   : lambda: forward_left(pwm),
                'forward_right'  : lambda: forward_right(pwm),
                'backward_left'  : lambda: backward_left(pwm),
                'backward_right' : lambda: backward_right(pwm),
                'spin_left'      : lambda: spin_left(pwm),
                'spin_right'     : lambda: spin_right(pwm),
                'stop'           : stop,
            }

            if action in cmd_map:
                cmd_map[action]()
                resp = b'{"status":"ok"}'
            else:
                stop()
                resp = b'{"status":"unknown"}'

        except Exception as e:
            stop()
            resp = b'{"status":"error"}'
            print("CMD ERR:", e)

        return (
            b'HTTP/1.0 200 OK\r\n'
            b'Content-Type: application/json\r\n'
            b'Access-Control-Allow-Origin: *\r\n\r\n'
            + resp
        )

    return b'HTTP/1.0 404 Not Found\r\n\r\nNot Found'

# ═══════════════════════════════════════
#      SERVER - FIXED EADDRINUSE
# ═══════════════════════════════════════

def start_server():
    ip = setup_wifi()

    # ✅ FIX 1: Close any existing socket
    srv = None

    # ✅ FIX 2: Retry loop if port busy
    for attempt in range(5):
        try:
            srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # ✅ FIX 3: SO_REUSEADDR - KEY FIX!
            srv.setsockopt(
                socket.SOL_SOCKET,
                socket.SO_REUSEADDR,
                1
            )

            srv.bind(('0.0.0.0', 80))
            srv.listen(3)
            srv.settimeout(1)

            print(f"Server started on http://{ip}")
            print("Waiting for connections...")
            break  # Success - exit retry loop

        except OSError as e:
            print(f"Attempt {attempt+1}/5 failed: {e}")
            if srv:
                try:
                    srv.close()
                except:
                    pass
            # ✅ FIX 4: Wait before retry
            time.sleep(3)

            if attempt == 4:
                print("All attempts failed - Restarting device...")
                time.sleep(2)
                reset()  # Hard reset as last resort

    stop()  # Make sure motors are off

    # ═══════════════════
    #   Main Server Loop
    # ═══════════════════
    while True:
        try:
            conn, addr = srv.accept()
            conn.settimeout(3)

            try:
                req = conn.recv(512)
                if req:
                    # Parse path
                    lines = req.decode('utf-8','ignore').split('\r\n')
                    path  = lines[0].split(' ')[1] if lines else '/'

                    # Get response
                    resp = handle(path)
                    conn.sendall(resp)

            except OSError:
                pass
            except Exception as e:
                print("Req err:", e)
            finally:
                # ✅ FIX 5: Always close connection
                try:
                    conn.close()
                except:
                    pass

        except OSError:
            # Timeout = no connection, normal
            pass
        except Exception as e:
            print("Server err:", e)
            time.sleep(0.1)

# ═══════════════════════════════════════
#           START
# ═══════════════════════════════════════

print("="*35)
print("  RC Car Booting...")
print("="*35)

# Quick motor test
print("Motor test...")
forward(300); time.sleep(0.2)
stop();       time.sleep(0.1)
backward(300);time.sleep(0.2)
stop()
print("Motor test OK")

# Start!
start_server()