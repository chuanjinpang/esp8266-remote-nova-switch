# esp8266-remote-nova-switch
low cost esp8266 remote switch for PC


没时间，太长不看版本：

１.方案架构

esp8266 +micropython + mqtt协议　+　mqtt客户端软件　+　　mqtt协议服务器

２.方案功能

远程开机：　　安卓手机/其它的mqtt客户端软件　－〉　mqtt协议服务器　－〉　esp8266运行micropython 　+　mqtt协议 +控制小脚本

本地开机：按下power键　－〉启动电脑

3. 使用

打开手机软件，点下按钮，就开机了。 或者按下电源按键。

 

相关代码，固件，硬件接线图，整理一下放github，有兴趣直接打包下载.

https://github.com/chuanjinpang/esp8266-remote-nova-switch

背景与需求：

１.　自从租了一台VPS云主机实现了内网穿透，这样人在外也能方便访问家里资源。最近在整IPV6的事，IPV6地址量大便宜是它的优势。

２. 　远程开关机的需要也就来了，按需运行家里的主机是在能用之后的直接需要。远程关机倒是容易，ssh上去poweroff就完事了。

３.　一开始整了一个智能开关的方案，也能用。只要在BIOS里面配置一下来电后自启动。

　　不过了，这方案有２个问题：１）贵，大厂要４０/个，小厂的便宜些但是方案是独有的，倒闭了大概率就用不了了。２)其次是不开源，不够open。通常产品由于这样那样的原因，设计实现成了一坨shi，除了嘴上报怨下，还能怎么样了？特别是别家也是８两。

目标：

所有我有一个梦想：如果可以的话，如果有一个自主可控（软件是开源的，可以二次开发自己升级更新，硬件原理图开放。类似于树莓派，nanoVNA这样的新范式的东东），成本低廉的的远程开关在网上卖，贵几块钱，我也会买。

万万没有想到，某宝没有这样的。果然我还是在年轻了。

为了自由的新范式。摸索了一段时间。发现其实还是有个还成的方案。最低只要１３块钱（连串口都不要的，９块的esp12f更便宜），肯折腾点动下手就可以实现远程开机。

用了一段时间，个人觉得还行。分享出来。

实现：

操作：

１.用uPyCraft_V1.0下载micropython的固件，网上有很多教程。　软件和固件都有：https://github.com/chuanjinpang/esp8266-remote-nova-switch

建议购买带串口的nodemcu，更新下载固件，控制程序都要方便点。

２.修改main.py下wifi的配置和mqtt的目标topic（与别人用同一个主题会相互影响）。mqtt服务器，如果你还没有，可以用我的先玩着（你要接受免责的哦）。



３.用uPyCraft_V1.0下载main.py和umqttsimple.py。

４，硬件连线，

准备：打开机箱，准备万用表，先确定下power的线电压是否为３.３V,如果不是，好了你的主板比较奇葩。这个方案不适合你的主板（建议放弃）。我家３台新老电脑都是３.３V的

开机线：把power的3.3Ｖ线接上esp8266的D2.  另一个地线接esp8266的GND. 如下图：



供电线：

供电问题，有２条路子：１）直接用USB充电头供电。２）取巧用TPM模块的供电，这个要翻下主板的手册。3)有的主板USB有standby电，看运气。

　

收工

手机端软件：

MQTT Dash IoT Smart Home_v4.4_apkpure.com.apk https://github.com/chuanjinpang/esp8266-remote-nova-switch

　配置服务器

配置一个按钮

　按钮发送on消息。

配置一下，网上有很多教程。

也可以用mosquitto的客户端命令来触发：

mosquitto_pub -h pcj2020.top -t epwr01 -m "on"

安全问题：

你看，没有用SSL这样的。暂时没有，有空或者谁加下
