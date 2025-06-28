import requests
import json
from datetime import datetime
from notion_handler import NotionHandler

class NotionKnowledgeDB(NotionHandler):
    """扩展NotionHandler以支持知识库操作"""
    
    def __init__(self, config):
        super().__init__(config)
        
        # 知识库数据库配置
        notion_config = config['notion']
        self.knowledge_db_id = notion_config.get('knowledge_database_id')
        self.category_db_id = notion_config.get('category_database_id')
        
        # 知识库字段名配置
        self.knowledge_title_prop = notion_config.get('knowledge_title_property', '知识标题')
        self.knowledge_category_prop = notion_config.get('knowledge_category_property', '知识分类')
        self.knowledge_subcategory_prop = notion_config.get('knowledge_subcategory_property', '知识子类')
        self.knowledge_keywords_prop = notion_config.get('knowledge_keywords_property', '关键词')
        self.knowledge_scenarios_prop = notion_config.get('knowledge_scenarios_property', '适用场景')
        self.knowledge_priority_prop = notion_config.get('knowledge_priority_property', '优先级')
        self.knowledge_status_prop = notion_config.get('knowledge_status_property', '状态')
        self.knowledge_relations_prop = notion_config.get('knowledge_relations_property', '关联知识')
        self.knowledge_usage_prop = notion_config.get('knowledge_usage_property', '使用频率')
    
    def search_knowledge_by_keywords(self, keywords: list):
        """根据关键词搜索知识"""
        if not self.knowledge_db_id:
            print("❌ 知识库数据库ID未配置")
            return []
        
        try:
            url = f"https://api.notion.com/v1/databases/{self.knowledge_db_id}/query"
            
            # 构建筛选条件：状态为启用 AND 包含任一关键词
            filters = {
                "and": [
                    {
                        "property": self.knowledge_status_prop,
                        "select": {"equals": "启用"}
                    },
                    {
                        "or": [
                            {
                                "property": self.knowledge_keywords_prop,
                                "multi_select": {"contains": keyword}
                            } for keyword in keywords
                        ]
                    }
                ]
            }
            
            payload = {
                "filter": filters,
                "sorts": [
                    {
                        "property": self.knowledge_priority_prop,
                        "direction": "ascending"  # 高优先级排在前面
                    },
                    {
                        "property": self.knowledge_usage_prop,
                        "direction": "descending"  # 使用频率高的排在前面
                    }
                ]
            }
            
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            knowledge_items = []
            
            for page in data.get("results", []):
                knowledge_data = self._extract_knowledge_data(page)
                if knowledge_data:
                    knowledge_items.append(knowledge_data)
            
            print(f"✅ 找到 {len(knowledge_items)} 个相关知识条目")
            return knowledge_items
            
        except Exception as e:
            print(f"❌ 搜索知识失败: {e}")
            return []
    
    def get_knowledge_by_category(self, category: str, subcategory: str = None):
        """根据分类获取知识"""
        if not self.knowledge_db_id:
            print("❌ 知识库数据库ID未配置")
            return []
            
        try:
            url = f"https://api.notion.com/v1/databases/{self.knowledge_db_id}/query"
            
            filters = {
                "and": [
                    {
                        "property": self.knowledge_status_prop,
                        "select": {"equals": "启用"}
                    },
                    {
                        "property": self.knowledge_category_prop,
                        "select": {"equals": category}
                    }
                ]
            }
            
            if subcategory:
                filters["and"].append({
                    "property": self.knowledge_subcategory_prop,
                    "select": {"equals": subcategory}
                })
            
            payload = {"filter": filters}
            
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            knowledge_items = []
            
            for page in data.get("results", []):
                knowledge_data = self._extract_knowledge_data(page)
                if knowledge_data:
                    knowledge_items.append(knowledge_data)
            
            return knowledge_items
            
        except Exception as e:
            print(f"❌ 按分类获取知识失败: {e}")
            return []
    
    def update_usage_frequency(self, knowledge_id: str):
        """更新知识条目的使用频率"""
        try:
            # 获取当前页面信息
            url = f"https://api.notion.com/v1/pages/{knowledge_id}"
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            page = response.json()
            properties = page.get("properties", {})
            
            # 获取当前使用频率
            usage_prop = properties.get(self.knowledge_usage_prop, {})
            current_frequency = usage_prop.get("number", 0) or 0
            
            # 更新使用频率
            update_url = f"https://api.notion.com/v1/pages/{knowledge_id}"
            update_payload = {
                "properties": {
                    self.knowledge_usage_prop: {
                        "number": current_frequency + 1
                    }
                }
            }
            
            update_response = requests.patch(update_url, headers=self.headers, json=update_payload, timeout=10)
            update_response.raise_for_status()
            
            print(f"📊 更新使用频率: {current_frequency} → {current_frequency + 1}")
            return True
            
        except Exception as e:
            print(f"⚠️  更新使用频率失败: {e}")
            return False
    
    def create_knowledge_entry(self, title: str, category: str, keywords: list, content: str, **kwargs):
        """创建新的知识条目"""
        if not self.knowledge_db_id:
            print("❌ 知识库数据库ID未配置")
            return None
            
        try:
            # 构建页面属性
            properties = {
                self.knowledge_title_prop: {
                    "title": [{"text": {"content": title}}]
                },
                self.knowledge_category_prop: {
                    "select": {"name": category}
                },
                self.knowledge_keywords_prop: {
                    "multi_select": [{"name": keyword} for keyword in keywords]
                },
                self.knowledge_priority_prop: {
                    "select": {"name": kwargs.get('priority', '中')}
                },
                self.knowledge_status_prop: {
                    "select": {"name": kwargs.get('status', '启用')}
                },
                self.knowledge_usage_prop: {
                    "number": 0
                }
            }
            
            # 可选字段（仅在数据库中存在时添加）
            # 暂时跳过可选字段，避免字段不存在错误
            # if kwargs.get('subcategory'):
            #     properties[self.knowledge_subcategory_prop] = {
            #         "select": {"name": kwargs['subcategory']}
            #     }
            # 
            # if kwargs.get('scenarios'):
            #     properties[self.knowledge_scenarios_prop] = {
            #         "multi_select": [{"name": scenario} for scenario in kwargs['scenarios']]
            #     }
            
            # 创建页面
            url = "https://api.notion.com/v1/pages"
            payload = {
                "parent": {"database_id": self.knowledge_db_id},
                "properties": properties
            }
            
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            response.raise_for_status()
            
            page = response.json()
            page_id = page["id"]
            
            # 添加页面内容
            if content:
                success = self._update_knowledge_content(page_id, content)
                if not success:
                    print("⚠️  知识条目创建成功，但内容添加失败")
            
            print(f"✅ 创建知识条目成功: {title}")
            return page_id
            
        except Exception as e:
            print(f"❌ 创建知识条目失败: {e}")
            return None
    
    def _extract_knowledge_data(self, page):
        """从Notion页面提取知识数据"""
        try:
            properties = page.get("properties", {})
            
            # 提取标题
            title_prop = properties.get(self.knowledge_title_prop, {})
            if title_prop.get("type") == "title":
                title_list = title_prop.get("title", [])
                title = title_list[0].get("text", {}).get("content", "") if title_list else ""
            else:
                title = ""
            
            if not title:
                return None
            
            # 提取分类
            category_prop = properties.get(self.knowledge_category_prop, {})
            category = ""
            if category_prop.get("type") == "select":
                category_obj = category_prop.get("select")
                category = category_obj.get("name", "") if category_obj else ""
            
            # 提取关键词
            keywords_prop = properties.get(self.knowledge_keywords_prop, {})
            keywords = []
            if keywords_prop.get("type") == "multi_select":
                keywords_list = keywords_prop.get("multi_select", [])
                keywords = [item.get("name", "") for item in keywords_list]
            
            # 提取优先级
            priority_prop = properties.get(self.knowledge_priority_prop, {})
            priority = "中"
            if priority_prop.get("type") == "select":
                priority_obj = priority_prop.get("select")
                priority = priority_obj.get("name", "中") if priority_obj else "中"
            
            # 提取使用频率
            usage_prop = properties.get(self.knowledge_usage_prop, {})
            usage_count = usage_prop.get("number", 0) or 0
            
            # 获取页面内容
            content = self._get_page_content(page["id"])
            
            return {
                'id': page["id"],
                'title': title,
                'category': category,
                'keywords': keywords,
                'priority': priority,
                'usage_count': usage_count,
                'content': content,
                'url': f"https://notion.so/{page['id'].replace('-', '')}"
            }
            
        except Exception as e:
            print(f"❌ 提取知识数据失败: {e}")
            return None
    
    def _update_knowledge_content(self, page_id: str, content: str):
        """更新知识条目的页面内容"""
        try:
            # 将内容分段处理
            paragraphs = self._split_content_into_paragraphs(content)
            
            # 构建内容块
            children = []
            
            for paragraph in paragraphs:
                if paragraph.strip():
                    children.append({
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [
                                {
                                    "type": "text",
                                    "text": {"content": paragraph}
                                }
                            ]
                        }
                    })
            
            # 更新页面内容
            url = f"https://api.notion.com/v1/blocks/{page_id}/children"
            payload = {"children": children}
            
            response = requests.patch(url, headers=self.headers, json=payload, timeout=30)
            response.raise_for_status()
            
            return True
            
        except Exception as e:
            print(f"❌ 更新知识内容失败: {e}")
            return False
    
    def test_knowledge_database_connection(self):
        """测试知识库数据库连接"""
        if not self.knowledge_db_id:
            return False, "知识库数据库ID未配置"
        
        try:
            url = f"https://api.notion.com/v1/databases/{self.knowledge_db_id}"
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            db_info = response.json()
            db_title = db_info.get("title", [{}])[0].get("text", {}).get("content", "未知")
            
            return True, f"知识库连接成功: {db_title}"
            
        except Exception as e:
            return False, f"知识库连接失败: {e}" 