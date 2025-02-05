from fastapi import APIRouter
import jsonDB
import os
from pydantic import BaseModel
import datetime
import csv
import requests


router = APIRouter()

iotJson = "dataBase/lotDevice.json"
irjson = "dataBase/irInfo.json"
datajson = "dataBase/observedDevice.json"

activeTime = None

# auto create file
if not os.path.exists(datajson):
    with open(datajson, 'w') as f:
        pass


class irData(BaseModel):
    name: str
    id: str
    data: list


class ObservedDevice(BaseModel):
    id: str
    name: str
    ip: str
    group: str
    type: str


class checkData(BaseModel):
    id: str
    group: str
    status: str


@router.post("/observed/add", tags=["observation"])
async def addObserved(addedData: ObservedDevice):
    # Try to get the existing data
    existing_data = jsonDB.read_db(datajson)

    # Prepare the new data
    data = {
        addedData.id: {
            "id": addedData.id,
            "name": addedData.name,
            "ip": addedData.ip,
            "group": addedData.group,
            "type": addedData.type,
            "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    }

    # If the id already exists in the database, return a message
    for x in existing_data:
        # Check if the ID already exists
        for y in existing_data[x]:
            if addedData.id == y:
                return {"message": "ID already exists"}

    # If the group does not exist, create a new one
    if addedData.group not in existing_data:
        newdata = {addedData.group: data}
        existing_data.update(newdata)
        jsonDB.write_db(datajson, existing_data)
    else:
        update_data = existing_data[addedData.group]
        update_data.update(data)
        # If the group exists, update it
        jsonDB.update_db(datajson, addedData.group, update_data)

    return {"message": "added"}


@router.post("/observed/check", tags=["observation"])
async def checkObserved(data: checkData):
    global activeTime
    if not os.path.exists(f"dataBase/{data.id}.csv"):
        with open(f"dataBase/{data.id}.csv", 'w') as f:
            pass

    if activeTime is None:
        activeTime = datetime.datetime.now()
        with open(f"dataBase/{data.id}.csv", 'a') as f:
            writer = csv.writer(f)
            writer.writerow([datetime.datetime.now(), "firts check"])

    # if (datetime.datetime.now() - activeTime).seconds > 180:
    activeTime = datetime.datetime.now()
    with open(f"dataBase/{data.id}.csv", 'a') as f:
        writer = csv.writer(f)
        writer.writerow([datetime.datetime.now(), data.status])


@router.get("/ir/read", tags=["observation", "ir"])
async def read():
    return jsonDB.read_db(irjson)


@router.post("/ir/add/{group}", tags=["observation", "ir"])
async def add(irdata: irData, group: str):
    # print(irdata)
    data = {
        irdata.id: {
            "name": irdata.name,
            "data": irdata.data,
            "id": irdata.id
        }
    }
    jsonDB.update_db(irjson, group, data)
    return {"message": "added"}


@router.get("/ir/delete/{group}/{id}", tags=["observation", "ir"])
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


@router.post("/resisterIP", tags=["observation", "iot"])
async def resisterIP(data: dict):
    jsonDB.update_db(iotJson, "device", data)
    return 'OK', 200


@router.get("/getIotData", tags=["observation", "iot"])
async def getIotData():
    data = jsonDB.read_db(iotJson)
    return data


@router.get("/check", tags=["observation", "iot"])
async def check():
    return 'OK', 200


@router.get("/irSend/{group}/{id}", tags=["iot", "ir"])
async def irSend(group: str, id: str):
    data = jsonDB.read_db(irjson)
    data = data[group][id]["data"]
    deviceIP = jsonDB.read_db(iotJson)
    deviceIP = deviceIP["device"]["roomRemote"]["ip"]
    res = requests.post(f"http://{deviceIP}/irsend", json={"data": data})
    if res.status_code == 200:
        return {"message": "sent"}


@router.get("/wakeonlan/{MAC}", tags=["iot", "pc"])
async def wakePC(MAC: str):
    os.system(f"/home/linuxbrew/.linuxbrew/bin/wakeonlan {MAC}")
    return {"message": "sent"}
