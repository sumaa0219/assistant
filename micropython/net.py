import network
import time
import socket
import os
from machine import Pin
import led


class setup:
    def __init__(self):
        global wlan
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        self.wifi = []
        
        
    
    def SetAP(self):# 独自のネットワークの構築
        ssid = 'SettingNetwork'
        password = 'skotakota0219'
        wlan = network.WLAN(network.AP_IF)
        wlan.config(essid=ssid, password=password)
        wlan.config(pm = 0xa11140)
        wlan.active(True)
        print("SetUP Complete")
        status = wlan.ifconfig()
        print('ip = ' + status[0])
        
    def SetSTA(self, ssid, password):# 引数指定によるネットワーク接続
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        wlan.connect(ssid, password)
        #wlan.config(pm = 0xa11140)
        print("aaaaa")
        ip = wlan.ifconfig()
        print('ip = ' + ip[0])
        

        # WiFi接続待機
        timeout = 20  # タイムアウト設定（秒）
        while not wlan.isconnected() and timeout > 0:
            timeout -= 1
            time.sleep(1)

        # タイムアウト発生時の処理
        if timeout <= 0:
            print("WiFi接続に失敗しました")
        else:
            # 接続成功時の処理
            ip_address = wlan.ifconfig()[0]
            print("自身のIPアドレス:", ip_address)
           
        
        print("Connect Netwotk Complete")
        return ip_address
        
    
    def Scan(self):# 近い順のAPをlist型式で取得
        APlist=[]
        networks = wlan.scan() # list with tupples with 6 fields ssid, bssid, channel, RSSI, security, hidden
        i=0
        networks.sort(key=lambda x:x[3],reverse=True) # sorted on RSSI (3)
        for w in networks:
              i+=1
              APlist.append(w[0].decode())
              #print(i,w[0].decode())]
        print(APlist)
        return APlist
    
    
    def Get(self):# 設定ファイルからSSIDだけ返す(globalとしてssidとpasswordを保持したlist:wifiを作成)
        ssid = []
        delim = ','
        global wifi
        with open('wifi.csv', 'r') as file:
            # CSVファイルの内容をテキストとして読み込む
            csv_content = file.read()      
        # 読み込んだCSVデータを行ごとに分割
        csv_lines = csv_content.split('\n')
        # CSVファイルの内容をすべてリストとして取得する場合
        wifi = [line.split(',') for line in csv_lines]
        for data in wifi:
            ssid.append(data[0])
        return ssid
    
    def Serch(self, scan_list:list, get_list:list): # 一番近いかつ設定にあるSSIDを取得
        self.scan_list = scan_list
        self.get_list = get_list
        
        for base in self.scan_list:
            for element in self.get_list:
                if base == element:
                    return base
                else:
                    pass
            return None
        
    def GetPassword(self, ssid:str):#SSIDから設定ファイルのpasswordを取得
        print(ssid)
        print("wifi")
        global wifi
        for D in wifi:
            print(D)
            if D[0]== ssid:
                return D[1]
            else:
                pass
                
                
    def AutoConnect(self): # 一番近いAPへ自動接続
        
        list1=setup().Scan()
        list2 =setup().Get()
        code=setup().Serch(list1,list2)
        
        if code == None:   
            print("Error Not Found NetWork")
            led.on()
            return None
            #write code
        else:
            password = setup().GetPassword(code)
            ip = setup().SetSTA(code,password)
            led.off()
            print("connected "+code)
            return ip
            
                
         


#setup().SetAP()
#list1=setup().Scan()
#list2 = setup().Get()
#aaa=setup().Serch(list1,list2)
#print(aaa)
#setup().AutoConnect()
 

