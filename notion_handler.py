import requests
import json
from datetime import datetime, timezone
import os

class NotionHandler:
    """处理与Notion API的所有交互"""
    
    def __init__(self, config):
        # 保存完整配置以便后续使用
        self.config = config
        
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
        
        # 模板库数据库配置
        self.template_database_id = notion_config.get('template_database_id')
        self.template_name_prop = notion_config.get('template_name_property', '模板名称')
        self.template_category_prop = notion_config.get('template_category_property', '分类')
        self.template_prompt_prop = notion_config.get('template_prompt_property', '提示词')
        self.template_description_prop = notion_config.get('template_description_property', '描述')
        self.template_status_prop = notion_config.get('template_status_property', '状态')

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
        """更新LLM回复和标题 - 将回复写入页面内容而不是属性栏"""
        try:
            # --- 改进的内容清洗逻辑 ---
            # 1. 基本清理：去除首尾空白
            cleaned_reply = llm_reply.strip() if llm_reply else ""
            
            # 3. 如果内容为空，设置默认提示
            if not cleaned_reply:
                cleaned_reply = "[AI未返回有效内容]"
            
            print(f"内容清洗: 原长度={len(llm_reply) if llm_reply else 0}, 清洗后长度={len(cleaned_reply)}")
            # --- 清洗结束 ---

            # 第一步：更新标题和清空回复属性栏
            properties = {}
            
            # 清空回复属性栏，因为内容将存储在页面内容中
            properties[self.output_prop] = {
                "rich_text": [
                    {
                        "text": {
                            "content": "✅ 已回复 (查看页面内容)"
                        }
                    }
                ]
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
            
            # 更新页面属性
            page_url = f"https://api.notion.com/v1/pages/{page_id}"
            payload = {"properties": properties}
            
            print(f"准备更新页面属性: {page_id}")
            response = requests.patch(page_url, headers=self.headers, json=payload, timeout=30)
            
            if response.status_code != 200:
                print(f"❌ 页面属性更新失败: HTTP {response.status_code}")
                print(f"错误详情: {response.text}")
                return False
            
            # 第二步：将LLM回复内容写入页面内容块
            success = self._append_content_to_page(page_id, cleaned_reply)
            
            if success:
                print(f"✅ 页面内容更新成功: {page_id[:8]}...")
                return True
            else:
                print(f"❌ 页面内容更新失败: {page_id[:8]}...")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"网络请求错误: {e}")
            return False
        except Exception as e:
            print(f"更新Notion回复时出错: {e}")
            return False

    def _append_content_to_page(self, page_id, content):
        """将内容追加到页面内容块中"""
        try:
            # 首先获取页面现有的内容块
            blocks_url = f"https://api.notion.com/v1/blocks/{page_id}/children"
            
            # 将长文本分割成多个段落，因为Notion对单个文本块有长度限制
            paragraphs = self._split_content_into_paragraphs(content)
            
            # 构建要添加的内容块
            children = []
            
            # 添加分割线
            children.append({
                "object": "block",
                "type": "divider",
                "divider": {}
            })
            
            # 添加标题
            children.append({
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": "🤖 AI 回复"
                            }
                        }
                    ]
                }
            })
            
            # 添加内容段落
            for paragraph in paragraphs:
                if paragraph.strip():  # 只添加非空段落
                    children.append({
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [
                                {
                                    "type": "text",
                                    "text": {
                                        "content": paragraph
                                    }
                                }
                            ]
                        }
                    })
            
            # 添加时间戳
            timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
            children.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": f"📅 生成时间：{timestamp}"
                            },
                            "annotations": {
                                "color": "gray"
                            }
                        }
                    ]
                }
            })
            
            # 发送请求添加内容块
            payload = {"children": children}
            
            response = requests.patch(blocks_url, headers=self.headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                print(f"✅ 页面内容追加成功")
                return True
            else:
                print(f"❌ 页面内容追加失败: HTTP {response.status_code}")
                print(f"错误详情: {response.text}")
                
                # 尝试解析错误信息
                try:
                    error_data = response.json()
                    if 'message' in error_data:
                        print(f"Notion错误信息: {error_data['message']}")
                except:
                    pass
                
                return False
                
        except Exception as e:
            print(f"追加页面内容时出错: {e}")
            return False

    def _split_content_into_paragraphs(self, content, max_length=1900):
        """将长文本分割成适合Notion的段落"""
        if not content:
            return []
        
        # 如果内容不太长，直接返回
        if len(content) <= max_length:
            return [content]
        
        # 按段落分割（双换行符）
        paragraphs = content.split('\n\n')
        result = []
        current_chunk = ""
        
        for paragraph in paragraphs:
            # 如果当前段落本身就很长，需要进一步分割
            if len(paragraph) > max_length:
                # 先保存当前chunk
                if current_chunk:
                    result.append(current_chunk.strip())
                    current_chunk = ""
                
                # 分割长段落
                sentences = paragraph.split('。')
                temp_chunk = ""
                
                for sentence in sentences:
                    if sentence:
                        sentence = sentence + '。' if not sentence.endswith('。') else sentence
                        if len(temp_chunk + sentence) <= max_length:
                            temp_chunk += sentence
                        else:
                            if temp_chunk:
                                result.append(temp_chunk.strip())
                            temp_chunk = sentence
                
                if temp_chunk:
                    result.append(temp_chunk.strip())
            else:
                # 检查添加这个段落是否会超出长度限制
                if len(current_chunk + '\n\n' + paragraph) <= max_length:
                    if current_chunk:
                        current_chunk += '\n\n' + paragraph
                    else:
                        current_chunk = paragraph
                else:
                    # 保存当前chunk并开始新的
                    if current_chunk:
                        result.append(current_chunk.strip())
                    current_chunk = paragraph
        
        # 添加最后的chunk
        if current_chunk:
            result.append(current_chunk.strip())
        
        return result
    
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
            if tags_prop.get("select") and tags_prop["select"]:
                tags = [tags_prop["select"]["name"]]

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
                                    "select": {
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
        支持新旧两种模式：
        - 新模式：智能语义检索 (enable_new_system=true)
        - 旧模式：文件名匹配 (enable_new_system=false)
        特殊处理：如果标签包含"无"，则跳过知识库读取。
        """
        # 检查是否包含"无"标签
        if "无" in tags:
            print("🚫 检测到'无'标签，跳过知识库读取")
            return ""
        
        # 检查是否启用新系统
        enable_new_system = self.config.get('knowledge_search', {}).get('enable_new_system', False)
        
        if enable_new_system:
            print("🧠 使用智能知识检索系统")
            return self._get_context_from_notion_knowledge_base(tags)
        else:
            print("📁 使用传统文件匹配系统")
            return self._get_context_from_file_system(tags)
    
    def _get_context_from_notion_knowledge_base(self, tags: list[str]) -> str:
        """从Notion知识库获取智能匹配的上下文"""
        try:
            from notion_knowledge_db import NotionKnowledgeDB
            
            # 创建知识库实例
            knowledge_db = NotionKnowledgeDB(self.config)
            
            # 使用标签作为关键词进行智能搜索
            knowledge_items = knowledge_db.search_knowledge_by_keywords(tags)
            
            if not knowledge_items:
                print("❌ 未找到相关知识条目")
                return ""
            
            # 组装上下文
            context_parts = []
            for item in knowledge_items[:3]:  # 最多取前3个最相关的
                title = item['title']
                content = item['content']
                
                # 智能截取相关片段
                snippet = self._extract_relevant_snippet(content, tags, max_length=800)
                context_part = f"--- 来自知识库: {title} ---\n{snippet}"
                context_parts.append(context_part)
                
                print(f"✅ 加载知识: {title} ({len(snippet)} 字符)")
                
                # 更新使用频率
                knowledge_db.update_usage_frequency(item['id'])
            
            final_context = "\n\n".join(context_parts)
            print(f"✅ 智能检索完成，共 {len(knowledge_items)} 个知识条目，{len(final_context)} 字符")
            return final_context
            
        except Exception as e:
            print(f"❌ 智能检索失败，降级到文件系统: {e}")
            return self._get_context_from_file_system(tags)
    
    def _get_context_from_file_system(self, tags: list[str]) -> str:
        """从本地文件系统获取上下文（原有实现）"""
        # 获取当前脚本所在目录，然后构建knowledge_base路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        base_path = os.path.join(current_dir, "knowledge_base")
        
        context_parts = []
        
        print(f"🔍 查找知识库目录: {base_path}")
        if not os.path.isdir(base_path):
            print(f"❌ 知识库目录未找到: {base_path}")
            return ""
        else:
            print(f"✅ 知识库目录存在: {base_path}")

        for tag in tags:
            # 兼容Windows和macOS/Linux的文件名
            safe_tag = tag.replace("/", "_").replace("\\", "_")
            file_path = os.path.join(base_path, f"{safe_tag}.md")
            
            print(f"🔍 查找文件: {file_path}")
            if os.path.exists(file_path):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        print(f"✅ 成功读取文件: {tag} ({len(content)} 字符)")
                        # 为每个上下文片段添加一个明确的标题，帮助LLM理解来源
                        context_parts.append(f"--- 来自知识库: {tag} ---\n{content}")
                except Exception as e:
                    print(f"❌ 读取知识文件 {file_path} 时出错: {e}")
            else:
                print(f"❌ 文件不存在: {file_path}")
        
        if not context_parts:
            print("❌ 没有找到任何背景文件")
            return ""
        
        final_context = "\n\n".join(context_parts)
        print(f"✅ 最终背景文件内容长度: {len(final_context)} 字符")
        return final_context
    
    def _extract_relevant_snippet(self, content: str, keywords: list[str], max_length: int = 800) -> str:
        """从内容中提取相关片段"""
        if len(content) <= max_length:
            return content
        
        # 按段落分割
        paragraphs = content.split('\n\n')
        relevant_paragraphs = []
        
        for paragraph in paragraphs:
            # 检查段落是否包含关键词
            paragraph_lower = paragraph.lower()
            if any(keyword.lower() in paragraph_lower for keyword in keywords):
                relevant_paragraphs.append(paragraph)
        
        # 如果找到相关段落，优先使用
        if relevant_paragraphs:
            snippet = '\n\n'.join(relevant_paragraphs)
            if len(snippet) <= max_length:
                return snippet
            else:
                # 截取到最大长度
                return snippet[:max_length] + '\n\n（... 内容过长已截断）'
        
        # 如果没有找到相关段落，返回开头部分
        return content[:max_length] + '\n\n（... 内容过长已截断）'

    def get_templates_from_notion(self):
        """从Notion模板库数据库获取所有模板"""
        if not self.template_database_id:
            print("⚠️  未配置模板库数据库ID")
            return {}
        
        try:
            url = f"https://api.notion.com/v1/databases/{self.template_database_id}/query"
            
            # 只获取启用状态的模板
            payload = {
                "filter": {
                    "property": self.template_status_prop,
                    "select": {
                        "equals": "启用"
                    }
                },
                "sorts": [
                    {
                        "property": self.template_name_prop,
                        "direction": "ascending"
                    }
                ]
            }
            
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            templates = {}
            categories = set()
            
            for page in data.get("results", []):
                template_data = self._extract_template_data(page)
                if template_data:
                    name = template_data['name']
                    templates[name] = {
                        'category': template_data['category'],
                        'prompt': template_data['prompt'],
                        'description': template_data['description'],
                        'updated': template_data['updated']
                    }
                    categories.add(template_data['category'])
            
            print(f"✅ 从Notion同步了 {len(templates)} 个模板")
            return {
                'templates': templates,
                'categories': list(categories)
            }
            
        except Exception as e:
            print(f"❌ 从Notion获取模板失败: {e}")
            return {}
    
    def _extract_template_data(self, page):
        """从Notion页面提取模板数据"""
        try:
            properties = page.get("properties", {})
            
            # 提取模板名称
            name_prop = properties.get(self.template_name_prop, {})
            if name_prop.get("type") == "title":
                name_list = name_prop.get("title", [])
                name = name_list[0].get("text", {}).get("content", "") if name_list else ""
            else:
                name = ""
            
            if not name:
                return None
            
            # 提取分类
            category_prop = properties.get(self.template_category_prop, {})
            if category_prop.get("type") == "select":
                category_obj = category_prop.get("select")
                category = category_obj.get("name", "基础") if category_obj else "基础"
            else:
                category = "基础"
            
            # 提取描述
            desc_prop = properties.get(self.template_description_prop, {})
            if desc_prop.get("type") == "rich_text":
                desc_list = desc_prop.get("rich_text", [])
                description = desc_list[0].get("text", {}).get("content", "") if desc_list else ""
            else:
                description = ""
            
            # 获取更新时间
            updated = page.get("last_edited_time", datetime.now().isoformat())
            
            # 获取提示词内容（从页面内容块中获取）
            prompt = self._get_page_content(page["id"])
            
            return {
                'name': name,
                'category': category,
                'prompt': prompt,
                'description': description,
                'updated': updated
            }
            
        except Exception as e:
            print(f"提取模板数据失败: {e}")
            return None
    
    def _get_page_content(self, page_id):
        """获取页面的文本内容"""
        try:
            url = f"https://api.notion.com/v1/blocks/{page_id}/children"
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            content_parts = []
            
            for block in data.get("results", []):
                text = self._extract_text_from_block(block)
                if text:
                    content_parts.append(text)
            
            return "\n\n".join(content_parts)
            
        except Exception as e:
            print(f"获取页面内容失败: {e}")
            return ""
    
    def _extract_text_from_block(self, block):
        """从Notion块中提取文本"""
        block_type = block.get("type")
        
        if block_type == "paragraph":
            rich_text = block.get("paragraph", {}).get("rich_text", [])
        elif block_type == "heading_1":
            rich_text = block.get("heading_1", {}).get("rich_text", [])
        elif block_type == "heading_2":
            rich_text = block.get("heading_2", {}).get("rich_text", [])
        elif block_type == "heading_3":
            rich_text = block.get("heading_3", {}).get("rich_text", [])
        elif block_type == "bulleted_list_item":
            rich_text = block.get("bulleted_list_item", {}).get("rich_text", [])
        elif block_type == "numbered_list_item":
            rich_text = block.get("numbered_list_item", {}).get("rich_text", [])
        elif block_type == "quote":
            rich_text = block.get("quote", {}).get("rich_text", [])
        elif block_type == "code":
            rich_text = block.get("code", {}).get("rich_text", [])
        else:
            return ""
        
        text_parts = []
        for text_obj in rich_text:
            if text_obj.get("type") == "text":
                text_parts.append(text_obj.get("text", {}).get("content", ""))
        
        return "".join(text_parts)
    
    def sync_template_to_notion(self, name, template_data):
        """将模板同步到Notion（创建或更新）"""
        if not self.template_database_id:
            print("⚠️  未配置模板库数据库ID")
            return False
        
        try:
            # 检查模板是否已存在
            existing_page_id = self._find_template_page(name)
            
            if existing_page_id:
                # 更新现有模板
                return self._update_template_page(existing_page_id, name, template_data)
            else:
                # 创建新模板
                return self._create_template_page(name, template_data)
                
        except Exception as e:
            print(f"同步模板到Notion失败: {e}")
            return False
    
    def _find_template_page(self, name):
        """查找指定名称的模板页面"""
        try:
            url = f"https://api.notion.com/v1/databases/{self.template_database_id}/query"
            
            payload = {
                "filter": {
                    "property": self.template_name_prop,
                    "title": {
                        "equals": name
                    }
                }
            }
            
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            results = data.get("results", [])
            
            if results:
                return results[0]["id"]
            
            return None
            
        except Exception as e:
            print(f"查找模板页面失败: {e}")
            return None
    
    def _create_template_page(self, name, template_data):
        """在Notion中创建新的模板页面"""
        try:
            url = "https://api.notion.com/v1/pages"
            
            # 分割长文本内容
            prompt_content = template_data.get("prompt", "")
            content_blocks = []
            
            if prompt_content:
                paragraphs = self._split_content_into_paragraphs(prompt_content)
                for paragraph in paragraphs:
                    if paragraph.strip():
                        content_blocks.append({
                            "object": "block",
                            "type": "paragraph",
                            "paragraph": {
                                "rich_text": [
                                    {
                                        "type": "text",
                                        "text": {
                                            "content": paragraph
                                        }
                                    }
                                ]
                            }
                        })
            
            payload = {
                "parent": {
                    "database_id": self.template_database_id
                },
                "properties": {
                    self.template_name_prop: {
                        "title": [
                            {
                                "text": {
                                    "content": name
                                }
                            }
                        ]
                    },
                    self.template_category_prop: {
                        "select": {
                            "name": template_data.get("category", "基础")
                        }
                    },
                    self.template_description_prop: {
                        "rich_text": [
                            {
                                "text": {
                                    "content": template_data.get("description", "")
                                }
                            }
                        ]
                    },
                    self.template_status_prop: {
                        "select": {
                            "name": "启用"
                        }
                    }
                },
                "children": content_blocks
            }
            
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            response.raise_for_status()
            
            print(f"✅ 创建模板成功: {name}")
            return True
            
        except Exception as e:
            print(f"创建模板页面失败: {e}")
            return False
    
    def _update_template_page(self, page_id, name, template_data):
        """更新现有的模板页面"""
        try:
            # 更新页面属性
            url = f"https://api.notion.com/v1/pages/{page_id}"
            
            payload = {
                "properties": {
                    self.template_category_prop: {
                        "select": {
                            "name": template_data.get("category", "基础")
                        }
                    },
                    self.template_description_prop: {
                        "rich_text": [
                            {
                                "text": {
                                    "content": template_data.get("description", "")
                                }
                            }
                        ]
                    },
                    self.template_status_prop: {
                        "select": {
                            "name": "启用"
                        }
                    }
                }
            }
            
            response = requests.patch(url, headers=self.headers, json=payload, timeout=30)
            response.raise_for_status()
            
            # 更新页面内容（清空并重新写入）
            self._update_page_content(page_id, template_data.get("prompt", ""))
            
            print(f"✅ 更新模板成功: {name}")
            return True
            
        except Exception as e:
            print(f"更新模板页面失败: {e}")
            return False
    
    def _update_page_content(self, page_id, content):
        """更新页面内容"""
        try:
            # 先获取现有的内容块
            blocks_url = f"https://api.notion.com/v1/blocks/{page_id}/children"
            response = requests.get(blocks_url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            existing_blocks = data.get("results", [])
            
            # 删除现有的内容块
            for block in existing_blocks:
                block_id = block["id"]
                delete_url = f"https://api.notion.com/v1/blocks/{block_id}"
                requests.delete(delete_url, headers=self.headers, timeout=30)
            
            # 添加新的内容
            paragraphs = self._split_content_into_paragraphs(content)
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
                                    "text": {
                                        "content": paragraph
                                    }
                                }
                            ]
                        }
                    })
            
            if children:
                append_url = f"https://api.notion.com/v1/blocks/{page_id}/children"
                payload = {"children": children}
                response = requests.patch(append_url, headers=self.headers, json=payload, timeout=30)
                response.raise_for_status()
            
            return True
            
        except Exception as e:
            print(f"更新页面内容失败: {e}")
            return False

    def test_template_database_connection(self):
        """测试模板库数据库连接"""
        if not self.template_database_id:
            return False, "未配置模板库数据库ID"
        
        try:
            url = f"https://api.notion.com/v1/databases/{self.template_database_id}"
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return True, "模板库数据库连接成功！"
        except Exception as e:
            return False, f"模板库数据库连接失败: {e}" 