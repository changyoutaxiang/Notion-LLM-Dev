#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本地RAG后台服务启动器
让RAG服务在后台静默运行，无需打开GUI界面
"""

import os
import sys
import json
import time
import signal
import psutil
import subprocess
from pathlib import Path

class LocalRAGServiceManager:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.config_file = self.project_root / "config.json"
        self.pid_file = self.project_root / "rag_service.pid"
        self.log_file = self.project_root / "logs" / "rag_service.log"
        
        # 确保logs目录存在
        self.log_file.parent.mkdir(exist_ok=True)
    
    def check_dependencies(self):
        """检查RAG依赖是否完整"""
        print("🔍 检查RAG依赖...")
        
        required_packages = [
            ('torch', 'torch'), 
            ('faiss-cpu', 'faiss'), 
            ('sentence_transformers', 'sentence_transformers'),
            ('numpy', 'numpy'), 
            ('requests', 'requests'), 
            ('fastapi', 'fastapi'), 
            ('uvicorn', 'uvicorn')
        ]
        
        missing = []
        for display_name, import_name in required_packages:
            try:
                __import__(import_name)
            except ImportError:
                missing.append(display_name)
        
        if missing:
            print(f"❌ 缺少依赖包: {', '.join(missing)}")
            print("请运行: pip install -r requirements-full.txt")
            return False
            
        print("✅ RAG依赖检查通过")
        return True
    
    def check_rag_config(self):
        """检查RAG配置是否启用"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            rag_enabled = config.get('knowledge_search', {}).get('rag_system', {}).get('enabled', False)
            if not rag_enabled:
                print("❌ RAG系统未启用")
                print("请在config.json中设置: knowledge_search.rag_system.enabled = true")
                return False
                
            print("✅ RAG配置检查通过")
            return True
            
        except Exception as e:
            print(f"❌ 配置文件错误: {e}")
            return False
    
    def is_service_running(self):
        """检查服务是否已在运行"""
        if not self.pid_file.exists():
            return False
            
        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            # 检查进程是否存在
            if psutil.pid_exists(pid):
                process = psutil.Process(pid)
                if 'python' in process.name().lower():
                    return True
            
            # PID文件存在但进程不存在，清理PID文件
            self.pid_file.unlink()
            return False
            
        except Exception:
            return False
    
    def start_service(self):
        """启动RAG后台服务"""
        if self.is_service_running():
            print("✅ RAG服务已在运行")
            return True
        
        print("🚀 启动RAG后台服务...")
        
        try:
            # 构建启动命令
            cmd = [
                sys.executable, "-c",
                """
import sys
sys.path.insert(0, '.')
from hybrid_retrieval import HybridRetrievalEngine
from semantic_search import HighPerformanceSemanticSearch
import uvicorn
from fastapi import FastAPI
import json
import time

# 创建FastAPI应用
app = FastAPI(title="Local RAG Service", version="1.0.0")

# 全局RAG引擎
rag_engine = None

@app.on_event("startup")
async def startup_event():
    global rag_engine
    print("🔄 加载RAG引擎...")
    
    # 加载配置
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # 初始化NotionKnowledgeDB
    from notion_knowledge_db import NotionKnowledgeDB
    knowledge_db = NotionKnowledgeDB(config)
    
    # 初始化RAG系统
    rag_engine = HybridRetrievalEngine(knowledge_db, config)
    print("✅ RAG引擎加载完成")

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "Local RAG Service",
        "version": "1.0.0",
        "rag_engine_ready": rag_engine is not None
    }

@app.post("/search")
async def search(query: str, tags: list = None, max_results: int = 5):
    if not rag_engine:
        return {"error": "RAG engine not ready"}
    
    try:
        results = rag_engine.smart_search(query, tags or [], max_results)
        context = rag_engine.build_context(results, query)
        
        return {
            "success": True,
            "results": results,
            "context": context,
            "query": query
        }
    except Exception as e:
        return {"error": str(e)}

# 启动服务
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")
                """
            ]
            
            # 后台启动进程
            with open(self.log_file, 'w') as log_f:
                process = subprocess.Popen(
                    cmd,
                    stdout=log_f,
                    stderr=subprocess.STDOUT,
                    cwd=self.project_root,
                    start_new_session=True  # 创建新会话，脱离终端
                )
            
            # 保存PID
            with open(self.pid_file, 'w') as f:
                f.write(str(process.pid))
            
            # 等待服务启动
            print("⏳ 等待服务启动...")
            time.sleep(3)
            
            # 检查服务状态
            if self.check_service_health():
                print("✅ RAG后台服务启动成功！")
                print(f"📋 服务地址: http://127.0.0.1:8001")
                print(f"📄 日志文件: {self.log_file}")
                print(f"🔧 进程ID: {process.pid}")
                return True
            else:
                print("❌ 服务启动失败，请查看日志文件")
                return False
                
        except Exception as e:
            print(f"❌ 启动服务失败: {e}")
            return False
    
    def stop_service(self):
        """停止RAG服务"""
        if not self.is_service_running():
            print("ℹ️ RAG服务未运行")
            return True
        
        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            print(f"🛑 停止RAG服务 (PID: {pid})...")
            
            # 尝试优雅停止
            process = psutil.Process(pid)
            process.terminate()
            
            # 等待进程结束
            try:
                process.wait(timeout=10)
            except psutil.TimeoutExpired:
                # 强制杀死进程
                process.kill()
                print("⚠️ 强制终止进程")
            
            # 清理PID文件
            self.pid_file.unlink()
            print("✅ RAG服务已停止")
            return True
            
        except Exception as e:
            print(f"❌ 停止服务失败: {e}")
            return False
    
    def check_service_health(self):
        """检查服务健康状态"""
        import requests
        try:
            response = requests.get("http://127.0.0.1:8001/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def show_status(self):
        """显示服务状态"""
        print("=" * 50)
        print("🤖 本地RAG服务状态")
        print("=" * 50)
        
        if self.is_service_running():
            print("✅ 服务状态: 运行中")
            print("📋 服务地址: http://127.0.0.1:8001")
            
            if self.check_service_health():
                print("💚 健康检查: 通过")
            else:
                print("💛 健康检查: 警告")
        else:
            print("❌ 服务状态: 未运行")
        
        print(f"📄 日志文件: {self.log_file}")
        print("=" * 50)

def main():
    manager = LocalRAGServiceManager()
    
    if len(sys.argv) < 2:
        print("🤖 本地RAG后台服务管理器")
        print("=" * 40)
        print("使用方法:")
        print("  python start_local_rag_service.py start   # 启动服务")
        print("  python start_local_rag_service.py stop    # 停止服务")  
        print("  python start_local_rag_service.py status  # 查看状态")
        print("  python start_local_rag_service.py restart # 重启服务")
        return
    
    command = sys.argv[1].lower()
    
    if command == "start":
        print("🚀 启动本地RAG后台服务")
        print("=" * 40)
        
        # 检查环境
        if not manager.check_dependencies():
            return
        if not manager.check_rag_config():
            return
        
        # 启动服务
        if manager.start_service():
            print("\n🎉 RAG后台服务已启动！")
            print("💡 提示:")
            print("  - 服务将在后台持续运行")
            print("  - 关闭此终端窗口不影响服务")
            print("  - 可随时使用 'python start_local_rag_service.py status' 查看状态")
    
    elif command == "stop":
        print("🛑 停止本地RAG服务")
        print("=" * 40)
        manager.stop_service()
    
    elif command == "status":
        manager.show_status()
    
    elif command == "restart":
        print("🔄 重启本地RAG服务")
        print("=" * 40)
        manager.stop_service()
        time.sleep(2)
        
        if not manager.check_dependencies():
            return
        if not manager.check_rag_config():
            return
            
        manager.start_service()
    
    else:
        print(f"❌ 未知命令: {command}")

if __name__ == "__main__":
    main() 