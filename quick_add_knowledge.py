#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
快速添加知识到Notion - 用于立即测试RAG系统
"""

import json
from notion_knowledge_db import NotionKnowledgeDB

def load_config():
    """加载配置"""
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def add_test_knowledge():
    """添加测试知识条目"""
    
    # 加载配置
    config = load_config()
    
    # 初始化NotionKnowledgeDB
    knowledge_db = NotionKnowledgeDB(config)
    
    # 测试知识条目
    test_knowledge = [
        {
            "title": "AI效率中心概述",
            "content": """AI效率中心是公司为应对智能化转型浪潮设立的战略级部门，致力于通过AI技术重构业务流程、赋能组织效能升级。

核心使命包括：
1. 流程智能化：将AI深度嵌入销售、运营等核心系统
2. 组织赋能：为业务团队提供AI工具与方法论  
3. 资源整合：搭建第三方供应商合作网络
4. AI文化渗透：向全球团队渗透AI思维
5. 人才体系重构：培养AI业务伙伴

运作模式：
- AI-First工作范式：引领性AI协作，构建统一AI决策系统
- 轻量化资源整合：优先对接第三方成熟解决方案
- 敏捷知识管理：设计高级循环学习体系

关键成果：
- 技术降本增效：GPT类模型成本降幅达5倍
- 业务范式革新：实现转介绍逻辑公式化
- 组织能力升级：培养首批AI经理人才""",
            "category": "组织架构",
            "subcategory": "部门职能",
            "keywords": ["AI效率中心", "智能化转型", "组织赋能", "流程智能化", "人才培养"],
            "scenarios": ["部门介绍", "战略规划", "组织架构查询"],
            "priority": "高"
        },
        {
            "title": "AI经理团队建设方案",
            "content": """AI经理团队建设与人才培养框架，解决企业智能化转型中"既懂AI又懂业务"的复合型人才稀缺痛点。

团队角色体系：
1. AI经理：业务主导型（70%业务+30%AI），负责业务单元智能化
2. AIBP（业务伙伴）：技术主导型（70%AI+30%业务），提供技术支持

四阶能力进阶模型：
- Stage 1：工具使用者（3个月）- 掌握Prompt工程、低代码开发
- Stage 2：场景赋能者（6-12个月）- 完成3+个业务场景落地
- Stage 3：价值设计者（1-2年）- 主导跨部门智能化方案设计
- Stage 4：生态构建者（2年+）- 搭建领域AI能力中心

组织保障：
- 每5个业务单元配置1组AI经理+AIBP组合
- 每10组配置1名教研专家+学科运营官
- 建立场景解决方案库和价值度量体系

培养策略：
- 训战结合模式：70%训练融入真实业务场景
- 结对机制：AIBP与业务伙伴配对工作
- 管培生计划：批量招募STEM背景人才""",
            "category": "人才发展",
            "subcategory": "团队建设",
            "keywords": ["AI经理", "AIBP", "人才培养", "团队建设", "能力进阶"],
            "scenarios": ["团队组建", "人才培养", "能力提升", "组织设计"],
            "priority": "高"
        },
        {
            "title": "业务转化策略与用户增长",
            "content": """业务转化策略包括多种方法提高用户参与度和转化率：

核心转化策略：
1. 个性化推荐：基于用户行为数据定制内容推荐
2. 用户体验优化：简化流程，降低转化阻力
3. 转介绍机制：通过现有用户推荐新用户
4. 数据驱动决策：基于转化漏斗分析优化各环节

转介绍逻辑公式化：
- 识别高价值用户特征
- 建立转介绍激励机制
- 优化推荐时机和方式
- 跟踪转化效果并持续优化

增长策略：
- 获客成本优化：平衡获客成本与用户生命周期价值
- 留存率提升：通过产品体验和服务质量提升用户黏性
- 复购率增加：建立用户忠诚度计划
- 口碑传播：提升用户满意度，促进自然传播

关键指标：
- 转化率：各环节转化效率
- 用户生命周期价值（LTV）
- 获客成本（CAC）
- 留存率和复购率""",
            "category": "业务运营",
            "subcategory": "增长策略",
            "keywords": ["用户转化", "增长策略", "转介绍", "个性化推荐", "数据驱动"],
            "scenarios": ["业务增长", "用户运营", "转化优化", "策略制定"],
            "priority": "高"
        }
    ]
    
    print("🚀 开始添加测试知识条目...")
    
    success_count = 0
    for i, knowledge in enumerate(test_knowledge, 1):
        try:
            print(f"\n📝 添加第{i}个知识条目: {knowledge['title']}")
            
            # 创建知识条目
            result = knowledge_db.create_knowledge_item(
                title=knowledge['title'],
                content=knowledge['content'],
                category=knowledge['category'],
                subcategory=knowledge['subcategory'],
                keywords=knowledge['keywords'],
                scenarios=knowledge['scenarios'],
                priority=knowledge['priority']
            )
            
            if result:
                print(f"✅ 成功添加: {knowledge['title']}")
                success_count += 1
            else:
                print(f"❌ 添加失败: {knowledge['title']}")
                
        except Exception as e:
            print(f"❌ 添加知识条目时出错: {e}")
    
    print(f"\n🎉 知识添加完成！成功添加 {success_count}/{len(test_knowledge)} 个条目")
    
    # 测试查询
    print(f"\n🔍 测试知识查询...")
    try:
        results = knowledge_db.search_knowledge_by_keywords(["AI效率中心"])
        print(f"✅ 查询测试成功，找到 {len(results)} 个结果")
        
        if results:
            print(f"📋 第一个结果: {results[0].get('title', 'N/A')}")
    except Exception as e:
        print(f"❌ 查询测试失败: {e}")

if __name__ == "__main__":
    add_test_knowledge() 