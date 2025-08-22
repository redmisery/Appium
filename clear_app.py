import os
import sys
import json

udId = sys.argv[1:][1]
public_paras_str = sys.argv[1:][2]
public_paras = json.loads(public_paras_str)

target_value = public_paras['ARD_beta_package']

# 清除应用数据
os.system(f"adb -s {udId} shell pm clear {target_value}")

# 修改全局参数为 1
public_paras['termination_signal'] = 1

# 输出修改后的参数
print(json.dumps(public_paras))
