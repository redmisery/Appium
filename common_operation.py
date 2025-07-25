from appium.webdriver.common.touch_action import TouchAction
from appium.webdriver.common.by import By
from appium import webdriver
from typing import Literal
# 拖拽操作


def swipe_until_text_appears(driver: webdriver, target_text: str, direction: Literal['down', 'up'], max_swipe: int = 5, is_xpath: bool = False):
    """
    使用W3C WebDriver协议的touchAction方法实现下拉操作
    下拉页面，直到找到指定文本。

    :param driver: Appium WebDriver 实例
    :param target_text: 目标文本
    :param direction: 下拉方向，'down' 或 'up'
    :param max_swipe: 最大下拉次数
    :return: 找到元素返回 True，否则返回 False
    """
    # 获取屏幕尺寸
    screen_size = driver.get_window_size()
    width = screen_size['width']
    height = screen_size['height']
    # 计算滑动距离
    if direction == 'down':
        start_x = end_x = width / 2
        start_y, end_y = height * 0.8, height * 0.2
    if direction == 'up':
        start_x = end_x = width / 2
        start_y, end_y = height * 0.2, height * 0.8
    # 执行滑动操作
    for _ in range(max_swipe):
        action = TouchAction(driver)
        action.press(start_x, start_y).move_to(
            end_x, end_y).release().perform()
        # 检查元素是否存在
        try:
            if is_xpath:
                element = driver.find_element(By.XPATH, target_text)
            else:
                element = driver.find_element(
                    By.ANDROID_UIAUTOMATOR, f'new UISelector().text("{target_text}")')
            return element
        except:
            continue
    return False
