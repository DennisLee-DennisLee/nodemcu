try:
    import usocket as socket
except:
    import socket

response_404 = """HTTP/1.0 404 NOT FOUND

<h1>404 Not Found</h1>
"""

response_500 = """HTTP/1.0 500 INTERNAL SERVER ERROR

<h1>500 Internal Server Error</h1>
"""

response_template = """HTTP/1.0 200 OK

%s
"""
import machine
import ntptime, utime
from machine import RTC
from time import sleep

led = machine.Pin(9, machine.Pin.OUT)
rtc = RTC()
try:
    seconds = ntptime.time()
except:
    seconds = 0
rtc.datetime(utime.localtime(seconds))

def time():
    body = """<html>
<body>
<h1>Time</h1>
<p>%s</p>
</body>
</html>
""" % str(rtc.datetime())

    return response_template % body

def dummy():
    body = "This is a dummy endpoint"

    return response_template % body

def turn_on_light():
    led.value(1)
    body = "You turned on a light."
    return response_template % body

def turn_off_light():
    led.value(0)
    body = "You turned off a light."
    return response_template % body

def read_switch():
    switch = machine.Pin(10, machine.Pin.IN)
    json_result = "{state: %i}" % switch.value()
    return response_template % json_result

def measure_light():
    val = machine.ADC(0)
    json_result = "{value: %i}" % val.read()
    return response_template % json_result

handlers = {
    'time': time,
    'dummy': dummy,
    'light_on': turn_on_light,
    'light_off': turn_off_light,
    'switch': read_switch,
    'light': measure_light,
}

def main():
    s = socket.socket()
    ai = socket.getaddrinfo("0.0.0.0", 8080)
    addr = ai[0][-1]

    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    s.bind(addr)
    s.listen(5)
    print("Listening, connect your browser to http://<this_host>:8080/")

    while True:
        sleep(.5)
        res = s.accept()
        client_s = res[0]
        client_addr = res[1]
        req = client_s.recv(4096)
        print("Request:")
        print(req)

        try:
            path = req.decode().split("\r\n")[0].split(" ")[1]
            handler = handlers[path.strip('/').split('/')[0]]
            response = handler()
        except KeyError:
            response = response_404
        except Exception as e:
            response = response_500
            print(str(e))

        client_s.send(b"\r\n".join([line.encode() for line in response.split("\n")]))

        client_s.close()
        print()

main()
