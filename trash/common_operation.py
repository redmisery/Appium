from appium.webdriver.webdriver import ActionHelpers
from appium.webdriver.common.appiumby import AppiumBy
from appium.webdriver.webdriver import WebDriver
from typing import Literal


# 定位方法封装
def find_element(
    driver: WebDriver,
    method: Literal["xpath", "id", "accessibility_id", "text"],
    value: str,
):
    """
    封装元素定位方法
    :param driver: Appium WebDriver 实例
    :param method: 定位方式
    :param value: 定位值
    :return: 元素对象
    """
    # 首先确定手机版本:Android|IOS
    platform = driver.capabilities["platformName"]
    if method == "xpath":
        return driver.find_element(AppiumBy.XPATH, value)
    elif method == "id":
        return driver.find_element(AppiumBy.ID, value)
    elif method == "accessibility_id":
        return driver.find_element(AppiumBy.ACCESSIBILITY_ID, value)
    elif method == "text" and platform == "Android":
        return driver.find_element(
            AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{value}")'
        )
    elif method == "text" and platform == "IOS":
        return driver.find_element(AppiumBy.IOS_PREDICATE, f'label == "{value}"')
    else:
        raise ValueError(f"不支持的定位方式: {method}")


# 拖拽操作
def swipe_until_text_appears(
    driver: WebDriver,
    target_text: str,
    direction: Literal["down", "up"],
    max_swipe: int = 5,
    is_xpath: bool = False,
):
    """
    使用W3C WebDriver协议的touchAction方法实现下拉操作
    下拉页面，直到找到指定文本。

    :param driver: Appium WebDriver 实例
    :param target_text: 目标文本
    :param direction: 下拉方向，'down' 或 'up'
    :param max_swipe: 最大下拉次数
    :param is_xpath: 是否为xpath表达式
    :return: 找到元素返回 True，否则返回 False
    """
    # 获取屏幕尺寸
    screen_size = driver.get_window_size()
    width = screen_size["width"]
    height = screen_size["height"]
    # 计算滑动距离
    if direction == "down":
        start_x = end_x = width / 2
        start_y, end_y = height * 0.8, height * 0.2
    if direction == "up":
        start_x = end_x = width / 2
        start_y, end_y = height * 0.2, height * 0.8
    # 执行滑动操作
    for _ in range(max_swipe):
        ActionHelpers.swipe(driver, start_x, start_y, end_x, end_y)
        # 检查元素是否存在
        try:
            if is_xpath:
                element = find_element(driver, "xpath", target_text)
            else:
                element = find_element(driver, "text", target_text)
                return element
        except:
            continue
    return False


# 安装应用
def install_app(driver: WebDriver, app_path: str, app_package_name: str) -> bool:
    """
    安装应用
    :param driver: Appium WebDriver 实例
    :param app_path: 应用路径
    :param app_package_name: 应用包名
    :return: 安装成功返回True，否则返回False
    """
    is_install_succeed = False
    if not driver.is_app_installed(app_package_name):
        driver.install_app(app_path)
        if driver.is_app_installed(app_package_name):
            logger.info(f"应用{app_package_name}安装成功")
            is_install_succeed = True
        else:
            logger.error(f"应用{app_package_name}安装失败")
    else:
        logger.info(f"应用{app_package_name}已安装")
    return is_install_succeed


# 卸载应用
def uninstall_app(driver: WebDriver, app_package_name: str) -> bool:
    """
    卸载应用
    :param driver: Appium WebDriver 实例
    :param app_package_name: 应用包名
    :return: 卸载成功返回True，否则返回False
    """
    is_uninstall_succeed = False
    if driver.is_app_installed(app_package_name):
        driver.uninstall_app(app_package_name)
        if not driver.is_app_installed(app_package_name):
            logger.info(f"应用{app_package_name}卸载成功")
            is_uninstall_succeed = True
        else:
            logger.error(f"应用{app_package_name}卸载失败")
    else:
        logger.info(f"应用{app_package_name}未安装")
    return is_uninstall_succeed
