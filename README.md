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

![User Interface](https://github.com/fuchse-ohren/warpi-ja/raw/master/warpi_gui.png)

* Blue button: Shutdown. Stops Kismet, converts the file and then powers down the raspberry pi.
* Red button: Reboot. Reboot from the raspberry pi without file conversion.
* Yellow push direction: Stop. Stops Kismet. Useful to reload the config.
* Green push direction: Start. Starts Kismet. Useful after it has been stopped.
* Left arrow: switch between screens.

## Screen information:

### デフォルト画面
![p1.png](https://github.com/fuchse-ohren/warpi-ja/raw/master/p1.png)

1行目: システムのメトリクスを表示します「CPU使用率，メモリ使用率，CPU温度」の順で表示されます
2行目: GPS測位状態を表示します「GPS測位:(エラー/未/2D/3D)  衛星: (測位に使用中の数/検出済みの数)」
3行目: WiFiの検出数を表示します
4行目: バックエンドアプリのkismet自体が使用しているメモリの量を表示します
5行目: 日時情報を表示します


## ボタン配置画面
![p2.png](https://github.com/fuchse-ohren/warpi-ja/raw/master/p2.png)
ボタン配置の解説を表示します


## システム状態画面
![p3.png](https://github.com/fuchse-ohren/warpi-ja/raw/master/p3.png)

1行目: RaspberryPiのIPアドレスを表示します
2行目: システム稼働時間を表示します
3行目: GPSの緯度/経度を表示します
