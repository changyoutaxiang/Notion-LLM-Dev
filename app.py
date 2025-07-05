#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
云端部署入口文件
专门为 Zeabur 等云端平台设计，确保不会导入 GUI 相关模块
"""

import os
import sys

# 确保不导入 GUI 相关模块
if __name__ == "__main__":
    # 设置云端环境标识
    os.environ['CLOUD_DEPLOYMENT'] = 'true'
    
    # 导入并启动云端版本
    try:
        from cloud_main import app, CloudScheduler
        
        # 创建全局调度器实例
        scheduler = CloudScheduler()
        
        # 启动 Flask 应用
        if __name__ == "__main__":
            port = int(os.environ.get('PORT', 8000))
            app.run(host='0.0.0.0', port=port, debug=False)
            
    except Exception as e:
        print(f"云端启动失败: {e}")
        sys.exit(1) 