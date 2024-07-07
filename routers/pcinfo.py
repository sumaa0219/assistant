import subprocess
import psutil
from fastapi import APIRouter

router = APIRouter()

# 関数


@router.get("/pcinfo", tags=["pcinfo"])
async def get_pc_info():
    # CPU情報
    cpu_usage = psutil.cpu_percent(interval=1)

    # メモリ情報
    memory_info = psutil.virtual_memory()
    memory_total = memory_info.total
    memory_used = memory_info.used
    memory_percentage = memory_info.percent

    return {
        "cpu_usage": cpu_usage,
        "cpu_temperature": get_cpu_temperature(),
        "cpu_power": None,
        "memory_total": memory_total,
        "memory_used": memory_used,
        "memory_percentage": memory_percentage,
        "disks_info": get_all_disk_info()
    }


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


def get_cpu_power():  # ＊＊＊＊機能しない＊＊＊＊
    try:
        # `-z` オプションを追加
        result = subprocess.run(['powerstat', '-d', '0', '-z'],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        output = result.stdout

        # 出力からCPU消費電力を解析
        for line in output.split('\n'):
            if 'Power' in line and 'Watts' in line:
                power_info = line.split(':')[1]
                power = power_info.split()[0]  # 最初の数値部分を取得
                return float(power)

    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr}")
        return None


def get_all_disk_info():
    disk_infos = []
    partitions = psutil.disk_partitions()
    for partition in partitions:
        try:
            # パーティションごとのディスク使用量を取得
            usage = psutil.disk_usage(partition.mountpoint)
            disk_info = {
                'device': partition.device,
                'mountpoint': partition.mountpoint,
                'fstype': partition.fstype,
                'total': usage.total,
                'used': usage.used,
                'free': usage.free,
                'percent': usage.percent
            }
            disk_infos.append(disk_info)
        except PermissionError:
            # 一部のシステムパーティションにはアクセスできない場合があります
            continue

    return disk_infos
