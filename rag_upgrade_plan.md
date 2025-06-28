# 🧠 RAG能力升级计划 v2.0

## 🎯 升级目标

### 当前能力
```
✅ 基础关键词匹配
✅ Notion实时查询
✅ 使用频率统计
✅ 简单片段提取
```

### 目标能力
```
🚀 语义相似度搜索
🚀 上下文理解
🚀 多轮对话支持
🚀 智能知识推理
🚀 自动知识更新建议
```

---

## 📋 技术实施路径

### Phase 1: 语义检索增强（立即可做，1周内完成）

#### 1.1 集成Sentence Transformers
```python
# 新增文件: semantic_search.py
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import os

class SemanticSearchEngine:
    def __init__(self, model_name="shibing624/text2vec-base-chinese"):
        self.model = SentenceTransformer(model_name)
        self.knowledge_embeddings = None
        self.knowledge_texts = []
        self.embedding_cache_file = "knowledge_embeddings.pkl"
    
    def build_knowledge_index(self, knowledge_items):
        """构建知识库向量索引"""
        print("🔄 构建知识库向量索引...")
        
        # 提取文本内容
        texts = []
        for item in knowledge_items:
            # 组合标题、关键词和内容摘要
            combined_text = f"{item['title']} {' '.join(item['keywords'])} {item['content'][:500]}"
            texts.append(combined_text)
        
        self.knowledge_texts = texts
        self.knowledge_embeddings = self.model.encode(texts)
        
        # 缓存embeddings
        self._save_embeddings()
        print(f"✅ 知识库索引构建完成，共 {len(texts)} 个条目")
    
    def semantic_search(self, query, top_k=5, similarity_threshold=0.3):
        """语义相似度搜索"""
        if self.knowledge_embeddings is None:
            self._load_embeddings()
        
        query_embedding = self.model.encode([query])
        similarities = cosine_similarity(query_embedding, self.knowledge_embeddings)[0]
        
        # 筛选超过阈值的结果
        valid_indices = np.where(similarities > similarity_threshold)[0]
        valid_similarities = similarities[valid_indices]
        
        # 按相似度排序
        sorted_indices = np.argsort(valid_similarities)[::-1][:top_k]
        
        results = []
        for idx in sorted_indices:
            original_idx = valid_indices[idx]
            results.append({
                'index': original_idx,
                'similarity': valid_similarities[idx],
                'text': self.knowledge_texts[original_idx]
            })
        
        return results
    
    def _save_embeddings(self):
        """保存embeddings到本地"""
        cache_data = {
            'embeddings': self.knowledge_embeddings,
            'texts': self.knowledge_texts
        }
        with open(self.embedding_cache_file, 'wb') as f:
            pickle.dump(cache_data, f)
    
    def _load_embeddings(self):
        """从本地加载embeddings"""
        if os.path.exists(self.embedding_cache_file):
            with open(self.embedding_cache_file, 'rb') as f:
                cache_data = pickle.load(f)
                self.knowledge_embeddings = cache_data['embeddings']
                self.knowledge_texts = cache_data['texts']
```

#### 1.2 集成到现有系统
```python
# 修改 notion_knowledge_db.py
class NotionKnowledgeDB(NotionHandler):
    def __init__(self, config):
        super().__init__(config)
        # 新增语义搜索引擎
        self.semantic_engine = None
        self._init_semantic_search()
    
    def _init_semantic_search(self):
        """初始化语义搜索引擎"""
        try:
            from semantic_search import SemanticSearchEngine
            self.semantic_engine = SemanticSearchEngine()
            print("✅ 语义搜索引擎初始化成功")
        except ImportError:
            print("⚠️  语义搜索依赖未安装，使用关键词搜索")
    
    def enhanced_search_knowledge(self, query, use_semantic=True):
        """增强版知识搜索"""
        results = []
        
        # 1. 传统关键词搜索
        keyword_results = self.search_knowledge_by_keywords([query])
        results.extend([{'source': 'keyword', 'data': item} for item in keyword_results])
        
        # 2. 语义相似度搜索
        if use_semantic and self.semantic_engine:
            # 获取所有知识用于语义搜索
            all_knowledge = self._get_all_knowledge()
            if all_knowledge:
                self.semantic_engine.build_knowledge_index(all_knowledge)
                semantic_results = self.semantic_engine.semantic_search(query)
                
                for result in semantic_results:
                    knowledge_item = all_knowledge[result['index']]
                    knowledge_item['semantic_score'] = result['similarity']
                    results.append({'source': 'semantic', 'data': knowledge_item})
        
        # 3. 合并和去重
        unique_results = self._merge_and_deduplicate(results)
        
        # 4. 重新排序（优先级 + 语义相似度 + 使用频率）
        sorted_results = self._smart_ranking(unique_results, query)
        
        return sorted_results[:5]  # 返回前5个最相关的
```

### Phase 2: 混合检索策略（2周内完成）

#### 2.1 智能片段提取
```python
# 新增文件: smart_chunking.py
import re
from typing import List, Dict

class SmartChunking:
    def __init__(self, chunk_size=300, overlap=50):
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def extract_relevant_snippets(self, content: str, query: str, max_snippets=3):
        """提取与查询最相关的内容片段"""
        # 1. 按段落分割
        paragraphs = self._split_by_semantics(content)
        
        # 2. 计算每个段落与查询的相关性
        paragraph_scores = []
        for para in paragraphs:
            score = self._calculate_relevance(para, query)
            paragraph_scores.append((para, score))
        
        # 3. 选择最相关的段落
        paragraph_scores.sort(key=lambda x: x[1], reverse=True)
        
        # 4. 生成连贯的片段
        snippets = []
        for para, score in paragraph_scores[:max_snippets]:
            if score > 0.1:  # 相关性阈值
                snippet = self._create_contextual_snippet(para, content)
                snippets.append({
                    'content': snippet,
                    'relevance': score,
                    'type': 'semantic_match'
                })
        
        return snippets
    
    def _split_by_semantics(self, content: str) -> List[str]:
        """按语义分割内容"""
        # 按段落分割
        paragraphs = content.split('\n\n')
        
        # 进一步按句子分割长段落
        refined_paragraphs = []
        for para in paragraphs:
            if len(para) > self.chunk_size:
                sentences = re.split(r'[。！？]', para)
                current_chunk = ""
                for sentence in sentences:
                    if len(current_chunk + sentence) < self.chunk_size:
                        current_chunk += sentence
                    else:
                        if current_chunk:
                            refined_paragraphs.append(current_chunk)
                        current_chunk = sentence
                if current_chunk:
                    refined_paragraphs.append(current_chunk)
            else:
                refined_paragraphs.append(para)
        
        return [p.strip() for p in refined_paragraphs if p.strip()]
    
    def _calculate_relevance(self, paragraph: str, query: str) -> float:
        """计算段落与查询的相关性"""
        # 简单的关键词重叠计算
        query_words = set(query.lower().split())
        para_words = set(paragraph.lower().split())
        
        if not query_words:
            return 0
        
        overlap = len(query_words.intersection(para_words))
        return overlap / len(query_words)
```

#### 2.2 上下文感知
```python
# 新增文件: context_analyzer.py
class ContextAnalyzer:
    def __init__(self):
        self.conversation_history = []
    
    def analyze_query_context(self, current_query: str, history: List[str] = None):
        """分析查询的上下文"""
        if history:
            self.conversation_history = history
        
        # 1. 识别查询类型
        query_type = self._identify_query_type(current_query)
        
        # 2. 提取关键实体
        entities = self._extract_entities(current_query)
        
        # 3. 分析对话意图
        intent = self._analyze_intent(current_query, self.conversation_history)
        
        # 4. 生成增强查询
        enhanced_query = self._enhance_query(current_query, entities, intent)
        
        return {
            'original_query': current_query,
            'enhanced_query': enhanced_query,
            'query_type': query_type,
            'entities': entities,
            'intent': intent,
            'context_keywords': self._extract_context_keywords()
        }
    
    def _identify_query_type(self, query: str) -> str:
        """识别查询类型"""
        question_patterns = {
            'what': ['什么', '是什么', '什么是'],
            'how': ['怎么', '如何', '怎样'],
            'why': ['为什么', '为何'],
            'when': ['什么时候', '何时'],
            'where': ['哪里', '在哪'],
            'who': ['谁', '什么人']
        }
        
        for qtype, patterns in question_patterns.items():
            if any(pattern in query for pattern in patterns):
                return qtype
        
        return 'general'
```

### Phase 3: 知识图谱集成（1个月内完成）

#### 3.1 知识关系建模
```python
# 新增文件: knowledge_graph.py
import networkx as nx
from typing import Dict, List, Tuple

class KnowledgeGraph:
    def __init__(self):
        self.graph = nx.DiGraph()
        self.entity_embeddings = {}
    
    def build_from_notion_data(self, knowledge_items: List[Dict]):
        """从Notion数据构建知识图谱"""
        # 1. 添加知识节点
        for item in knowledge_items:
            self.graph.add_node(
                item['id'],
                title=item['title'],
                category=item['category'],
                keywords=item['keywords'],
                content=item['content']
            )
        
        # 2. 基于关键词建立关系
        self._build_keyword_relations(knowledge_items)
        
        # 3. 基于分类建立关系
        self._build_category_relations(knowledge_items)
        
        # 4. 基于内容相似度建立关系
        self._build_semantic_relations(knowledge_items)
    
    def find_related_knowledge(self, knowledge_id: str, relation_types: List[str] = None, max_depth=2):
        """查找相关知识"""
        if knowledge_id not in self.graph:
            return []
        
        related = []
        
        # 广度优先搜索相关节点
        visited = set()
        queue = [(knowledge_id, 0)]
        
        while queue:
            node_id, depth = queue.pop(0)
            
            if depth >= max_depth or node_id in visited:
                continue
            
            visited.add(node_id)
            
            # 获取邻居节点
            for neighbor in self.graph.neighbors(node_id):
                edge_data = self.graph[node_id][neighbor]
                relation_type = edge_data.get('relation_type')
                
                if relation_types is None or relation_type in relation_types:
                    related.append({
                        'id': neighbor,
                        'relation_type': relation_type,
                        'strength': edge_data.get('strength', 0),
                        'depth': depth + 1
                    })
                    
                    queue.append((neighbor, depth + 1))
        
        # 按关系强度排序
        related.sort(key=lambda x: x['strength'], reverse=True)
        return related[:10]  # 返回前10个最相关的
```

### Phase 4: 大模型集成（2-3个月）

#### 4.1 智能推理增强
```python
# 新增文件: llm_enhanced_rag.py
class LLMEnhancedRAG:
    def __init__(self, llm_handler):
        self.llm = llm_handler
        self.knowledge_db = None
        self.semantic_engine = None
        self.knowledge_graph = None
    
    def intelligent_knowledge_retrieval(self, query: str, context: Dict = None):
        """智能知识检索与推理"""
        # 1. 查询分析和增强
        analyzed_query = self._analyze_and_enhance_query(query, context)
        
        # 2. 多策略知识检索
        knowledge_candidates = self._multi_strategy_retrieval(analyzed_query)
        
        # 3. 知识推理和整合
        integrated_knowledge = self._integrate_and_reason(knowledge_candidates, query)
        
        # 4. 动态上下文生成
        final_context = self._generate_dynamic_context(integrated_knowledge, query)
        
        return final_context
    
    def _analyze_and_enhance_query(self, query: str, context: Dict) -> Dict:
        """使用LLM分析和增强查询"""
        analysis_prompt = f"""
        请分析以下用户查询的意图和关键信息：
        
        查询: {query}
        上下文: {context or '无'}
        
        请提供：
        1. 查询意图分类
        2. 关键实体提取
        3. 可能的相关概念
        4. 建议的搜索关键词
        
        以JSON格式返回结果。
        """
        
        response = self.llm.generate_response(analysis_prompt)
        return self._parse_analysis_response(response)
    
    def _multi_strategy_retrieval(self, analyzed_query: Dict) -> List[Dict]:
        """多策略知识检索"""
        all_results = []
        
        # 策略1: 关键词精确匹配
        keyword_results = self.knowledge_db.search_knowledge_by_keywords(
            analyzed_query['search_keywords']
        )
        all_results.extend([{'source': 'keyword', 'data': r} for r in keyword_results])
        
        # 策略2: 语义相似度搜索
        semantic_results = self.semantic_engine.semantic_search(
            analyzed_query['enhanced_query']
        )
        all_results.extend([{'source': 'semantic', 'data': r} for r in semantic_results])
        
        # 策略3: 知识图谱关系查找
        if analyzed_query.get('entities'):
            graph_results = self._graph_based_search(analyzed_query['entities'])
            all_results.extend([{'source': 'graph', 'data': r} for r in graph_results])
        
        return all_results
    
    def _integrate_and_reason(self, knowledge_candidates: List[Dict], query: str) -> Dict:
        """知识整合和推理"""
        integration_prompt = f"""
        基于以下知识片段，为用户查询提供最相关和准确的信息：
        
        用户查询: {query}
        
        可用知识:
        {self._format_knowledge_for_prompt(knowledge_candidates)}
        
        请：
        1. 筛选最相关的知识片段
        2. 整合互补信息
        3. 解决可能的冲突
        4. 生成结构化的上下文
        
        返回整合后的知识上下文。
        """
        
        integrated_response = self.llm.generate_response(integration_prompt)
        return self._parse_integration_response(integrated_response)
```

---

## 📅 实施时间表

### 第1周：基础增强
```
✅ 安装sentence-transformers
✅ 实现语义搜索基础功能
✅ 集成到现有系统
✅ 本地测试验证
```

### 第2-3周：混合检索
```
🔄 智能片段提取
🔄 上下文感知分析
🔄 多策略结果合并
🔄 云端部署测试
```

### 第4-6周：图谱集成
```
🔄 知识关系建模
🔄 图谱构建算法
🔄 关系推理功能
🔄 可视化管理界面
```

### 第7-12周：LLM增强
```
🔄 查询分析增强
🔄 知识推理集成
🔄 动态上下文生成
🔄 自学习优化机制
```

---

## 🛠️ 技术依赖和部署

### 新增依赖包
```bash
# 核心依赖
pip install sentence-transformers
pip install scikit-learn
pip install numpy
pip install networkx

# 可选增强
pip install faiss-cpu  # 向量索引加速
pip install jieba      # 中文分词
pip install transformers  # 预训练模型支持
```

### 云端部署考虑
```dockerfile
# 更新Dockerfile
FROM python:3.9-slim

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# ... 现有配置 ...

# 新增RAG依赖
COPY requirements_rag.txt .
RUN pip install --no-cache-dir -r requirements_rag.txt

# 预下载模型（可选，减少启动时间）
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('shibing624/text2vec-base-chinese')"
```

### 配置文件扩展
```json
{
  "rag_config": {
    "enable_semantic_search": true,
    "embedding_model": "shibing624/text2vec-base-chinese",
    "similarity_threshold": 0.3,
    "max_semantic_results": 5,
    "enable_knowledge_graph": true,
    "enable_llm_reasoning": false,
    "chunk_size": 300,
    "chunk_overlap": 50
  }
}
```

---

## 🎯 预期效果

### 性能提升目标
```
当前 → 目标

匹配准确率: 70% → 90%
响应相关性: 60% → 85%
上下文质量: 中等 → 优秀
多轮对话: 不支持 → 完全支持
推理能力: 无 → 基础推理
自学习能力: 无 → 持续优化
```

### 用户体验改善
```
✅ 模糊查询也能精准匹配
✅ 支持自然语言描述问题
✅ 多轮对话理解上下文
✅ 自动补充相关知识
✅ 智能推理和解释
```

---

*升级计划版本: v2.0*  
*制定时间: 2025-01-20*  
*预计完成: 2025-04-20* 