#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Notion-LLM 混合架构云端服务 v2.0
专为Zeabur部署设计，轻量化服务，智能调用本地RAG
"""

import os
import json
import time
import logging
import requests
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

class HybridCloudScheduler:
    """混合架构云端调度器 - 智能调用本地RAG服务"""
    
    def __init__(self):
        # 从环境变量加载配置
        self.config = self.load_config_from_env()
        
        # 初始化核心组件（无RAG依赖）
        self.notion_handler = NotionHandler(self.config)
        self.llm_handler = LLMHandler(
            self.config["openrouter"]["api_key"],
            self.config["openrouter"]["model"]
        )
        
        # 初始化模板管理器
        self.template_manager = TemplateManager(notion_handler=self.notion_handler)
        
        # 运行状态
        self.is_running = False
        self.message_count = 0
        self.last_check = None
        self.last_template_sync = None
        
        # 🎯 混合架构状态追踪
        self.local_rag_available = False
        self.local_rag_last_check = None
        self.rag_fallback_count = 0
        self.rag_success_count = 0
        
        logger.info("🔄 混合架构云端调度器初始化完成")
        logger.info("🎯 [版本标识] 混合架构云端版本 v2.0")
        
        # 启动时检查本地RAG服务状态
        self.check_local_rag_status()
        
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
                "template_status_property": os.getenv("NOTION_TEMPLATE_STATUS_PROP", "状态")
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
            # 🎯 混合架构配置
            "hybrid_rag": {
                "local_service_url": os.getenv("LOCAL_RAG_SERVICE_URL", ""),
                "enable_fallback": os.getenv("ENABLE_RAG_FALLBACK", "true").lower() == "true",
                "health_check_interval": int(os.getenv("RAG_HEALTH_CHECK_INTERVAL", "300")),  # 5分钟
                "request_timeout": int(os.getenv("RAG_REQUEST_TIMEOUT", "10")),
                "max_retry_attempts": int(os.getenv("RAG_MAX_RETRIES", "2")),
                "fallback_message": os.getenv("RAG_FALLBACK_MESSAGE", "本地知识库暂时不可用，已采用基础模式处理")
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
        
        # 🎯 检查混合架构配置
        if config["hybrid_rag"]["local_service_url"]:
            logger.info("🔄 混合架构模式已启用")
            logger.info(f"📡 本地RAG服务地址: {config['hybrid_rag']['local_service_url']}")
        else:
            logger.warning("⚠️  未配置本地RAG服务地址，将使用纯云端模式")
        
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
    
    def check_local_rag_status(self):
        """检查本地RAG服务状态"""
        if not self.config["hybrid_rag"]["local_service_url"]:
            self.local_rag_available = False
            return False
        
        try:
            health_url = f"{self.config['hybrid_rag']['local_service_url']}/health"
            response = requests.get(
                health_url, 
                timeout=self.config["hybrid_rag"]["request_timeout"]
            )
            
            if response.status_code == 200:
                result = response.json()
                self.local_rag_available = result.get("status") == "healthy"
                self.local_rag_last_check = datetime.now()
                
                if self.local_rag_available:
                    logger.info("✅ 本地RAG服务运行正常")
                else:
                    logger.warning("⚠️  本地RAG服务响应异常")
                    
                return self.local_rag_available
            else:
                logger.warning(f"❌ 本地RAG服务健康检查失败: HTTP {response.status_code}")
                self.local_rag_available = False
                return False
                
        except requests.exceptions.RequestException as e:
            logger.warning(f"🔌 无法连接本地RAG服务: {e}")
            self.local_rag_available = False
            return False
    
    def call_local_rag_search(self, query, max_results=3):
        """调用本地RAG搜索服务"""
        if not self.local_rag_available:
            return None
        
        try:
            search_url = f"{self.config['hybrid_rag']['local_service_url']}/search"
            data = {
                "query": query,
                "max_results": max_results
            }
            
            response = requests.post(
                search_url,
                json=data,
                timeout=self.config["hybrid_rag"]["request_timeout"]
            )
            
            if response.status_code == 200:
                result = response.json()
                self.rag_success_count += 1
                logger.info(f"📡 RAG搜索成功，返回 {len(result.get('results', []))} 个结果")
                return result.get('results', [])
            else:
                logger.warning(f"❌ RAG搜索失败: HTTP {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.warning(f"🔌 RAG服务调用失败: {e}")
            # 标记服务不可用，下次检查时重新测试
            self.local_rag_available = False
            return None
    
    def start(self):
        """启动调度器"""
        self.is_running = True
        logger.info("🔄 混合架构云端调度器启动")
        
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
            
            # 定期检查本地RAG服务状态
            if (not self.local_rag_last_check or 
                (datetime.now() - self.local_rag_last_check).seconds > 
                self.config["hybrid_rag"]["health_check_interval"]):
                self.check_local_rag_status()
            
            # 检查模板库定期同步
            self.check_template_sync_schedule()
            
            # 获取等待处理的消息
            pending_messages = self.notion_handler.get_pending_messages()
            waiting_count = self.notion_handler.get_waiting_count()
            
            if not pending_messages:
                if waiting_count > 0:
                    logger.info(f"📋 当前有 {waiting_count} 条待处理消息，但暂无符合条件的消息")
                return
            
            logger.info(f"📨 发现 {len(pending_messages)} 条新消息待处理")
            
            # 处理每条消息
            for message in pending_messages:
                try:
                    self.process_single_message(message)
                    self.message_count += 1
                    time.sleep(1)  # 避免API限制
                except Exception as e:
                    logger.error(f"处理消息失败 {message.get('id', 'Unknown')}: {e}")
                    
        except Exception as e:
            logger.error(f"检查消息时出错: {e}")
    
    def process_single_message(self, message):
        """处理单条消息 - 混合架构版本"""
        try:
            user_input = message["user_input"]
            template_choice = message.get("template_choice", "")
            selected_model = message.get("selected_model", "")
            
            logger.info(f"🔄 开始处理消息: {user_input[:50]}...")
            
            # 1. 尝试调用本地RAG服务获取知识背景
            knowledge_context = ""
            rag_used = False
            
            if self.config["hybrid_rag"]["local_service_url"]:
                rag_results = self.call_local_rag_search(user_input)
                if rag_results and len(rag_results) > 0:
                    # 构建知识背景
                    knowledge_parts = []
                    for idx, result in enumerate(rag_results[:3], 1):
                        title = result.get('title', f'知识片段{idx}')
                        content = result.get('content', '')
                        score = result.get('score', 0)
                        knowledge_parts.append(f"**{title}** (相关度: {score:.2f})\n{content}\n")
                    
                    knowledge_context = "\n".join(knowledge_parts)
                    rag_used = True
                    logger.info(f"📚 使用本地RAG，获取到 {len(rag_results)} 个相关知识片段")
                else:
                    self.rag_fallback_count += 1
                    if self.config["hybrid_rag"]["enable_fallback"]:
                        knowledge_context = self.config["hybrid_rag"]["fallback_message"]
                        logger.warning("🔄 本地RAG不可用，使用降级模式")
                    else:
                        logger.warning("❌ 本地RAG不可用，且未启用降级模式")
            
            # 2. 获取系统提示词
            system_prompt = self._get_system_prompt(template_choice)
            
            # 3. 构建完整的提示词
            if knowledge_context:
                full_prompt = f"{system_prompt}\n\n【知识背景】\n{knowledge_context}\n\n【用户问题】\n{user_input}"
            else:
                full_prompt = f"{system_prompt}\n\n【用户问题】\n{user_input}"
            
            # 4. 获取实际模型名称
            actual_model = self.config["settings"]["model_mapping"].get(
                selected_model, 
                self.config["openrouter"]["model"]
            )
            
            # 5. 调用LLM
            logger.info(f"🤖 调用LLM模型: {actual_model}")
            response = self.llm_handler.call_llm(full_prompt, model=actual_model)
            
            # 6. 添加混合架构状态信息
            if rag_used:
                response += f"\n\n---\n💡 *本回复使用了本地智能检索增强，共找到 {len(rag_results)} 个相关知识片段*"
            elif self.rag_fallback_count > 0:
                response += f"\n\n---\n⚠️ *本地知识库暂时不可用，使用基础模式回复*"
            
            # 7. 更新Notion页面
            update_data = {
                "output": response,
                "knowledge_base": knowledge_context[:1000] if knowledge_context else ""  # 限制长度
            }
            
            # 自动生成标题
            if (self.config["settings"]["auto_generate_title"] and 
                not message.get("title")):
                title = self.llm_handler.generate_title(user_input)
                if title:
                    update_data["title"] = title
            
            self.notion_handler.update_message(message["id"], update_data)
            
            logger.info(f"✅ 消息处理完成: {message['id']}")
            
        except Exception as e:
            logger.error(f"处理消息时出错: {e}")
            # 更新页面显示错误信息
            error_response = f"处理失败: {str(e)}"
            self.notion_handler.update_message(message["id"], {"output": error_response})
    
    def _get_system_prompt(self, template_choice):
        """获取系统提示词"""
        if template_choice and template_choice != "无":
            template = self.template_manager.get_template(template_choice)
            return template if template else "你是一个有用的AI助手，请根据用户的问题提供准确、有用的回答。"
        else:
            return "你是一个有用的AI助手，请根据用户的问题提供准确、有用的回答。"
    
    def auto_sync_templates_on_startup(self):
        """启动时自动同步模板库"""
        try:
            if (self.config["settings"]["auto_sync_templates"] and 
                self.config["notion"]["template_database_id"]):
                
                logger.info("🔄 启动时自动同步模板库...")
                result = self.template_manager.sync_from_notion()
                
                if result["success"]:
                    logger.info(f"✅ 模板库同步成功: {result['message']}")
                    self.last_template_sync = datetime.now()
                else:
                    logger.warning(f"⚠️  模板库同步失败: {result['message']}")
            else:
                logger.info("⏭️  跳过模板库同步（未配置或已禁用）")
                
        except Exception as e:
            logger.error(f"模板库同步时出错: {e}")
    
    def check_template_sync_schedule(self):
        """检查模板库定期同步"""
        if not self.config["settings"]["auto_sync_templates"]:
            return
        
        if not self.last_template_sync:
            return
        
        sync_interval = self.config["settings"]["sync_interval_hours"]
        hours_passed = (datetime.now() - self.last_template_sync).total_seconds() / 3600
        
        if hours_passed >= sync_interval:
            logger.info(f"⏰ 定期同步模板库（间隔: {sync_interval}小时）")
            try:
                result = self.template_manager.sync_from_notion()
                if result["success"]:
                    logger.info(f"✅ 定期同步成功: {result['message']}")
                    self.last_template_sync = datetime.now()
                else:
                    logger.warning(f"⚠️  定期同步失败: {result['message']}")
            except Exception as e:
                logger.error(f"定期同步时出错: {e}")
    
    def manual_sync_templates_from_notion(self):
        """手动从Notion同步模板库"""
        try:
            result = self.template_manager.sync_from_notion()
            if result["success"]:
                self.last_template_sync = datetime.now()
            return result
        except Exception as e:
            logger.error(f"手动同步模板库时出错: {e}")
            return {"success": False, "message": f"同步失败: {str(e)}"}
    
    def manual_sync_templates_to_notion(self):
        """手动向Notion同步模板库"""
        try:
            return self.template_manager.sync_to_notion()
        except Exception as e:
            logger.error(f"手动向Notion同步模板库时出错: {e}")
            return {"success": False, "message": f"同步失败: {str(e)}"}
    
    def stop(self):
        """停止调度器"""
        self.is_running = False
        logger.info("混合架构云端调度器已停止")
    
    def get_status(self):
        """获取系统状态"""
        return {
            "service_type": "hybrid_cloud",
            "version": "2.0",
            "is_running": self.is_running,
            "message_count": self.message_count,
            "last_check": self.last_check.isoformat() if self.last_check else None,
            "local_rag": {
                "available": self.local_rag_available,
                "service_url": self.config["hybrid_rag"]["local_service_url"],
                "last_check": self.local_rag_last_check.isoformat() if self.local_rag_last_check else None,
                "success_count": self.rag_success_count,
                "fallback_count": self.rag_fallback_count
            },
            "templates": {
                "count": len(self.template_manager.templates),
                "last_sync": self.last_template_sync.isoformat() if self.last_template_sync else None,
                "auto_sync_enabled": self.config["settings"]["auto_sync_templates"]
            }
        }


# Flask应用和API路由
app = Flask(__name__)
scheduler = None

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        "status": "healthy",
        "service": "hybrid_cloud_scheduler",
        "version": "2.0",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/start', methods=['POST'])
def start_scheduler():
    """启动调度器"""
    global scheduler
    try:
        if scheduler and scheduler.is_running:
            return jsonify({"success": False, "message": "调度器已在运行"})
        
        scheduler = HybridCloudScheduler()
        
        # 在后台线程中启动
        def run_scheduler():
            scheduler.start()
        
        threading.Thread(target=run_scheduler, daemon=True).start()
        
        return jsonify({"success": True, "message": "混合架构调度器启动成功"})
        
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
    else:
        return jsonify({"success": False, "message": "调度器未运行"})

@app.route('/status', methods=['GET'])
def get_status():
    """获取状态"""
    global scheduler
    if scheduler:
        return jsonify(scheduler.get_status())
    else:
        return jsonify({"is_running": False, "message": "调度器未初始化"})

@app.route('/process-once', methods=['POST'])
def process_once():
    """手动处理一次"""
    global scheduler
    try:
        if not scheduler:
            return jsonify({"success": False, "message": "调度器未初始化"})
        
        scheduler.check_and_process_messages()
        return jsonify({"success": True, "message": "处理完成"})
        
    except Exception as e:
        logger.error(f"手动处理失败: {e}")
        return jsonify({"success": False, "message": f"处理失败: {str(e)}"})

@app.route('/rag/status', methods=['GET'])
def rag_status():
    """RAG服务状态检查"""
    global scheduler
    if not scheduler:
        return jsonify({"success": False, "message": "调度器未初始化"})
    
    # 强制检查RAG状态
    rag_available = scheduler.check_local_rag_status()
    
    return jsonify({
        "success": True,
        "rag_available": rag_available,
        "service_url": scheduler.config["hybrid_rag"]["local_service_url"],
        "last_check": scheduler.local_rag_last_check.isoformat() if scheduler.local_rag_last_check else None,
        "success_count": scheduler.rag_success_count,
        "fallback_count": scheduler.rag_fallback_count
    })

@app.route('/templates/sync-from-notion', methods=['POST'])
def sync_templates_from_notion():
    """从Notion同步模板库"""
    global scheduler
    try:
        if not scheduler:
            return jsonify({"success": False, "message": "调度器未初始化"})
        
        result = scheduler.manual_sync_templates_from_notion()
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"同步模板库失败: {e}")
        return jsonify({"success": False, "message": f"同步失败: {str(e)}"})

@app.route('/templates/sync-to-notion', methods=['POST'])
def sync_templates_to_notion():
    """向Notion同步模板库"""
    global scheduler
    try:
        if not scheduler:
            return jsonify({"success": False, "message": "调度器未初始化"})
        
        result = scheduler.manual_sync_templates_to_notion()
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"同步模板库失败: {e}")
        return jsonify({"success": False, "message": f"同步失败: {str(e)}"})

@app.route('/templates', methods=['GET'])
def get_templates():
    """获取模板列表"""
    global scheduler
    try:
        if not scheduler:
            return jsonify({"success": False, "message": "调度器未初始化"})
        
        templates = scheduler.template_manager.templates
        return jsonify({
            "success": True,
            "count": len(templates),
            "templates": list(templates.keys()),
            "last_sync": scheduler.last_template_sync.isoformat() if scheduler.last_template_sync else None
        })
        
    except Exception as e:
        logger.error(f"获取模板列表失败: {e}")
        return jsonify({"success": False, "message": f"获取失败: {str(e)}"})

@app.route('/templates/<template_name>', methods=['GET'])
def get_template(template_name):
    """获取特定模板内容"""
    global scheduler
    try:
        if not scheduler:
            return jsonify({"success": False, "message": "调度器未初始化"})
        
        template_content = scheduler.template_manager.get_template(template_name)
        if template_content:
            return jsonify({
                "success": True,
                "template_name": template_name,
                "content": template_content
            })
        else:
            return jsonify({"success": False, "message": f"模板 '{template_name}' 不存在"})
            
    except Exception as e:
        logger.error(f"获取模板失败: {e}")
        return jsonify({"success": False, "message": f"获取失败: {str(e)}"})

if __name__ == "__main__":
    # 自动启动调度器（如果启用）
    auto_start = os.getenv("AUTO_START", "true").lower() == "true"
    if auto_start:
        logger.info("🚀 自动启动混合架构调度器")
        scheduler = HybridCloudScheduler()
        
        def run_scheduler():
            scheduler.start()
        
        threading.Thread(target=run_scheduler, daemon=True).start()
    
    # 启动Flask应用
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False) 