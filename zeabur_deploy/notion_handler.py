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
        
        # === 云端版本增强：环境诊断和多路径策略 ===
        print("🌐 [云端版本] 开始背景文件加载 - v2.1")
        
        # 环境诊断
        import sys
        print(f"🔍 [环境诊断] Python版本: {sys.version}")
        print(f"🔍 [环境诊断] 当前工作目录: {os.getcwd()}")
        print(f"🔍 [环境诊断] 脚本文件路径: {__file__}")
        print(f"🔍 [环境诊断] 脚本所在目录: {os.path.dirname(os.path.abspath(__file__))}")
        
        # 多路径策略：尝试多个可能的knowledge_base位置
        possible_paths = [
            # 策略1：脚本同目录下的knowledge_base
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "knowledge_base"),
            # 策略2：当前工作目录下的knowledge_base
            os.path.join(os.getcwd(), "knowledge_base"),
            # 策略3：上级目录的knowledge_base（防止在子目录中运行）
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "knowledge_base"),
            # 策略4：绝对路径（如果在容器中）
            "/app/knowledge_base",
            # 策略5：相对路径（备用）
            "knowledge_base"
        ]
        
        base_path = None
        for i, path in enumerate(possible_paths, 1):
            print(f"🔍 [路径策略{i}] 尝试路径: {path}")
            if os.path.isdir(path):
                print(f"✅ [路径策略{i}] 路径存在，使用此路径")
                base_path = path
                break
            else:
                print(f"❌ [路径策略{i}] 路径不存在")
        
        if not base_path:
            print("❌ [错误] 所有路径策略都失败，无法找到knowledge_base目录")
            # 列出当前目录和脚本目录的内容进行调试
            current_dir_files = os.listdir(os.getcwd())
            script_dir_files = os.listdir(os.path.dirname(os.path.abspath(__file__)))
            print(f"🔍 [调试] 当前工作目录内容: {current_dir_files}")
            print(f"🔍 [调试] 脚本所在目录内容: {script_dir_files}")
            return ""
        
        # 列出knowledge_base目录内容
        try:
            kb_files = os.listdir(base_path)
            print(f"🔍 [目录内容] knowledge_base目录包含: {kb_files}")
        except Exception as e:
            print(f"❌ [错误] 无法列出knowledge_base目录内容: {e}")
        
        context_parts = []
        
        for tag in tags:
            # 兼容Windows和macOS/Linux的文件名
            safe_tag = tag.replace("/", "_").replace("\\", "_")
            file_path = os.path.join(base_path, f"{safe_tag}.md")
            
            print(f"🔍 [文件查找] 标签'{tag}' -> 查找文件: {file_path}")
            if os.path.exists(file_path):
                try:
                    # 尝试多种编码方式读取文件
                    encodings = ['utf-8', 'utf-8-sig', 'gbk', 'gb2312']
                    content = None
                    used_encoding = None
                    
                    for encoding in encodings:
                        try:
                            with open(file_path, "r", encoding=encoding) as f:
                                content = f.read()
                                used_encoding = encoding
                                break
                        except UnicodeDecodeError:
                            continue
                    
                    if content is not None:
                        print(f"✅ [文件读取] 成功读取文件: {tag} ({len(content)} 字符, 编码: {used_encoding})")
                        # 为每个上下文片段添加一个明确的标题，帮助LLM理解来源
                        context_parts.append(f"--- 来自知识库: {tag} ---\n{content}")
                    else:
                        print(f"❌ [文件读取] 无法用任何编码读取文件: {file_path}")
                        
                except Exception as e:
                    print(f"❌ [文件读取] 读取知识文件 {file_path} 时出错: {e}")
            else:
                print(f"❌ [文件查找] 文件不存在: {file_path}")
                # 尝试查找相似的文件名
                try:
                    dir_files = [f for f in os.listdir(base_path) if f.endswith('.md')]
                    similar_files = [f for f in dir_files if safe_tag.lower() in f.lower() or f.lower().replace('.md', '') in safe_tag.lower()]
                    if similar_files:
                        print(f"🔍 [建议] 发现相似文件: {similar_files}")
                except Exception as e:
                    print(f"❌ [建议] 无法搜索相似文件: {e}")
        
        if not context_parts:
            print("❌ [结果] 没有找到任何背景文件")
            return ""
        
        final_context = "\n\n".join(context_parts)
        print(f"✅ [结果] 最终背景文件内容长度: {len(final_context)} 字符")
        print(f"🎯 [版本标识] 云端版本 v2.1 - 增强路径检测")
        return final_context 