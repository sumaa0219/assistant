import net
import socket
import re
import urequests
import json
import led
import time
from machine import Pin


# masterServerIP = "http://172.24.139.139:8000"
masterServerIP = "https://sssumaa.com"  # デバック


timecounter = 0
activeFlag = False


def connect(ip):
    print("resister")
    response = urequests.get(masterServerIP + "/check")
    # レスポンスが成功した場合
    if response.status_code == 200:
        data = {
            "id": "0001",
            "name": "toiletSystem",
            "ip": ip,
            "group": "MakuyamaHouse",
            "type": "humanSensor"
        }
        # JSONデータを処理
        print(data)
        # JSONデータをPOSTリクエストで送信
        url = masterServerIP + "/observed/add"
        headers = {"Content-Type": "application/json"}
        responsee = urequests.post(url, data=json.dumps(data), headers=headers)

        # レスポンスを処理
        if responsee.status_code == 200:
            print("POSTリクエストが成功しました。")
            led.blink(3)
        else:
            led.on()
            print(responsee.content)
            print("POSTリクエストが失敗しました。ステータスコード:", responsee.status_code)

        # リクエストの終了
        responsee.close()
    else:
        led.on()
        print("GETリクエストが失敗しました。ステータスコード:", response.status_code)

    # リクエストの終了
    response.close()


ip = net.setup().AutoConnect()
connect(ip)


while True:
    p0 = Pin(2, Pin.IN)
    if p0.value() == 1 and activeFlag == False:
        activeFlag = True
        data = {
            "id": "0001",
            "group": "MakuyamaHouse",
            "status": "active"
        }
        url = masterServerIP + "/observed/check"
        headers = {"Content-Type": "application/json"}
        responsee = urequests.post(url, data=json.dumps(data), headers=headers)

        if responsee.status_code == 200:
            print("POSTリクエストが成功しました。")
            led.blink(3)
        else:
            led.on()
            print(responsee.content)
            print("POSTリクエストが失敗しました。ステータスコード:", responsee.status_code)

        responsee.close()

    elif p0.value() == 1 and activeFlag == True:
        pass

    if p0.value() == 0 and activeFlag == True:
        activeFlag = False

    # print("Data Received")
    if timecounter/10 == 60:
        response = urequests.get(masterServerIP + "/check")
        # レスポンスが成功した場合
        if response.status_code == 200:
            timecounter = 0
            response.close()
        else:
            faildcounter = 0
            networkFlag = False
            while networkFlag == False or faildcounter < 6:
                ip = net.setup().AutoConnect()
                print(ip)
                response = urequests.get(masterServerIP + "/check")
                # レスポンスが成功した場合
                if response.status_code == 200:
                    networkFlag = True
                    faildcounter = 0
                    connect(ip)
                    response.close()
                else:
                    faildcounter += 1
                    response.close()

    timecounter += 1
    time.sleep_ms(100)
