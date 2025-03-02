import hashlib
import platform
import subprocess
import re

def get_hardware_info():
    system = platform.system()
    info = {}

    if system == "Linux":
        # 获取CPU信息
        with open('/proc/cpuinfo', 'r') as f:
            cpu_info = f.read()
        info['cpu'] = re.search(r'model name\s*:\s*(.+)', cpu_info).group(1)

        # 获取主板序列号
        try:
            info['motherboard'] = subprocess.check_output("sudo dmidecode -s baseboard-serial-number", shell=True).decode().strip()
        except:
            info['motherboard'] = "unknown"

    elif system == "Windows":
        # 获取CPU信息
        cpu = subprocess.check_output('wmic cpu get ProcessorId').decode().split('\n')[1].strip()
        info['cpu'] = cpu

        # 获取磁盘序列号
        disk = subprocess.check_output("wmic diskdrive get serialnumber").decode().split('\n')[1].strip()
        info['disk'] = disk

    elif system == "Darwin":  # macOS系统
        try:
            # 获取CPU信息
            cpu_info = subprocess.check_output(
                "sysctl -n machdep.cpu.brand_string",
                shell=True
            ).decode().strip()
            info['cpu'] = cpu_info
        except Exception as e:
            info['cpu'] = "unknown"

        try:
            # 获取主板序列号
            board_info = subprocess.check_output(
                "ioreg -l | grep IOPlatformSerialNumber | awk '{print $NF}'",
                shell=True
            ).decode().strip().replace('"', '')
            info['motherboard'] = board_info
        except:
            info['motherboard'] = "unknown"

        try:
            # 获取系统UUID（更稳定的标识）
            system_uuid = subprocess.check_output(
                "system_profiler SPHardwareDataType | grep UUID",
                shell=True
            ).decode().split(': ')[1].strip()
            info['system_uuid'] = system_uuid
        except:
            info['system_uuid'] = "unknown"

        try:
            # 获取磁盘UUID（系统盘）
            disk_info = subprocess.check_output(
                "diskutil info / | grep 'Volume UUID'",
                shell=True
            ).decode().split(': ')[1].strip()
            info['disk'] = disk_info
        except:
            info['disk'] = "unknown"

    # 提取设备信息
    print(str(info))
    # 生成哈希指纹
    fingerprint = hashlib.sha256(str(info).encode()).hexdigest()
    return fingerprint

if __name__ == '__main__':
    print(get_hardware_info())