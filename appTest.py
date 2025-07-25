from appium import webdriver
from appium.options.android import UiAutomator2Options
from common_operation import find_element, swipe_until_text_appears
from appium_logger import logger
from appium_server import *

# 安卓终端配置
ANDROID_CONFIG = {
    "platformName": "Android",
    "automationName": "UIAutomator2",
    "deviceName": "127.0.0.1:62001",
    "noReset": True,
    "newCommandTimeout": 6000,
}
logger.info(f"安卓终端配置: {ANDROID_CONFIG}")

# 启动Appium服务器
process = start_appium_server()

APPIUM_SERVER = {"url": "http://127.0.0.1:4723"}
logger.info(f'Appium服务器地址: {APPIUM_SERVER["url"]}')
# 初始化驱动 (配置与逻辑分离)
logger.info("开始初始化Appium驱动...")

# 所有应用的配置
apps = {
    "setting": {"appPackage": "com.android.settings", "appActivity": ".Settings"},
    "launcher": {
        "appPackage": "com.android.launcher3",
        "appActivity": ".launcher3.Launcher",
    },
}
# 连接安卓终端
try:
    driver = webdriver.Remote(
        command_executor=APPIUM_SERVER["url"],
        options=UiAutomator2Options().load_capabilities(ANDROID_CONFIG),
    )
    logger.info("Appium驱动初始化成功!")
except Exception as e:
    logger.error(f"Appium驱动初始化失败: {str(e)}")
    raise
try:
    # 打开设置应用
    driver.activate_app(apps["setting"]["appPackage"])
    # 往下拖拽页面，直至页面出现“无障碍”
    element = swipe_until_text_appears(driver, "无障碍", "down")
    if element:
        element.click()
    else:
        raise Exception("未找到“无障碍”选项")
except Exception as e:
    logger.error(f"{str(e)}")

logger.info("测试完成，准备退出驱动...")
driver.quit()
logger.info("驱动已退出，测试结束。")
