import logging
import os
from datetime import datetime

class AppiumLogger:
    def __init__(self, log_name='appium_server'):
        # 确保logs目录存在
        log_dir = os.path.join(os.getcwd(), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        # 生成带时间戳的日志文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = os.path.join(log_dir, f'{log_name}_{timestamp}.log')
        
        # 配置日志记录器
        self.logger = logging.getLogger(log_name)
        self.logger.setLevel(logging.DEBUG)
        
        # 避免重复添加处理器
        if not self.logger.handlers:
            # 创建文件处理器
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            
            # 创建控制台处理器
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            
            # 定义日志格式
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            # 添加处理器到记录器
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
        
        self.log_file = log_file
        self.logger.info(f'日志文件已创建: {log_file}')
        
    def debug(self, message):
        self.logger.debug(message)
        
    def info(self, message):
        self.logger.info(message)
        
    def warning(self, message):
        self.logger.warning(message)
        
    def error(self, message):
        self.logger.error(message)
        
    def critical(self, message):
        self.logger.critical(message)

# 创建一个默认的日志记录器实例
logger = AppiumLogger()