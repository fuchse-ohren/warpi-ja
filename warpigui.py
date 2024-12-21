#!/usr/bin/python3
# encoding=utf-8

# Menu for the wigle/replacement device
# https://www.designer2k2.at 2021-2022
#
# This is working on a rpi4 with kali 64bit os
#
# Libs:
# gpsd https://github.com/MartijnBraam/gpsd-py3
#
#
# kismet conf must be correct!
# gpsd will be called, check that it works with UART
#
# it expects a USB drive on /media/usb/ with the folder kismet there.
# Logs will be written to /media/usb/
#
# Warning:
# there are only some failsafes, it will stop working on error!

# The username and password must match with kismet_site.conf
httpd_username = "root"
httpd_password = "toor"

import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
    datefmt="%Y-%m-%d %H:%M",
    filename="/media/usb/warpi.log",
)

logging.info("Startup")

# Sync HW Clock::
import subprocess

subprocess.run(["hwclock", "-s"])

logging.debug("HW Clock synced")

import board
import busio
from digitalio import DigitalInOut, Direction, Pull
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306
from time import sleep, localtime, strftime
import gpsd
import psutil
import os
import signal
import RPi.GPIO as GPIO
import json
import requests
import socket

logging.debug("All imports done")

# Turn some logger to only show warnings:
logging.getLogger("gpsd").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

# Create the I2C interface.
i2c = busio.I2C(board.SCL, board.SDA)

# Create the SSD1306 OLED class.
disp = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)

# flip screen that the usb ports from the rpi are on top
disp.rotation = 2

# Input Pin:
GPIO.setmode(GPIO.BCM)

logging.debug("IO Setup")

# Page:
Page = 0

def InterruptLeft(_):
    global Page
    # Loop over Pager 1,2,3
    Page = ( Page + 1 ) % 3
    print(f"Page to be shown: {Page}")

def InterruptRight(_):
    global Page
    # Loop over Pager 1,2,3
    Page = ( Page - 1 ) % 3

    print(f"Page to be shown: {Page}")

def InterruptB(_):
    fshutdown()


def InterruptA(_):
    freboot()


def InterruptUp(_):
    startservice()


def InterruptDown(_):
    stopservice()


# 5 button A reboot
GPIO.setup(5, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(5, GPIO.RISING, callback=InterruptA, bouncetime=300)

# 6 button B shutdown
GPIO.setup(6, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(6, GPIO.RISING, callback=InterruptB, bouncetime=300)

# Up dir button start
GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(22, GPIO.RISING, callback=InterruptUp, bouncetime=300)

# Down dir button stop
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(17, GPIO.RISING, callback=InterruptDown, bouncetime=300)

# Left dir button (switch display info)
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(23, GPIO.RISING, callback=InterruptLeft, bouncetime=300)

# Right dir button (switch display info)
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(27, GPIO.RISING, callback=InterruptRight, bouncetime=300)


logging.debug("GPIO Setup done")

# Clear display.
disp.fill(0)
disp.show()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = disp.width
height = disp.height
image = Image.new("1", (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0, 0, width, height), outline=0, fill=0)

# Load a font
font = ImageFont.truetype("/opt/warpi/fonts/misaki_gothic_2nd.ttf", 8)
fontbig = ImageFont.truetype("/opt/warpi/fonts/KikaiChokokuJIS-Md.otf", 24)

logging.debug("Display setup done")

# set country code
# call("iw reg set AT", shell=True)

gpsrun = False
life = True
sleeptime = 1

# globals for the log:
kisuselog = open("/media/usb/kisuselog.log", "w")  # new every time
kiserrlog = open("/media/usb/kiserrlog.log", "a+")  # append
kissubproc = 0

# this delay will be waited, then it starts automatically
autostart = 10
autostarted = False


def startservice():
    logging.info("Starting Kismet")
    #subprocess.Popen(["gpsd", "/dev/serial0", "-s", "9600"])
    global kisuselog, kiserrlog, gpsrun, kissubproc
    kissubproc = subprocess.Popen(["kismet"], stdout=kisuselog, stderr=kiserrlog)
    gpsrun = True


def stopservice():
    logging.info("Stopping Kismet")
    global gpsrun, kissubproc
    gpsrun = False
    # Send a polite INT (CTRL+C)
    kissubproc.send_signal(signal.SIGINT)
    try:
        kissubproc.wait(10)  # wait max 10sec to close
    except subprocess.TimeoutExpired:
        logging.debug("timeout during kill kismet happened")
    #try:
    #    subprocess.run(
    #        ["killall", "gpsd", "--verbose", "--wait", "--signal", "QUIT"], timeout=5
    #    )
    #except subprocess.TimeoutExpired:
    #    logging.debug("timeout during kill gpsd happened")


def freboot():
    global looping, kisuselog, kiserrlog
    looping = False
    logging.info("Rebooting")
    stopservice()
    kisuselog.close()
    kiserrlog.close()
    logging.debug("Kismet shutdown")
    draw.rectangle((0, 0, width, height), outline=0, fill=0)
    draw.text((0, 20), "再起動", font=fontbig, fill=255)
    disp.image(image)
    disp.show()
    logging.debug("LCD Black")
    subprocess.Popen(["reboot"])
    logging.debug("reboot triggered")
    quit()


def fshutdown():
    global looping, kisuselog, kiserrlog
    looping = False
    logging.info("Shutdown")
    stopservice()
    kisuselog.close()
    kiserrlog.close()
    logging.debug("Kismet shutdown")
    draw.rectangle((0, 0, width, height), outline=0, fill=0)
    draw.text((0, 20), "電源切", font=fontbig, fill=255)
    disp.image(image)
    disp.show()
    logging.debug("LCD Black")
    subprocess.call("sudo shutdown -h now", shell=True)
    logging.debug("shutdown -h triggered")
    quit()


logging.debug("All setup, go into loop")

looping = True

while looping:
    draw.rectangle((0, 0, width, height), outline=0, fill=0)

    if life:
        draw.rectangle((120, 56, width, height), outline=0, fill=255)
        life = False
    else:
        draw.rectangle((120, 56, width, height), outline=0, fill=0)
        life = True

    cpu = psutil.cpu_percent()
    mem = dict(psutil.virtual_memory()._asdict())["percent"]
    swp = dict(psutil.swap_memory()._asdict())["percent"]
    f = open("/sys/class/thermal/thermal_zone0/temp")
    t = f.read()
    f.close()
    ct = int(t) / 1000.0

    if cpu > 50:
        subprocess.call(
            "ps aux | sort -nrk 3,3 | head -n 10 >> /media/usb/highcpu.log", shell=True
        )
        logging.debug(f"High CPU: {cpu}")
        sleeptime = 5
    else:
        sleeptime = 0.5

    if Page == 0:
        # Page 0 is the main screen, it shows information while the device runs.
        draw.text(
            (0, 0),
            f"CPU:{cpu / 100:>4.0%} メモリ:{mem / 100:>4.0%} 温度:{ct:5.1f}" ,
            font=font,
            fill=255,
        )
        draw.text(
            (0, 54), strftime("%Y年%m月%d日 %H:%M:%S", localtime()), font=font, fill=255
        )

        if gpsrun:
            try:
                gpsd.connect()
                packet = gpsd.get_current()
                gpsmode = ""
                if packet.mode == 0:
                    gpsmode = "エラー"
                if packet.mode == 1:
                    gpsmode = "  未"
                if packet.mode == 2:
                    gpsmode = "  2D"
                if packet.mode == 3:
                    gpsmode = "  3D"
                draw.text(
                    (0, 10),
                    f"GPS測位:{gpsmode}  衛星:{packet.sats_valid:>3}/{packet.sats:>3}",
                    font=font,
                    fill=255,
                )

                resp = requests.get(
                    "http://127.0.0.1:2501/system/status.json",
                    auth=(httpd_username, httpd_password),
                )
                data = resp.json()
                devices = data["kismet.system.devices.count"]
                kismetmemory = data["kismet.system.memory.rss"] / 1024
                if devices <= 99999:
                    draw.text((0, 20), f"検出 {devices:>5}", font=fontbig, fill=255)
                elif devices > 99999 and devices < 9999499:
                    draw.text((0, 20), f"検出 {devices/1000:>4.0f}K", font=fontbig, fill=255)
                else:
                    draw.text((0, 20), f"検出 {devices/1000/1000:>4.0f}M", font=fontbig, fill=255)
                draw.text(
                    (0, 44),
                    f"メモリ使用量: {kismetmemory:>4.0f}MB",
                    font=font,
                    fill=255,
                )
            except Exception as e:
                logging.error(f"An exception occurred {e}")
        else:
            draw.text(
                (0, 22),
                "停止中",
                font=fontbig,
                fill=255,
            )

    if Page == 2:
        # Page 2 shows the IP from the system
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0)
        try:
            s.connect(("10.254.254.254", 1))
            rpiIP = s.getsockname()[0]
        except Exception:
            rpiIP = "127.0.0.1"
        finally:
            s.close()
        draw.text(
            (0, 0),
            f"IPアドレス: {rpiIP}",
            font=font,
            fill=255,
        )

        try:
            uptime = os.popen('uptime -p | sed -e "s/minut\\(e\\|es\\)/分/g" -e  "s/hou\\(r\\|rs\\)/時間/g" -e "s/da\\(y\\|ys\\)/日/g" -e "s/wee\\(k\\|ks\\)/週/g" -e "s/, //g" -e "s/up //g" -e "s/ //g"').read()
            draw.text(
                (0, 10),
                f"稼働時間: {uptime}",
                font=font,
                fill=255,
            )
        except Exception as e:
            logging.error(f"An exception occurred {e}")

        if gpsrun:
            try:
                gpsd.connect()
                packet = gpsd.get_current()
                lat,lon = packet.position()
                speed = packet.speed()
                draw.text(
                    (0, 20),
                    f"緯度:{lat:.5f} 経度:{lon:.5f}",
                    font=font,
                    fill=255,
                )
                draw.txt(
                    (0, 30),
                    f"速度:",
                    font=font,
                    fill=255,
                )

            except Exception as e:
                logging.error(f"An exception occurred {e}")


    if Page == 1:
        # Page 1 gives a short info about the buttons
        draw.text(
            (0, 0),
            f"ボタン5 : 再起動",
            font=font,
            fill=255,
        )
        draw.text(
            (0, 10),
            f"ボタン6 : 電源切",
            font=font,
            fill=255,
        )
        draw.text(
            (0, 20),
            f"上      : 開始",
            font=font,
            fill=255,
        )
        draw.text(
            (0, 30),
            f"下      : 停止",
            font=font,
            fill=255,
        )
        draw.text(
            (0, 40),
            f"左右    : 画面切替",
            font=font,
            fill=255,
        )

    #if not autostarted:
    #    if autostart > 0:
    #        autostart = autostart - 1
    #    else:
    #        autostarted = True
    #        if not gpsrun:
    #            startservice()

    # draw the screen:
    disp.image(image)
    disp.show()

    # wait a bit:
    sleep(sleeptime)

while True:
    sleep(10)