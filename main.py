import network
import utime

topic_sub = b'epwr01'
topic_pub = b'epwr01ntf'
mqtt_server = 'pcj2020.top'
wifi_cfg=[
{'SSID': 'upy','PASSWORD' : 'upy12345'},
{'SSID': 'OpenWrt','PASSWORD' : 'rootroot'}
]


def do_connect():
    
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.scan()   
    for i in wifi_cfg:
        if not wlan.isconnected():
            print('connecting to network...%s' % i['SSID'])
            wlan.connect(i['SSID'], i['PASSWORD'])
            start = utime.time()
            while not wlan.isconnected():
                utime.sleep(1)
                print(".")
                if utime.time()-start > 15:
                #openwrt seem need 3sec to connect,5 second for dhcp.so double it need about 15
                    print("connect timeout!")
                    break
        else :
            break;
             

    if wlan.isconnected():
        print('network config:', wlan.ifconfig())


def restart_and_reconnect():
  print('Failed to connect to MQTT broker. Reconnecting...')
  time.sleep(10)
  machine.reset()

from umqttsimple import MQTTClient
import ubinascii
import machine
import micropython
import time
from machine import Pin

last_message = 0
message_interval = 30
counter = 0
power_cnt =0


client_id = ubinascii.hexlify(machine.unique_id())


power_sw = Pin(5,Pin.IN,Pin.PULL_UP)
power_sw33_oc = Pin(4,Pin.OPEN_DRAIN,value=1)
power_led= Pin(16,Pin.OUT,value=1)

def poweron_action():
  global power_cnt
  power_led.off()
  power_sw33_oc.off()
  time.sleep_ms(100)
  power_led.on()
  power_sw33_oc.on()
  time.sleep_ms(100)
  power_cnt+=1


def sub_cb(topic, msg):
  print((topic, msg))
  if topic == topic_sub:
    if msg == b'on':
      print('get a on msg so poweron it')
      poweron_action()
    else :
      print('ignor it %s' % msg)


def connect_and_subscribe():
  print(client_id,mqtt_server)
  client = MQTTClient(client_id, mqtt_server)
  client.set_callback(sub_cb)
  client.connect()
  client.subscribe(topic_sub)
  print('Connected to %s MQTT broker, subscribed to %s topic' % (mqtt_server, topic_sub))
  return client

# go jobs
from machine import Timer

last_user_sw_toggle=1
last_user_sw_low_cnt=0
last_user_sw_high_cnt=0
def user_sw_func(t):
  #need a filter for trigger
  global last_user_sw_toggle,last_user_sw_low_cnt,last_user_sw_high_cnt
  if power_sw.value() == 0 :
    last_user_sw_high_cnt=0
    if last_user_sw_low_cnt <  50:
      last_user_sw_low_cnt+=1
    print("user sw:%d,%d,%d" % (last_user_sw_low_cnt,last_user_sw_high_cnt,last_user_sw_toggle))
    if  last_user_sw_low_cnt > 3 and 1 == last_user_sw_toggle:
      print("usr push sw for poweron:",time.time())
      poweron_action()      
      last_user_sw_toggle=0
  else :
    last_user_sw_low_cnt=0
    if last_user_sw_high_cnt <  50:
      last_user_sw_high_cnt+=1
    print("user sw:%d,%d,%d" % (last_user_sw_low_cnt,last_user_sw_high_cnt,last_user_sw_toggle)) 
    if last_user_sw_high_cnt>5:
      last_user_sw_toggle=1

try:
  print("go task...")
  tim = Timer(-1)
  tim.init(period=200, mode=Timer.PERIODIC, callback=user_sw_func)
  do_connect()
  client = connect_and_subscribe()
except OSError as e:
  print("os error when connect")
  restart_and_reconnect()


while True:  
  try:
    time.sleep_ms(100) 
    client.check_msg()
    if (time.time() - last_message) > message_interval:
      msg = b'esp8266 act:#%d pwr#%d' % (counter,power_cnt)
      client.publish(topic_pub, msg)
      last_message = time.time()
      counter += 1
  except OSError as e:
    print("os error in loop")
    restart_and_reconnect()
  
  
    









