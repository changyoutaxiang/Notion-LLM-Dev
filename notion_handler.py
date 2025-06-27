import requests
import json
from datetime import datetime, timezone

class NotionHandler:
    """处理与Notion API的所有交互"""
    
    def __init__(self, api_key, database_id):
        self.api_key = api_key
        self.database_id = database_id
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
    
    def get_pending_messages(self, require_template_selection=True):
        """获取待处理的消息"""
        try:
            url = f"https://api.notion.com/v1/databases/{self.database_id}/query"
            
            # 查询条件：LLM 回复字段为空 AND 模板选择不为空（双异步模式）
            if require_template_selection:
                payload = {
                    "filter": {
                        "and": [
                            {
                                "property": "LLM 回复",
                                "rich_text": {
                                    "is_empty": True
                                }
                            },
                            {
                                "property": "模板选择",
                                "select": {
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
            else:
                # 兼容模式：只检查LLM回复为空
                payload = {
                    "filter": {
                        "property": "LLM 回复",
                        "rich_text": {
                            "is_empty": True
                        }
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
            
            # 准备更新数据
            properties = {
                "LLM 回复": {
                    "rich_text": [
                        {
                            "text": {
                                "content": llm_reply
                            }
                        }
                    ]
                }
            }
            
            # 如果提供了标题，同时更新标题
            if title:
                properties["标题"] = {
                    "title": [
                        {
                            "text": {
                                "content": title
                            }
                        }
                    ]
                }
            
            payload = {"properties": properties}
            
            response = requests.patch(url, headers=self.headers, json=payload, timeout=30)
            response.raise_for_status()
            
            return True
            
        except Exception as e:
            print(f"更新Notion回复时出错: {e}")
            return False
    
    def _extract_message_data(self, page):
        """从Notion页面中提取消息数据"""
        try:
            properties = page.get("properties", {})
            
            # 提取标题
            title_prop = properties.get("标题", {})
            title = ""
            if title_prop.get("title"):
                title = title_prop["title"][0]["text"]["content"]
            
            # 提取输入内容
            content_prop = properties.get("输入内容", {})
            content = ""
            if content_prop.get("rich_text"):
                content = content_prop["rich_text"][0]["text"]["content"]
            
            # 提取模板选择
            template_prop = properties.get("模板选择", {})
            template_choice = ""
            if template_prop.get("select") and template_prop["select"]:
                template_choice = template_prop["select"]["name"]
            
            if not content:  # 如果没有内容，跳过这条记录
                return None
            
            return {
                "page_id": page["id"],
                "title": title,
                "content": content,
                "template_choice": template_choice,
                "created_time": page.get("created_time", "")
            }
            
        except Exception as e:
            print(f"解析Notion数据时出错: {e}")
            return None
    
    def get_waiting_count(self):
        """获取等待模板选择的记录数量"""
        try:
            url = f"https://api.notion.com/v1/databases/{self.database_id}/query"
            
            # 查询条件：LLM回复为空 AND 模板选择为空
            payload = {
                "filter": {
                    "and": [
                        {
                            "property": "LLM 回复",
                            "rich_text": {
                                "is_empty": True
                            }
                        },
                        {
                            "property": "模板选择",
                            "select": {
                                "is_empty": True
                            }
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