import sys
import json
import subprocess
import time

# 常见的Android权限列表
permissions = [
    "android.permission.READ_EXTERNAL_STORAGE",
    "android.permission.WRITE_EXTERNAL_STORAGE",
    "android.permission.ACCESS_FINE_LOCATION",
    "android.permission.ACCESS_COARSE_LOCATION",
    "android.permission.ACCESS_BACKGROUND_LOCATION",
    "android.permission.ACCESS_MEDIA_LOCATION",
    "android.permission.READ_CONTACTS",
    "android.permission.WRITE_CONTACTS",
    "android.permission.READ_SMS",
    "android.permission.SEND_SMS",
    "android.permission.READ_CALL_LOG",
    "android.permission.READ_PHONE_STATE",
    "android.permission.CALL_PHONE",
    "android.permission.CAMERA",
    "android.permission.RECORD_AUDIO",
    "android.permission.READ_CALENDAR",
    "android.permission.WRITE_CALENDAR",
    "android.permission.ACTIVITY_RECOGNITION",
    "android.permission.BLUETOOTH_CONNECT",
    "android.permission.BLUETOOTH_SCAN",
    "android.permission.POST_NOTIFICATIONS",
    "android.permission.READ_MEDIA_IMAGES",
    "android.permission.READ_MEDIA_VIDEO",
    "android.permission.READ_MEDIA_AUDIO"
]

# 保留原来的参数获取方式
udId = sys.argv[1:][1]
public_paras_str = sys.argv[1:][2]
public_paras = json.loads(public_paras_str)
apk_path = public_paras['ARD_apk_path_4.1beta']
app_package = public_paras['ARD_beta_package']

# 停止应用
command1 = f"adb -s {udId} shell am force-stop {app_package}"
result = subprocess.run(command1, shell=True, check=False,
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

force_stop_failed = (
    result.returncode != 0 or
    "Exception" in result.stderr or
    "Unknown package" in result.stderr
)

if force_stop_failed:
    # 卸载应用
    command2 = f"adb -s {udId} uninstall {app_package}"
    result = subprocess.run(command2, shell=True, check=False,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode == 0:
        time.sleep(1)

        # 安装应用
        command3 = f"adb -s {udId} install -r -t {apk_path}"
        result = subprocess.run(command3, shell=True, check=False,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            time.sleep(1)
            # 赋权
            for permission in permissions:
                command4 = f"adb -s {udId} shell pm grant {app_package} {permission}"
                subprocess.run(command4, shell=True, check=False,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

print(result.stdout.strip())
print(result.stderr.strip())
