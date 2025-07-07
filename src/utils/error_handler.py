"""
WGARP 错误处理器
统一的错误处理和日志记录
"""

import logging
import traceback
from typing import Optional, Any
from datetime import datetime
import os


class ErrorHandler:
    """统一的错误处理器"""
    
    def __init__(self, log_level: int = logging.INFO):
        self.logger = self._setup_logger(log_level)
        self.error_count = 0
        self.last_error = None
    
    def _setup_logger(self, log_level: int) -> logging.Logger:
        """设置日志记录器"""
        logger = logging.getLogger('WGARP')
        logger.setLevel(log_level)
        
        # 避免重复添加处理器
        if not logger.handlers:
            # 控制台处理器
            console_handler = logging.StreamHandler()
            console_handler.setLevel(log_level)
            
            # 文件处理器
            try:
                log_dir = os.path.join(os.getcwd(), 'logs')
                os.makedirs(log_dir, exist_ok=True)
                
                file_handler = logging.FileHandler(
                    os.path.join(log_dir, 'wgarp.log'),
                    encoding='utf-8'
                )
                file_handler.setLevel(logging.DEBUG)
                
                # 格式化器
                formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                )
                console_handler.setFormatter(formatter)
                file_handler.setFormatter(formatter)
                
                logger.addHandler(console_handler)
                logger.addHandler(file_handler)
            except Exception as e:
                # 如果文件日志失败，只使用控制台日志
                console_handler.setFormatter(logging.Formatter(
                    '%(asctime)s - %(levelname)s - %(message)s'
                ))
                logger.addHandler(console_handler)
                print(f"警告: 无法创建文件日志，仅使用控制台日志: {e}")
        
        return logger
    
    def handle_llm_error(self, error: Exception, context: str = "") -> None:
        """处理 LLM 相关错误"""
        self.error_count += 1
        self.last_error = {
            "type": "LLM_ERROR",
            "error": str(error),
            "context": context,
            "timestamp": datetime.now()
        }
        
        error_msg = f"LLM错误"
        if context:
            error_msg += f" ({context})"
        error_msg += f": {error}"
        
        self.logger.error(error_msg)
        self.logger.debug(f"LLM错误详情:\n{traceback.format_exc()}")
    
    def handle_api_error(self, error: Exception, endpoint: str = "", 
                        status_code: int = None) -> None:
        """处理 API 相关错误"""
        self.error_count += 1
        self.last_error = {
            "type": "API_ERROR",
            "error": str(error),
            "endpoint": endpoint,
            "status_code": status_code,
            "timestamp": datetime.now()
        }
        
        error_msg = f"API错误"
        if endpoint:
            error_msg += f" ({endpoint})"
        if status_code:
            error_msg += f" [状态码: {status_code}]"
        error_msg += f": {error}"
        
        self.logger.error(error_msg)
        self.logger.debug(f"API错误详情:\n{traceback.format_exc()}")
    
    def handle_file_error(self, error: Exception, file_path: str = "", 
                         operation: str = "") -> None:
        """处理文件操作错误"""
        self.error_count += 1
        self.last_error = {
            "type": "FILE_ERROR",
            "error": str(error),
            "file_path": file_path,
            "operation": operation,
            "timestamp": datetime.now()
        }
        
        error_msg = f"文件错误"
        if operation:
            error_msg += f" ({operation})"
        if file_path:
            error_msg += f" [文件: {file_path}]"
        error_msg += f": {error}"
        
        self.logger.error(error_msg)
        self.logger.debug(f"文件错误详情:\n{traceback.format_exc()}")
    
    def handle_config_error(self, error: Exception, config_key: str = "") -> None:
        """处理配置相关错误"""
        self.error_count += 1
        self.last_error = {
            "type": "CONFIG_ERROR",
            "error": str(error),
            "config_key": config_key,
            "timestamp": datetime.now()
        }
        
        error_msg = f"配置错误"
        if config_key:
            error_msg += f" ({config_key})"
        error_msg += f": {error}"
        
        self.logger.error(error_msg)
        self.logger.debug(f"配置错误详情:\n{traceback.format_exc()}")
    
    def handle_websocket_error(self, error: Exception, session_id: str = "") -> None:
        """处理 WebSocket 相关错误"""
        self.error_count += 1
        self.last_error = {
            "type": "WEBSOCKET_ERROR",
            "error": str(error),
            "session_id": session_id,
            "timestamp": datetime.now()
        }
        
        error_msg = f"WebSocket错误"
        if session_id:
            error_msg += f" (会话: {session_id})"
        error_msg += f": {error}"
        
        self.logger.error(error_msg)
        self.logger.debug(f"WebSocket错误详情:\n{traceback.format_exc()}")
    
    def handle_general_error(self, error: Exception, context: str = "") -> None:
        """处理一般性错误"""
        self.error_count += 1
        self.last_error = {
            "type": "GENERAL_ERROR",
            "error": str(error),
            "context": context,
            "timestamp": datetime.now()
        }
        
        error_msg = f"系统错误"
        if context:
            error_msg += f" ({context})"
        error_msg += f": {error}"
        
        self.logger.error(error_msg)
        self.logger.debug(f"系统错误详情:\n{traceback.format_exc()}")
    
    def log_info(self, message: str, context: str = "") -> None:
        """记录信息日志"""
        log_msg = message
        if context:
            log_msg = f"[{context}] {message}"
        self.logger.info(log_msg)
    
    def log_warning(self, message: str, context: str = "") -> None:
        """记录警告日志"""
        log_msg = message
        if context:
            log_msg = f"[{context}] {message}"
        self.logger.warning(log_msg)
    
    def log_debug(self, message: str, context: str = "") -> None:
        """记录调试日志"""
        log_msg = message
        if context:
            log_msg = f"[{context}] {message}"
        self.logger.debug(log_msg)
    
    def get_error_stats(self) -> dict:
        """获取错误统计信息"""
        return {
            "total_errors": self.error_count,
            "last_error": self.last_error
        }
    
    def reset_error_count(self) -> None:
        """重置错误计数"""
        self.error_count = 0
        self.last_error = None
    
    def set_log_level(self, level: int) -> None:
        """设置日志级别"""
        self.logger.setLevel(level)
        for handler in self.logger.handlers:
            handler.setLevel(level)


# 创建全局错误处理器实例
error_handler = ErrorHandler()

# 创建便捷的 logger 实例
logger = error_handler.logger
