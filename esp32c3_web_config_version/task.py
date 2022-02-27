import network
import socket
import utime
import ujson as ujson


from umqttsimple import MQTTClient
import machine
import micropython
import time
from machine import Pin
import ubinascii


g_essid="essid"
g_passwd="passwd"
g_cfg_essid='upy'
g_cfg_passwd="upy12345"


topic_sub = b'epwr_itx'
topic_pub = b'epwr_itx_ntf'
mqtt_server = '192.168.0.1'
client_id = ubinascii.hexlify(machine.unique_id())



power_cnt =0

power_sw33_opendrain = Pin(0,Pin.OPEN_DRAIN,value=1)
power_sw = Pin(6,Pin.IN,Pin.PULL_UP) #pin1 seem pull_up NG
power_led= Pin(18,Pin.OUT,value=0)
net_led= Pin(19,Pin.OUT,value=0)

def poweron_action():
  global power_cnt
  #work 
  power_led.on() 
  power_sw33_opendrain.off()
  time.sleep_ms(100)
  #hold to idle
  power_led.off()
  power_sw33_opendrain.on()
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
        


def get_configuration():
  file = open('config.json', 'r')
  configuration = ujson.loads(file.read())
  file.close()

  return configuration

def load_config():
    global g_essid
    global g_passwd
    configuration = get_configuration()      

    for key, value in configuration.items():
        if key == 'parameters':
          for parameter in value:
            print(parameter) 
            if parameter['name'] =='essid':
               g_essid=parameter['value']
            if parameter['name'] =='passwd':
               g_passwd=parameter['value']
    print("load cfg %s %s" %(g_essid,g_passwd))
                

def get_configuration_table(configuration):
  configTable = ''

  for key, value in configuration.items():
      if key == 'parameters':
          for parameter in value:
              if parameter['type'] == 'text':
                  configTable += """<tr><td>""" + parameter['name'] + """</td><td><input name='""" + parameter['name'] + """' type='text' value='""" + parameter['value'] + """'></td></tr>"""

              if parameter['type'] == 'number':
                  configTable += """<tr><td>""" + parameter['name'] + """</td><td><input name='""" + parameter['name'] + """' type='number' value='""" + parameter['value'] + """'></td></tr>"""

              if parameter['type'] == 'dropdown':
                  optionsHtml = str(list(map(lambda x: """<option value='""" + x['value'] + """'>""" + x['key'] + """</option>'""", parameter['options']))).strip('["]').replace('\'", "', '').strip('\'')
                  configTable += """<tr><td>""" + parameter['name'] + """</td><td><select name='""" + parameter['name'] + """'>""" + optionsHtml + """</select></td></tr>""" 
  
  return configTable

def qs_parse(qs): 
  parameters = {} 
  ampersandSplit = qs.split("&")
 
  for element in ampersandSplit: 
    equalSplit = element.split("=") 
    parameters[equalSplit[0]] = equalSplit[1] 

  return parameters


led=int(1)
def web_page():
    global g_essid
    global g_passwd
    print("essid cfg %s %s" %(g_essid,g_passwd))
    if led == 1:
        gpio_state="ON"
    else:
        gpio_state="OFF"
  
    html = """<!DOCTYPE html>
            <html>
              <head>
                  <title>ESP Web Config</title>
                  <meta name="viewport" content="width=device-width, initial-scale=1">
                  <link rel="icon" href="data:,">
                  <style>
                  html{
                      font-family: Helvetica;
                      display:inline-block;
                      margin: 0px auto;
                      text-align: center;
                  }
                  h1{
                      color: #0F3376;
                      padding: 2vh;
                  }
                  p{
                      font-size: 1.5rem;
                  }
                  .button{
                      display: inline-block;
                      background-color: rgb(201, 242, 221, 0.99);
                      border: none;
                      border-radius: 4px;
                      color: white;
                      padding: 16px 40px;
                      text-decoration: none;
                      font-size: 15px;
                      margin: 2px;
                      cursor: pointer;
                  }
                  .button2{
                      background-color: rgb(201, 201, 230, 0.99);
                  }

                  .configTable {
                    margin: 0 auto;
                  }

                  </style>
              </head>
              <body>
                <h1>""" + get_configuration()['title'] + """</h1>
                <textarea rows="3" cols="32">wlan config info: """ + "\r\nessid:"+g_essid+ "\r\npasswd:"+g_passwd + """
                </textarea>              
                <div>
                  <form ... action="/" method="GET">
                    <input type="hidden" name="c" value="3" /> 
                    <table class="configTable">""" + get_configuration_table(get_configuration()) + """</table>
                    <input class="button" type="submit" value="apply essid cfg">
               
                  </form>
                </div>
                 <textarea rows="1" cols="32">control info:"""+"power_cnt:"+str(power_cnt)+"""</textarea>  
                <div>
                 <a href="/?led=on"><button class="button">ON</button></a>
                 <a href="/?led=off"><button class="button button2">OFF</button></a>
                </div>
              </body>
            </html>"""     

    return html

def web_server(wlan):
    global g_essid
    global g_passwd
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('', 8080))
    s.listen(2)

    while True:
        try:
            update_cfg_flag=0
            print('wait for accept')
            s.settimeout(10)
            conn, addr = s.accept()
            print('Got a connection from %s' % str(addr))
            request = conn.recv(1024)
            request = str(request)
            print('Content = %s' % request)
            
            
            url = request.split(' HTTP/1.1')[0][7:]
            
            queryString = ''
            
            # At the moment only serving a page at /
            if (url.find('?') > -1):
                queryStringDict = qs_parse(url[1:])
                configuration = get_configuration()
            
                for configName, configValue in queryStringDict.items():
                    print("k:%s v:%s" %( configName,configValue))
                    if configName == 'led':
                        if configValue == 'on':
                            print('get a on msg so poweron it')
                            poweron_action()
                    for key, value in configuration.items():
                        if key == 'parameters':
                          for parameter in value:
                            print(parameter)
                            if parameter['name'] == configName:                      
                               parameter['value'] = configValue.replace('%26','&')
                               if configName=='essid':
                                   g_essid= parameter['value']
                                   print("update essid:%s",g_essid)
                                   update_cfg_flag=1
                               if configName=='passwd':                         
                                   g_passwd= parameter['value']
                                   print("update passwd:",g_passwd)
                                   update_cfg_flag=1
            if update_cfg_flag:
                update_cfg_flag=0;
                print('update cfg file')
                print(ujson.dumps(configuration))
                f = open('config.json', 'w')
                f.write(ujson.dumps(configuration))
                f.close()
            #
            print("essid cfg %s %s" %(g_essid,g_passwd))
            response = web_page()
            conn.send('HTTP/1.1 200 OK\n'.encode())
            conn.send('Content-Type: text/html\n'.encode())
            conn.send('Connection: close\n\n'.encode())
            conn.sendall(response.encode())
            #print(response);
            conn.close()
            print("conn close")
        except OSError as e:
            print(e)
            if  not wlan.isconnected():
                print("wlan is disconnect")
                s.close()
                break;
                

def do_cfg_task(wlan):
    global g_cfg_essid
    global g_cfg_passwd
    wlan.connect(g_cfg_essid, g_cfg_passwd)
    start = utime.time()
    while not wlan.isconnected():
        utime.sleep(1)
        print(".")
        if utime.time()-start > 15:
            #openwrt seem need 3sec to connect,5 second for dhcp.so double it need about 15
            print("connect timeout!")      
            break
    print('WLAN connection succeeded!')
    print(wlan.ifconfig())
    try:
        web_server(wlan)
    except OSError as e:
        print(e)
    print("exit cfg state")
            
def do_work_task(wlan):
    global g_essid
    global g_passwd
    global power_cnt
    global topic_pub
    print("connect %s %s" %(g_essid, g_passwd))
    wlan.connect(g_essid, g_passwd)
    start = utime.time()
    while not wlan.isconnected():
        utime.sleep(1)
        print(".")
        if utime.time()-start > 15:
            #openwrt seem need 3sec to connect,5 second for dhcp.so double it need about 15
            print("connect timeout!")      
            break
    print('WLAN connection succeeded!')
    print(wlan.ifconfig())
    #
    client = connect_and_subscribe()
    #start mqtt
    last_time = utime.time()
    last_power_cnt = power_cnt 
    while True:    
        try:
            utime.sleep_ms(500) 
            client.check_msg()
            if last_power_cnt != power_cnt:
                last_power_cnt=power_cnt
                print('send a notify msg for power action flag')
                msg = b'esp act:#%s pwr#%d' % (str(utime.localtime()),power_cnt)
                client.publish(topic_pub, msg)
            if (utime.time() - last_time) > 30:
                print("done mqtt lite task")                
                msg = b'esp act:#%s pwr#%d' % (str(utime.localtime()),power_cnt)
                client.publish(topic_pub, msg)
                break;
              
        except OSError as e:
            print(e)
    print('exit work task')
    
def main_task(cfg_essid,work_essid):
    global g_essid
    print(cfg_essid,work_essid)
    wlan = network.WLAN(network.STA_IF)
    
    while True:
        work_essid=g_essid       
        wlan.active(False) 
        print(wlan.status())
        wlan.active(True)
        print(wlan.status())
        print("1st scan")
        nets=wlan.scan()
        print("nets:",len(nets))
        for net in nets:
            print(net[0])
            if net[0] == cfg_essid.encode():
                print('Cfg Network found!')
                do_cfg_task(wlan)
                break
            
        
        for net in nets:
            if net[0] == work_essid.encode() :
                print('work Network found!')
                try:
                    do_work_task(wlan)
                except OSError as e:
                    print(e)
                break
        print("rescan %s" %str(utime.localtime()))
        utime.sleep(3)

from machine import Timer

last_user_sw_toggle=1
last_user_sw_low_cnt=0
last_user_sw_high_cnt=0
def user_sw_func(t):
  #need a filter for trigger
  global last_user_sw_toggle,last_user_sw_low_cnt,last_user_sw_high_cnt
  if power_sw.value() == 0 :
    last_user_sw_high_cnt=0
    if last_user_sw_low_cnt <  6:
        last_user_sw_low_cnt+=1
        print("user sw:L%d,H%d,T%d" % (last_user_sw_low_cnt,last_user_sw_high_cnt,last_user_sw_toggle))
    if  last_user_sw_low_cnt > 3 and 1 == last_user_sw_toggle:
      print("usr push sw for poweron:",time.time())
      poweron_action()      
      last_user_sw_toggle=0
  else :
    last_user_sw_low_cnt=0
    if last_user_sw_high_cnt <  6 :
        last_user_sw_high_cnt+=1
        print("user sw:L%d,H%d,T%d" % (last_user_sw_low_cnt,last_user_sw_high_cnt,last_user_sw_toggle)) 
    if last_user_sw_high_cnt>5:
        last_user_sw_toggle=1

def timer_user_hardware_power_switch():
    tim = Timer(0)
    tim.init(period=150, mode=Timer.PERIODIC, callback=user_sw_func)


timer_user_hardware_power_switch()
load_config()
main_task(g_cfg_essid,g_essid)
