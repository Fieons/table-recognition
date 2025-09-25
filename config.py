import os
from typing import Optional

class Config:
    """配置类，用于管理API密钥和设置"""
    
    # 智谱AI API配置
    ZHIPU_API_KEY: Optional[str] = "2b8ad3d867a34e8add6a8efabbb09953.zchjMfbNOKQxT08a"
    ZHIPU_API_BASE_URL: str = "https://open.bigmodel.cn/api/paas/v4/"
    
    # 模型配置
    MODEL_NAME: str = "glm-4v"
    
    # 请求配置
    TIMEOUT: int = 60
    MAX_RETRIES: int = 3
    
    # 输出配置
    DEFAULT_OUTPUT_FORMAT: str = "csv"
    SUPPORTED_FORMATS: list = ["csv", "excel", "json"]
    
    @classmethod
    def validate_config(cls) -> bool:
        """验证配置是否完整"""
        if not cls.ZHIPU_API_KEY:
            print("错误: 未设置ZHIPU_API_KEY环境变量")
            print("请设置环境变量: export ZHIPU_API_KEY=your_api_key")
            return False
        return True