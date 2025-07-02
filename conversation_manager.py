"""
连续对话管理器 - ConversationManager
负责管理Notion-LLM系统中的连续对话功能

作者: AI Assistant  
版本: 1.0.0
创建时间: 2024-01-XX
"""

import uuid
import time
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple

class ConversationManager:
    """连续对话管理器"""
    
    def __init__(self, notion_handler, config=None):
        """
        初始化连续对话管理器
        
        Args:
            notion_handler: NotionHandler实例
            config: 配置字典
        """
        self.notion_handler = notion_handler
        self.config = config or {}
        
        # 从配置中获取连续对话设置
        self.conv_config = self.config.get("settings", {}).get("continuous_conversation", {})
        
        # 连续对话功能开关
        self.enabled = self.conv_config.get("enabled", True)
        
        # 对话历史设置
        self.max_history_turns = self.conv_config.get("max_history_turns", 5)
        self.max_context_length = self.conv_config.get("max_context_length", 8000)
        self.history_weight = self.conv_config.get("history_weight", 0.3)
        
        # 会话管理设置
        self.auto_generate_session_id = self.conv_config.get("auto_generate_session_id", True)
        self.session_id_format = self.conv_config.get("session_id_format", "sess_{timestamp}_{random}")
        self.enable_context_summary = self.conv_config.get("enable_context_summary", True)
        
        # 从notion配置中获取字段名称
        notion_config = self.config.get("notion", {})
        self.session_id_prop = notion_config.get("session_id_property", "会话ID")
        self.parent_id_prop = notion_config.get("parent_id_property", "父消息ID")
        self.session_status_prop = notion_config.get("session_status_property", "会话状态")
        self.conversation_turn_prop = notion_config.get("conversation_turn_property", "对话轮次")
        self.session_title_prop = notion_config.get("session_title_property", "会话标题")
        self.context_length_prop = notion_config.get("context_length_property", "上下文长度")
        
        print(f"✅ ConversationManager初始化完成 - 连续对话{'已启用' if self.enabled else '已禁用'}")
    
    def is_enabled(self) -> bool:
        """检查连续对话功能是否启用"""
        return self.enabled
    
    def generate_session_id(self) -> str:
        """
        生成新的会话ID
        
        Returns:
            str: 新生成的会话ID
        """
        if not self.auto_generate_session_id:
            return ""
        
        # 使用时间戳和随机字符串生成唯一ID
        timestamp = int(time.time())
        random_part = str(uuid.uuid4())[:8]
        
        # 根据配置格式生成ID
        session_id = self.session_id_format.format(
            timestamp=timestamp,
            random=random_part
        )
        
        return session_id
    
    def extract_conversation_fields(self, page_data: Dict) -> Dict:
        """
        从页面数据中提取连续对话相关字段
        
        Args:
            page_data: Notion页面数据
            
        Returns:
            Dict: 包含连续对话字段的字典
        """
        properties = page_data.get("properties", {})
        
        conv_fields = {
            "session_id": self._extract_text_property(properties, self.session_id_prop),
            "parent_id": self._extract_text_property(properties, self.parent_id_prop),
            "session_status": self._extract_select_property(properties, self.session_status_prop),
            "conversation_turn": self._extract_number_property(properties, self.conversation_turn_prop),
            "session_title": self._extract_text_property(properties, self.session_title_prop),
            "context_length": self._extract_number_property(properties, self.context_length_prop)
        }
        
        return conv_fields
    
    def _extract_text_property(self, properties: Dict, prop_name: str) -> str:
        """提取文本属性"""
        prop_data = properties.get(prop_name)
        if not prop_data:
            return ""
        
        # 处理Rich Text类型
        if prop_data.get("type") == "rich_text":
            rich_text_list = prop_data.get("rich_text", [])
            if rich_text_list:
                return rich_text_list[0].get("text", {}).get("content", "")
        
        # 处理Title类型
        elif prop_data.get("type") == "title":
            title_list = prop_data.get("title", [])
            if title_list:
                return title_list[0].get("text", {}).get("content", "")
        
        return ""
    
    def _extract_select_property(self, properties: Dict, prop_name: str) -> str:
        """提取选择属性"""
        prop_data = properties.get(prop_name)
        if not prop_data or prop_data.get("type") != "select":
            return ""
        
        select_data = prop_data.get("select")
        if select_data:
            return select_data.get("name", "")
        
        return ""
    
    def _extract_number_property(self, properties: Dict, prop_name: str) -> int:
        """提取数字属性"""
        prop_data = properties.get(prop_name)
        if not prop_data or prop_data.get("type") != "number":
            return 0
        
        return prop_data.get("number", 0) or 0
    
    def is_conversation_message(self, message_data: Dict) -> bool:
        """
        判断是否为连续对话消息
        
        Args:
            message_data: 消息数据（来自_extract_message_data）
            
        Returns:
            bool: 是否为连续对话消息
        """
        if not self.enabled:
            return False
        
        # 如果有parent_id，则认为是连续对话
        parent_id = message_data.get("parent_id", "")
        return bool(parent_id.strip())
    
    def prepare_new_conversation(self, page_id: str) -> Dict:
        """
        为新对话准备会话信息
        
        Args:
            page_id: 当前页面ID
            
        Returns:
            Dict: 会话信息
        """
        session_id = self.generate_session_id()
        
        session_info = {
            "session_id": session_id,
            "parent_id": "",
            "session_status": "active",
            "conversation_turn": 1,
            "session_title": "",
            "context_length": 0,
            "is_new_conversation": True
        }
        
        print(f"🆕 创建新对话会话: {session_id}")
        return session_info
    
    def get_conversation_history(self, session_id: str, current_page_id: str = None) -> List[Dict]:
        """
        获取对话历史
        
        Args:
            session_id: 会话ID
            current_page_id: 当前页面ID（用于排除自己）
            
        Returns:
            List[Dict]: 对话历史列表，按时间顺序排列
        """
        if not self.enabled or not session_id:
            return []
        
        try:
            print(f"🔍 获取对话历史: {session_id}")
            
            # 构建查询条件：查找同一会话ID的所有消息
            url = f"https://api.notion.com/v1/databases/{self.notion_handler.database_id}/query"
            
            payload = {
                "filter": {
                    "and": [
                        {
                            "property": self.session_id_prop,
                            "rich_text": {
                                "equals": session_id
                            }
                        },
                        {
                            "property": self.notion_handler.output_prop,
                            "rich_text": {
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
            
            # 如果提供了当前页面ID，排除它
            if current_page_id:
                payload["filter"]["and"].append({
                    "property": "ID",  # 使用页面ID过滤
                    "unique_id": {
                        "does_not_equal": current_page_id
                    }
                })
            
            response = self.notion_handler._make_request("POST", url, payload)
            if not response:
                return []
            
            history = []
            for page in response.get("results", []):
                # 提取消息内容
                message_data = self.notion_handler._extract_message_data(page)
                if message_data:
                    # 获取页面内容作为AI回复
                    page_content = self.notion_handler._get_page_content(page["id"])
                    message_data["ai_reply"] = page_content
                    history.append(message_data)
            
            # 限制历史长度
            if len(history) > self.max_history_turns:
                history = history[-self.max_history_turns:]
            
            print(f"📚 获取到 {len(history)} 条历史消息")
            return history
            
        except Exception as e:
            print(f"❌ 获取对话历史失败: {e}")
            return []
    
    def build_conversation_context(self, history: List[Dict], current_content: str) -> str:
        """
        构建连续对话上下文
        
        Args:
            history: 对话历史
            current_content: 当前用户输入
            
        Returns:
            str: 构建好的对话上下文
        """
        if not history:
            return ""
        
        context_parts = []
        context_parts.append("=== 对话历史 ===")
        
        for i, msg in enumerate(history, 1):
            user_input = msg.get("content", "").strip()
            ai_reply = msg.get("ai_reply", "").strip()
            
            if user_input:
                context_parts.append(f"用户 {i}: {user_input}")
            if ai_reply:
                context_parts.append(f"助手 {i}: {ai_reply}")
            context_parts.append("")  # 空行分隔
        
        context_parts.append("=== 当前问题 ===")
        context_parts.append(f"用户: {current_content}")
        context_parts.append("")
        context_parts.append("请基于以上对话历史，自然地回答用户的当前问题。")
        
        full_context = "\n".join(context_parts)
        
        # 检查上下文长度
        if len(full_context) > self.max_context_length:
            print(f"⚠️ 对话上下文过长 ({len(full_context)}字符)，将进行压缩")
            full_context = self._compress_context(full_context)
        
        return full_context
    
    def _compress_context(self, context: str) -> str:
        """
        压缩过长的对话上下文
        
        Args:
            context: 原始上下文
            
        Returns:
            str: 压缩后的上下文
        """
        # 简单的压缩策略：保留最近的对话，总结较早的对话
        lines = context.split("\n")
        
        # 找到"当前问题"部分的开始
        current_start = -1
        for i, line in enumerate(lines):
            if "=== 当前问题 ===" in line:
                current_start = i
                break
        
        if current_start > 0:
            # 保留当前问题部分
            current_part = "\n".join(lines[current_start:])
            
            # 压缩历史部分 - 简单截取
            history_part = "\n".join(lines[:current_start])
            if len(history_part) > self.max_context_length * 0.7:
                # 保留最后的部分历史
                target_length = int(self.max_context_length * 0.7)
                history_part = "=== 对话历史（已压缩）===\n...\n" + history_part[-target_length:]
            
            return history_part + "\n" + current_part
        
        # 如果无法找到分界点，直接截取
        return context[:self.max_context_length]
    
    def update_conversation_fields(self, page_id: str, session_info: Dict) -> bool:
        """
        更新页面的连续对话字段
        
        Args:
            page_id: 页面ID
            session_info: 会话信息
            
        Returns:
            bool: 更新是否成功
        """
        if not self.enabled:
            return True
        
        try:
            properties = {}
            
            # 更新会话ID
            if session_info.get("session_id"):
                properties[self.session_id_prop] = {
                    "rich_text": [
                        {
                            "text": {
                                "content": session_info["session_id"]
                            }
                        }
                    ]
                }
            
            # 更新会话状态
            if session_info.get("session_status"):
                properties[self.session_status_prop] = {
                    "select": {
                        "name": session_info["session_status"]
                    }
                }
            
            # 更新对话轮次
            if session_info.get("conversation_turn"):
                properties[self.conversation_turn_prop] = {
                    "number": session_info["conversation_turn"]
                }
            
            # 更新会话标题
            if session_info.get("session_title"):
                properties[self.session_title_prop] = {
                    "rich_text": [
                        {
                            "text": {
                                "content": session_info["session_title"]
                            }
                        }
                    ]
                }
            
            # 更新上下文长度
            if session_info.get("context_length"):
                properties[self.context_length_prop] = {
                    "number": session_info["context_length"]
                }
            
            if properties:
                return self.notion_handler._update_page_properties(page_id, properties)
            
            return True
            
        except Exception as e:
            print(f"❌ 更新连续对话字段失败: {e}")
            return False 