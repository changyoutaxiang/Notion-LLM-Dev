#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Notion-LLM 友好启动器
双击即可启动程序
"""

import sys
import os
import subprocess
import tkinter as tk
from tkinter import messagebox
import threading

class NotionLLMLauncher:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Notion-LLM 异步通信助手")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        
        # 设置窗口居中
        self.center_window()
        
        # 创建UI
        self.create_ui()
        
    def center_window(self):
        """窗口居中显示"""
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.root.winfo_screenheight() // 2) - (400 // 2)
        self.root.geometry(f"500x400+{x}+{y}")
    
    def create_ui(self):
        """创建用户界面"""
        # 标题
        title_label = tk.Label(
            self.root, 
            text="🤖 Notion-LLM 异步通信助手", 
            font=("Arial", 18, "bold"),
            fg="#2c3e50"
        )
        title_label.pack(pady=20)
        
        # 描述
        desc_text = """
📝 自动处理Notion数据库中的消息
🧠 调用AI模型生成智能回复
🔄 将回复写入页面内容，提供更好的阅读体验
        """
        desc_label = tk.Label(
            self.root, 
            text=desc_text.strip(),
            font=("Arial", 11),
            justify=tk.LEFT,
            fg="#34495e"
        )
        desc_label.pack(pady=10)
        
        # 状态显示
        self.status_var = tk.StringVar(value="准备启动...")
        status_label = tk.Label(
            self.root,
            textvariable=self.status_var,
            font=("Arial", 10),
            fg="#7f8c8d"
        )
        status_label.pack(pady=5)
        
        # 按钮框架
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=30)
        
        # 启动按钮
        self.start_button = tk.Button(
            button_frame,
            text="🚀 启动程序",
            font=("Arial", 14, "bold"),
            bg="#3498db",
            fg="white",
            padx=30,
            pady=10,
            command=self.start_program,
            cursor="hand2"
        )
        self.start_button.pack(side=tk.LEFT, padx=10)
        
        # 检查环境按钮
        check_button = tk.Button(
            button_frame,
            text="🔍 检查环境",
            font=("Arial", 12),
            bg="#95a5a6",
            fg="white",
            padx=20,
            pady=8,
            command=self.check_environment,
            cursor="hand2"
        )
        check_button.pack(side=tk.LEFT, padx=10)
        
        # 使用说明
        help_frame = tk.Frame(self.root)
        help_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=20)
        
        help_text = """
💡 使用提示：
1. 首次使用请先点击"检查环境"
2. 确保config.json已正确配置API密钥
3. 点击"启动程序"即可开始使用
        """
        help_label = tk.Label(
            help_frame,
            text=help_text.strip(),
            font=("Arial", 9),
            justify=tk.LEFT,
            fg="#7f8c8d",
            bg="#ecf0f1"
        )
        help_label.pack(fill=tk.X, padx=10, pady=10)
    
    def check_environment(self):
        """检查运行环境"""
        self.status_var.set("正在检查环境...")
        
        def check():
            try:
                # 检查Python版本
                python_version = sys.version.split()[0]
                
                # 检查依赖包
                try:
                    import requests
                    deps_ok = True
                except ImportError:
                    deps_ok = False
                
                # 检查配置文件
                config_exists = os.path.exists("config.json")
                
                # 检查主程序文件
                main_exists = os.path.exists("main.py")
                
                # 更新状态
                if deps_ok and config_exists and main_exists:
                    self.status_var.set("✅ 环境检查通过，可以启动")
                    messagebox.showinfo(
                        "环境检查", 
                        f"✅ 环境检查通过！\n\nPython版本: {python_version}\n依赖包: ✅ 已安装\n配置文件: ✅ 存在\n主程序: ✅ 存在"
                    )
                else:
                    issues = []
                    if not deps_ok:
                        issues.append("• 缺少依赖包 (运行: pip install -r requirements.txt)")
                    if not config_exists:
                        issues.append("• 缺少配置文件 config.json")
                    if not main_exists:
                        issues.append("• 缺少主程序文件 main.py")
                    
                    self.status_var.set("❌ 环境检查失败")
                    messagebox.showerror(
                        "环境检查", 
                        f"❌ 环境检查失败！\n\n问题：\n" + "\n".join(issues)
                    )
                    
            except Exception as e:
                self.status_var.set(f"检查出错: {e}")
                messagebox.showerror("检查出错", f"环境检查时出错：{e}")
        
        threading.Thread(target=check, daemon=True).start()
    
    def start_program(self):
        """启动主程序"""
        def start():
            try:
                self.start_button.config(state=tk.DISABLED, text="正在启动...")
                self.status_var.set("正在启动主程序...")
                
                # 启动主程序
                if os.path.exists("main.py"):
                    subprocess.run([sys.executable, "main.py"], check=True)
                else:
                    messagebox.showerror("启动失败", "找不到main.py文件")
                    
            except subprocess.CalledProcessError as e:
                messagebox.showerror("启动失败", f"程序启动失败：{e}")
            except Exception as e:
                messagebox.showerror("启动出错", f"启动时出错：{e}")
            finally:
                self.start_button.config(state=tk.NORMAL, text="🚀 启动程序")
                self.status_var.set("准备启动...")
        
        threading.Thread(target=start, daemon=True).start()
    
    def run(self):
        """运行启动器"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            pass

def main():
    """主函数"""
    launcher = NotionLLMLauncher()
    launcher.run()

if __name__ == "__main__":
    main() 