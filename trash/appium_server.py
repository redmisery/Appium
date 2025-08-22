# 命令行启动Appium Server并记录日志
import subprocess
import time
import os
from appium_logger import logger

IS_USE_EXISTS_SERVER = True # 是否使用已存在的Appium服务器 - 已启用
def check_and_stop_appium_server():
    try:
        # 查找占用4723端口的进程（Appium默认端口）
        result = subprocess.run(
            ['netstat', '-ano', '|', 'findstr', ':4723'],
            capture_output=True,
            text=True,
            shell=True
        )
        
        if result.stdout:
            # 提取进程ID(可能存在多行，取LISTEN状态的PID)
            for line in result.stdout.splitlines():
                if 'LISTEN' in line:
                    pid = line.split()[-1]
                    logger.info(f'发现正在运行的Appium服务器，PID: {pid}')
                    break
            else:
                logger.warning('未找到LISTEN状态的Appium服务器')
                return
            
            # 结束进程
            subprocess.run(['taskkill', '/F', '/PID', pid], shell=True)
            logger.info(f'已关闭Appium服务器，PID: {pid}')
        else:
            logger.info('未发现正在运行的Appium服务器')
    except Exception as e:
        logger.error(f'检查或关闭Appium服务器时发生错误: {str(e)}')


def start_appium_server():
    try:
        # 检查是否使用已存在的服务器
        if IS_USE_EXISTS_SERVER:
            result = subprocess.run(
                ['netstat', '-ano', '|', 'findstr', ':4723'],
                capture_output=True,
                text=True,
                shell=True
            )
            if result.stdout and 'LISTEN' in result.stdout:
                logger.info('已检测到运行中的Appium服务器，将使用现有服务器')
                return None
            else:
                logger.info('未检测到运行中的Appium服务器，将启动新服务器')
        
        # 如不使用现有服务器，则先检查并关闭已运行的服务器
        if not IS_USE_EXISTS_SERVER:
            check_and_stop_appium_server()
        
        # 创建日志目录
        log_dir = os.path.join('logs', 'appium_server')
        os.makedirs(log_dir, exist_ok=True)
        
        # 生成日志文件名（包含时间戳）
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        log_file = os.path.join(log_dir, f'appium_server_{timestamp}.log')
        
        # 启动Appium服务器，将输出重定向到日志文件
        with open(log_file, 'a+', encoding='utf-8') as f:
            process = subprocess.Popen(
            "appium",
            stdout=f,
            stderr=f,
            text=True,
            shell=True
        )
            # 检测是否完全启动
            time.sleep(3)
            f.seek(0)
            log_content = f.read()
            if "Appium REST http interface listener started" in log_content:
                logger.info("Appium服务器启动成功")
            else:
                raise Exception("Appium服务器启动失败")
        logger.info(f'Appium服务器输出已重定向到: {log_file}')
        return process
    except Exception as e:
        logger.error(f'启动Appium服务器失败: {str(e)}')
        exit(1)


if __name__ == '__main__':
    start_appium_server()
