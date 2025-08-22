# get and input test user of current phone

import os,sys,json
udId = sys.argv[1:][1]
public_paras_str = sys.argv[1:][2]

print(f"udId={udId},text={public_paras_str},type={type(public_paras_str)}")

public_paras = json.loads(public_paras_str)
my_phone = public_paras['wtf_test_account1']
print(f"my_phone={my_phone}")
ptuString = public_paras['ARD_phone_online_users']
print(f"ptuString={ptuString}")
phone_test_users = json.loads(public_paras['ARD_phone_online_users'])
print(f"phone_test_users={phone_test_users}")
if udId in phone_test_users:
  phone = phone_test_users[udId]
else:
  phone = my_phone
  print(f"""will use default test user phone={phone}""")
for n in phone:
  command=f"""adb -s {udId} shell input text {n}"""
  os.system(command)