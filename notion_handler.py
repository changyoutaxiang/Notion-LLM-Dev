import requests
import json
from datetime import datetime, timezone
import os

class NotionHandler:
    """处理与Notion API的所有交互"""
    
    def __init__(self, api_key, database_id, knowledge_base_property="标签"):
        self.api_key = api_key
        self.database_id = database_id
        self.knowledge_base_property = knowledge_base_property
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
            
            # --- 升级内容清洗逻辑 ---
            # 1. 移除代码块标记
            cleaned_reply = llm_reply.replace("```", "")
            # 2. 移除Markdown标题标记 (#) 和列表标记 (*, -)
            lines = cleaned_reply.split('\n')
            lines = [line.lstrip('#*-. ') for line in lines]
            cleaned_reply = '\n'.join(lines)
            # 3. 去除首尾的空行和空格
            cleaned_reply = cleaned_reply.strip()
            
            # 4. 如果内容为空，则设置一个默认提示
            if not cleaned_reply:
                cleaned_reply = "[AI未返回有效内容]"
            # --- 清洗结束 ---

            # 准备更新数据
            properties = {
                "LLM 回复": {
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
            
            # 提取标签
            tags_prop = properties.get(self.knowledge_base_property, {})
            tags = []
            if tags_prop.get("multi_select"):
                tags = [tag["name"] for tag in tags_prop["multi_select"]]

            if not content:  # 如果没有内容，跳过这条记录
                return None
            
            return {
                "page_id": page["id"],
                "title": title,
                "content": content,
                "template_choice": template_choice,
                "tags": tags,
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

    def get_context_from_knowledge_base(self, tags: list[str]) -> str:
        """
        根据标签从知识库中获取上下文。
        简单实现：标签名直接对应 knowledge_base 文件夹下的 .md 文件名。
        """
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