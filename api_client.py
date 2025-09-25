import base64
import json
import requests
from typing import Dict, Any, Optional
from config import Config


class ZhipuAIClient:
    """智谱AI API客户端"""
    
    def __init__(self):
        self.api_key = Config.ZHIPU_API_KEY
        self.base_url = Config.ZHIPU_API_BASE_URL
        self.timeout = Config.TIMEOUT
        self.max_retries = Config.MAX_RETRIES
    
    def _encode_image(self, image_path: str) -> str:
        """将图片编码为base64"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def _build_payload(self, image_path: str, prompt: str) -> Dict[str, Any]:
        """构建API请求载荷"""
        image_data = self._encode_image(image_path)
        
        return {
            "model": "glm-4.5v",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_data}"
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ],
            "max_tokens": 4096,
            "thinking": {
                "type": "enabled"
            }
        }
    
    def _make_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """发送API请求"""
        # 使用Bearer认证方式
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # 打印请求信息用于调试
        print(f"发送请求到: {self.base_url}chat/completions")
        print(f"请求头: {headers}")
        print(f"请求载荷: {json.dumps(payload, ensure_ascii=False, indent=2)}")
        
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    f"{self.base_url}chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=self.timeout
                )
                
                # 打印详细的错误信息
                if response.status_code != 200:
                    print(f"API响应状态码: {response.status_code}")
                    print(f"API响应内容: {response.text}")
                    print(f"响应头: {dict(response.headers)}")
                    # 强制抛出异常以显示错误
                    response.raise_for_status()
                
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                if attempt == self.max_retries - 1:
                    print(f"最终请求失败: {e}")
                    if hasattr(e, 'response') and e.response is not None:
                        print(f"错误响应: {e.response.text}")
                        print(f"错误响应头: {dict(e.response.headers)}")
                    raise e
                print(f"请求失败，第{attempt + 1}次重试...")
    
    def recognize_table(self, image_path: str) -> Dict[str, Any]:
        """识别图片中的表格"""
        prompt = """请识别这张图片中的表格内容，并以JSON格式返回表格数据。
        返回格式要求：
        {
            "table_data": [
                ["表头1", "表头2", ...],
                ["数据1", "数据2", ...],
                ...
            ],
            "description": "表格的简要描述"
        }
        请确保数据准确，保持原有的行列结构。"""
        
        payload = self._build_payload(image_path, prompt)
        response = self._make_request(payload)
        
        return response
    
    def extract_table_data(self, response: Dict[str, Any]) -> Optional[list]:
        """从API响应中提取表格数据"""
        try:
            content = response["choices"][0]["message"]["content"]
            
            print(f"AI返回内容: {content}")
            
            # 尝试解析JSON内容
            if "<|begin_of_box|>" in content:
                # 提取智谱AI的特殊格式
                json_start = content.find("<|begin_of_box|>") + len("<|begin_of_box|>")
                json_end = content.find("<|end_of_box|>")
                json_str = content[json_start:json_end].strip()
            elif "```json" in content:
                # 提取JSON代码块
                json_start = content.find("```json") + 7
                json_end = content.find("```", json_start)
                json_str = content[json_start:json_end].strip()
            else:
                # 直接解析整个内容
                json_str = content.strip()
            
            data = json.loads(json_str)
            return data.get("table_data", [])
            
        except (KeyError, json.JSONDecodeError, IndexError) as e:
            print(f"解析API响应失败: {e}")
            print(f"原始响应内容: {content}")
            return None