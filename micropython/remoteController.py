import net
import socket
import re
import urequests
import json
import led
import time
from machine import Pin
from UpyIrTx import UpyIrTx

# masterServerIP = "http://172.24.139.139:8000"
masterServerIP = "https://sssumaa.com"  # デバック
tx_pin = Pin(25, Pin.OUT)  # Pin No.26
tx = UpyIrTx(0, tx_pin)    # 0ch

timecounter = 0


def connect(ip):
    print("resister")
    response = urequests.get(masterServerIP + "/getIotData")
    # レスポンスが成功した場合
    if response.status_code == 200:
        # JSONデータを取得
        data = response.json()
        data = data["device"]
        new_data = {
            "ip": ip,
            "status": ""
        }
        data["roomRemote"].update(new_data)
        # JSONデータを処理
        print(data)
        # JSONデータをPOSTリクエストで送信
        url = masterServerIP + "/resisterIP"
        headers = {"Content-Type": "application/json"}
        responsee = urequests.post(url, data=json.dumps(data), headers=headers)

        # レスポンスを処理
        if responsee.status_code == 200:
            print("POSTリクエストが成功しました。")
            led.blink(3)
        else:
            led.on()
            print("POSTリクエストが失敗しました。ステータスコード:", responsee.status_code)

        # リクエストの終了
        responsee.close()
    else:
        led.on()
        print("GETリクエストが失敗しました。ステータスコード:", response.status_code)

    # リクエストの終了
    response.close()


def parse_http_request(request):
    headers, body = request.split('\r\n\r\n', 1)
    return headers, body


ip = net.setup().AutoConnect()
connect(ip)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)

while True:
    conn, addr = s.accept()
    request = conn.recv(3072).decode('utf-8')

    headers, body = parse_http_request(request)
    print(headers, body)
    # print(headers)
    # POSTリクエストのボディを処理
    if "POST" in headers:
        if re.search(r'/irsend', headers.lower()) is not None:
            data = json.loads(body)
            print("Received data for /irsend:", data)
            print(list(data["data"]))
            tx.send(list(data["data"]))
#            if op:
#                door.open()
#                led.blink(3)
#        elif re.search(r'/close', headers.lower()) is not None:
#            data = json.loads(body)
#            print("Received data for /close:", data)
 #           if cl:
#                door.close()
#                led.blink(3)

    conn.close()
    # print("Data Received")
    if timecounter/10 == 60:
        response = urequests.get(masterServerIP + "/check")
        # レスポンスが成功した場合
        if response.status_code == 200:
            timecounter = 0
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
                else:
                    faildcounter += 1

    timecounter += 1
    time.sleep_ms(100)
