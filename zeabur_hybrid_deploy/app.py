#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Zeabur部署入口文件
链接到混合架构云端主程序，支持自动启动
"""

import os
import threading
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 直接导入同目录下的混合架构云端主程序
from cloud_hybrid_main import app, HybridCloudScheduler

def auto_start_scheduler():
    """自动启动调度器"""
    auto_start = os.getenv("AUTO_START", "true").lower() == "true"
    if auto_start:
        logger.info("🚀 Zeabur自动启动混合架构调度器")
        try:
            scheduler = HybridCloudScheduler()
            
            def run_scheduler():
                scheduler.start()
            
            # 存储到全局变量供API使用
            import cloud_hybrid_main
            cloud_hybrid_main.scheduler = scheduler
            
            threading.Thread(target=run_scheduler, daemon=True).start()
            logger.info("✅ 调度器自动启动成功")
            
        except Exception as e:
            logger.error(f"❌ 自动启动失败: {e}")
    else:
        logger.info("⏸️ 自动启动已禁用，请手动启动调度器")

if __name__ == "__main__":
    # 启动时自动启动调度器
    auto_start_scheduler()
    
    # Zeabur会自动设置PORT环境变量
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False) 