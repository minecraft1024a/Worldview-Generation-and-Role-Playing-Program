class ErrorHandler:
    def handle_llm_error(self, error):
        """处理LLM生成时的异常捕获，输出中文错误信息"""
        error_messages = {
            "APIError": "API调用失败，请检查网络连接或API密钥有效性。",
            "Timeout": "请求超时，请尝试重新发送请求，或检查网络状况。",
            "Authentication": "身份验证失败，请检查API密钥或凭证配置。",
            "AuthenticationError": "身份验证失败（401），API密钥无效或已过期，请检查API Key设置。",
            "RateLimit": "达到API调用频率限制，请稍后重试或减少请求频率。",
            "ContentFilter": "生成内容被过滤器拦截，请调整输入内容或尝试更换表达方式。",
            "ModelNotReady": "模型未加载完成，请等待初始化完成后重试。",
            "InternalServerError": "服务器内部错误，可能是OpenAI服务暂时不可用，请稍后重试。",
            "ConnectionError": "无法连接到服务器，请检查网络连接。",
            "InvalidRequestError": "请求参数有误，请检查模型名称、消息内容等设置。",
            "PermissionError": "权限不足，API Key可能无权访问该模型。",
            "ServiceUnavailableError": "服务暂时不可用，请稍后重试。",
            "ValueError": "输入值有误，请检查输入内容。",
            "KeyError": "程序内部配置错误，请联系开发者。",
            "TypeError": "数据类型错误，请联系开发者修复。",
            "AttributeError": "程序内部属性错误，请联系开发者。",
            "OpenAIError": "OpenAI接口调用发生未知错误，请检查API Key和网络。"
        }
        
        error_type = type(error).__name__
        # 针对常见HTTP错误特殊处理
        error_str = str(error)
        if ("401" in error_str and ("Invalid token" in error_str or "invalid authentication" in error_str.lower())) \
            or ("AuthenticationError" in error_type and "401" in error_str):
            user_message = "身份验证失败（401），API密钥无效或已过期，请检查API Key设置。"
        elif "403" in error_str:
            user_message = "权限被拒绝（403），API Key无权访问该资源或被封禁，请检查权限设置。"
        elif "429" in error_str:
            user_message = "请求过于频繁（429），达到API调用频率限制，请稍后重试或减少请求频率。"
        elif "404" in error_str:
            user_message = "资源未找到（404），可能是模型名称错误或API路径不正确，请检查配置。"
        elif "400" in error_str:
            user_message = "请求参数错误（400），请检查模型名称、消息内容等设置。"
        elif "503" in error_str:
            user_message = "服务不可用（503），OpenAI服务器暂时不可用，请稍后重试。"
        elif "500" in error_str:
            user_message = "服务器内部错误（500），OpenAI服务暂时不可用，请稍后重试。"
        elif "502" in error_str:
            user_message = "网关错误（502），OpenAI服务器暂时不可用或网络异常，请稍后重试。"
        else:
            user_message = error_messages.get(error_type, f"未知错误({error_type})：{str(error)}，请联系开发者或稍后重试。")
        
        self._log_error(error, user_message)
        return user_message
    
    def _log_error(self, error, user_message):
        """记录错误日志到控制台"""
        print(f"[错误日志] 原始错误: {error} | 用户提示: {user_message}")

# 全局错误处理器实例
error_handler = ErrorHandler()
