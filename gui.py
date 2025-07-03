import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import json
import threading
from datetime import datetime
from template_manager import TemplateManager
from notion_handler import NotionHandler

class NotionLLMGUI:
    """图形用户界面 - 现代化美化版本"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🤖 Notion-LLM 异步通信助手")
        self.root.geometry("900x700")
        self.root.configure(bg="#ffffff")  # 纯白背景
        
        # 设置现代化样式
        self.setup_styles()
        
        # 配置数据
        self.config = self.load_config()
        
        # 初始化Notion处理器
        self.notion_handler = None
        if self.config:
            try:
                self.notion_handler = NotionHandler(self.config)
            except Exception as e:
                print(f"初始化Notion处理器失败: {e}")
        
        # 模板管理器（传入notion_handler以支持同步）
        self.template_manager = TemplateManager(notion_handler=self.notion_handler)
        
        # 运行状态
        self.is_running = False
        self.scheduler_thread = None
        
        self.setup_ui()
        
        # 绑定关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def setup_styles(self):
        """设置现代化UI样式 - 精细版"""
        style = ttk.Style()
        
        # 设置主题为浅色
        style.theme_use('clam')
        
        # 配置精细的颜色方案
        colors = {
            'bg': '#ffffff',           # 纯白主背景
            'card_bg': '#f9fafb',      # 卡片背景
            'card_border': '#e5e7eb',  # 卡片边框
            'accent': '#2563eb',       # 主题色-蓝色
            'accent_light': '#60a5fa', # 浅蓝色
            'accent_hover': '#1d4ed8', # 主题色悬停
            'success': '#00b894',      # 成功绿色
            'success_light': '#55efc4',# 浅绿色
            'warning': '#fdcb6e',      # 警告黄色
            'warning_light': '#ffdd59',# 浅黄色
            'danger': '#e84393',       # 危险红色
            'danger_light': '#fd79a8', # 浅红色
            'text': '#111827',         # 主文字
            'text_secondary': '#6b7280', # 次要文字
            'text_muted': '#a0aec0',   # 静音文字
            'border': '#e5e7eb',       # 边框
            'shadow': '#f3f4f6'        # 阴影
        }
        
        # 配置Notebook样式
        style.configure('TNotebook', 
                       background=colors['bg'],
                       borderwidth=0,
                       tabmargins=[2, 5, 2, 0])
        style.configure('TNotebook.Tab', 
                       background=colors['card_bg'],
                       foreground=colors['text_secondary'],
                       padding=[24, 14],
                       borderwidth=0,
                       focuscolor='none',
                       lightcolor=colors['card_border'],
                       darkcolor=colors['card_border'])
        style.map('TNotebook.Tab',
                 background=[('selected', colors['accent']),
                            ('active', colors['accent_hover'])],
                 foreground=[('selected', '#ffffff'),
                            ('active', '#ffffff')])
        
        # 配置Frame样式
        style.configure('Card.TFrame',
                       background=colors['card_bg'],
                       relief='flat',
                       borderwidth=1,
                       lightcolor=colors['card_border'],
                       darkcolor=colors['card_border'])
        
        # 配置LabelFrame样式  
        style.configure('Card.TLabelframe',
                       background=colors['card_bg'],
                       foreground=colors['text'],
                       borderwidth=2,
                       relief='flat',
                       lightcolor=colors['card_border'],
                       darkcolor=colors['card_border'])
        style.configure('Card.TLabelframe.Label',
                       background=colors['card_bg'],
                       foreground=colors['accent_light'],
                       font=('SF Pro Display', 12, 'bold'))
        
        # 配置Button样式 - 现代化圆角风格
        style.configure('Accent.TButton',
                       background=colors['accent'],
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       padding=[20, 10],
                       font=('SF Pro Display', 10, 'bold'),
                       relief='flat')
        style.map('Accent.TButton',
                 background=[('active', colors['accent_hover']),
                            ('pressed', colors['accent_hover'])],
                 relief=[('pressed', 'flat'), ('!pressed', 'flat')])
        
        style.configure('Success.TButton',
                       background=colors['success'],
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       padding=[20, 10],
                       font=('SF Pro Display', 10, 'bold'),
                       relief='flat')
        style.map('Success.TButton',
                 background=[('active', colors['success_light'])])
        
        style.configure('Warning.TButton',
                       background=colors['warning'],
                       foreground='#2d3436',
                       borderwidth=0,
                       focuscolor='none',
                       padding=[20, 10],
                       font=('SF Pro Display', 10, 'bold'),
                       relief='flat')
        style.map('Warning.TButton',
                 background=[('active', colors['warning_light'])])
        
        style.configure('Danger.TButton',
                       background=colors['danger'],
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       padding=[20, 10],
                       font=('SF Pro Display', 10, 'bold'),
                       relief='flat')
        style.map('Danger.TButton',
                 background=[('active', colors['danger_light'])])
        
        # 配置Entry样式 - 现代化输入框
        style.configure('Modern.TEntry',
                       fieldbackground=colors['card_bg'],
                       foreground=colors['text'],
                       borderwidth=2,
                       insertcolor=colors['accent'],
                       relief='flat',
                       lightcolor=colors['card_border'],
                       darkcolor=colors['card_border'],
                       selectbackground=colors['accent'],
                       selectforeground='white')
        style.map('Modern.TEntry',
                 bordercolor=[('focus', colors['accent']),
                             ('!focus', colors['card_border'])],
                 lightcolor=[('focus', colors['accent']),
                            ('!focus', colors['card_border'])],
                 darkcolor=[('focus', colors['accent']),
                           ('!focus', colors['card_border'])])
        
        # 配置Combobox样式
        style.configure('Modern.TCombobox',
                       fieldbackground=colors['card_bg'],
                       foreground=colors['text'],
                       borderwidth=2,
                       relief='flat',
                       lightcolor=colors['card_border'],
                       darkcolor=colors['card_border'],
                       selectbackground=colors['accent'],
                       selectforeground='white',
                       arrowcolor=colors['accent'])
        style.map('Modern.TCombobox',
                 bordercolor=[('focus', colors['accent']),
                             ('!focus', colors['card_border'])],
                 lightcolor=[('focus', colors['accent']),
                            ('!focus', colors['card_border'])],
                 darkcolor=[('focus', colors['accent']),
                           ('!focus', colors['card_border'])])
        
        # 配置Treeview样式 - 现代化列表
        style.configure('Modern.Treeview',
                       background=colors['card_bg'],
                       foreground=colors['text'],
                       fieldbackground=colors['card_bg'],
                       borderwidth=0,
                       relief='flat',
                       rowheight=32)
        style.configure('Modern.Treeview.Heading',
                       background=colors['accent'],
                       foreground='white',
                       borderwidth=0,
                       relief='flat',
                       font=('SF Pro Display', 11, 'bold'))
        style.map('Modern.Treeview',
                 background=[('selected', colors['accent'])],
                 foreground=[('selected', 'white')])
        
        # 配置Label样式 - 精美字体层次
        style.configure('Title.TLabel',
                       background=colors['bg'],
                       foreground=colors['text'],
                       font=('SF Pro Display', 20, 'bold'))
        style.configure('Subtitle.TLabel',
                       background=colors['bg'],
                       foreground=colors['text_secondary'],
                       font=('SF Pro Display', 14))
        style.configure('CardText.TLabel',
                       background=colors['card_bg'],
                       foreground=colors['text'],
                       font=('SF Pro Display', 11))
        style.configure('CardLabel.TLabel',
                       background=colors['card_bg'],
                       foreground=colors['text_secondary'],
                       font=('SF Pro Display', 10, 'bold'))
        style.configure('Success.TLabel',
                       background=colors['card_bg'],
                       foreground=colors['success_light'],
                       font=('SF Pro Display', 11, 'bold'))
        style.configure('Warning.TLabel',
                       background=colors['card_bg'],
                       foreground=colors['warning'],
                       font=('SF Pro Display', 11, 'bold'))
        style.configure('Danger.TLabel',
                       background=colors['card_bg'],
                       foreground=colors['danger_light'],
                       font=('SF Pro Display', 11, 'bold'))
        style.configure('Muted.TLabel',
                       background=colors['card_bg'],
                       foreground=colors['text_muted'],
                       font=('SF Pro Display', 10))

    def setup_ui(self):
        """设置现代化用户界面"""
        # 主容器
        main_container = tk.Frame(self.root, bg="#ffffff")
        main_container.pack(fill="both", expand=True, padx=24, pady=24)
        
        # 顶部标题区域
        header_frame = tk.Frame(main_container, bg="#ffffff")
        header_frame.pack(fill="x", pady=(0, 24))
        
        title_label = ttk.Label(header_frame, text="🤖 Notion-LLM 异步通信助手", style="Title.TLabel")
        title_label.pack(anchor="w")
        
        subtitle_label = ttk.Label(header_frame, text="现代化智能工作流程助手 - 让AI成为您的得力助手", style="Subtitle.TLabel")
        subtitle_label.pack(anchor="w", pady=(5, 0))
        
        # 创建笔记本组件（标签页）
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill="both", expand=True)
        
        # 配置标签页
        config_frame = ttk.Frame(self.notebook, style="Card.TFrame")
        self.notebook.add(config_frame, text="⚙️  配置设置")
        self.setup_config_tab(config_frame)
        
        # 监控标签页
        monitor_frame = ttk.Frame(self.notebook, style="Card.TFrame")
        self.notebook.add(monitor_frame, text="📊  运行监控")
        self.setup_monitor_tab(monitor_frame)
        
        # 模板库标签页
        template_frame = ttk.Frame(self.notebook, style="Card.TFrame")
        self.notebook.add(template_frame, text="📝  模板库")
        self.setup_template_tab(template_frame)
        
        # 日志标签页
        log_frame = ttk.Frame(self.notebook, style="Card.TFrame")
        self.notebook.add(log_frame, text="📋  运行日志")
        self.setup_log_tab(log_frame)
    
    def setup_config_tab(self, parent):
        """设置现代化配置标签页"""
        # 滚动容器
        canvas = tk.Canvas(parent, bg="#ffffff", highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style="Card.TFrame")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 添加鼠标滚轮支持
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _bind_to_mousewheel(event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _unbind_from_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")
        
        # 绑定鼠标进入和离开事件
        canvas.bind('<Enter>', _bind_to_mousewheel)
        canvas.bind('<Leave>', _unbind_from_mousewheel)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Notion配置卡片
        notion_frame = ttk.LabelFrame(scrollable_frame, text="🔗 Notion 数据库配置", style="Card.TLabelframe", padding=20)
        notion_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        ttk.Label(notion_frame, text="API密钥:", style="CardLabel.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 12), padx=(0, 15))
        self.notion_key_entry = ttk.Entry(notion_frame, width=50, show="*", style="Modern.TEntry", font=("SF Mono", 10))
        self.notion_key_entry.grid(row=0, column=1, padx=(0, 0), pady=(0, 12), sticky="ew")
        self.notion_key_entry.insert(0, self.config.get("notion", {}).get("api_key", ""))
        
        ttk.Label(notion_frame, text="数据库ID:", style="CardLabel.TLabel").grid(row=1, column=0, sticky="w", pady=(0, 12), padx=(0, 15))
        self.notion_db_entry = ttk.Entry(notion_frame, width=50, style="Modern.TEntry", font=("SF Mono", 10))
        self.notion_db_entry.grid(row=1, column=1, padx=(0, 0), pady=(0, 12), sticky="ew")
        self.notion_db_entry.insert(0, self.config.get("notion", {}).get("database_id", ""))
        
        notion_frame.columnconfigure(1, weight=1)
        
        # OpenRouter配置卡片
        openrouter_frame = ttk.LabelFrame(scrollable_frame, text="🤖 AI模型配置", style="Card.TLabelframe", padding=20)
        openrouter_frame.pack(fill="x", padx=20, pady=10)
        
        ttk.Label(openrouter_frame, text="API密钥:", style="CardText.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 8))
        self.openrouter_key_entry = ttk.Entry(openrouter_frame, width=50, show="*", style="Modern.TEntry", font=("Consolas", 10))
        self.openrouter_key_entry.grid(row=0, column=1, padx=(10, 0), pady=(0, 8), sticky="ew")
        self.openrouter_key_entry.insert(0, self.config.get("openrouter", {}).get("api_key", ""))
        
        ttk.Label(openrouter_frame, text="AI模型:", style="CardText.TLabel").grid(row=1, column=0, sticky="w", pady=(0, 8))
        self.model_var = tk.StringVar(value=self.config.get("openrouter", {}).get("model", "anthropic/claude-sonnet-4"))
        model_combo = ttk.Combobox(openrouter_frame, textvariable=self.model_var, width=47, style="Modern.TCombobox", font=("Helvetica", 10))
        model_combo["values"] = [
            "anthropic/claude-sonnet-4",
            "google/gemini-2.5-pro", 
            "deepseek/deepseek-r1"
        ]
        model_combo.grid(row=1, column=1, padx=(10, 0), pady=(0, 8), sticky="ew")
        
        openrouter_frame.columnconfigure(1, weight=1)
        
        # 运行设置卡片
        settings_frame = ttk.LabelFrame(scrollable_frame, text="⚙️ 运行参数设置", style="Card.TLabelframe", padding=20)
        settings_frame.pack(fill="x", padx=20, pady=10)
        
        ttk.Label(settings_frame, text="检查间隔(秒):", style="CardText.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 8))
        self.interval_var = tk.StringVar(value=str(self.config.get("settings", {}).get("check_interval", 120)))
        interval_entry = ttk.Entry(settings_frame, textvariable=self.interval_var, width=20, style="Modern.TEntry", font=("Helvetica", 10))
        interval_entry.grid(row=0, column=1, padx=(10, 0), pady=(0, 8), sticky="w")
        
        # 工作流程说明卡片（替代复杂的提示词设置）
        workflow_frame = ttk.LabelFrame(scrollable_frame, text="📋 工作流程说明", style="Card.TLabelframe", padding=20)
        workflow_frame.pack(fill="x", padx=20, pady=10)
        
        workflow_text = """🎯 使用步骤：
1. 配置好上方的API密钥和数据库ID
2. 在"模板库"页面管理你的AI助手模板
3. 在Notion数据库中输入内容并选择对应模板
4. 系统将自动处理消息并智能回复

💡 关键点：
• AI提示词在"模板库"页面统一管理
• 模板会自动同步到Notion作为选择选项
• 用户在Notion中选择模板，系统自动应用对应提示词
• 无需在此页面手动设置系统提示词"""
        
        workflow_label = ttk.Label(workflow_frame, text=workflow_text, style="CardText.TLabel", justify="left")
        workflow_label.pack(anchor="w")
        
        # 按钮区域
        button_frame = ttk.Frame(scrollable_frame, style="Card.TFrame")
        button_frame.pack(fill="x", padx=20, pady=(10, 20))
        
        ttk.Button(button_frame, text="💾 保存配置", command=self.save_config, style="Success.TButton").pack(side="left", padx=(0, 10))
        ttk.Button(button_frame, text="🔄 测试连接", command=self.test_connections, style="Warning.TButton").pack(side="left", padx=(0, 10))
    
    def setup_monitor_tab(self, parent):
        """设置现代化监控标签页"""
        # 主容器
        main_container = ttk.Frame(parent, style="Card.TFrame")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 状态卡片网格
        status_grid = ttk.Frame(main_container, style="Card.TFrame")
        status_grid.pack(fill="x", pady=(0, 20))
        
        # 运行状态卡片
        status_card = ttk.LabelFrame(status_grid, text="📊 运行状态", style="Card.TLabelframe", padding=20)
        status_card.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        
        self.status_label = ttk.Label(status_card, text="⏸️ 未运行", style="Warning.TLabel", font=("Helvetica", 12, "bold"))
        self.status_label.pack(anchor="w", pady=(0, 8))
        
        self.last_check_label = ttk.Label(status_card, text="上次检查: 从未", style="CardText.TLabel")
        self.last_check_label.pack(anchor="w", pady=(0, 5))
        
        # 统计信息卡片
        stats_card = ttk.LabelFrame(status_grid, text="📈 处理统计", style="Card.TLabelframe", padding=20)
        stats_card.grid(row=0, column=1, padx=(5, 5), sticky="ew")
        
        self.message_count_label = ttk.Label(stats_card, text="已处理: 0条", style="Success.TLabel", font=("Helvetica", 11, "bold"))
        self.message_count_label.pack(anchor="w", pady=(0, 8))
        
        self.waiting_count_label = ttk.Label(stats_card, text="等待选择模板: 0条", style="Warning.TLabel", font=("Helvetica", 11, "bold"))
        self.waiting_count_label.pack(anchor="w", pady=(0, 5))
        
        # 配置grid权重
        status_grid.columnconfigure(0, weight=1)
        status_grid.columnconfigure(1, weight=1)
        
        # 控制按钮面板
        control_card = ttk.LabelFrame(main_container, text="🎛️ 操作控制", style="Card.TLabelframe", padding=20)
        control_card.pack(fill="x", pady=(0, 20))
        
        control_frame = ttk.Frame(control_card, style="Card.TFrame")
        control_frame.pack(fill="x")
        
        self.start_button = ttk.Button(control_frame, text="▶️ 开始监听", command=self.start_monitoring, style="Success.TButton")
        self.start_button.pack(side="left", padx=(0, 10))
        
        self.stop_button = ttk.Button(control_frame, text="⏹️ 停止监听", command=self.stop_monitoring, state="disabled", style="Danger.TButton")
        self.stop_button.pack(side="left", padx=(0, 10))
        
        self.sync_button = ttk.Button(control_frame, text="🔄 同步模板", command=self.sync_templates, style="Accent.TButton")
        self.sync_button.pack(side="left", padx=(0, 10))
        
        # 当前处理信息
        current_frame = ttk.LabelFrame(main_container, text="🔄 实时处理信息", style="Card.TLabelframe", padding=20)
        current_frame.pack(fill="both", expand=True)
        
        # 创建美化的文本区域
        text_container = tk.Frame(current_frame, bg="#ffffff")
        text_container.pack(fill="both", expand=True)
        
        self.current_text = scrolledtext.ScrolledText(
            text_container,
            height=15, 
            state="disabled",
            bg="#ffffff",
            fg="#111827",
            insertbackground="#2563eb",
            selectbackground="#e5e7eb",
            selectforeground="#111827",
            font=("SF Mono", 10),
            relief="flat",
            borderwidth=2,
            wrap=tk.WORD,
            highlightthickness=1,
            highlightcolor="#2563eb",
            highlightbackground="#e5e7eb"
        )
        self.current_text.pack(fill="both", expand=True, padx=1, pady=1)
    
    def setup_log_tab(self, parent):
        """设置现代化日志标签页"""
        # 主容器
        main_container = ttk.Frame(parent, style="Card.TFrame")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 日志卡片
        log_card = ttk.LabelFrame(main_container, text="📋 系统运行日志", style="Card.TLabelframe", padding=20)
        log_card.pack(fill="both", expand=True, pady=(0, 15))
        
        # 创建美化的日志文本区域
        log_container = tk.Frame(log_card, bg="#ffffff")
        log_container.pack(fill="both", expand=True)
        
        self.log_text = scrolledtext.ScrolledText(
            log_container,
            height=20,
            bg="#ffffff",
            fg="#111827",
            insertbackground="#2563eb",
            selectbackground="#e5e7eb",
            selectforeground="#111827",
            font=("SF Mono", 10),
            relief="flat",
            borderwidth=2,
            wrap=tk.WORD,
            highlightthickness=1,
            highlightcolor="#2563eb",
            highlightbackground="#e5e7eb"
        )
        self.log_text.pack(fill="both", expand=True, padx=1, pady=1)
        
        # 操作按钮卡片
        control_card = ttk.LabelFrame(main_container, text="🛠️ 日志操作", style="Card.TLabelframe", padding=20)
        control_card.pack(fill="x")
        
        control_frame = ttk.Frame(control_card, style="Card.TFrame")
        control_frame.pack(fill="x")
        
        ttk.Button(control_frame, text="🗑️ 清空日志", command=self.clear_log, style="Danger.TButton").pack(side="left", padx=(0, 10))
        
        # 添加日志级别说明
        ttk.Label(control_frame, text="💡 日志自动记录所有操作和状态变化", style="CardText.TLabel").pack(side="left", padx=(20, 0))
        
        # 初始日志
        self.add_log("🚀 程序启动完成")
    
    def load_config(self):
        """加载配置文件，并自动补全Notion字段"""
        default_notion = {
            "api_key": "",
            "database_id": "",
            "input_property_name": "输入",
            "output_property_name": "回复",
            "status_property_name": "状态",
            "status_in_progress": "In progress",
            "status_done": "Done",
            "template_property_name": "模板选择",
            "knowledge_base_property_name": "背景",
            "model_property_name": "模型",
            "title_property_name": "标题"
        }
        try:
            with open("config.json", "r", encoding="utf-8") as f:
                config = json.load(f)
                # 自动补全notion字段
                if "notion" not in config:
                    config["notion"] = default_notion.copy()
                else:
                    for k, v in default_notion.items():
                        if k not in config["notion"]:
                            config["notion"][k] = v
                return config
        except FileNotFoundError:
            self.add_log("配置文件不存在，使用默认配置")
            return {"notion": default_notion}
        except Exception as e:
            self.add_log(f"加载配置文件失败: {e}")
            return {"notion": default_notion}
    
    def save_config(self):
        """保存配置到config.json"""
        try:
            config = {
                "notion": {
                    "api_key": self.notion_key_entry.get(),
                    "database_id": self.notion_db_entry.get(),
                    "input_property_name": "输入",
                    "output_property_name": "回复",
                    "status_property_name": "状态",
                    "status_in_progress": "In progress",
                    "status_done": "Done",
                    "template_property_name": "模板选择",
                    "knowledge_base_property_name": "背景",
                    "model_property_name": "模型",
                    "title_property_name": "标题"
                },
                "openrouter": {
                    "api_key": self.openrouter_key_entry.get(),
                    "model": self.model_var.get(),
                },
                "settings": {
                    "check_interval": int(self.interval_var.get()),
                }
            }
            with open("config.json", "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("保存成功", "配置已保存！")
        except Exception as e:
            messagebox.showerror("保存配置失败", str(e))
    
    def test_connections(self):
        """测试API连接"""
        if not self.validate_config():
            return
        
        self.add_log("开始测试API连接...")
        
        def test_thread():
            try:
                # 测试Notion
                from notion_handler import NotionHandler
                notion = NotionHandler(self.config)
                notion_success, notion_msg = notion.test_connection()
                
                # 测试OpenRouter
                from llm_handler import LLMHandler
                llm = LLMHandler(
                    self.config["openrouter"]["api_key"],
                    self.config["openrouter"]["model"]
                )
                llm_success, llm_msg = llm.test_connection()
                
                # 显示结果
                self.root.after(0, lambda: self.show_test_results(notion_success, notion_msg, llm_success, llm_msg))
                
            except Exception as e:
                error_msg = str(e)
                self.root.after(0, lambda msg=error_msg: messagebox.showerror("错误", f"测试连接时出错: {msg}"))
        
        threading.Thread(target=test_thread, daemon=True).start()
    
    def show_test_results(self, notion_success, notion_msg, llm_success, llm_msg):
        """显示测试结果"""
        result = f"Notion: {notion_msg}\nOpenRouter: {llm_msg}"
        
        if notion_success and llm_success:
            messagebox.showinfo("测试结果", f"所有连接测试成功！\n\n{result}")
            self.add_log("API连接测试全部成功")
        else:
            messagebox.showwarning("测试结果", f"部分连接测试失败\n\n{result}")
            self.add_log(f"API连接测试结果: Notion={notion_success}, OpenRouter={llm_success}")
    
    def validate_config(self):
        """验证配置"""
        if not self.notion_key_entry.get() or self.notion_key_entry.get() == "请填入你的Notion API密钥":
            messagebox.showwarning("配置错误", "请填入Notion API密钥")
            return False
        
        if not self.notion_db_entry.get() or self.notion_db_entry.get() == "请填入你的Notion数据库ID":
            messagebox.showwarning("配置错误", "请填入Notion数据库ID")
            return False
        
        if not self.openrouter_key_entry.get() or self.openrouter_key_entry.get() == "请填入你的OpenRouter API密钥":
            messagebox.showwarning("配置错误", "请填入OpenRouter API密钥")
            return False
        
        # --- 修复：不再创建新配置，而是在现有配置上更新 ---
        # 确保self.config存在且结构完整
        if not self.config or "notion" not in self.config:
            self.config = self.load_config() # 如果丢失，重新加载

        # 更新内存中的配置，而不是覆盖它
        self.config["notion"]["api_key"] = self.notion_key_entry.get()
        self.config["notion"]["database_id"] = self.notion_db_entry.get()
        
        if "openrouter" not in self.config:
            self.config["openrouter"] = {}
        self.config["openrouter"]["api_key"] = self.openrouter_key_entry.get()
        self.config["openrouter"]["model"] = self.model_var.get()
        
        if "settings" not in self.config:
            self.config["settings"] = {}
        self.config["settings"]["check_interval"] = int(self.interval_var.get())
        
        return True
    
    def start_monitoring(self):
        """开始监听"""
        if not self.validate_config():
            return
        
        self.is_running = True
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
        self.status_label.config(text="状态: 运行中")
        
        # 根据RAG配置选择调度器
        rag_enabled = self.config.get("knowledge_search", {}).get("enable_smart_rag", False)
        
        if rag_enabled and self.check_rag_dependencies_silent():
            # 使用RAG增强调度器
            from scheduler_rag_enhanced import RAGEnhancedScheduler
            self.scheduler = RAGEnhancedScheduler(self.config, self)
            self.add_log("🧠 启动RAG智能检索模式")
        else:
            # 使用传统调度器
            from scheduler import MessageScheduler
            self.scheduler = MessageScheduler(self.config, self)
            if rag_enabled:
                self.add_log("⚠️ RAG已启用但依赖缺失，使用传统模式")
            else:
                self.add_log("🏷️ 启动传统标签检索模式")
        
        self.scheduler_thread = threading.Thread(target=self.scheduler.start, daemon=True)
        self.scheduler_thread.start()
        
        self.add_log("开始监听Notion数据库")
    
    def stop_monitoring(self):
        """停止监听"""
        self.is_running = False
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.status_label.config(text="状态: 已停止")
        
        if hasattr(self, 'scheduler'):
            self.scheduler.stop()
        
        self.add_log("停止监听")
    
    def update_status(self, last_check_time, message_count):
        """更新状态显示"""
        if self.is_running:
            self.status_label.config(text="🟢 运行中", style="Success.TLabel")
        else:
            self.status_label.config(text="⏸️ 已停止", style="Warning.TLabel")
        
        self.last_check_label.config(text=f"上次检查: {last_check_time}")
        self.message_count_label.config(text=f"已处理: {message_count}条")
        
        # 更新等待模板选择数量
        if hasattr(self, 'scheduler') and self.scheduler:
            waiting_count = getattr(self.scheduler, 'waiting_count', 0)
            self.waiting_count_label.config(text=f"等待选择模板: {waiting_count}条")
    
    def update_current_processing(self, text):
        """更新当前处理信息"""
        self.current_text.config(state="normal")
        self.current_text.delete(1.0, tk.END)
        self.current_text.insert(1.0, text)
        self.current_text.config(state="disabled")
    
    def add_log(self, message):
        """添加日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
    
    def clear_log(self):
        """清空日志"""
        self.log_text.delete(1.0, tk.END)
    
    def sync_templates(self):
        """同步模板到Notion"""
        if not self.validate_config():
            return
        
        def sync_thread():
            try:
                from notion_handler import NotionHandler
                notion = NotionHandler(self.config)
                
                template_names = list(self.template_manager.get_all_templates().keys())
                if template_names:
                    success, message = notion.sync_template_options(template_names)
                    if success:
                        self.root.after(0, lambda: self.add_log(f"模板同步成功: {message}"))
                        self.root.after(0, lambda: messagebox.showinfo("成功", message))
                    else:
                        self.root.after(0, lambda: self.add_log(f"模板同步失败: {message}"))
                        self.root.after(0, lambda: messagebox.showerror("失败", message))
                else:
                    msg = "没有模板需要同步"
                    self.root.after(0, lambda: self.add_log(msg))
                    self.root.after(0, lambda: messagebox.showinfo("提示", msg))
                    
            except Exception as e:
                error_msg = f"同步模板时出错: {e}"
                self.root.after(0, lambda: self.add_log(error_msg))
                self.root.after(0, lambda: messagebox.showerror("错误", error_msg))
        
        threading.Thread(target=sync_thread, daemon=True).start()
    
    def setup_template_tab(self, parent):
        """设置现代化模板库标签页"""
        # 主容器
        main_container = ttk.Frame(parent, style="Card.TFrame")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 左侧：模板列表和操作
        left_frame = ttk.Frame(main_container, style="Card.TFrame")
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # 分类筛选卡片
        category_card = ttk.LabelFrame(left_frame, text="🏷️ 分类筛选", style="Card.TLabelframe", padding=15)
        category_card.pack(fill="x", pady=(0, 15))
        
        category_inner = ttk.Frame(category_card, style="Card.TFrame")
        category_inner.pack(fill="x")
        
        self.category_var = tk.StringVar(value="全部")
        self.category_combo = ttk.Combobox(category_inner, textvariable=self.category_var, width=20, style="Modern.TCombobox")
        self.category_combo.pack(side="left", padx=(0, 10))
        self.category_combo.bind("<<ComboboxSelected>>", self.on_category_change)
        
        ttk.Button(category_inner, text="🔄 刷新", command=self.refresh_templates, style="Accent.TButton").pack(side="left")
        
        # 模板列表卡片
        list_card = ttk.LabelFrame(left_frame, text="📝 模板列表", style="Card.TLabelframe", padding=15)
        list_card.pack(fill="both", expand=True, pady=(0, 15))
        
        # 创建美化的Treeview
        tree_container = tk.Frame(list_card, bg="#f9fafb")
        tree_container.pack(fill="both", expand=True)
        
        self.template_tree = ttk.Treeview(tree_container, show="tree", height=12, style="Modern.Treeview")
        
        # 设置列标题和宽度
        self.template_tree.heading("#0", text="模板名称")
        self.template_tree.column("#0", width=280)
        
        # 滚动条
        tree_scroll = ttk.Scrollbar(tree_container, orient="vertical", command=self.template_tree.yview)
        self.template_tree.configure(yscrollcommand=tree_scroll.set)
        
        self.template_tree.pack(side="left", fill="both", expand=True)
        tree_scroll.pack(side="right", fill="y")
        
        # 绑定选择事件
        self.template_tree.bind("<<TreeviewSelect>>", self.on_template_select)
        
        # 操作按钮卡片
        button_card = ttk.LabelFrame(left_frame, text="🛠️ 模板操作", style="Card.TLabelframe", padding=15)
        button_card.pack(fill="x")
        
        # 第一行：主要操作
        row1 = ttk.Frame(button_card, style="Card.TFrame")
        row1.pack(fill="x", pady=(0, 8))
        ttk.Button(row1, text="🆕 新建", command=self.new_template, style="Success.TButton").pack(side="left", padx=(0, 6))
        ttk.Button(row1, text="📝 编辑", command=self.edit_template, style="Accent.TButton").pack(side="left", padx=(0, 6))
        ttk.Button(row1, text="🗑️ 删除", command=self.delete_template, style="Danger.TButton").pack(side="left")
        
        # 第二行：应用操作
        row2 = ttk.Frame(button_card, style="Card.TFrame")
        row2.pack(fill="x", pady=(0, 8))
        ttk.Button(row2, text="✅ 应用模板", command=self.apply_template, style="Success.TButton").pack(side="left", padx=(0, 6))
        
        # 第三行：Notion同步操作
        row3 = ttk.Frame(button_card, style="Card.TFrame")
        row3.pack(fill="x")
        ttk.Button(row3, text="📥 从Notion同步", command=self.sync_from_notion, style="Warning.TButton").pack(side="left", padx=(0, 6))
        ttk.Button(row3, text="📤 同步到Notion", command=self.sync_to_notion, style="Warning.TButton").pack(side="left")
        
        # 右侧：模板详情
        right_frame = ttk.Frame(main_container, style="Card.TFrame")
        right_frame.pack(side="right", fill="both", expand=True)
        
        # 模板详情卡片
        detail_card = ttk.LabelFrame(right_frame, text="📋 模板详情", style="Card.TLabelframe", padding=20)
        detail_card.pack(fill="both", expand=True, pady=(0, 15))
        
        # 模板信息
        info_frame = ttk.Frame(detail_card, style="Card.TFrame")
        info_frame.pack(fill="x", pady=(0, 15))
        
        ttk.Label(info_frame, text="名称:", style="CardText.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 8))
        self.detail_name_label = ttk.Label(info_frame, text="", style="CardText.TLabel", font=("Helvetica", 10, "bold"))
        self.detail_name_label.grid(row=0, column=1, sticky="w", padx=(15, 0), pady=(0, 8))
        
        ttk.Label(info_frame, text="分类:", style="CardText.TLabel").grid(row=1, column=0, sticky="w", pady=(0, 8))
        self.detail_category_label = ttk.Label(info_frame, text="", style="CardText.TLabel")
        self.detail_category_label.grid(row=1, column=1, sticky="w", padx=(15, 0), pady=(0, 8))
        
        ttk.Label(info_frame, text="描述:", style="CardText.TLabel").grid(row=2, column=0, sticky="w", pady=(0, 8))
        self.detail_desc_label = ttk.Label(info_frame, text="", style="CardText.TLabel", wraplength=280)
        self.detail_desc_label.grid(row=2, column=1, sticky="w", padx=(15, 0), pady=(0, 8))
        
        # 模板内容
        ttk.Label(detail_card, text="提示词内容:", style="CardText.TLabel").pack(anchor="w", pady=(10, 5))
        
        text_container = tk.Frame(detail_card, bg="#f9fafb")
        text_container.pack(fill="both", expand=True)
        
        self.detail_text = scrolledtext.ScrolledText(
            text_container, 
            height=8, 
            state="disabled", 
            wrap=tk.WORD,
            bg="#f9fafb",
            fg="#111827",
            selectbackground="#e5e7eb",
            selectforeground="#111827",
            font=("SF Pro Text", 10),
            relief="flat",
            borderwidth=2,
            highlightthickness=1,
            highlightcolor="#2563eb",
            highlightbackground="#e5e7eb"
        )
        self.detail_text.pack(fill="both", expand=True, padx=1, pady=1)
        
        # 简化的使用说明卡片
        help_card = ttk.LabelFrame(right_frame, text="💡 使用说明", style="Card.TLabelframe", padding=20)
        help_card.pack(fill="x")
        
        help_text = ttk.Label(help_card, text="选择左侧模板，点击'应用模板'即可将模板内容设置为系统提示词", 
                             style="CardText.TLabel", wraplength=280)
        help_text.pack(anchor="w")
        
        # 初始化模板列表
        self.refresh_templates()
    
    def run(self):
        """运行程序"""
        self.root.mainloop()
    
    def refresh_templates(self):
        """刷新模板列表"""
        # 清空现有项目
        for item in self.template_tree.get_children():
            self.template_tree.delete(item)
        
        # 更新分类下拉框
        categories = ["全部"] + self.template_manager.get_categories()
        self.category_combo["values"] = categories
        
        # 获取选中的分类
        selected_category = self.category_var.get()
        
        # 添加模板到列表
        templates = self.template_manager.get_all_templates()
        for name, template in templates.items():
            category = template.get("category", "基础")
            
            # 根据分类过滤
            if selected_category == "全部" or category == selected_category:
                self.template_tree.insert("", "end", text=name)
    
    def on_category_change(self, event=None):
        """分类选择改变时刷新列表"""
        self.refresh_templates()
    
    def on_template_select(self, event=None):
        """模板选择改变时更新详情"""
        selection = self.template_tree.selection()
        if not selection:
            self.clear_template_detail()
            return
        
        item = self.template_tree.item(selection[0])
        template_name = item["text"]
        
        template = self.template_manager.get_template(template_name)
        if template:
            self.show_template_detail(template_name, template)
    
    def clear_template_detail(self):
        """清空模板详情显示"""
        self.detail_name_label.config(text="")
        self.detail_category_label.config(text="")
        self.detail_desc_label.config(text="")
        self.detail_text.config(state="normal")
        self.detail_text.delete(1.0, tk.END)
        self.detail_text.config(state="disabled")
    
    def show_template_detail(self, name, template):
        """显示模板详情"""
        self.detail_name_label.config(text=name)
        self.detail_category_label.config(text=template.get("category", ""))
        self.detail_desc_label.config(text=template.get("description", ""))
        
        self.detail_text.config(state="normal")
        self.detail_text.delete(1.0, tk.END)
        self.detail_text.insert(1.0, template.get("prompt", ""))
        self.detail_text.config(state="disabled")
    
    def apply_template(self):
        """将选中的模板同步到Notion数据库"""
        selection = self.template_tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请先选择一个模板")
            return
        
        item = self.template_tree.item(selection[0])
        template_name = item["text"]
        
        template = self.template_manager.get_template(template_name)
        if template:
            # 同步模板到Notion数据库
            self.sync_templates()
            self.add_log(f"模板已准备就绪: {template_name}")
            messagebox.showinfo("成功", f"模板 '{template_name}' 已同步到Notion！\n\n现在可以在Notion数据库中选择这个模板了。")
        else:
            messagebox.showerror("错误", "模板不存在")
    
    def new_template(self):
        """新建模板"""
        self.open_template_editor()
    
    def edit_template(self):
        """编辑选中的模板"""
        selection = self.template_tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请先选择一个模板")
            return
        
        item = self.template_tree.item(selection[0])
        template_name = item["text"]
        template = self.template_manager.get_template(template_name)
        
        if template:
            self.open_template_editor(template_name, template)
        else:
            messagebox.showerror("错误", "模板不存在")
    
    def delete_template(self):
        """删除选中的模板"""
        selection = self.template_tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请先选择一个模板")
            return
        
        item = self.template_tree.item(selection[0])
        template_name = item["text"]
        
        if messagebox.askyesno("确认删除", f"确定要删除模板 '{template_name}' 吗？"):
            success, message = self.template_manager.delete_template(template_name)
            if success:
                self.refresh_templates()
                self.clear_template_detail()
                self.add_log(f"已删除模板: {template_name}")
                messagebox.showinfo("成功", message)
            else:
                messagebox.showerror("错误", message)
    
    def open_template_editor(self, template_name=None, template=None):
        """打开简化的模板编辑器窗口"""
        # 创建新窗口
        editor_window = tk.Toplevel(self.root)
        editor_window.title("编辑模板" if template_name else "新建模板")
        editor_window.geometry("500x400")
        editor_window.configure(bg="#ffffff")
        editor_window.transient(self.root)
        editor_window.grab_set()
        
        # 简化的模板信息框架
        info_frame = ttk.LabelFrame(editor_window, text="📝 模板名称", padding=15, style="Card.TLabelframe")
        info_frame.pack(fill="x", padx=15, pady=15)
        
        # 模板名称（唯一必填项）
        name_var = tk.StringVar(value=template_name or "")
        name_entry = ttk.Entry(info_frame, textvariable=name_var, font=("Microsoft YaHei", 11), style="Modern.TEntry")
        name_entry.pack(fill="x")
        
        # 提示词内容框架
        content_frame = ttk.LabelFrame(editor_window, text="💬 提示词内容", padding=15, style="Card.TLabelframe")
        content_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        prompt_text = scrolledtext.ScrolledText(content_frame, height=12, wrap=tk.WORD, font=("Microsoft YaHei", 10))
        prompt_text.pack(fill="both", expand=True)
        
        if template:
            prompt_text.insert(1.0, template.get("prompt", ""))
        
        # 使用提示
        tip_label = ttk.Label(editor_window, text="💡 提示：给模板起个好记的名称，填写提示词内容即可", 
                             style="CardText.TLabel", foreground="#6b7280")
        tip_label.pack(padx=15, pady=(0, 10))
        
        # 按钮框架
        button_frame = ttk.Frame(editor_window)
        button_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        def save_template():
            name = name_var.get().strip()
            prompt = prompt_text.get(1.0, tk.END).strip()
            
            if not name:
                messagebox.showerror("错误", "请输入模板名称")
                name_entry.focus()
                return
            
            if not prompt:
                messagebox.showerror("错误", "请输入提示词内容")
                prompt_text.focus()
                return
            
            # 自动设置分类和描述
            category = "自定义"
            import datetime
            description = f"创建于 {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}"
            
            if template_name and template_name != name:
                # 名称改变了，需要删除旧模板
                self.template_manager.delete_template(template_name)
            
            if template_name:
                # 更新模板
                success, message = self.template_manager.update_template(name, prompt, category, description)
            else:
                # 新建模板
                success, message = self.template_manager.add_template(name, prompt, category, description)
            
            if success:
                self.refresh_templates()
                self.add_log(f"模板保存成功: {name}")
                messagebox.showinfo("成功", f"模板 '{name}' 保存成功！")
                editor_window.destroy()
            else:
                messagebox.showerror("错误", message)
        
        ttk.Button(button_frame, text="💾 保存模板", command=save_template, style="Success.TButton").pack(side="right", padx=5)
        ttk.Button(button_frame, text="取消", command=editor_window.destroy, style="Accent.TButton").pack(side="right")
        
        # 设置焦点到名称输入框
        name_entry.focus()
    
    def sync_from_notion(self):
        """从Notion同步模板到本地"""
        def sync_thread():
            try:
                success, message = self.template_manager.sync_from_notion()
                if success:
                    # 刷新模板列表显示
                    self.root.after(0, self.refresh_templates)
                    self.root.after(0, lambda: messagebox.showinfo("同步成功", message))
                    self.root.after(0, lambda: self.add_log(f"从Notion同步模板成功"))
                else:
                    self.root.after(0, lambda: messagebox.showerror("同步失败", message))
                    self.root.after(0, lambda: self.add_log(f"从Notion同步模板失败: {message}"))
            except Exception as e:
                error_msg = f"从Notion同步失败: {e}"
                self.root.after(0, lambda: messagebox.showerror("同步错误", error_msg))
                self.root.after(0, lambda: self.add_log(error_msg))
        
        # 显示同步开始的提示
        self.add_log("开始从Notion同步模板...")
        threading.Thread(target=sync_thread, daemon=True).start()
    
    def sync_to_notion(self):
        """将本地模板同步到Notion"""
        def sync_thread():
            try:
                success, message = self.template_manager.sync_to_notion()
                if success:
                    self.root.after(0, lambda: messagebox.showinfo("同步成功", message))
                    self.root.after(0, lambda: self.add_log(f"向Notion同步模板成功"))
                else:
                    self.root.after(0, lambda: messagebox.showerror("同步失败", message))
                    self.root.after(0, lambda: self.add_log(f"向Notion同步模板失败: {message}"))
            except Exception as e:
                error_msg = f"同步到Notion失败: {e}"
                self.root.after(0, lambda: messagebox.showerror("同步错误", error_msg))
                self.root.after(0, lambda: self.add_log(error_msg))
        
        # 显示同步开始的提示
        self.add_log("开始向Notion同步模板...")
        threading.Thread(target=sync_thread, daemon=True).start()
    
    def on_closing(self):
        """程序关闭时的处理"""
        if self.is_running:
            self.stop_monitoring()
        self.root.destroy()

    def check_rag_dependencies_silent(self):
        """静默检查RAG依赖是否已安装"""
        try:
            import sentence_transformers
            import faiss
            from notion_knowledge_db import NotionKnowledgeDB
            return True
        except ImportError:
            return False
    
    def check_rag_dependencies(self):
        """检查RAG依赖状态并显示详细信息"""
        missing_packages = []
        installed_packages = []
        
        # 检查关键包
        packages_to_check = [
            ('sentence_transformers', 'Sentence Transformers'),
            ('faiss', 'FAISS向量数据库'),
            ('torch', 'PyTorch'),
            ('transformers', 'Transformers'),
            ('numpy', 'NumPy'),
            ('sklearn', 'Scikit-learn')
        ]
        
        for package_name, display_name in packages_to_check:
            try:
                __import__(package_name)
                installed_packages.append(display_name)
            except ImportError:
                missing_packages.append(display_name)
        
        # 检查自定义模块
        try:
            from notion_knowledge_db import NotionKnowledgeDB
            installed_packages.append('Notion知识库模块')
        except ImportError:
            missing_packages.append('Notion知识库模块')
        
        # 显示结果
        result_msg = "🔍 RAG依赖检查结果:\n\n"
        
        if installed_packages:
            result_msg += "✅ 已安装的包:\n"
            for pkg in installed_packages:
                result_msg += f"  • {pkg}\n"
            result_msg += "\n"
        
        if missing_packages:
            result_msg += "❌ 缺失的包:\n"
            for pkg in missing_packages:
                result_msg += f"  • {pkg}\n"
            result_msg += "\n建议点击'安装RAG依赖'按钮进行安装。"
        else:
            result_msg += "🎉 所有RAG依赖都已安装，可以启用智能检索功能！"
        
        messagebox.showinfo("RAG依赖检查", result_msg)
        
    def install_rag_dependencies(self):
        """安装RAG依赖"""
        def install_thread():
            try:
                import subprocess
                import sys
                
                self.add_log("📦 开始安装RAG依赖包...")
                self.add_log("⏳ 这可能需要几分钟时间，请耐心等待...")
                
                # 检查requirements-full.txt是否存在
                import os
                if not os.path.exists("requirements-full.txt"):
                    self.add_log("❌ requirements-full.txt 文件不存在")
                    messagebox.showerror("错误", "requirements-full.txt 文件不存在")
                    return
                
                # 安装依赖
                result = subprocess.run([
                    sys.executable, "-m", "pip", "install", "-r", "requirements-full.txt"
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    self.add_log("✅ RAG依赖安装成功！")
                    self.root.after(0, lambda: messagebox.showinfo("安装完成", "RAG依赖安装成功！\n\n现在可以启用智能检索功能了。"))
                    self.root.after(0, self.update_rag_status)
                else:
                    error_msg = f"❌ 安装失败: {result.stderr}"
                    self.add_log(error_msg)
                    self.root.after(0, lambda: messagebox.showerror("安装失败", f"安装RAG依赖时出错:\n\n{result.stderr}"))
                    
            except Exception as e:
                error_msg = f"❌ 安装过程出错: {e}"
                self.add_log(error_msg)
                self.root.after(0, lambda: messagebox.showerror("安装错误", f"安装过程中出现错误:\n\n{e}"))
        
        # 在后台线程中执行安装
        threading.Thread(target=install_thread, daemon=True).start()
        
    def update_rag_status(self):
        """更新RAG状态显示"""
        if hasattr(self, 'rag_status_label'):
            if self.check_rag_dependencies_silent():
                self.rag_status_label.config(text="✅ RAG智能检索已启用，依赖包完整", foreground="#059669")
                # 显示RAG配置选项
                for widget in self.rag_config_frame.winfo_children():
                    widget.pack_configure()
            else:
                self.rag_status_label.config(text="🏷️ 使用传统标签检索模式", foreground="#6b7280")
                # 隐藏RAG配置选项
                for widget in self.rag_config_frame.winfo_children():
                    widget.pack_forget()

if __name__ == "__main__":
    # 创建并运行GUI
    app = NotionLLMGUI()
    app.run() 