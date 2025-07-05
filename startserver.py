#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
云端服务启动器
专用于云端部署，确保不会导入任何GUI相关模块
"""

import os
import sys
import threading

# 设置云端环境标识
os.environ['CLOUD_DEPLOYMENT'] = 'true'

def main():
    """云端启动主函数"""
    print("🌐 启动 Notion-LLM 云端服务...")
    
    try:
        # 导入云端模块
        from cloud_main import app, CloudScheduler
        
        # 创建调度器实例
        scheduler = CloudScheduler()
        
        # 如果设置了自动启动，则启动调度器
        if os.environ.get("AUTO_START", "true").lower() == "true":
            def start_scheduler():
                scheduler.start()
            
            threading.Thread(target=start_scheduler, daemon=True).start()
            print("✅ 自动启动调度器")
        
        # 启动Flask服务
        port = int(os.environ.get('PORT', 5000))
        print(f"🚀 启动Web服务，端口: {port}")
        
        app.run(host="0.0.0.0", port=port, debug=False)
        
    except Exception as e:
        print(f"❌ 云端服务启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 