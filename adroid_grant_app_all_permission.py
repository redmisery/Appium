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
    "android.permission.READ_MEDIA_AUDIO",
    "android.permission.GET_ACCOUNTS",
    "android.permission.READ_PROFILE",
    "android.permission.READ_PHONE_NUMBERS"
]

for permission in permissions:
    command4 = f"adb -s {udId} shell pm grant {app_package} {permission}"
    proc = subprocess.run(command4, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if proc.stderr.strip():
        print(f"[赋权失败] {permission}: {proc.stderr.strip()}")
    else:
        print(f"[赋权成功] {permission}")