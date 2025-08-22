#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import time
import re
import json
import subprocess
import logging
import argparse
from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from appium.options.android import UiAutomator2Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

class XPathOptimizer:
    def __init__(self, device_id=None):
        """
        初始化XPath优化器
        :param device_id: 设备ID，如果为None则自动获取连接的设备
        """
        self.device_id = device_id
        self.driver = None
        self.page_source = None
        self.connected = False
    
    def connect(self):
        """
        连接设备并启动Appium会话
        :return: 是否连接成功
        """
        # 如果没有指定设备ID，则获取当前连接的设备
        if not self.device_id:
            try:
                result = subprocess.check_output(['adb', 'devices']).decode('utf-8')
                devices = []
                for line in result.split('\n')[1:]:  # 跳过第一行（标题行）
                    if '\t' in line:
                        device_id = line.split('\t')[0].strip()
                        if device_id:
                            devices.append(device_id)
                
                if not devices:
                    print("错误：未找到连接的设备")
                    return False
                
                self.device_id = devices[0]  # 使用第一个设备
                print(f"已自动选择设备: {self.device_id}")
            except Exception as e:
                print(f"获取设备列表时出错: {e}")
                return False
        
        # 使用UiAutomator2Options配置Appium会话
        options = UiAutomator2Options()

        # 固定包名
        app_package = "im.thebot.messenger.beta"
        try:
            # 尝试获取当前activity
            current_activity = subprocess.check_output(
                ["adb", "-s", self.device_id, "shell", "dumpsys", "window", "windows"]
            ).decode("utf-8", errors="ignore")
            import re as _re
            match = _re.search(r"mCurrentFocus=Window{.*? (.*?)/([^\s}]+)", current_activity)
            if match:
                app_activity = match.group(2)
                print(f"检测到当前Activity: {app_activity}")
            else:
                app_activity = None
                print("未能检测到当前Activity，将由Appium自行启动默认Activity")
        except Exception as e:
            print(f"获取当前Activity失败: {e}")
            app_activity = None


        options.platform_name = 'Android'
        options.device_name = self.device_id
        options.udid = self.device_id
        options.new_command_timeout = 600
        options.automation_name = 'UiAutomator2'
        options.app_package = app_package
        if app_activity:
            options.app_activity = app_activity
        options.no_reset = True
        options.auto_grant_permissions = True
        options.no_reset = True
        options.full_reset = False
        
        # 启动Appium会话
        try:
            # 检查Appium服务器是否运行
            self._ensure_appium_server()
            
            # 连接到Appium服务器
            self.driver = webdriver.Remote('http://localhost:4723/wd/hub', options=options)
            self.connected = True
            print(f"已成功连接到设备 {self.device_id}")
            return True
        except Exception as e:
            print(f"连接设备时出错: {e}")
            return False
    
    def _ensure_appium_server(self):
        """
        确保Appium服务器正在运行
        """
        try:
            # 检查Appium服务器是否运行
            import requests
            requests.get('http://localhost:4723/wd/hub/status', timeout=5)
            print("Appium服务器已运行")
        except Exception as e:
            print(f"无法连接到Appium服务器: {e}")
            print("请确保Appium服务器正在运行在 http://localhost:4723")
            sys.exit(1)
    
    def get_page_source(self):
        """
        获取当前页面的源代码
        :return: 页面源代码
        """
        if not self.connected or not self.driver:
            if not self.connect():
                return None
        
        try:
            self.page_source = self.driver.page_source
            print("已成功获取页面源代码")
            return self.page_source
        except Exception as e:
            print(f"获取页面源代码时出错: {e}")
            return None
    
    def optimize_xpath(self, original_xpath):
        """
        优化XPath表达式，使其更加稳定和通用
        :param original_xpath: 原始XPath表达式
        :return: 优化后的XPath表达式列表，按可靠性排序
        """
        if not self.page_source:
            self.get_page_source()
            if not self.page_source:
                return [original_xpath]  # 如果无法获取页面源代码，则返回原始XPath
        
        # 尝试使用原始XPath定位元素
        try:
            element = self.driver.find_element(AppiumBy.XPATH, original_xpath)
            print(f"原始XPath可以成功定位元素: {original_xpath}")
        except NoSuchElementException:
            print(f"警告：原始XPath无法定位元素: {original_xpath}")
            return [original_xpath]  # 如果原始XPath无法定位元素，则返回原始XPath
        
        # 获取元素的属性
        attributes = self._get_element_attributes(element)
        if not attributes:
            return [original_xpath]
        
        # 生成优化的XPath表达式
        optimized_xpaths = self._generate_optimized_xpaths(attributes, original_xpath)
        
        # 验证生成的XPath表达式
        validated_xpaths = self._validate_xpaths(optimized_xpaths)
        
        # 如果没有有效的XPath，则返回原始XPath
        if not validated_xpaths:
            return [original_xpath]
        
        return validated_xpaths
    
    def _get_element_attributes(self, element):
        """
        获取元素的属性
        :param element: 元素对象
        :return: 属性字典
        """
        attributes = {}
        try:
            # 获取常用属性
            for attr in ['resource-id', 'content-desc', 'text', 'class', 'package', 'bounds']:
                try:
                    value = element.get_attribute(attr)
                    if value:
                        attributes[attr] = value
                except:
                    pass
            
            return attributes
        except Exception as e:
            print(f"获取元素属性时出错: {e}")
            return {}
    
    def _generate_optimized_xpaths(self, attributes, original_xpath):
        """
        根据元素属性生成优化的XPath表达式
        :param attributes: 元素属性字典
        :param original_xpath: 原始XPath表达式
        :return: 优化后的XPath表达式列表
        """
        optimized_xpaths = []
        
        # 添加原始XPath
        optimized_xpaths.append(original_xpath)
        
        # 根据resource-id生成XPath（最稳定的定位方式之一）
        if 'resource-id' in attributes and attributes['resource-id']:
            resource_id = attributes['resource-id']
            # 完整的resource-id定位
            optimized_xpaths.append(f"//*[@resource-id='{resource_id}']")
            
            # 如果resource-id包含包名，尝试提取不带包名的id部分
            if '/' in resource_id:
                id_part = resource_id.split('/')[-1]
                optimized_xpaths.append(f"//*[contains(@resource-id, '{id_part}')]")
        
        # 根据content-desc生成XPath（非常稳定的定位方式）
        if 'content-desc' in attributes and attributes['content-desc']:
            content_desc = attributes['content-desc']
            optimized_xpaths.append(f"//*[@content-desc='{content_desc}']")
            
            # 对于长content-desc，添加部分匹配
            if len(content_desc) > 10:
                optimized_xpaths.append(f"//*[contains(@content-desc, '{content_desc[:10]}')]")
        
        # 根据text生成XPath
        if 'text' in attributes and attributes['text']:
            text = attributes['text']
            optimized_xpaths.append(f"//*[@text='{text}']")
            
            # 对于长文本，添加部分匹配
            if len(text) > 10:
                optimized_xpaths.append(f"//*[contains(@text, '{text[:10]}')]")
            
            # 添加不区分大小写的文本匹配（使用translate函数）
            lower_text = text.lower()
            if lower_text != text:
                optimized_xpaths.append(
                    f"//*[translate(@text, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')='{lower_text}']"
                )
        
        # 根据class和其他属性组合生成XPath
        if 'class' in attributes:
            class_name = attributes['class']
            
            # 类名和text组合
            if 'text' in attributes and attributes['text']:
                text = attributes['text']
                optimized_xpaths.append(f"//{class_name}[@text='{text}']")
            
            # 类名和content-desc组合
            if 'content-desc' in attributes and attributes['content-desc']:
                content_desc = attributes['content-desc']
                optimized_xpaths.append(f"//{class_name}[@content-desc='{content_desc}']")
            
            # 类名和resource-id组合
            if 'resource-id' in attributes and attributes['resource-id']:
                resource_id = attributes['resource-id']
                optimized_xpaths.append(f"//{class_name}[@resource-id='{resource_id}']")
        
        # 使用bounds属性（当其他属性不可靠时）
        if 'bounds' in attributes and attributes['bounds']:
            bounds = attributes['bounds']
            optimized_xpaths.append(f"//*[@bounds='{bounds}']")
            
            # 尝试解析bounds获取位置信息
            try:
                # 通常bounds格式为[x1,y1][x2,y2]
                if re.match(r'\[\d+,\d+\]\[\d+,\d+\]', bounds):
                    bounds_parts = re.findall(r'\[(\d+),(\d+)\]', bounds)
                    if len(bounds_parts) == 2:
                        x1, y1 = bounds_parts[0]
                        x2, y2 = bounds_parts[1]
                        # 使用中心点坐标
                        center_x = (int(x1) + int(x2)) // 2
                        center_y = (int(y1) + int(y2)) // 2
                        # 添加基于位置的XPath（不太稳定，但在某些情况下有用）
                        if 'class' in attributes:
                            optimized_xpaths.append(
                                f"//{attributes['class']}[contains(@bounds, '{center_x}') and contains(@bounds, '{center_y}')]"
                            )
            except Exception as e:
                print(f"解析bounds时出错: {e}")
        
        # 移除重复的XPath
        return list(dict.fromkeys(optimized_xpaths))
    
    def _validate_xpaths(self, xpaths):
        """
        验证XPath表达式是否可以唯一定位元素，并评估其稳定性
        :param xpaths: XPath表达式列表
        :return: 验证通过的XPath表达式列表，按稳定性排序
        """
        validated_xpaths = []
        xpath_scores = {}
        
        for xpath in xpaths:
            try:
                # 测量查找元素所需的时间（性能指标）
                start_time = time.time()
                elements = self.driver.find_elements(AppiumBy.XPATH, xpath)
                end_time = time.time()
                search_time = end_time - start_time
                
                if len(elements) == 1:
                    # XPath可以唯一定位元素
                    # 计算XPath的复杂度（简洁性指标）
                    complexity = self._calculate_xpath_complexity(xpath)
                    
                    # 计算XPath的稳定性得分
                    stability_score = self._calculate_stability_score(1, search_time, complexity)
                    
                    validated_xpaths.append(xpath)
                    xpath_scores[xpath] = stability_score
                    
                    print(f"有效的XPath: {xpath}")
                    print(f"  - 查找时间: {search_time:.4f}秒, 复杂度: {complexity}")
                    print(f"  - 稳定性得分: {stability_score:.2f}")
                elif len(elements) > 1:
                    # XPath定位到多个元素，尝试进一步优化
                    print(f"XPath定位到多个元素: {xpath}, 元素数量: {len(elements)}")
                    
                    # 即使找到多个元素，也可能是有用的XPath，给予较低的得分
                    complexity = self._calculate_xpath_complexity(xpath)
                    stability_score = self._calculate_stability_score(len(elements), search_time, complexity)
                    
                    validated_xpaths.append(xpath)
                    xpath_scores[xpath] = stability_score
                    
                    print(f"  - 查找时间: {search_time:.4f}秒, 复杂度: {complexity}")
                    print(f"  - 稳定性得分: {stability_score:.2f} (较低，因为找到多个元素)")
                else:
                    print(f"无效的XPath: {xpath} (未找到元素)")
            except Exception as e:
                print(f"验证XPath时出错: {xpath}, 错误: {e}")
        
        # 按稳定性得分排序（得分越高越稳定）
        sorted_xpaths = sorted(validated_xpaths, key=lambda x: xpath_scores.get(x, 0), reverse=True)
        
        return sorted_xpaths
    
    def _calculate_xpath_complexity(self, xpath):
        """
        计算XPath表达式的复杂度
        :param xpath: XPath表达式
        :return: 复杂度得分（越低越好）
        """
        # 计算XPath的长度（越短越好）
        length_score = len(xpath) / 10
        
        # 计算XPath中的条件数量（越少越好）
        condition_count = xpath.count('@')
        
        # 计算XPath中的函数调用数量（越少越好）
        function_count = sum(1 for func in ['contains', 'translate', 'starts-with'] if func in xpath)
        
        # 计算XPath的层级深度（越浅越好）
        depth = xpath.count('/')
        
        # 综合计算复杂度得分
        complexity = length_score + condition_count * 2 + function_count * 3 + depth
        
        return complexity
    
    def _calculate_stability_score(self, element_count, search_time, complexity):
        """
        计算XPath的稳定性得分
        :param element_count: 找到的元素数量
        :param search_time: 查找时间（秒）
        :param complexity: XPath复杂度
        :return: 稳定性得分（越高越稳定）
        """
        # 理想情况是只找到一个元素
        uniqueness_score = 10 if element_count == 1 else (5 / element_count)
        
        # 查找速度得分（越快越好）
        speed_score = 10 / (1 + search_time * 10)  # 归一化到0-10之间
        
        # 简洁性得分（越简洁越好）
        simplicity_score = 10 / (1 + complexity / 10)  # 归一化到0-10之间
        
        # 综合得分（权重可以根据实际情况调整）
        stability_score = uniqueness_score * 0.5 + speed_score * 0.3 + simplicity_score * 0.2
        
        return stability_score
    
    def close(self):
        """
        关闭Appium会话
        """
        if self.driver:
            try:
                self.driver.quit()
                print("已关闭Appium会话")
            except:
                pass
            finally:
                self.driver = None
                self.connected = False

# 提供一个简单的函数接口
def optimize_xpath(xpath, device_id=None):
    """
    优化XPath表达式，使其更加稳定和通用
    :param xpath: 原始XPath表达式
    :param device_id: 设备ID，如果为None则自动获取连接的设备
    :return: 优化后的最佳XPath表达式
    """
    optimizer = XPathOptimizer(device_id)
    try:
        optimized_xpaths = optimizer.optimize_xpath(xpath)
        if optimized_xpaths:
            print("\n优化后的XPath表达式（按可靠性排序）:")
            for i, xpath in enumerate(optimized_xpaths):
                print(f"{i+1}. {xpath}")
            return optimized_xpaths[0]  # 返回最可靠的XPath
        else:
            print("无法生成优化的XPath表达式")
            return xpath
    finally:
        optimizer.close()

# 提供一个更简单的示例用法函数
def get_optimized_xpath(xpath, device_id=None):
    """
    获取优化后的XPath表达式（简化版接口）
    :param xpath: 原始XPath表达式
    :param device_id: 设备ID，如果为None则自动获取连接的设备
    :return: 优化后的最佳XPath表达式
    """
    print(f"正在优化XPath: {xpath}")
    print("正在连接设备并获取页面...")
    optimizer = XPathOptimizer(device_id)
    
    try:
        # 连接设备
        optimizer.connect()
        
        # 获取当前页面源码
        optimizer.get_page_source()
        
        # 优化XPath
        optimized_xpaths = optimizer.optimize_xpath(xpath)
        
        if optimized_xpaths:
            print(f"\n优化成功! 找到 {len(optimized_xpaths)} 个有效XPath")
            print(f"最佳XPath: {optimized_xpaths[0]}")
            return optimized_xpaths[0]
        else:
            print("\n未能找到有效的优化XPath")
            return xpath
    except Exception as e:
        print(f"优化XPath时出错: {e}")
        return xpath
    finally:
        # 关闭连接
        optimizer.close()

# 命令行接口
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="XPath优化工具 - 自动连接Android设备并优化XPath表达式")
    parser.add_argument("xpath", help="要优化的XPath表达式")
    parser.add_argument("-d", "--device", help="Android设备ID，如果不提供则自动获取")
    parser.add_argument("-a", "--all", action="store_true", help="显示所有优化后的XPath，而不仅仅是最佳XPath")
    parser.add_argument("-v", "--verbose", action="store_true", help="显示详细的调试信息")
    
    args = parser.parse_args()
    
    # 设置日志级别
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    
    try:
        # 获取优化后的XPath
        optimizer = XPathOptimizer(args.device)
        
        try:
            # 连接设备
            print("正在连接设备...")
            optimizer.connect()
            
            # 获取当前页面源码
            print("正在获取页面源码...")
            optimizer.get_page_source()
            
            # 优化XPath
            print(f"正在优化XPath: {args.xpath}")
            optimized_xpaths = optimizer.optimize_xpath(args.xpath)
            
            if optimized_xpaths:
                print("\n优化成功!")
                
                if args.all:
                    # 显示所有优化后的XPath
                    print(f"找到 {len(optimized_xpaths)} 个有效XPath:")
                    for i, opt_xpath in enumerate(optimized_xpaths, 1):
                        print(f"{i}. {opt_xpath}")
                else:
                    # 只显示最佳XPath
                    print(f"最佳XPath: {optimized_xpaths[0]}")
            else:
                print("\n未能找到有效的优化XPath")
        finally:
            # 关闭连接
            optimizer.close()
    except KeyboardInterrupt:
        print("\n操作已取消")
    except Exception as e:
        print(f"\n发生错误: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()