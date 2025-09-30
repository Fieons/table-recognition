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
            "thinking": {
                "type": "disabled"
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
                    
                    # 处理特定的错误状态码，提供详细的错误信息和解决方案
                    if response.status_code == 401:
                        error_msg = "API密钥无效或已过期"
                        solution = "请检查config.py中的ZHIPU_API_KEY配置，或重新获取有效的API密钥"
                        raise Exception(f"{error_msg} | 解决方案: {solution}")
                    elif response.status_code == 429:
                        error_msg = "API请求频率超限"
                        solution = "请等待一段时间后重试，或联系API服务商增加配额"
                        raise Exception(f"{error_msg} | 解决方案: {solution}")
                    elif response.status_code == 400:
                        error_msg = "请求参数错误"
                        solution = "请检查图片格式和大小是否符合要求，或联系技术支持"
                        raise Exception(f"{error_msg} | 解决方案: {solution}")
                    elif response.status_code == 403:
                        error_msg = "访问被拒绝"
                        solution = "请检查API密钥权限或账户状态"
                        raise Exception(f"{error_msg} | 解决方案: {solution}")
                    elif response.status_code >= 500:
                        error_msg = f"服务器内部错误 ({response.status_code})"
                        solution = "这是服务器端问题，请稍后重试或联系API服务商"
                        raise Exception(f"{error_msg} | 解决方案: {solution}")
                    else:
                        # 强制抛出异常以显示错误
                        response.raise_for_status()
                
                response.raise_for_status()
                return response.json()
            except (requests.exceptions.RequestException, requests.exceptions.Timeout) as e:
                if attempt == self.max_retries - 1:
                    print(f"最终请求失败: {e}")
                    if hasattr(e, 'response') and e.response is not None:
                        print(f"错误响应: {e.response.text}")
                        print(f"错误响应头: {dict(e.response.headers)}")
                    
                    # 提供更友好的错误信息和解决方案
                    error_msg = str(e)
                    if "401" in error_msg:
                        raise Exception("API密钥验证失败 | 解决方案: 请检查config.py中的ZHIPU_API_KEY配置")
                    elif "timed out" in error_msg.lower():
                        raise Exception("API请求超时 | 解决方案: 请检查网络连接，或增加config.py中的TIMEOUT值")
                    elif "connection" in error_msg.lower():
                        raise Exception("网络连接失败 | 解决方案: 请检查网络连接和代理设置")
                    elif "ssl" in error_msg.lower():
                        raise Exception("SSL证书错误 | 解决方案: 请检查系统时间或尝试更新证书")
                    else:
                        raise Exception(f"API请求失败: {error_msg} | 解决方案: 请检查网络连接和API配置")
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
            
            # 检查内容是否为空
            if not content or content.strip() == "":
                print("AI返回内容为空")
                return None
            
            # 尝试解析JSON内容
            json_str = ""
            if "<|begin_of_box|>" in content:
                # 提取智谱AI的特殊格式
                json_start = content.find("<|begin_of_box|>") + len("<|begin_of_box|>")
                json_end = content.find("<|end_of_box|>")
                if json_end > json_start:
                    json_str = content[json_start:json_end].strip()
            elif "```json" in content:
                # 提取JSON代码块
                json_start = content.find("```json") + 7
                json_end = content.find("```", json_start)
                if json_end > json_start:
                    json_str = content[json_start:json_end].strip()
            else:
                # 直接解析整个内容
                json_str = content.strip()
            
            # 如果提取失败，尝试直接解析整个内容
            if not json_str:
                json_str = content.strip()
            
            # 清理JSON字符串中的特殊字符
            json_str = json_str.replace('\\n', '').replace('\\t', '').strip()
            
            # 如果内容以```开头和结尾，去除它们
            if json_str.startswith('```') and json_str.endswith('```'):
                json_str = json_str[3:-3].strip()
            
            # 尝试解析JSON
            data = json.loads(json_str)
            return data.get("table_data", [])
            
        except (KeyError, json.JSONDecodeError, IndexError) as e:
            print(f"解析API响应失败: {e}")
            print(f"原始响应内容: {content}")
            
            # 尝试手动解析简单的表格格式
            try:
                # 如果JSON解析失败，尝试从文本中提取表格数据
                lines = content.strip().split('\\n')
                table_data = []
                for line in lines:
                    # 简单的行解析，假设每行用|或空格分隔
                    if '|' in line:
                        row = [cell.strip() for cell in line.split('|') if cell.strip()]
                    else:
                        row = [cell.strip() for cell in line.split() if cell.strip()]
                    if row:
                        table_data.append(row)
                
                if table_data:
                    print("成功从文本中提取表格数据")
                    return table_data
            except Exception as parse_error:
                print(f"文本解析也失败: {parse_error}")
            
            return None