#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 RAG智能检索系统启动器
简化启动流程，提供图形化界面
"""

import os
import sys
import json
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import subprocess
from pathlib import Path

class RAGSystemLauncher:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🚀 RAG智能检索系统启动器")
        self.root.geometry("800x600")
        self.setup_ui()
        self.is_running = False
        self.config = None
        
    def setup_ui(self):
        """设置用户界面"""
        # 主标题
        title_frame = ttk.Frame(self.root)
        title_frame.pack(fill=tk.X, padx=10, pady=10)
        
        title_label = ttk.Label(
            title_frame, 
            text="🧠 RAG智能检索系统",
            font=("Arial", 20, "bold")
        )
        title_label.pack()
        
        subtitle_label = ttk.Label(
            title_frame,
            text="高性能语义搜索 + 混合检索引擎",
            font=("Arial", 12)
        )
        subtitle_label.pack()
        
        # 状态面板
        status_frame = ttk.LabelFrame(self.root, text="📊 系统状态")
        status_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.status_text = tk.StringVar(value="🔍 正在检查系统状态...")
        status_label = ttk.Label(status_frame, textvariable=self.status_text)
        status_label.pack(padx=10, pady=5)
        
        # 进度条
        self.progress = ttk.Progressbar(status_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, padx=10, pady=5)
        
        # 按钮区域
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # 检查系统按钮
        self.check_btn = ttk.Button(
            button_frame,
            text="🔍 检查系统",
            command=self.check_system_threaded
        )
        self.check_btn.pack(side=tk.LEFT, padx=5)
        
        # 安装依赖按钮
        self.install_btn = ttk.Button(
            button_frame,
            text="📦 安装依赖",
            command=self.install_dependencies_threaded,
            state=tk.DISABLED
        )
        self.install_btn.pack(side=tk.LEFT, padx=5)
        
        # 运行测试按钮
        self.test_btn = ttk.Button(
            button_frame,
            text="🧪 运行测试",
            command=self.run_tests_threaded,
            state=tk.DISABLED
        )
        self.test_btn.pack(side=tk.LEFT, padx=5)
        
        # 启动系统按钮
        self.start_btn = ttk.Button(
            button_frame,
            text="🚀 启动RAG系统",
            command=self.start_rag_system,
            state=tk.DISABLED
        )
        self.start_btn.pack(side=tk.RIGHT, padx=5)
        
        # 日志区域
        log_frame = ttk.LabelFrame(self.root, text="📝 系统日志")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=15,
            font=("Consolas", 10)
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 开始检查系统
        self.root.after(1000, self.check_system_threaded)
    
    def log(self, message: str, level: str = "INFO"):
        """记录日志"""
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {level}: {message}\n"
        
        # 在主线程中更新UI
        self.root.after(0, lambda: self._update_log(log_message))
    
    def _update_log(self, message: str):
        """更新日志显示"""
        self.log_text.insert(tk.END, message)
        self.log_text.see(tk.END)
    
    def update_status(self, status: str):
        """更新状态"""
        self.root.after(0, lambda: self.status_text.set(status))
    
    def check_system_threaded(self):
        """在线程中检查系统"""
        threading.Thread(target=self.check_system, daemon=True).start()
    
    def check_system(self):
        """检查系统环境"""
        self.update_status("🔍 检查系统环境...")
        self.progress.start()
        
        try:
            self.log("开始系统环境检查")
            
            # 检查Python版本
            python_version = sys.version_info
            self.log(f"Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
            
            if python_version < (3, 8):
                self.log("❌ Python版本过低，需要3.8+", "ERROR")
                self.update_status("❌ Python版本过低")
                return
            
            # 检查配置文件
            config_path = Path("config.json")
            if not config_path.exists():
                self.log("⚠️ config.json不存在，检查示例配置")
                example_path = Path("config.example.json")
                if example_path.exists():
                    self.log("✅ 找到config.example.json")
                    self.install_btn.config(state=tk.NORMAL)
                else:
                    self.log("❌ 配置文件缺失", "ERROR")
                    self.update_status("❌ 配置文件缺失")
                    return
            else:
                self.log("✅ 配置文件存在")
            
            # 检查依赖包
            self.log("检查依赖包...")
            missing_packages = self._check_dependencies()
            
            if missing_packages:
                self.log(f"⚠️ 缺少依赖包: {', '.join(missing_packages)}")
                self.install_btn.config(state=tk.NORMAL)
                self.update_status("⚠️ 需要安装依赖包")
            else:
                self.log("✅ 所有依赖包已安装")
                self.test_btn.config(state=tk.NORMAL)
                self.start_btn.config(state=tk.NORMAL)
                self.update_status("✅ 系统就绪")
            
        except Exception as e:
            self.log(f"❌ 系统检查失败: {e}", "ERROR")
            self.update_status("❌ 系统检查失败")
        finally:
            self.progress.stop()
    
    def _check_dependencies(self):
        """检查依赖包"""
        required_packages = [
            'torch', 'transformers', 'sentence-transformers',
            'numpy', 'faiss-cpu', 'loguru'
        ]
        
        missing = []
        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
            except ImportError:
                missing.append(package)
        
        return missing
    
    def install_dependencies_threaded(self):
        """在线程中安装依赖"""
        threading.Thread(target=self.install_dependencies, daemon=True).start()
    
    def install_dependencies(self):
        """安装依赖包"""
        self.update_status("📦 安装依赖包...")
        self.progress.start()
        
        try:
            self.log("开始安装依赖包")
            
            # 复制配置文件
            if not Path("config.json").exists():
                if Path("config.example.json").exists():
                    import shutil
                    shutil.copy("config.example.json", "config.json")
                    self.log("✅ 配置文件已创建")
            
            # 安装依赖
            if Path("requirements_rag.txt").exists():
                self.log("安装RAG依赖包...")
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "install", "-r", "requirements_rag.txt"],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    self.log("✅ 依赖安装完成")
                    self.test_btn.config(state=tk.NORMAL)
                    self.start_btn.config(state=tk.NORMAL)
                    self.update_status("✅ 依赖安装完成")
                else:
                    self.log(f"❌ 安装失败: {result.stderr}", "ERROR")
                    self.update_status("❌ 安装失败")
            else:
                self.log("❌ requirements_rag.txt不存在", "ERROR")
                self.update_status("❌ 依赖文件缺失")
        
        except Exception as e:
            self.log(f"❌ 安装过程出错: {e}", "ERROR")
            self.update_status("❌ 安装失败")
        finally:
            self.progress.stop()
    
    def run_tests_threaded(self):
        """在线程中运行测试"""
        threading.Thread(target=self.run_tests, daemon=True).start()
    
    def run_tests(self):
        """运行系统测试"""
        self.update_status("🧪 运行系统测试...")
        self.progress.start()
        
        try:
            self.log("开始运行系统测试")
            
            if Path("test_rag_phase1.py").exists():
                result = subprocess.run(
                    [sys.executable, "test_rag_phase1.py"],
                    capture_output=True,
                    text=True
                )
                
                self.log("测试输出:")
                for line in result.stdout.split('\n'):
                    if line.strip():
                        self.log(line)
                
                if result.returncode == 0:
                    self.log("✅ 所有测试通过")
                    self.update_status("✅ 测试通过，系统就绪")
                else:
                    self.log("❌ 部分测试失败", "WARNING")
                    self.update_status("⚠️ 部分测试失败")
            else:
                self.log("❌ 测试文件不存在", "ERROR")
                self.update_status("❌ 测试文件缺失")
        
        except Exception as e:
            self.log(f"❌ 测试运行失败: {e}", "ERROR")
            self.update_status("❌ 测试失败")
        finally:
            self.progress.stop()
    
    def start_rag_system(self):
        """启动RAG系统"""
        try:
            self.log("🚀 启动RAG智能检索系统")
            
            # 启动主程序
            if Path("main.py").exists():
                self.log("启动主程序...")
                subprocess.Popen([sys.executable, "main.py"])
                self.log("✅ RAG系统已启动")
                
                # 询问是否关闭启动器
                if messagebox.askyesno("启动成功", "RAG系统已启动！\n是否关闭启动器？"):
                    self.root.quit()
            else:
                self.log("❌ 主程序文件不存在", "ERROR")
                messagebox.showerror("错误", "main.py文件不存在")
        
        except Exception as e:
            self.log(f"❌ 启动失败: {e}", "ERROR")
            messagebox.showerror("启动失败", f"启动RAG系统失败:\n{e}")
    
    def run(self):
        """运行启动器"""
        self.root.mainloop()

def main():
    """主函数"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║                    🚀 RAG智能检索系统启动器                    ║
║                        图形化启动界面                         ║
╚═══════════════════════════════════════════════════════════════╝
    """)
    
    try:
        launcher = RAGSystemLauncher()
        launcher.run()
    except KeyboardInterrupt:
        print("\n👋 用户取消启动")
    except Exception as e:
        print(f"❌ 启动器失败: {e}")
        input("按Enter键退出...")

if __name__ == "__main__":
    main() 