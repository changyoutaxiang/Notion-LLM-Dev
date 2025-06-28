"""
混合检索引擎
整合关键词精确匹配和语义相似度搜索，提供最佳检索体验

特性：
- 多策略融合（关键词 + 语义 + 权重排序）
- 智能结果排序和去重
- 自适应搜索策略
- 结果质量评估
"""

import time
import hashlib
from typing import List, Dict, Tuple, Optional, Union
from dataclasses import dataclass, asdict
from collections import defaultdict

import numpy as np
from loguru import logger

from semantic_search import HighPerformanceSemanticSearch, SearchResult, SearchConfig
from notion_knowledge_db import NotionKnowledgeDB

@dataclass
class HybridSearchConfig:
    """混合搜索配置"""
    # 策略权重
    keyword_weight: float = 0.3
    semantic_weight: float = 0.5
    
    # 融合参数
    fusion_method: str = "weighted_sum"  # weighted_sum, rrf, cascade
    max_results_per_strategy: int = 10
    final_top_k: int = 5
    
    # 排序权重
    similarity_weight: float = 0.4
    priority_weight: float = 0.2
    frequency_weight: float = 0.2
    recency_weight: float = 0.1
    authority_weight: float = 0.1
    
    # 质量控制
    min_similarity_threshold: float = 0.2
    enable_deduplication: bool = True
    enable_reranking: bool = True

@dataclass
class QueryAnalysis:
    """查询分析结果"""
    original_query: str
    processed_keywords: List[str]
    query_type: str  # informational, navigational, transactional
    complexity: str  # simple, medium, complex
    requires_semantic: bool = True
    requires_keyword: bool = True

class SmartQueryAnalyzer:
    """智能查询分析器"""
    
    def __init__(self):
        # 查询模式
        self.patterns = {
            'question_words': ['什么', '怎么', '如何', '为什么', '哪里', '哪个', '谁', '何时'],
            'navigation_words': ['打开', '找到', '查看', '进入', '访问'],
            'action_words': ['创建', '删除', '修改', '更新', '配置', '设置']
        }
    
    def analyze(self, query: str) -> QueryAnalysis:
        """分析查询意图和特征"""
        query = query.strip()
        
        # 提取关键词
        keywords = self._extract_keywords(query)
        
        # 分析查询类型
        query_type = self._classify_query_type(query)
        
        # 分析复杂度
        complexity = self._analyze_complexity(query)
        
        # 决定搜索策略
        requires_semantic = len(query) > 5 or any(word in query for word in self.patterns['question_words'])
        requires_keyword = len(keywords) > 0
        
        return QueryAnalysis(
            original_query=query,
            processed_keywords=keywords,
            query_type=query_type,
            complexity=complexity,
            requires_semantic=requires_semantic,
            requires_keyword=requires_keyword
        )
    
    def _extract_keywords(self, query: str) -> List[str]:
        """提取关键词"""
        import jieba
        
        # 使用jieba分词
        words = list(jieba.cut(query))
        
        # 过滤停用词和短词
        stop_words = {'的', '是', '在', '有', '和', '与', '及', '或', '也', '了', '就', '都', '要', '能', '会'}
        keywords = [word.strip() for word in words 
                   if len(word.strip()) > 1 and word.strip() not in stop_words]
        
        return keywords
    
    def _classify_query_type(self, query: str) -> str:
        """分类查询类型"""
        if any(word in query for word in self.patterns['question_words']):
            return "informational"
        elif any(word in query for word in self.patterns['navigation_words']):
            return "navigational"  
        elif any(word in query for word in self.patterns['action_words']):
            return "transactional"
        else:
            return "informational"
    
    def _analyze_complexity(self, query: str) -> str:
        """分析查询复杂度"""
        if len(query) < 10:
            return "simple"
        elif len(query) < 30:
            return "medium"
        else:
            return "complex"

class ResultFusion:
    """结果融合器"""
    
    def __init__(self, config: HybridSearchConfig):
        self.config = config
    
    def fuse_results(self, 
                    keyword_results: List[SearchResult],
                    semantic_results: List[SearchResult]) -> List[SearchResult]:
        """融合多策略搜索结果"""
        
        if self.config.fusion_method == "weighted_sum":
            return self._weighted_sum_fusion(keyword_results, semantic_results)
        elif self.config.fusion_method == "rrf":
            return self._reciprocal_rank_fusion(keyword_results, semantic_results)
        elif self.config.fusion_method == "cascade":
            return self._cascade_fusion(keyword_results, semantic_results)
        else:
            # 默认：简单合并
            return self._simple_merge(keyword_results, semantic_results)
    
    def _weighted_sum_fusion(self, 
                           keyword_results: List[SearchResult],
                           semantic_results: List[SearchResult]) -> List[SearchResult]:
        """加权求和融合"""
        
        # 创建结果字典
        result_dict = {}
        
        # 处理关键词结果
        for i, result in enumerate(keyword_results):
            key = result.knowledge_id
            score = (1.0 - i / len(keyword_results)) * self.config.keyword_weight
            
            if key not in result_dict:
                result_dict[key] = result
                result_dict[key].similarity_score = score
                result_dict[key].source_type = "keyword"
            else:
                result_dict[key].similarity_score += score
                result_dict[key].source_type = "hybrid"
        
        # 处理语义结果
        for i, result in enumerate(semantic_results):
            key = result.knowledge_id
            score = result.similarity_score * self.config.semantic_weight
            
            if key not in result_dict:
                result_dict[key] = result
                result_dict[key].similarity_score = score
                result_dict[key].source_type = "semantic"
            else:
                result_dict[key].similarity_score += score
                result_dict[key].source_type = "hybrid"
        
        # 排序并返回
        fused_results = list(result_dict.values())
        fused_results.sort(key=lambda x: x.similarity_score, reverse=True)
        
        return fused_results[:self.config.final_top_k]
    
    def _reciprocal_rank_fusion(self,
                              keyword_results: List[SearchResult],
                              semantic_results: List[SearchResult]) -> List[SearchResult]:
        """倒数排名融合（RRF）"""
        
        result_scores = defaultdict(float)
        result_items = {}
        k = 60  # RRF参数
        
        # 关键词结果RRF
        for rank, result in enumerate(keyword_results, 1):
            key = result.knowledge_id
            result_scores[key] += self.config.keyword_weight / (k + rank)
            if key not in result_items:
                result_items[key] = result
                result_items[key].source_type = "keyword"
            else:
                result_items[key].source_type = "hybrid"
        
        # 语义结果RRF
        for rank, result in enumerate(semantic_results, 1):
            key = result.knowledge_id
            result_scores[key] += self.config.semantic_weight / (k + rank)
            if key not in result_items:
                result_items[key] = result
                result_items[key].source_type = "semantic"
            else:
                result_items[key].source_type = "hybrid"
        
        # 更新分数并排序
        for key, score in result_scores.items():
            result_items[key].similarity_score = score
        
        fused_results = list(result_items.values())
        fused_results.sort(key=lambda x: x.similarity_score, reverse=True)
        
        return fused_results[:self.config.final_top_k]
    
    def _cascade_fusion(self,
                       keyword_results: List[SearchResult],
                       semantic_results: List[SearchResult]) -> List[SearchResult]:
        """级联融合：优先关键词，不足时补充语义"""
        
        result_dict = {}
        
        # 优先添加关键词结果
        for result in keyword_results:
            key = result.knowledge_id
            result_dict[key] = result
            result_dict[key].source_type = "keyword"
        
        # 补充语义结果
        for result in semantic_results:
            key = result.knowledge_id
            if key not in result_dict:
                result_dict[key] = result
                result_dict[key].source_type = "semantic"
        
        # 按原始分数排序
        fused_results = list(result_dict.values())
        fused_results.sort(key=lambda x: x.similarity_score, reverse=True)
        
        return fused_results[:self.config.final_top_k]
    
    def _simple_merge(self,
                     keyword_results: List[SearchResult],
                     semantic_results: List[SearchResult]) -> List[SearchResult]:
        """简单合并去重"""
        
        seen_ids = set()
        merged_results = []
        
        # 先添加关键词结果
        for result in keyword_results:
            if result.knowledge_id not in seen_ids:
                seen_ids.add(result.knowledge_id)
                merged_results.append(result)
        
        # 再添加语义结果
        for result in semantic_results:
            if result.knowledge_id not in seen_ids:
                seen_ids.add(result.knowledge_id)
                merged_results.append(result)
        
        return merged_results[:self.config.final_top_k]

class AdvancedRanking:
    """高级排序算法"""
    
    def __init__(self, config: HybridSearchConfig):
        self.config = config
    
    def rerank_results(self, results: List[SearchResult], 
                      knowledge_db: NotionKnowledgeDB) -> List[SearchResult]:
        """重新排序结果"""
        
        if not self.config.enable_reranking or not results:
            return results
        
        try:
            # 获取额外的排序特征
            enhanced_results = []
            
            for result in results:
                enhanced_result = self._enhance_result_features(result, knowledge_db)
                enhanced_results.append(enhanced_result)
            
            # 计算综合分数
            for result in enhanced_results:
                composite_score = self._calculate_composite_score(result)
                result.similarity_score = composite_score
            
            # 按综合分数排序
            enhanced_results.sort(key=lambda x: x.similarity_score, reverse=True)
            
            logger.info(f"🔄 重新排序完成，调整了 {len(enhanced_results)} 个结果")
            
            return enhanced_results
            
        except Exception as e:
            logger.warning(f"⚠️ 重新排序失败，使用原始排序: {e}")
            return results
    
    def _enhance_result_features(self, result: SearchResult, 
                               knowledge_db: NotionKnowledgeDB) -> SearchResult:
        """增强结果特征"""
        
        # 这里可以从Notion获取额外信息
        # 比如优先级、使用频率、最后更新时间等
        
        # 为简化实现，使用默认值
        result.metadata.update({
            'priority_score': 0.5,  # 可以从Notion优先级字段获取
            'frequency_score': 0.5,  # 可以从使用频率字段获取
            'recency_score': 0.5,   # 可以从更新时间计算
            'authority_score': 0.5   # 可以从知识权威性评估
        })
        
        return result
    
    def _calculate_composite_score(self, result: SearchResult) -> float:
        """计算综合分数"""
        
        similarity_score = result.similarity_score
        priority_score = result.metadata.get('priority_score', 0.5)
        frequency_score = result.metadata.get('frequency_score', 0.5)
        recency_score = result.metadata.get('recency_score', 0.5)
        authority_score = result.metadata.get('authority_score', 0.5)
        
        composite_score = (
            similarity_score * self.config.similarity_weight +
            priority_score * self.config.priority_weight +
            frequency_score * self.config.frequency_weight +
            recency_score * self.config.recency_weight +
            authority_score * self.config.authority_weight
        )
        
        return composite_score

class HybridRetrievalEngine:
    """混合检索引擎主类"""
    
    def __init__(self, knowledge_db: NotionKnowledgeDB, config: Dict):
        self.knowledge_db = knowledge_db
        self.hybrid_config = HybridSearchConfig(**config.get('hybrid_search', {}))
        
        # 初始化组件
        self.query_analyzer = SmartQueryAnalyzer()
        self.result_fusion = ResultFusion(self.hybrid_config)
        self.advanced_ranking = AdvancedRanking(self.hybrid_config)
        
        # 语义搜索引擎
        self.semantic_engine = None
        self._initialize_semantic_engine(config)
        
        # 性能统计
        self.stats = {
            "total_searches": 0,
            "keyword_only": 0,
            "semantic_only": 0,
            "hybrid_searches": 0,
            "avg_response_time": 0.0
        }
        
        logger.info("🚀 混合检索引擎初始化完成")
    
    def _initialize_semantic_engine(self, config: Dict):
        """初始化语义搜索引擎"""
        try:
            if config.get('knowledge_search', {}).get('rag_system', {}).get('enabled', False):
                embedding_config = config['knowledge_search']['rag_system']['embedding']
                
                # 映射配置参数（处理参数名不匹配）
                search_config_params = {
                    'embedding_model': embedding_config.get('model_name', 'BAAI/bge-large-zh-v1.5'),
                    'device': embedding_config.get('device', 'auto'),
                    'max_seq_length': embedding_config.get('max_seq_length', 512),
                    'batch_size': embedding_config.get('batch_size', 32),
                    'enable_gpu': embedding_config.get('enable_gpu', True),
                    'similarity_threshold': config['knowledge_search']['rag_system']['search'].get('similarity_threshold', 0.3),
                    'max_results': config['knowledge_search']['rag_system']['search'].get('max_results', 10),
                    'chunk_size': config['knowledge_search']['rag_system']['search'].get('chunk_size', 300),
                    'chunk_overlap': config['knowledge_search']['rag_system']['search'].get('chunk_overlap', 50),
                    'enable_cache': config['knowledge_search']['rag_system']['search'].get('enable_caching', True),
                    'cache_ttl_hours': config['knowledge_search']['rag_system']['search'].get('cache_ttl_hours', 24),
                    'enable_batch_processing': config['knowledge_search']['rag_system']['search'].get('enable_batch_processing', True)
                }
                
                search_config = SearchConfig(**search_config_params)
                self.semantic_engine = HighPerformanceSemanticSearch(search_config)
                
                if not self.semantic_engine.initialize_model():
                    logger.error("❌ 语义搜索引擎初始化失败")
                    self.semantic_engine = None
                else:
                    logger.success("✅ 语义搜索引擎就绪")
        except Exception as e:
            logger.error(f"❌ 语义搜索引擎初始化失败: {e}")
            self.semantic_engine = None
    
    def build_semantic_index(self, force_rebuild: bool = False) -> bool:
        """构建语义索引"""
        if not self.semantic_engine:
            logger.warning("⚠️ 语义搜索引擎未启用")
            return False
        
        try:
            # 从Notion获取所有知识条目
            logger.info("📥 从Notion获取知识库数据...")
            
            # 这里需要实现从NotionKnowledgeDB获取所有条目的方法
            # 暂时使用模拟数据
            knowledge_items = self._get_all_knowledge_items()
            
            if not knowledge_items:
                logger.warning("⚠️ 未找到知识条目")
                return False
            
            # 构建语义索引
            return self.semantic_engine.build_index(knowledge_items, force_rebuild)
            
        except Exception as e:
            logger.error(f"❌ 构建语义索引失败: {e}")
            return False
    
    def _get_all_knowledge_items(self) -> List[Dict]:
        """获取所有知识条目"""
        try:
            if self.knowledge_db:
                return self.knowledge_db.get_all_knowledge_items()
            else:
                logger.warning("⚠️  NotionKnowledgeDB未初始化")
                return []
        except Exception as e:
            logger.error(f"❌ 获取知识条目失败: {e}")
            return []
    
    def intelligent_search(self, query: str, max_results: int = 5) -> List[SearchResult]:
        """智能搜索主入口"""
        start_time = time.time()
        
        try:
            # 分析查询
            query_analysis = self.query_analyzer.analyze(query)
            logger.info(f"🔍 查询分析: {query_analysis.query_type}, 复杂度: {query_analysis.complexity}")
            
            # 决定搜索策略
            keyword_results = []
            semantic_results = []
            
            # 关键词搜索
            if query_analysis.requires_keyword and query_analysis.processed_keywords:
                keyword_results = self._keyword_search(query_analysis.processed_keywords)
                logger.info(f"📝 关键词搜索: {len(keyword_results)} 个结果")
            
            # 语义搜索
            if query_analysis.requires_semantic and self.semantic_engine:
                semantic_results = self._semantic_search(query, max_results)
                logger.info(f"🧠 语义搜索: {len(semantic_results)} 个结果")
            
            # 融合结果
            if keyword_results and semantic_results:
                fused_results = self.result_fusion.fuse_results(keyword_results, semantic_results)
                self.stats["hybrid_searches"] += 1
                logger.info("🔀 混合搜索完成")
            elif keyword_results:
                fused_results = keyword_results[:max_results]
                self.stats["keyword_only"] += 1
                logger.info("📝 仅关键词搜索")
            elif semantic_results:
                fused_results = semantic_results[:max_results]
                self.stats["semantic_only"] += 1
                logger.info("🧠 仅语义搜索")
            else:
                fused_results = []
                logger.warning("❌ 未找到相关结果")
            
            # 高级排序
            if fused_results:
                fused_results = self.advanced_ranking.rerank_results(fused_results, self.knowledge_db)
            
            # 去重处理
            if self.hybrid_config.enable_deduplication:
                fused_results = self._deduplicate_results(fused_results)
            
            # 更新统计
            self.stats["total_searches"] += 1
            search_time = time.time() - start_time
            self.stats["avg_response_time"] = (
                (self.stats["avg_response_time"] * (self.stats["total_searches"] - 1) + search_time) /
                self.stats["total_searches"]
            )
            
            logger.success(f"✅ 智能搜索完成: '{query}' → {len(fused_results)} 个结果，耗时: {search_time:.3f}秒")
            
            return fused_results
            
        except Exception as e:
            logger.error(f"❌ 智能搜索失败: {e}")
            return []
    
    def _keyword_search(self, keywords: List[str]) -> List[SearchResult]:
        """关键词搜索"""
        try:
            # 使用现有的NotionKnowledgeDB搜索
            notion_results = self.knowledge_db.search_knowledge_by_keywords(keywords)
            
            # 转换为SearchResult格式
            search_results = []
            for i, item in enumerate(notion_results):
                result = SearchResult(
                    knowledge_id=item.get('id', str(i)),
                    title=item.get('title', ''),
                    content_snippet=item.get('content', '')[:300],
                    similarity_score=1.0 - (i * 0.1),  # 简单递减分数
                    source_type='keyword',
                    metadata={'rank': i + 1},
                    full_content=item.get('content', '')
                )
                search_results.append(result)
            
            return search_results[:self.hybrid_config.max_results_per_strategy]
            
        except Exception as e:
            logger.error(f"❌ 关键词搜索失败: {e}")
            return []
    
    def _semantic_search(self, query: str, max_results: int) -> List[SearchResult]:
        """语义搜索"""
        if not self.semantic_engine:
            return []
        
        try:
            return self.semantic_engine.search(
                query,
                top_k=min(max_results, self.hybrid_config.max_results_per_strategy)
            )
        except Exception as e:
            logger.error(f"❌ 语义搜索失败: {e}")
            return []
    
    def _deduplicate_results(self, results: List[SearchResult]) -> List[SearchResult]:
        """去重处理"""
        seen_ids = set()
        unique_results = []
        
        for result in results:
            if result.knowledge_id not in seen_ids:
                seen_ids.add(result.knowledge_id)
                unique_results.append(result)
        
        if len(unique_results) < len(results):
            logger.info(f"🧹 去重处理: {len(results)} → {len(unique_results)} 个结果")
        
        return unique_results
    
    def get_search_stats(self) -> Dict:
        """获取搜索统计信息"""
        total = self.stats["total_searches"]
        if total == 0:
            return self.stats
        
        return {
            **self.stats,
            "keyword_ratio": self.stats["keyword_only"] / total,
            "semantic_ratio": self.stats["semantic_only"] / total,
            "hybrid_ratio": self.stats["hybrid_searches"] / total
        }

# 创建混合检索引擎的工厂函数
def create_hybrid_retrieval_engine(knowledge_db: NotionKnowledgeDB, config: Dict) -> HybridRetrievalEngine:
    """创建混合检索引擎实例"""
    return HybridRetrievalEngine(knowledge_db, config) 