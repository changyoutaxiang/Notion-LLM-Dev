import requests
import json

class LLMHandler:
    """处理与OpenRouter API的所有交互"""
    
    def __init__(self, api_key, model="anthropic/claude-3.5-sonnet"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def send_message(self, message_content, system_prompt=None, override_model=None):
        """发送消息给LLM并获取回复"""
        try:
            # 确定本次调用使用的模型
            current_model = override_model or self.model

            # 构建消息
            messages = []
            
            # 如果有系统提示，添加系统消息
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            
            # 添加用户消息
            messages.append({
                "role": "user",
                "content": message_content
            })
            
            # 准备请求数据
            payload = {
                "model": current_model,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 2000
            }
            
            # 发送请求
            response = requests.post(
                self.base_url, 
                headers=self.headers, 
                json=payload, 
                timeout=60
            )
            response.raise_for_status()
            
            # 解析响应
            data = response.json()
            
            if "choices" in data and len(data["choices"]) > 0:
                choice = data["choices"][0]
                message = choice.get("message", {})
                
                # 优先获取推理内容（适用于Gemini 2.5 Pro等推理模型）
                reasoning = message.get("reasoning", "")
                content = message.get("content", "")
                
                # 如果有推理内容且主要内容为空或只是换行，使用推理内容
                if reasoning and (not content.strip() or content.strip() == ""):
                    reply = reasoning
                    print(f"📝 使用推理模式内容 (长度: {len(reasoning)})")
                else:
                    reply = content
                    print(f"📝 使用标准内容 (长度: {len(content)})")
                
                return True, reply
            else:
                return False, "LLM响应格式异常"
                
        except requests.exceptions.Timeout:
            return False, "请求超时，请稍后重试"
        except requests.exceptions.RequestException as e:
            return False, f"网络请求失败: {e}"
        except Exception as e:
            return False, f"处理LLM响应时出错: {e}"
    
    def generate_title(self, content, max_length=20, min_length=10):
        """生成简洁标题"""
        try:
            title_prompt = f"""
为以下内容生成一个非常简洁的中文标题。

要求:
1.  **直接输出**: 只返回标题本身，不要包含任何解释、思考、引号或"标题："这样的前缀。
2.  **语言**: 必须是中文。
3.  **长度**: {min_length}到{max_length}个汉字。
4.  **内容**: 精准概括核心主题。

内容：
---
{content[:200]}
---
"""
            
            success, title = self.send_message(title_prompt)
            
            if success:
                # 确保标题不超过限制长度
                title = title.strip()
                if len(title) > max_length:
                    title = title[:max_length]
                return True, title
            else:
                return False, title
                
        except Exception as e:
            return False, f"生成标题时出错: {e}"
    
    def process_with_template_and_title(self, content, system_prompt, max_title_length=20, min_title_length=10, override_model=None):
        """处理消息并生成标题（并行处理）"""
        try:
            # 生成主要回复
            main_success, main_reply = self.send_message(content, system_prompt, override_model=override_model)
            
            if not main_success:
                return False, main_reply, None
            
            # 生成标题
            title_success, title = self.generate_title(content, max_title_length, min_title_length)
            
            if not title_success:
                # 如果标题生成失败，使用备选方案
                title = self._generate_fallback_title(content, max_title_length)
            
            return True, main_reply, title
            
        except Exception as e:
            return False, f"处理消息时出错: {e}", None
    
    def _generate_fallback_title(self, content, max_length=10):
        """AI生成标题失败时的备选方案"""
        # 方法1：提取前N字
        if len(content) <= max_length:
            return content
        
        # 方法2：智能截取到标点符号
        for i, char in enumerate(content[:max_length+5]):
            if char in "。！？，；":
                if i <= max_length:
                    return content[:i]
                break
        
        # 方法3：简单截取
        return content[:max_length]
    
    def test_connection(self):
        """测试OpenRouter连接"""
        try:
            success, reply = self.send_message(
                "请简单回复'连接测试成功'", 
                "你是一个测试助手，请简洁回复。"
            )
            
            if success:
                return True, f"OpenRouter连接成功！LLM回复: {reply[:50]}..."
            else:
                return False, f"OpenRouter测试失败: {reply}"
                
        except Exception as e:
            return False, f"OpenRouter连接测试出错: {e}"
    
    def get_available_models(self):
        """获取可用模型列表（可选功能）"""
        try:
            url = "https://openrouter.ai/api/v1/models"
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            models = []
            
            for model in data.get("data", []):
                models.append({
                    "id": model.get("id", ""),
                    "name": model.get("name", ""),
                    "description": model.get("description", "")
                })
            
            return models
            
        except Exception as e:
            print(f"获取模型列表时出错: {e}")
            return [] 