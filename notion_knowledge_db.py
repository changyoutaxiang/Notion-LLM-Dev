import requests
import json
from datetime import datetime
from notion_handler import NotionHandler
from typing import List, Dict

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
        
        # RAG系统配置
        self.config = config
        self._hybrid_engine = None
        self._initialize_rag_system()
    
    def _initialize_rag_system(self):
        """初始化RAG系统"""
        try:
            rag_config = self.config.get('knowledge_search', {}).get('rag_system', {})
            if rag_config.get('enabled', False):
                from hybrid_retrieval import create_hybrid_retrieval_engine
                self._hybrid_engine = create_hybrid_retrieval_engine(self, self.config)
                print("🚀 RAG智能检索系统已启用")
                
                # 异步构建语义索引
                import threading
                index_thread = threading.Thread(target=self._build_semantic_index_async)
                index_thread.daemon = True
                index_thread.start()
            else:
                print("📝 使用传统关键词检索")
        except Exception as e:
            print(f"⚠️ RAG系统初始化失败，使用传统检索: {e}")
            self._hybrid_engine = None
    
    def _build_semantic_index_async(self):
        """异步构建语义索引"""
        try:
            if self._hybrid_engine:
                print("🔄 正在后台构建语义索引...")
                if self._hybrid_engine.build_semantic_index():
                    print("✅ 语义索引构建完成")
                else:
                    print("❌ 语义索引构建失败")
        except Exception as e:
            print(f"❌ 构建语义索引时出错: {e}")
    
    def smart_search_knowledge(self, query: str, max_results: int = 5) -> List[Dict]:
        """智能知识搜索 - 新的主要搜索接口"""
        if self._hybrid_engine:
            try:
                # 使用混合检索引擎
                search_results = self._hybrid_engine.intelligent_search(query, max_results)
                
                # 转换为传统格式以保持兼容性
                knowledge_items = []
                for result in search_results:
                    knowledge_item = {
                        'id': result.knowledge_id,
                        'title': result.title,
                        'content': result.full_content or result.content_snippet,
                        'similarity_score': result.similarity_score,
                        'source_type': result.source_type,
                        'metadata': result.metadata
                    }
                    knowledge_items.append(knowledge_item)
                
                print(f"🧠 智能搜索完成: '{query}' → {len(knowledge_items)} 个结果")
                return knowledge_items
                
            except Exception as e:
                print(f"⚠️ 智能搜索失败，回退到关键词搜索: {e}")
                # 回退到传统搜索
                return self._fallback_search(query)
        else:
            # 使用传统关键词搜索
            return self._fallback_search(query)
    
    def _fallback_search(self, query: str) -> List[Dict]:
        """回退搜索方法"""
        # 简单的关键词提取
        import jieba
        words = list(jieba.cut(query))
        keywords = [word.strip() for word in words if len(word.strip()) > 1]
        
        if keywords:
            return self.search_knowledge_by_keywords(keywords)
        else:
            return []
    
    def search_knowledge_by_keywords(self, keywords: list):
        """根据关键词搜索知识"""
        if not self.knowledge_db_id:
            print("❌ 知识库数据库ID未配置")
            return []
        
        try:
            # 首先尝试精确关键词匹配
            exact_results = self._search_by_exact_keywords(keywords)
            
            # 如果精确匹配没有结果，使用智能匹配
            if not exact_results:
                smart_results = self._search_by_smart_matching(keywords)
                print(f"✅ 找到 {len(smart_results)} 个相关知识条目（智能匹配）")
                return smart_results
            else:
                print(f"✅ 找到 {len(exact_results)} 个相关知识条目（精确匹配）")
                return exact_results
            
        except Exception as e:
            print(f"❌ 搜索知识失败: {e}")
            return []
    
    def _search_by_exact_keywords(self, keywords: list):
        """精确关键词匹配搜索"""
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
                        "direction": "ascending"
                    },
                    {
                        "property": self.knowledge_usage_prop,
                        "direction": "descending"
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
            
            return knowledge_items
            
        except Exception as e:
            print(f"❌ 精确关键词搜索失败: {e}")
            return []
    
    def _search_by_smart_matching(self, keywords: list):
        """智能匹配搜索（标题和内容中查找关键词）"""
        try:
            # 获取所有启用的知识条目
            all_items = self.get_all_knowledge_items()
            
            # 在内存中进行智能匹配
            matched_items = []
            
            for item in all_items:
                # 检查标题、关键词列表、内容
                title = item.get('title', '').lower()
                keywords_list = [kw.lower() for kw in item.get('keywords', [])]
                content = item.get('content', '').lower()
                
                # 计算匹配分数
                match_score = 0
                matched_keywords = []
                
                for keyword in keywords:
                    keyword_lower = keyword.lower()
                    
                    # 标题匹配 (权重最高)
                    if keyword_lower in title:
                        match_score += 3
                        matched_keywords.append(keyword)
                    
                    # 关键词列表匹配 (权重高)
                    for existing_kw in keywords_list:
                        if keyword_lower in existing_kw:
                            match_score += 2
                            matched_keywords.append(keyword)
                            break
                    
                    # 内容匹配 (权重中等)
                    if keyword_lower in content:
                        match_score += 1
                        matched_keywords.append(keyword)
                
                # 如果有匹配，添加到结果
                if match_score > 0:
                    item['match_score'] = match_score
                    item['matched_keywords'] = list(set(matched_keywords))
                    matched_items.append(item)
            
            # 按匹配分数排序
            matched_items.sort(key=lambda x: (x['match_score'], x.get('usage_count', 0)), reverse=True)
            
            return matched_items
            
        except Exception as e:
            print(f"❌ 智能匹配搜索失败: {e}")
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
    
    def get_all_knowledge_items(self) -> List[Dict]:
        """获取所有知识条目（用于构建语义索引）"""
        if not self.knowledge_db_id:
            print("❌ 知识库数据库ID未配置")
            return []
            
        try:
            url = f"https://api.notion.com/v1/databases/{self.knowledge_db_id}/query"
            
            # 只获取启用状态的知识条目
            payload = {
                "filter": {
                    "property": self.knowledge_status_prop,
                    "select": {"equals": "启用"}
                },
                "sorts": [
                    {
                        "property": self.knowledge_priority_prop,
                        "direction": "ascending"
                    }
                ],
                "page_size": 100  # 一次获取100条
            }
            
            all_knowledge_items = []
            has_more = True
            
            while has_more:
                response = requests.post(url, headers=self.headers, json=payload, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                results = data.get("results", [])
                
                for page in results:
                    knowledge_data = self._extract_knowledge_data(page)
                    if knowledge_data:
                        all_knowledge_items.append(knowledge_data)
                
                # 检查是否还有更多页面
                has_more = data.get("has_more", False)
                if has_more:
                    payload["start_cursor"] = data.get("next_cursor")
            
            print(f"📚 获取到 {len(all_knowledge_items)} 个知识条目用于构建索引")
            return all_knowledge_items
            
        except Exception as e:
            print(f"❌ 获取所有知识条目失败: {e}")
            return []

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