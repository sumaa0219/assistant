from fastapi import FastAPI
import uvicorn
from pydantic import BaseModel
import requests
import json
import jsonDB
import subprocess
import psutil

app = FastAPI()

irjson = "irInfo.json"


class irData(BaseModel):
    name: str
    id: str
    data: list


class ObservedDevice(BaseModel):
    id: str
    name: str
    ip: str
    group: str


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/ir/read")
async def read():
    return jsonDB.read_db(irjson)


@app.post("/ir/add/{group}")
async def add(irdata: irData, group: str):
    data = {
        irdata.id: {
            "name": irdata.name,
            "data": irdata.data,
            "id": irdata.id
        }
    }
    jsonDB.update_db(irjson, group, data)
    return {"message": "added"}


@app.get("/ir/delete/{group}/{id}")
async def delete(group: str, id: str):
    data = jsonDB.read_db(irjson)
    if group in data:
        if id in data[group]:
            del data[group][id]
            jsonDB.write_db(irjson, data)
            return {"message": "deleted"}
        else:
            return {"message": "id not found"}
    else:
        return {"message": "group not found"}


@app.get("/pcinfo")
async def get_pc_info():
    # CPU情報
    cpu_usage = psutil.cpu_percent(interval=1)

    # メモリ情報
    memory_info = psutil.virtual_memory()
    memory_total = memory_info.total
    memory_used = memory_info.used
    memory_percentage = memory_info.percent

    # ディスク情報
    disk_info = psutil.disk_usage('/')
    disk_total = disk_info.total
    disk_used = disk_info.used
    disk_percentage = disk_info.percent

    return {
        "cpu_usage": cpu_usage,
        "cpu_temperature": get_cpu_temperature(),
        "cpu_power": get_cpu_power(),
        "memory_total": memory_total,
        "memory_used": memory_used,
        "memory_percentage": memory_percentage,
        "disk_total": disk_total,
        "disk_used": disk_used,
        "disk_percentage": disk_percentage
    }


@app.post("/observed/add/")
async def addObserved(addedData: ObservedDevice):
    data = {
        addedData.id: {
            "id": str,
            "name": str,
            "ip": str,
            "group": str
        }
    }
    jsonDB.update_db("dataBase/observedDevice.json",
                     "observed", {data: data.dict()})
    return {"message": "added"}


# 関数
def get_cpu_temperature():
    result = subprocess.run(['/usr/bin/sensors'], stdout=subprocess.PIPE)
    output = result.stdout.decode()
    # 出力からCPU温度を解析します。出力の形式はハードウェアによります。
    # ここでは、'Core 0:'で始まる行から温度を取得する例を示します。
    for line in output.split('\n'):
        if line.startswith('Core 0:'):
            temp_info = line.split('+')[1]
            temperature = temp_info.split('°')[0]
            return float(temperature)
    return None


def get_cpu_power():
    result = subprocess.run(
        ['sudo', 'powerstat', '-d', '0'], stdout=subprocess.PIPE)
    output = result.stdout.decode()
    # 出力からCPU消費電力を解析します。出力の形式はハードウェアによります。
    # ここでは、'Power (Watts):'で始まる行から消費電力を取得する例を示します。
    for line in output.split('\n'):
        if line.startswith('Power (Watts):'):
            power_info = line.split(':')[1]
            power = power_info.split(' ')[1]
            return float(power)
    return None


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug")
