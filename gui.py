import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import json
import threading
from datetime import datetime
from template_manager import TemplateManager

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
        
        # 模板管理器
        self.template_manager = TemplateManager()
        
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
        
        # 系统提示词设置卡片
        prompt_frame = ttk.LabelFrame(scrollable_frame, text="💭 AI提示词设置", style="Card.TLabelframe", padding=20)
        prompt_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        ttk.Label(prompt_frame, text="系统提示词 (控制AI回复风格和行为):", style="CardText.TLabel").pack(anchor="w", pady=(0, 10))
        
        # 创建提示词编辑区域
        prompt_container = tk.Frame(prompt_frame, bg="#ffffff")
        prompt_container.pack(fill="both", expand=True, pady=(0, 15))
        
        self.prompt_text = scrolledtext.ScrolledText(
            prompt_container, 
            height=6, 
            wrap=tk.WORD,
            bg="#ffffff",
            fg="#111827",
            insertbackground="#2563eb",
            selectbackground="#e5e7eb",
            selectforeground="#111827",
            font=("SF Pro Text", 11),
            relief="flat",
            borderwidth=2,
            highlightthickness=1,
            highlightcolor="#2563eb",
            highlightbackground="#e5e7eb"
        )
        self.prompt_text.pack(fill="both", expand=True, padx=1, pady=1)
        
        # 加载现有的系统提示词
        current_prompt = self.config.get("settings", {}).get("system_prompt", "你是一个智能助手，请认真回答用户的问题。请用中文回复。")
        self.prompt_text.insert(1.0, current_prompt)
        
        # 预设提示词按钮
        preset_frame = ttk.Frame(prompt_frame, style="Card.TFrame")
        preset_frame.pack(fill="x", pady=(10, 0))
        
        ttk.Label(preset_frame, text="快速模板:", style="CardText.TLabel").pack(side="left", padx=(0, 10))
        ttk.Button(preset_frame, text="🤝 通用助手", command=lambda: self.set_preset_prompt("general"), style="Accent.TButton").pack(side="left", padx=3)
        ttk.Button(preset_frame, text="📊 专业分析师", command=lambda: self.set_preset_prompt("analyst"), style="Accent.TButton").pack(side="left", padx=3)
        ttk.Button(preset_frame, text="✍️ 创意写手", command=lambda: self.set_preset_prompt("creative"), style="Accent.TButton").pack(side="left", padx=3)
        ttk.Button(preset_frame, text="💻 技术顾问", command=lambda: self.set_preset_prompt("tech"), style="Accent.TButton").pack(side="left", padx=3)
        
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
        """加载配置文件"""
        try:
            with open("config.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            self.add_log("配置文件不存在，使用默认配置")
            return {}
        except Exception as e:
            self.add_log(f"加载配置文件失败: {e}")
            return {}
    
    def save_config(self):
        """保存配置"""
        try:
            config = {
                "notion": {
                    "api_key": self.notion_key_entry.get(),
                    "database_id": self.notion_db_entry.get()
                },
                "openrouter": {
                    "api_key": self.openrouter_key_entry.get(),
                    "model": self.model_var.get()
                },
                "settings": {
                    "check_interval": int(self.interval_var.get()),
                    "max_retries": 3,
                    "request_timeout": 30,
                    "system_prompt": self.prompt_text.get(1.0, tk.END).strip(),
                    "require_template_selection": True,
                    "auto_generate_title": True,
                    "title_max_length": 20,
                    "title_min_length": 10,
                    "auto_sync_templates": True,
                    "sync_on_startup": True
                }
            }
            
            with open("config.json", "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            
            self.config = config
            messagebox.showinfo("成功", "配置已保存!")
            self.add_log("配置已保存")
            
        except Exception as e:
            messagebox.showerror("错误", f"保存配置失败: {e}")
            self.add_log(f"保存配置失败: {e}")
    
    def test_connections(self):
        """测试API连接"""
        if not self.validate_config():
            return
        
        self.add_log("开始测试API连接...")
        
        def test_thread():
            try:
                # 测试Notion
                from notion_handler import NotionHandler
                notion = NotionHandler(
                    self.config["notion"]["api_key"],
                    self.config["notion"]["database_id"]
                )
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
                self.root.after(0, lambda: messagebox.showerror("错误", f"测试连接时出错: {e}"))
        
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
        
        # 保存当前配置到内存
        self.config = {
            "notion": {
                "api_key": self.notion_key_entry.get(),
                "database_id": self.notion_db_entry.get()
            },
            "openrouter": {
                "api_key": self.openrouter_key_entry.get(),
                "model": self.model_var.get()
            },
            "settings": {
                "check_interval": int(self.interval_var.get()),
                "max_retries": 3,
                "request_timeout": 30,
                "system_prompt": self.prompt_text.get(1.0, tk.END).strip(),
                "require_template_selection": True,
                "auto_generate_title": True,
                "title_max_length": 20,
                "title_min_length": 10,
                "auto_sync_templates": True,
                "sync_on_startup": True
            }
        }
        
        return True
    
    def set_preset_prompt(self, preset_type):
        """设置预设提示词"""
        presets = {
            "general": "你是一个智能助手，请认真回答用户的问题。请用中文回复。",
            "analyst": "你是一个专业的数据分析师和商业顾问。请用逻辑清晰、数据驱动的方式分析问题，提供深入的见解和实用的建议。回复要结构化，包含关键要点和可行的建议。",
            "creative": "你是一个富有创意的写作助手。请用生动、有趣的语言回答问题，善于运用比喻、故事和创新的角度来解释概念。让回复既有用又引人入胜。",
            "tech": "你是一个资深的技术顾问。请用准确、专业的技术语言回答问题，提供详细的技术解决方案、最佳实践和代码示例（如适用）。注重实用性和可操作性。"
        }
        
        if preset_type in presets:
            self.prompt_text.delete(1.0, tk.END)
            self.prompt_text.insert(1.0, presets[preset_type])
            self.add_log(f"已应用预设提示词: {preset_type}")
    
    def start_monitoring(self):
        """开始监听"""
        if not self.validate_config():
            return
        
        self.is_running = True
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
        self.status_label.config(text="状态: 运行中")
        
        # 启动调度器线程
        from scheduler import MessageScheduler
        self.scheduler = MessageScheduler(self.config, self)
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
                notion = NotionHandler(
                    self.config["notion"]["api_key"],
                    self.config["notion"]["database_id"]
                )
                
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
        row2.pack(fill="x")
        ttk.Button(row2, text="✅ 应用模板", command=self.apply_template, style="Success.TButton").pack(side="left", padx=(0, 6))
        ttk.Button(row2, text="💾 保存当前", command=self.save_current_prompt, style="Warning.TButton").pack(side="left")
        
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
        
        # 管理操作卡片
        action_card = ttk.LabelFrame(right_frame, text="📦 模板库管理", style="Card.TLabelframe", padding=20)
        action_card.pack(fill="x")
        
        # 导入导出按钮
        io_frame = ttk.Frame(action_card, style="Card.TFrame")
        io_frame.pack(fill="x")
        ttk.Button(io_frame, text="📤 导出", command=self.export_templates, style="Accent.TButton").pack(side="left", padx=(0, 10))
        ttk.Button(io_frame, text="📥 导入", command=self.import_templates, style="Accent.TButton").pack(side="left")
        
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
        """应用选中的模板到系统提示词"""
        selection = self.template_tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请先选择一个模板")
            return
        
        item = self.template_tree.item(selection[0])
        template_name = item["text"]
        
        template = self.template_manager.get_template(template_name)
        if template:
            # 将模板内容设置到配置页面的提示词编辑器
            self.prompt_text.delete(1.0, tk.END)
            self.prompt_text.insert(1.0, template["prompt"])
            
            self.add_log(f"已应用模板: {template_name}")
            messagebox.showinfo("成功", f"已应用模板 '{template_name}'")
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
    
    def save_current_prompt(self):
        """保存当前提示词为模板"""
        current_prompt = self.prompt_text.get(1.0, tk.END).strip()
        if not current_prompt:
            messagebox.showwarning("提示", "当前提示词为空")
            return
        
        # 创建一个简单的模板对象
        template = {
            "prompt": current_prompt,
            "category": "基础",
            "description": "从当前提示词保存"
        }
        
        self.open_template_editor(template=template)
    
    def export_templates(self):
        """导出模板库"""
        filename = filedialog.asksaveasfilename(
            title="导出模板库",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            success, message = self.template_manager.export_templates(filename)
            if success:
                self.add_log(f"模板库已导出到: {filename}")
                messagebox.showinfo("成功", message)
            else:
                messagebox.showerror("错误", message)
    
    def import_templates(self):
        """导入模板库"""
        filename = filedialog.askopenfilename(
            title="导入模板库",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            # 询问是否合并
            merge = messagebox.askyesno("导入方式", "是否与现有模板合并？\n选择'是'合并，选择'否'替换全部模板")
            
            success, message = self.template_manager.import_templates(filename, merge)
            if success:
                self.refresh_templates()
                self.add_log(f"已导入模板库: {filename}")
                messagebox.showinfo("成功", message)
            else:
                messagebox.showerror("错误", message)
    
    def open_template_editor(self, template_name=None, template=None):
        """打开模板编辑器窗口"""
        # 创建新窗口
        editor_window = tk.Toplevel(self.root)
        editor_window.title("模板编辑器" if template_name else "新建模板")
        editor_window.geometry("600x500")
        editor_window.configure(bg="#ffffff")
        editor_window.transient(self.root)
        editor_window.grab_set()
        
        # 模板信息框架
        info_frame = ttk.LabelFrame(editor_window, text="模板信息", padding=10, style="Card.TLabelframe")
        info_frame.pack(fill="x", padx=10, pady=10)
        
        # 模板名称
        ttk.Label(info_frame, text="模板名称:").grid(row=0, column=0, sticky="w", pady=5)
        name_var = tk.StringVar(value=template_name or "")
        name_entry = ttk.Entry(info_frame, textvariable=name_var, width=40, style="Modern.TEntry")
        name_entry.grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=5)
        
        # 分类
        ttk.Label(info_frame, text="分类:").grid(row=1, column=0, sticky="w", pady=5)
        category_var = tk.StringVar(value=template.get("category", "基础") if template else "基础")
        category_combo = ttk.Combobox(info_frame, textvariable=category_var, width=37, style="Modern.TCombobox")
        category_combo["values"] = self.template_manager.get_categories()
        category_combo.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=5)
        
        # 描述
        ttk.Label(info_frame, text="描述:").grid(row=2, column=0, sticky="w", pady=5)
        desc_var = tk.StringVar(value=template.get("description", "") if template else "")
        desc_entry = ttk.Entry(info_frame, textvariable=desc_var, width=40, style="Modern.TEntry")
        desc_entry.grid(row=2, column=1, sticky="ew", padx=(10, 0), pady=5)
        
        info_frame.columnconfigure(1, weight=1)
        
        # 提示词内容框架
        content_frame = ttk.LabelFrame(editor_window, text="提示词内容", padding=10, style="Card.TLabelframe")
        content_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # 创建文本容器
        text_container = tk.Frame(content_frame, bg="#ffffff")
        text_container.pack(fill="both", expand=True)
        
        prompt_text = scrolledtext.ScrolledText(content_frame, height=15, wrap=tk.WORD)
        prompt_text.pack(fill="both", expand=True)
        
        if template:
            prompt_text.insert(1.0, template.get("prompt", ""))
        
        # 按钮框架
        button_frame = ttk.Frame(editor_window)
        button_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        def save_template():
            name = name_var.get().strip()
            category = category_var.get().strip()
            description = desc_var.get().strip()
            prompt = prompt_text.get(1.0, tk.END).strip()
            
            if not name:
                messagebox.showerror("错误", "请输入模板名称")
                return
            
            if not prompt:
                messagebox.showerror("错误", "请输入提示词内容")
                return
            
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
                messagebox.showinfo("成功", message)
                editor_window.destroy()
            else:
                messagebox.showerror("错误", message)
        
        ttk.Button(button_frame, text="保存", command=save_template).pack(side="right", padx=5)
        ttk.Button(button_frame, text="取消", command=editor_window.destroy).pack(side="right")
    
    def on_closing(self):
        """程序关闭时的处理"""
        if self.is_running:
            self.stop_monitoring()
        self.root.destroy()

if __name__ == "__main__":
    # 创建并运行GUI
    app = NotionLLMGUI()
    app.run() 