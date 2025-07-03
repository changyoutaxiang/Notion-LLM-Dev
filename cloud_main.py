#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Notion-LLM 云端版本 (简化版)
无GUI版本，使用环境变量配置，专注核心Notion+LLM处理功能
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
    """云端调度器 - 简化版"""
    
    def __init__(self):
        # 从环境变量加载配置
        self.config = self.load_config_from_env()
        
        # 初始化组件
        self.notion_handler = NotionHandler(self.config)
        self.llm_handler = LLMHandler(
            self.config["openrouter"]["api_key"],
            self.config["openrouter"]["model"]
        )
        
        # 初始化TemplateManager
        self.template_manager = TemplateManager(notion_handler=self.notion_handler)
        
        # 运行状态
        self.is_running = False
        self.message_count = 0
        self.last_check = None
        self.last_template_sync = None
        
        logger.info("☁️ 云端调度器初始化完成")
        logger.info("🎯 [版本标识] 简化云端版本 v3.0 - 专注核心功能")
        
        # 启动时自动同步模板库
        self.auto_sync_templates_on_startup()
    
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
        
        logger.info("✅ 配置加载成功")
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
        logger.info("☁️ 云端调度器启动")
        
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
            
            # 检查模板库定期同步
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
            knowledge_context = self.notion_handler.get_context_from_knowledge_base(tags)
            
            # 获取基础系统提示词
            base_system_prompt = self._get_system_prompt(template_choice)
            
            # 组合系统提示词
            if knowledge_context:
                system_prompt = f"""{base_system_prompt}

---

## 补充背景知识
{knowledge_context}

---

## 执行指令
请在严格遵循上述角色设定和输出格式的前提下，充分利用补充背景知识来增强回答质量。"""
            else:
                system_prompt = base_system_prompt
            
            # 确定模型
            model_mapping = self.config["settings"]["model_mapping"]
            override_model_id = model_mapping.get(model_choice)
            
            # 处理消息
            auto_title = self.config["settings"]["auto_generate_title"]
            if auto_title:
                success, llm_reply, generated_title = self.llm_handler.process_with_template_and_title(
                    content, 
                    system_prompt,
                    self.config["settings"]["title_max_length"],
                    self.config["settings"]["title_min_length"],
                    override_model=override_model_id
                )
            else:
                success, llm_reply = self.llm_handler.send_message(
                    content, 
                    system_prompt,
                    override_model=override_model_id
                )
                generated_title = None
            
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
            else:
                logger.info("🔄 自动同步已禁用，跳过模板库同步")
                
        except Exception as e:
            logger.error(f"❌ 启动时模板库同步异常: {e}")
    
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
    
    def stop(self):
        """停止调度器"""
        self.is_running = False
        logger.info("调度器已停止")
    
    def get_status(self):
        """获取运行状态"""
        return {
            "is_running": self.is_running,
            "message_count": self.message_count,
            "last_check": self.last_check.isoformat() if self.last_check else None,
            "last_template_sync": self.last_template_sync.isoformat() if self.last_template_sync else None
        }

# Flask应用
app = Flask(__name__)
scheduler = None

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        "status": "healthy",
        "service": "notion-llm-cloud-simplified",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/start', methods=['POST'])
def start_scheduler():
    """启动调度器"""
    global scheduler
    try:
        if scheduler and scheduler.is_running:
            return jsonify({"success": False, "message": "调度器已在运行"})
        
        scheduler = CloudScheduler()
        
        # 在后台线程中启动
        def run_scheduler():
            scheduler.start()
        
        threading.Thread(target=run_scheduler, daemon=True).start()
        
        return jsonify({"success": True, "message": "云端调度器启动成功"})
        
    except Exception as e:
        logger.error(f"启动调度器失败: {e}")
        return jsonify({"success": False, "message": f"启动失败: {str(e)}"})

@app.route('/stop', methods=['POST'])
def stop_scheduler():
    """停止调度器"""
    global scheduler
    if scheduler:
        scheduler.stop()
        return jsonify({"success": True, "message": "调度器已停止"})
    return jsonify({"success": False, "message": "调度器未运行"})

@app.route('/status', methods=['GET'])
def get_status():
    """获取状态"""
    global scheduler
    if scheduler:
        return jsonify(scheduler.get_status())
    return jsonify({"is_running": False, "message": "调度器未初始化"})

if __name__ == "__main__":
    # 获取端口（云端平台会自动设置PORT环境变量）
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