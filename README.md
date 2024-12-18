# warpi-ja
"GUI" script running on a Raspberry Pi 4 (and 3b), handling the startup, conversion and shutdown procedure.

## オリジナルからの変更
* GUIを日本語に対応，使用フォントを以下のものに変更
	* フォント1 ![美咲フォント](https://littlelimit.net/misaki.htm)
	* フォント2 ![機械彫刻用標準書体フォント - 基本フォント](https://font.kim/)
* gpsdの起動に関与しないように変更．(systemdを使ってください)
* 情報表示画面を少し拡張
* kali 2024.xxで動かすためにrequirements.txtの内容を変更

## Setup:

See the article on my website on how to setup the complete system: [designer2k2.at Wardriving setup](https://www.designer2k2.at/de/mods/elektronik/156-raspberry-pi-wardriving-setup)

![warpi in action](https://www.designer2k2.at/images/stories/rpiwarpiinaction.jpg)

## User interface:

![User Interface](https://github.com/designer2k2/warpi/raw/master/warpi_gui.png)

* Blue button: Shutdown. Stops Kismet, converts the file and then powers down the raspberry pi.
* Red button: Reboot. Reboot from the raspberry pi without file conversion.
* Yellow push direction: Stop. Stops Kismet. Useful to reload the config.
* Green push direction: Start. Starts Kismet. Useful after it has been stopped.
* Left arrow: switch between screens.

## Screen information:

![Screen](https://github.com/designer2k2/warpi/raw/master/warpi_screen.png)

First line: CPU Load in % / Memory usage in % / CPU Temperature in °C  
Second line: GPS Status (3=3D lock, 2=2D lock, 1=No lock) / Satellites in View / Satellites used / Status  
Third line: Devices found by kismet  
Fourth line: Memory used by kismet  
Fifth line: Current time / Live blink  
