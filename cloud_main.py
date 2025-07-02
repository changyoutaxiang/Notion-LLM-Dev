#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Notion-LLM 云端版本 (适用于Zeabur等平台)
无GUI版本，使用环境变量配置，支持定时任务和API接口
"""

import os
import json
import time
import logging
from datetime import datetime
from flask import Flask, jsonify, request
import threading
from notion_handler import NotionHandler
from llm_handler import LLMHandler
from template_manager import TemplateManager

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

class CloudScheduler:
    """云端调度器 - 无GUI版本"""
    
    def __init__(self):
        # 从环境变量加载配置
        self.config = self.load_config_from_env()
        
        # 初始化组件
        self.notion_handler = NotionHandler(self.config)
        self.llm_handler = LLMHandler(
            self.config["openrouter"]["api_key"],
            self.config["openrouter"]["model"]
        )
        
        # 🔥 新增：正确初始化TemplateManager并连接NotionHandler
        self.template_manager = TemplateManager(notion_handler=self.notion_handler)
        
        # 运行状态
        self.is_running = False
        self.message_count = 0
        self.last_check = None
        self.last_template_sync = None
        
        logger.info("云端调度器初始化完成")
        logger.info("🎯 [版本标识] 本地版本 v2.2 - 模板库管理功能")
        
        # 🔥 新增：启动时自动同步模板库
        self.auto_sync_templates_on_startup()
        
        # 本地版本无需紧急诊断功能
    
    def load_config_from_env(self):
        """从环境变量加载配置"""
        config = {
            "notion": {
                "api_key": os.getenv("NOTION_API_KEY", ""),
                "database_id": os.getenv("NOTION_DATABASE_ID", ""),
                "input_property_name": os.getenv("NOTION_INPUT_PROP", "输入"),
                "output_property_name": os.getenv("NOTION_OUTPUT_PROP", "回复"),
                "template_property_name": os.getenv("NOTION_TEMPLATE_PROP", "模板选择"),
                "knowledge_base_property_name": os.getenv("NOTION_KNOWLEDGE_PROP", "背景"),
                "model_property_name": os.getenv("NOTION_MODEL_PROP", "模型"),
                "title_property_name": os.getenv("NOTION_TITLE_PROP", "标题"),
                "template_database_id": os.getenv("NOTION_TEMPLATE_DATABASE_ID", ""),
                "template_name_property": os.getenv("NOTION_TEMPLATE_NAME_PROP", "模板名称"),
                "template_category_property": os.getenv("NOTION_TEMPLATE_CATEGORY_PROP", "分类"),
                "template_description_property": os.getenv("NOTION_TEMPLATE_DESC_PROP", "描述"),
                "template_status_property": os.getenv("NOTION_TEMPLATE_STATUS_PROP", "状态"),
                "knowledge_base_path": os.getenv("KNOWLEDGE_BASE_PATH", "knowledge_base")
            },
            "openrouter": {
                "api_key": os.getenv("OPENROUTER_API_KEY", ""),
                "model": os.getenv("OPENROUTER_MODEL", "anthropic/claude-3.5-sonnet")
            },
            "settings": {
                "check_interval": int(os.getenv("CHECK_INTERVAL", "120")),
                "max_retries": int(os.getenv("MAX_RETRIES", "3")),
                "request_timeout": int(os.getenv("REQUEST_TIMEOUT", "30")),
                "auto_generate_title": os.getenv("AUTO_TITLE", "true").lower() == "true",
                "title_max_length": int(os.getenv("TITLE_MAX_LENGTH", "20")),
                "title_min_length": int(os.getenv("TITLE_MIN_LENGTH", "10")),
                "model_mapping": self.load_model_mapping(),
                "auto_sync_templates": os.getenv("AUTO_SYNC_TEMPLATES", "true").lower() == "true",
                "sync_interval_hours": int(os.getenv("SYNC_INTERVAL_HOURS", "24"))
            },
            # 🧠 新增：智能知识库系统配置 (v3.0)
            "knowledge_search": {
                "enable_new_system": os.getenv("ENABLE_NEW_KNOWLEDGE_SYSTEM", "true").lower() == "true",
                "knowledge_database_id": os.getenv("NOTION_KNOWLEDGE_DATABASE_ID", ""),
                "category_database_id": os.getenv("NOTION_CATEGORY_DATABASE_ID", ""),
                "max_context_length": int(os.getenv("KNOWLEDGE_MAX_CONTEXT_LENGTH", "4000")),
                "max_snippets": int(os.getenv("KNOWLEDGE_MAX_SNIPPETS", "5")),
                "similarity_threshold": float(os.getenv("KNOWLEDGE_SIMILARITY_THRESHOLD", "0.3")),
                "snippet_max_length": int(os.getenv("KNOWLEDGE_SNIPPET_MAX_LENGTH", "800")),
                "enable_semantic_search": os.getenv("ENABLE_SEMANTIC_SEARCH", "true").lower() == "true",
                "enable_usage_weighting": os.getenv("ENABLE_USAGE_WEIGHTING", "true").lower() == "true",
                # 知识库属性名称映射
                "property_names": {
                    "title": os.getenv("NOTION_KNOWLEDGE_TITLE_PROP", "知识标题"),
                    "category": os.getenv("NOTION_KNOWLEDGE_CATEGORY_PROP", "知识分类"),
                    "subcategory": os.getenv("NOTION_KNOWLEDGE_SUBCATEGORY_PROP", "知识子类"),
                    "keywords": os.getenv("NOTION_KNOWLEDGE_KEYWORDS_PROP", "关键词"),
                    "scenarios": os.getenv("NOTION_KNOWLEDGE_SCENARIOS_PROP", "适用场景"),
                    "priority": os.getenv("NOTION_KNOWLEDGE_PRIORITY_PROP", "优先级"),
                    "status": os.getenv("NOTION_KNOWLEDGE_STATUS_PROP", "状态"),
                    "relations": os.getenv("NOTION_KNOWLEDGE_RELATIONS_PROP", "关联知识"),
                    "usage_frequency": os.getenv("NOTION_KNOWLEDGE_USAGE_PROP", "使用频率")
                }
            }
        }
        
        # 验证必要配置
        required_vars = [
            ("NOTION_API_KEY", config["notion"]["api_key"]),
            ("NOTION_DATABASE_ID", config["notion"]["database_id"]),
            ("OPENROUTER_API_KEY", config["openrouter"]["api_key"])
        ]
        
        missing_vars = []
        for var_name, var_value in required_vars:
            if not var_value:
                missing_vars.append(var_name)
        
        if missing_vars:
            logger.error(f"缺少必要的环境变量: {', '.join(missing_vars)}")
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        # 🧠 检查智能知识库配置
        if config["knowledge_search"]["enable_new_system"]:
            knowledge_db_id = config["knowledge_search"]["knowledge_database_id"]
            if knowledge_db_id:
                logger.info("🧠 智能知识库系统已启用")
            else:
                logger.warning("⚠️  智能知识库系统已启用，但缺少知识库数据库ID，将降级为传统模式")
                config["knowledge_search"]["enable_new_system"] = False
        
        logger.info("配置加载成功")
        return config
    
    def load_model_mapping(self):
        """加载模型映射"""
        default_mapping = {
            "Gemini 2.5 pro": "google/gemini-2.5-pro",
            "Gemini 2.5 flash": "google/gemini-2.5-flash",
            "Claude 4 sonnet": "anthropic/claude-sonnet-4",
            "Chatgpt 4.1": "openai/gpt-4.1",
            "Chatgpt O3": "openai/o3",
            "Deepseek R1": "deepseek/deepseek-r1-0528",
            "Deepseek V3": "deepseek/deepseek-chat-v3-0324"
        }
        
        # 从环境变量加载自定义映射（JSON格式）
        custom_mapping = os.getenv("MODEL_MAPPING", "{}")
        try:
            custom_mapping = json.loads(custom_mapping)
            default_mapping.update(custom_mapping)
        except json.JSONDecodeError:
            logger.warning("MODEL_MAPPING环境变量格式错误，使用默认映射")
        
        return default_mapping
    
    def start(self):
        """启动调度器"""
        self.is_running = True
        logger.info("云端调度器启动")
        
        while self.is_running:
            try:
                self.check_and_process_messages()
                time.sleep(self.config["settings"]["check_interval"])
            except KeyboardInterrupt:
                logger.info("收到停止信号")
                break
            except Exception as e:
                logger.error(f"运行时错误: {e}")
                time.sleep(30)  # 出错后等待30秒再重试
    
    def check_and_process_messages(self):
        """检查并处理消息"""
        try:
            self.last_check = datetime.now()
            
            # 🔥 新增：检查模板库定期同步
            self.check_template_sync_schedule()
            
            # 获取等待处理的消息
            pending_messages = self.notion_handler.get_pending_messages()
            waiting_count = self.notion_handler.get_waiting_count()
            
            if not pending_messages:
                if waiting_count > 0:
                    logger.info(f"等待条件满足: {waiting_count}条")
                else:
                    logger.info("没有待处理的消息")
                return
            
            logger.info(f"等待条件满足: {waiting_count}条，待处理: {len(pending_messages)}条")
            
            # 处理消息
            for message in pending_messages:
                if not self.is_running:
                    break
                self.process_single_message(message)
                
        except Exception as e:
            logger.error(f"检查消息时出错: {e}")
    
    def process_single_message(self, message):
        """处理单条消息"""
        try:
            page_id = message["page_id"]
            content = message["content"]
            template_choice = message.get("template_choice", "")
            tags = message.get("tags", [])
            model_choice = message.get("model_choice", "")
            
            logger.info(f"处理消息: {template_choice} - {content[:50]}...")
            
            # 获取知识库上下文
            logger.info(f"🔍 [云端调试] 开始获取知识库上下文，标签: {tags}")
            knowledge_context = self.notion_handler.get_context_from_knowledge_base(tags)
            logger.info(f"🔍 [云端调试] 知识库上下文获取完成，长度: {len(knowledge_context)} 字符")
            
            # 获取基础系统提示词
            base_system_prompt = self._get_system_prompt(template_choice)
            
            # 组合系统提示词（优化版本：明确层次和优先级）
            if knowledge_context:
                system_prompt = f"""{base_system_prompt}

---

## 补充背景知识
{knowledge_context}

---

## 执行指令
请在严格遵循上述角色设定和输出格式的前提下，充分利用补充背景知识来增强回答质量。执行优先级：
1. 首要：保持角色设定的风格、格式和字数要求
2. 重要：当背景知识与用户问题相关时，深度融合背景信息
3. 补充：如背景知识不足或不相关，请明确说明并基于角色专业知识回答
4. 冲突处理：如背景信息与角色设定冲突，优先遵循角色设定"""
            else:
                system_prompt = base_system_prompt
            
            # 用户消息保持原样
            final_content = content
            
            # 确定模型
            model_mapping = self.config["settings"]["model_mapping"]
            override_model_id = model_mapping.get(model_choice)
            
            # 处理消息
            auto_title = self.config["settings"]["auto_generate_title"]
            if auto_title:
                success, llm_reply, generated_title = self.llm_handler.process_with_template_and_title(
                    final_content, 
                    system_prompt,
                    self.config["settings"]["title_max_length"],
                    self.config["settings"]["title_min_length"],
                    override_model=override_model_id
                )
            else:
                success, llm_reply = self.llm_handler.send_message(
                    final_content, 
                    system_prompt,
                    override_model=override_model_id
                )
                generated_title = None
            
            # --- 增加调试日志 ---
            logger.info("---------- LLM Context Debug ----------")
            logger.info("=== System Prompt ===")
            logger.info(system_prompt)
            logger.info("=== Final Content Sent to LLM ===")
            logger.info(final_content)
            logger.info("=== Knowledge Context Length ===")
            logger.info(f"Background file content length: {len(knowledge_context) if knowledge_context else 0} characters")  
            logger.info("=== LLM Reply ===")
            logger.info(llm_reply)
            logger.info("---------------------------------------")
            # --- 调试日志结束 ---
            
            if success:
                # 更新Notion页面
                update_success = self.notion_handler.update_message_reply(
                    page_id, llm_reply, generated_title
                )
                
                if update_success:
                    self.message_count += 1
                    logger.info(f"✅ 消息处理成功: {template_choice}")
                else:
                    logger.error(f"❌ 更新Notion失败: {template_choice}")
            else:
                logger.error(f"❌ LLM处理失败: {llm_reply}")
                # 写入错误信息
                error_reply = f"处理失败：{llm_reply}"
                self.notion_handler.update_message_reply(page_id, error_reply, "处理失败")
            
            time.sleep(2)  # 避免API限制
            
        except Exception as e:
            logger.error(f"处理消息时出错: {e}")
    
    def _get_system_prompt(self, template_choice):
        """获取系统提示词"""
        # 特殊处理：如果选择"无"，则不使用任何提示词模板
        if template_choice == "无":
            return ""
        
        if template_choice:
            template = self.template_manager.get_template(template_choice)
            if template:
                return template["prompt"]
        return "你是一个智能助手，请认真回答用户的问题。请用中文回复。"
    
    def auto_sync_templates_on_startup(self):
        """启动时自动同步模板库"""
        try:
            if self.config["settings"]["auto_sync_templates"]:
                logger.info("🔄 启动时自动同步模板库...")
                
                # 检查是否配置了模板库数据库ID
                if not self.config["notion"]["template_database_id"]:
                    logger.warning("⚠️ 未配置NOTION_TEMPLATE_DATABASE_ID，跳过模板库同步")
                    return
                
                # 尝试从Notion同步模板
                success, message = self.template_manager.sync_from_notion()
                if success:
                    logger.info(f"✅ 启动时模板库同步成功: {message}")
                    self.last_template_sync = datetime.now()
                else:
                    logger.warning(f"⚠️ 启动时模板库同步失败: {message}")
                    # 如果同步失败，检查是否需要创建默认模板
                    self.template_manager.auto_sync_from_notion_if_empty()
            else:
                logger.info("🔄 自动同步已禁用，跳过模板库同步")
                # 仍然检查是否需要创建默认模板
                self.template_manager.auto_sync_from_notion_if_empty()
                
        except Exception as e:
            logger.error(f"❌ 启动时模板库同步异常: {e}")
            # 确保至少有默认模板可用
            self.template_manager.auto_sync_from_notion_if_empty()
    
    def check_template_sync_schedule(self):
        """检查是否需要定期同步模板库"""
        try:
            if not self.config["settings"]["auto_sync_templates"]:
                return
            
            if not self.config["notion"]["template_database_id"]:
                return
            
            # 检查是否需要定期同步
            sync_interval = self.config["settings"]["sync_interval_hours"]
            if self.last_template_sync:
                hours_since_sync = (datetime.now() - self.last_template_sync).total_seconds() / 3600
                if hours_since_sync >= sync_interval:
                    logger.info(f"🔄 定期同步模板库（距离上次同步 {hours_since_sync:.1f} 小时）...")
                    success, message = self.template_manager.sync_from_notion()
                    if success:
                        logger.info(f"✅ 定期模板库同步成功: {message}")
                        self.last_template_sync = datetime.now()
                    else:
                        logger.warning(f"⚠️ 定期模板库同步失败: {message}")
                        
        except Exception as e:
            logger.error(f"❌ 定期模板库同步检查异常: {e}")
    
    def manual_sync_templates_from_notion(self):
        """手动从Notion同步模板库"""
        try:
            if not self.config["notion"]["template_database_id"]:
                return False, "未配置模板库数据库ID"
            
            success, message = self.template_manager.sync_from_notion()
            if success:
                self.last_template_sync = datetime.now()
                logger.info(f"✅ 手动同步模板库成功: {message}")
            else:
                logger.warning(f"⚠️ 手动同步模板库失败: {message}")
            
            return success, message
            
        except Exception as e:
            error_msg = f"手动同步异常: {e}"
            logger.error(f"❌ {error_msg}")
            return False, error_msg
    
    def manual_sync_templates_to_notion(self):
        """手动同步模板库到Notion"""
        try:
            if not self.config["notion"]["template_database_id"]:
                return False, "未配置模板库数据库ID"
            
            success, message = self.template_manager.sync_to_notion()
            if success:
                logger.info(f"✅ 手动同步模板到Notion成功: {message}")
            else:
                logger.warning(f"⚠️ 手动同步模板到Notion失败: {message}")
            
            return success, message
            
        except Exception as e:
            error_msg = f"同步到Notion异常: {e}"
            logger.error(f"❌ {error_msg}")
            return False, error_msg
    
    def stop(self):
        """停止调度器"""
        self.is_running = False
        logger.info("调度器已停止")
    
    def get_status(self):
        """获取运行状态"""
        template_count = len(self.template_manager.get_all_templates()) if self.template_manager else 0
        
        return {
            "is_running": self.is_running,
            "message_count": self.message_count,
            "last_check": self.last_check.isoformat() if self.last_check else None,
            "last_template_sync": self.last_template_sync.isoformat() if self.last_template_sync else None,
            "template_count": template_count,
            "template_database_configured": bool(self.config["notion"]["template_database_id"]),
            "auto_sync_enabled": self.config["settings"]["auto_sync_templates"],
            "config_loaded": bool(self.config)
        }

# Flask API接口
app = Flask(__name__)
scheduler = None

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "scheduler_status": scheduler.get_status() if scheduler else None
    })

@app.route('/start', methods=['POST'])
def start_scheduler():
    """启动调度器"""
    global scheduler
    try:
        if scheduler and scheduler.is_running:
            return jsonify({"error": "调度器已在运行"}), 400
        
        scheduler = CloudScheduler()
        # 在后台线程中启动
        threading.Thread(target=scheduler.start, daemon=True).start()
        
        return jsonify({"message": "调度器启动成功"})
    except Exception as e:
        logger.error(f"启动调度器失败: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/stop', methods=['POST'])
def stop_scheduler():
    """停止调度器"""
    global scheduler
    if scheduler:
        scheduler.stop()
        return jsonify({"message": "调度器停止成功"})
    return jsonify({"error": "调度器未运行"}), 400

@app.route('/status', methods=['GET'])
def get_status():
    """获取状态"""
    if scheduler:
        return jsonify(scheduler.get_status())
    return jsonify({"error": "调度器未初始化"}), 400

@app.route('/process-once', methods=['POST'])
def process_once():
    """手动处理一次"""
    if scheduler:
        try:
            scheduler.check_and_process_messages()
            return jsonify({"message": "处理完成"})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    return jsonify({"error": "调度器未运行"}), 400

# 🔥 新增：模板库管理API接口

@app.route('/templates/sync-from-notion', methods=['POST'])
def sync_templates_from_notion():
    """从Notion同步模板库"""
    if not scheduler:
        return jsonify({"error": "调度器未初始化"}), 400
    
    try:
        success, message = scheduler.manual_sync_templates_from_notion()
        if success:
            return jsonify({"message": message, "success": True})
        else:
            return jsonify({"error": message, "success": False}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/templates/sync-to-notion', methods=['POST'])
def sync_templates_to_notion():
    """同步模板库到Notion"""
    if not scheduler:
        return jsonify({"error": "调度器未初始化"}), 400
    
    try:
        success, message = scheduler.manual_sync_templates_to_notion()
        if success:
            return jsonify({"message": message, "success": True})
        else:
            return jsonify({"error": message, "success": False}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/templates', methods=['GET'])
def get_templates():
    """获取所有模板"""
    if not scheduler:
        return jsonify({"error": "调度器未初始化"}), 400
    
    try:
        templates = scheduler.template_manager.get_all_templates()
        categories = scheduler.template_manager.get_categories()
        
        return jsonify({
            "templates": templates,
            "categories": categories,
            "count": len(templates),
            "last_sync": scheduler.last_template_sync.isoformat() if scheduler.last_template_sync else None
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/templates/<template_name>', methods=['GET'])
def get_template(template_name):
    """获取指定模板"""
    if not scheduler:
        return jsonify({"error": "调度器未初始化"}), 400
    
    try:
        template = scheduler.template_manager.get_template(template_name)
        if template:
            return jsonify({"template": template, "name": template_name})
        else:
            return jsonify({"error": "模板不存在"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # 获取端口（Zeabur会自动设置PORT环境变量）
    port = int(os.getenv("PORT", 5000))
    
    # 如果设置了自动启动，则在启动时开始调度器
    if os.getenv("AUTO_START", "true").lower() == "true":
        try:
            scheduler = CloudScheduler()
            threading.Thread(target=scheduler.start, daemon=True).start()
            logger.info("自动启动调度器")
        except Exception as e:
            logger.error(f"自动启动失败: {e}")
    
    # 启动Flask服务
    app.run(host="0.0.0.0", port=port, debug=False) 