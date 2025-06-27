import requests
import json
from datetime import datetime, timezone
import os

class NotionHandler:
    """处理与Notion API的所有交互"""
    
    def __init__(self, config):
        notion_config = config['notion']
        self.api_key = notion_config['api_key']
        self.database_id = notion_config['database_id']
        
        # 从配置中加载所有需要的属性名称
        self.input_prop = notion_config['input_property_name']
        self.output_prop = notion_config['output_property_name']
        self.template_prop = notion_config['template_property_name']
        self.knowledge_prop = notion_config['knowledge_base_property_name']
        self.model_prop = notion_config['model_property_name']
        self.title_prop = notion_config['title_property_name']

        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
    
    def get_pending_messages(self):
        """获取待处理的消息"""
        try:
            url = f"https://api.notion.com/v1/databases/{self.database_id}/query"
            
            # 更新查询逻辑：当输出为空，且另外三个关键字段都已选择时，触发任务
            payload = {
                "filter": {
                    "and": [
                        {
                            "property": self.output_prop,
                            "rich_text": {
                                "is_empty": True
                            }
                        },
                        {
                            "property": self.template_prop,
                            "select": {
                                "is_not_empty": True
                            }
                        },
                        {
                            "property": self.model_prop,
                            "select": {
                                "is_not_empty": True
                            }
                        },
                        {
                            "property": self.knowledge_prop,
                            "multi_select": {
                                "is_not_empty": True
                            }
                        }
                    ]
                },
                "sorts": [
                    {
                        "timestamp": "created_time",
                        "direction": "ascending"
                    }
                ]
            }
            
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            messages = []
            
            for page in data.get("results", []):
                message = self._extract_message_data(page)
                if message:
                    messages.append(message)
            
            return messages
            
        except Exception as e:
            print(f"获取Notion消息时出错: {e}")
            return []
    
    def update_message_reply(self, page_id, llm_reply, title=None):
        """更新LLM回复和标题"""
        try:
            url = f"https://api.notion.com/v1/pages/{page_id}"
            
            # --- 改进的内容清洗逻辑 ---
            # 1. 基本清理：去除首尾空白
            cleaned_reply = llm_reply.strip() if llm_reply else ""
            
            # 2. 长度限制：Notion Rich Text 限制 2000 字符
            if len(cleaned_reply) > 1900:  # 留一些余量
                cleaned_reply = cleaned_reply[:1900] + "...\n\n[内容过长，已截断]"
            
            # 3. 如果内容为空，设置默认提示
            if not cleaned_reply:
                cleaned_reply = "[AI未返回有效内容]"
            
            print(f"内容清洗: 原长度={len(llm_reply) if llm_reply else 0}, 清洗后长度={len(cleaned_reply)}")
            # --- 清洗结束 ---

            # 准备更新数据
            properties = {
                self.output_prop: {
                    "rich_text": [
                        {
                            "text": {
                                "content": cleaned_reply
                            }
                        }
                    ]
                }
            }
            
            # 如果提供了标题，同时更新标题
            if title:
                # 确保标题长度不超过限制
                title = title.strip()
                if len(title) > 100:  # Notion标题限制
                    title = title[:100]
                    
                properties[self.title_prop] = {
                    "title": [
                        {
                            "text": {
                                "content": title
                            }
                        }
                    ]
                }
            
            payload = {"properties": properties}
            
            print(f"准备更新页面: {page_id}")
            response = requests.patch(url, headers=self.headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                print(f"✅ 页面更新成功: {page_id[:8]}...")
                return True
            else:
                print(f"❌ 页面更新失败: HTTP {response.status_code}")
                print(f"错误详情: {response.text}")
                
                # 尝试解析错误信息
                try:
                    error_data = response.json()
                    if 'message' in error_data:
                        print(f"Notion错误信息: {error_data['message']}")
                except:
                    pass
                
                return False
            
        except requests.exceptions.RequestException as e:
            print(f"网络请求错误: {e}")
            return False
        except Exception as e:
            print(f"更新Notion回复时出错: {e}")
            return False
    
    def _extract_message_data(self, page):
        """从Notion页面中提取消息数据"""
        try:
            properties = page.get("properties", {})
            
            # 提取标题
            title_prop = properties.get(self.title_prop, {})
            title = ""
            if title_prop.get("title"):
                title = title_prop["title"][0]["text"]["content"]
            
            # 提取输入内容
            content_prop = properties.get(self.input_prop, {})
            content = ""
            if content_prop.get("rich_text"):
                content = content_prop["rich_text"][0]["text"]["content"]
            
            # 提取模板选择
            template_prop = properties.get(self.template_prop, {})
            template_choice = ""
            if template_prop.get("select") and template_prop["select"]:
                template_choice = template_prop["select"]["name"]
            
            # 提取标签
            tags_prop = properties.get(self.knowledge_prop, {})
            tags = []
            if tags_prop.get("multi_select"):
                tags = [tag["name"] for tag in tags_prop["multi_select"]]

            # 提取模型选择
            model_prop = properties.get(self.model_prop, {})
            model_choice = ""
            if model_prop.get("select") and model_prop["select"]:
                model_choice = model_prop["select"]["name"]

            if not content:  # 如果没有内容，跳过这条记录
                return None
            
            return {
                "page_id": page["id"],
                "title": title,
                "content": content,
                "template_choice": template_choice,
                "tags": tags,
                "model_choice": model_choice,
                "created_time": page.get("created_time", "")
            }
            
        except Exception as e:
            print(f"解析Notion数据时出错: {e}")
            return None
    
    def get_waiting_count(self):
        """获取等待模板选择的记录数量"""
        try:
            url = f"https://api.notion.com/v1/databases/{self.database_id}/query"
            
            # 查询条件：LLM回复为空 AND (模板选择为空 OR 模型选择为空 or 背景为空)
            payload = {
                "filter": {
                    "and": [
                        {
                            "property": self.output_prop,
                            "rich_text": {
                                "is_empty": True
                            }
                        },
                        {
                            "or": [
                                {
                                    "property": self.template_prop,
                                    "select": {
                                        "is_empty": True
                                    }
                                },
                                {
                                    "property": self.model_prop,
                                    "select": {
                                        "is_empty": True
                                    }
                                },
                                {
                                    "property": self.knowledge_prop,
                                    "multi_select": {
                                        "is_empty": True
                                    }
                                }
                            ]
                        }
                    ]
                }
            }
            
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            return len(data.get("results", []))
            
        except Exception as e:
            print(f"获取等待数量时出错: {e}")
            return 0
    
    def sync_template_options(self, template_names):
        """同步模板选项到Notion数据库"""
        try:
            url = f"https://api.notion.com/v1/databases/{self.database_id}"
            
            # 构建模板选项
            options = []
            for name in template_names:
                options.append({
                    "name": name,
                    "color": "default"
                })
            
            # 更新数据库Schema
            payload = {
                "properties": {
                    "模板选择": {
                        "select": {
                            "options": options
                        }
                    }
                }
            }
            
            response = requests.patch(url, headers=self.headers, json=payload, timeout=30)
            response.raise_for_status()
            
            return True, f"已同步{len(template_names)}个模板选项到Notion"
            
        except Exception as e:
            print(f"同步模板选项时出错: {e}")
            return False, f"同步失败: {e}"

    def test_connection(self):
        """测试Notion连接"""
        try:
            url = f"https://api.notion.com/v1/databases/{self.database_id}"
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return True, "Notion连接成功！"
        except Exception as e:
            return False, f"Notion连接失败: {e}"

    def get_context_from_knowledge_base(self, tags: list[str]) -> str:
        """
        根据标签从知识库中获取上下文。
        简单实现：标签名直接对应 knowledge_base 文件夹下的 .md 文件名。
        特殊处理：如果标签包含"无"，则跳过知识库读取。
        """
        # 检查是否包含"无"标签
        if "无" in tags:
            print("🚫 检测到'无'标签，跳过知识库读取")
            return ""
        
        base_path = "knowledge_base"
        context_parts = []
        
        if not os.path.isdir(base_path):
            print(f"知识库目录未找到: {base_path}")
            return ""

        for tag in tags:
            # 兼容Windows和macOS/Linux的文件名
            safe_tag = tag.replace("/", "_").replace("\\", "_")
            file_path = os.path.join(base_path, f"{safe_tag}.md")
            
            if os.path.exists(file_path):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        # 为每个上下文片段添加一个明确的标题，帮助LLM理解来源
                        context_parts.append(f"--- 来自知识库: {tag} ---\n{content}")
                except Exception as e:
                    print(f"读取知识文件 {file_path} 时出错: {e}")
        
        if not context_parts:
            return ""
            
        # 将所有找到的上下文拼接成一个字符串
        return "\n\n".join(context_parts) 