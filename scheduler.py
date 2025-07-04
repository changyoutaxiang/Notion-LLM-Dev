import time
import threading
from datetime import datetime
from notion_handler import NotionHandler
from llm_handler import LLMHandler
from template_manager import TemplateManager

class MessageScheduler:
    """消息处理调度器"""
    
    def __init__(self, config, gui=None):
        self.config = config
        self.gui = gui
        self.is_running = False
        
        # 初始化处理器
        self.notion_handler = NotionHandler(config)
        
        self.llm_handler = LLMHandler(
            config["openrouter"]["api_key"]
        )
        
        self.template_manager = TemplateManager()
        
        # 统计信息
        self.message_count = 0
        self.last_check_time = "从未"
        self.waiting_count = 0
        
        # 启动时同步模板（如果配置了）
        if config.get("settings", {}).get("sync_on_startup", True):
            self.sync_templates_to_notion()
        
    def start(self):
        """开始调度"""
        self.is_running = True
        
        while self.is_running:
            try:
                self.check_and_process_messages()
                
                # 更新检查时间
                self.last_check_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # 更新GUI状态
                if self.gui:
                    self.gui.root.after(0, lambda: self.gui.update_status(
                        self.last_check_time, 
                        self.message_count
                    ))
                
                # 等待下次检查
                interval = self.config.get("settings", {}).get("check_interval", 120)
                
                # 分段等待，这样停止时更responsive
                for _ in range(interval):
                    if not self.is_running:
                        break
                    time.sleep(1)
                    
            except Exception as e:
                error_msg = f"调度器运行出错: {e}"
                print(error_msg)
                if self.gui:
                    self.gui.root.after(0, lambda: self.gui.add_log(error_msg))
                
                # 出错后稍等再继续
                time.sleep(10)
    
    def check_and_process_messages(self):
        """检查并处理消息"""
        try:
            # 获取待处理消息
            pending_messages = self.notion_handler.get_pending_messages()
            
            # 获取等待处理的数量
            self.waiting_count = self.notion_handler.get_waiting_count()
            
            if not pending_messages:
                if self.waiting_count > 0:
                    log_msg = f"等待条件满足: {self.waiting_count}条，待处理: 0条"
                else:
                    log_msg = "没有待处理的消息"
                print(log_msg)
                if self.gui:
                    self.gui.root.after(0, lambda: self.gui.add_log(log_msg))
                    self.gui.root.after(0, lambda: self.gui.update_current_processing("等待新消息..."))
                return
            
            status_msg = f"等待条件满足: {self.waiting_count}条，待处理: {len(pending_messages)}条"
            print(status_msg)
            if self.gui:
                self.gui.root.after(0, lambda: self.gui.add_log(status_msg))
            
            # 逐一处理消息
            for message in pending_messages:
                if not self.is_running:  # 检查是否要停止
                    break
                
                self.process_single_message(message)
                
        except Exception as e:
            error_msg = f"检查消息时出错: {e}"
            print(error_msg)
            if self.gui:
                self.gui.root.after(0, lambda: self.gui.add_log(error_msg))
    
    def process_single_message(self, message):
        """处理单条消息"""
        try:
            page_id = message["page_id"]
            title = message["title"] or "无标题"
            content = message["content"]
            template_choice = message.get("template_choice", "")
            tags = message.get("tags", [])
            model_choice = message.get("model_choice", "")
            
            process_info = f"正在处理消息:\n模板: {template_choice}\n标签: {tags}\n模型: {model_choice}\n内容: {content[:100]}..."
            print(f"处理消息: {template_choice} - {content[:50]}...")
            
            if self.gui:
                self.gui.root.after(0, lambda: self.gui.add_log(f"开始处理 [{template_choice}]: {content[:30]}..."))
                self.gui.root.after(0, lambda: self.gui.update_current_processing(process_info))
            
            # 1. 根据标签从知识库获取上下文
            knowledge_context = self.notion_handler.get_context_from_knowledge_base(tags)
            if "无" in tags:
                log_msg = f"📝 已选择'无'背景，不使用知识库上下文"
                print(log_msg)
                if self.gui:
                    self.gui.root.after(0, lambda: self.gui.add_log(log_msg))
            elif knowledge_context:
                valid_tags = [tag for tag in tags if tag != "无"]  # 排除"无"标签
                log_msg = f"📚 已加载知识库上下文: {', '.join(valid_tags)}"
                print(log_msg)
                if self.gui:
                    self.gui.root.after(0, lambda: self.gui.add_log(log_msg))
            else:
                valid_tags = [tag for tag in tags if tag != "无"]  # 排除"无"标签
                if valid_tags:
                    log_msg = f"⚠️ 知识库文件未找到: {', '.join(valid_tags)}"
                    print(log_msg)
                    if self.gui:
                        self.gui.root.after(0, lambda: self.gui.add_log(log_msg))

            # 2. 获取基础系统提示词
            base_system_prompt = self._get_system_prompt(template_choice)
            
            # 3. 组合系统提示词（优化版本：明确层次和优先级）
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

            # 4. 确定要使用的模型ID
            model_mapping = self.config.get("settings", {}).get("model_mapping", {})
            override_model_id = model_mapping.get(model_choice) # 如果没找到，会是None

            if model_choice and override_model_id:
                log_msg = f"检测到模型选择: {model_choice} -> 使用模型: {override_model_id}"
                print(log_msg)
                if self.gui:
                    self.gui.root.after(0, lambda: self.gui.add_log(log_msg))

            # 检查是否启用自动标题生成
            auto_title = self.config.get("settings", {}).get("auto_generate_title", True)
            title_max_length = self.config.get("settings", {}).get("title_max_length", 20)
            title_min_length = self.config.get("settings", {}).get("title_min_length", 10)
            
            if auto_title:
                # 使用新的处理方法（生成回复+标题）
                success, llm_reply, generated_title = self.llm_handler.process_with_template_and_title(
                    final_content, 
                    system_prompt, 
                    title_max_length, 
                    title_min_length,
                    override_model=override_model_id
                )
            else:
                # 传统处理方法（只生成回复）
                success, llm_reply = self.llm_handler.send_message(
                    final_content, 
                    system_prompt,
                    override_model=override_model_id
                )
                generated_title = None
            
            # --- 增加详细日志 ---
            print("---------- LLM Context Debug ----------")
            print("=== System Prompt ===")
            print(system_prompt)
            print("\n=== Final Content Sent to LLM ===")
            print(final_content)
            print("\n=== Knowledge Context Length ===")
            print(f"Background file content length: {len(knowledge_context) if knowledge_context else 0} characters")
            print("\n=== LLM Raw Reply ===")
            print(llm_reply)
            print("---------------------------------------")
            if self.gui:
                self.gui.root.after(0, lambda: self.gui.add_log(f"LLM 原始回复: {llm_reply[:100]}..."))
                # 添加调试信息到GUI
                if knowledge_context:
                    self.gui.root.after(0, lambda: self.gui.add_log(f"🔍 背景文件长度: {len(knowledge_context)} 字符"))
            # --- 日志结束 ---

            if success:
                # 成功：更新LLM回复和标题
                update_success = self.notion_handler.update_message_reply(
                    page_id, 
                    llm_reply, 
                    generated_title
                )
                
                if update_success:
                    self.message_count += 1
                    success_msg = f"✅ 消息处理成功 [{template_choice}]: {content[:30]}..."
                    print(success_msg)
                    if self.gui:
                        self.gui.root.after(0, lambda: self.gui.add_log(success_msg))
                else:
                    error_msg = f"❌ 更新Notion失败 [{template_choice}]: {content[:30]}..."
                    print(error_msg)
                    if self.gui:
                        self.gui.root.after(0, lambda: self.gui.add_log(error_msg))
            else:
                # LLM处理失败
                error_msg = f"❌ LLM处理失败 [{template_choice}]: {llm_reply}"
                print(error_msg)
                if self.gui:
                    self.gui.root.after(0, lambda: self.gui.add_log(error_msg))
                    
                # 即使LLM失败，也可以更新一个错误信息到Notion
                error_reply = f"处理失败：{llm_reply}"
                self.notion_handler.update_message_reply(page_id, error_reply, "处理失败")
            
            # 处理间隔（避免API限制）
            time.sleep(2)
            
        except Exception as e:
            error_msg = f"处理消息时出错: {e}"
            print(error_msg)
            
            if self.gui:
                self.gui.root.after(0, lambda: self.gui.add_log(error_msg))
    
    def _get_system_prompt(self, template_choice):
        """根据模板选择获取系统提示词"""
        # 特殊处理：如果选择"无"，则不使用任何提示词模板
        if template_choice == "无":
            return ""
        
        if template_choice:
            template = self.template_manager.get_template(template_choice)
            if template:
                return template["prompt"]
        
        # 回退到默认提示词
        return self.config.get("settings", {}).get("system_prompt", "你是一个智能助手，请认真回答用户的问题。请用中文回复。")
    
    def sync_templates_to_notion(self):
        """同步模板到Notion数据库"""
        try:
            template_names = list(self.template_manager.get_all_templates().keys())
            if template_names:
                success, message = self.notion_handler.sync_template_options(template_names)
                log_msg = f"模板同步: {message}"
                print(log_msg)
                if self.gui:
                    self.gui.root.after(0, lambda: self.gui.add_log(log_msg))
            else:
                log_msg = "没有模板需要同步"
                print(log_msg)
                if self.gui:
                    self.gui.root.after(0, lambda: self.gui.add_log(log_msg))
        except Exception as e:
            error_msg = f"同步模板失败: {e}"
            print(error_msg)
            if self.gui:
                self.gui.root.after(0, lambda: self.gui.add_log(error_msg))
    
    def stop(self):
        """停止调度"""
        self.is_running = False
        print("调度器已停止") 