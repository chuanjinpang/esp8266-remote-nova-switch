# esp32c3-remote-nova-switch
low cost esp32c3 remote switch for PC


没时间，太长不看版本：

**１.方案架构**

  1.mqtt远程控制

安卓手机/其它的mqtt客户端软件　－〉　mqtt协议服务器　－〉　esp32c3运行micropython 　+　mqtt协议 +控制小脚本

2. http服务器提供web配网，web控制

   

**２.方案功能**

1.远程开机：使用APP手机软件 mqtt协议进行控制开机　　

2.本地物理按键开机：按下power键　－〉启动电脑

3.使用web配网

打开手机软件，点下按钮，就开机了。 或者按下电源按键。

 

3. 运行机制

   没有采用esp-now协议。我不需要一个什么复位按键。

   基本思路：

   1. 周期扫描AP list来看要不要进行配置状态，通过一个特定的essid。通常是手机上开启AP。

   2. 然后在8080端口运行web sever进行配网

   3. 关掉配置热点，则退出配置状态。
   4. 正常时，联网运行mqtt.

   

   机制如下：

   1.采用周期scan扫描AP list，看有没有upy这个AP热点，如果有，就连接。

   2.连接上了，开始8080 web server,等待连接。手机可以开一个AP热点“upy”，password:"upy12345",

   查下连接上的IP.

   用firefox打开http://192.168.43.139:8080

   3.进行配网，也可以在页面上控制开关

   4.关掉手机upy热点，esp32c3会检测到断开。

   5. 然后使用配网的wlan信息，进行扫描连接网络。
   6. 联上mqtt. 目前没有使用web配置mqtt相关信息。运行15秒
   7. 回到第1步，进行配置热点扫描。如果没有，跳到第5步。 

   