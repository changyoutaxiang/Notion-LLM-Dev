"""
高性能语义搜索引擎
专为Notion知识库RAG系统设计，采用最佳性能实践

性能特性：
- BGE/FlagEmbedding高质量中文嵌入模型
- FAISS高速向量索引
- 多级缓存策略（内存+磁盘）
- GPU加速支持
- 批量处理优化
- 异步操作支持
"""

import os
import json
import time
import pickle
import hashlib
import logging
from typing import List, Dict, Tuple, Optional, Union
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import torch
import faiss
from sentence_transformers import SentenceTransformer
from FlagEmbedding import BGEM3FlagModel
import psutil
from diskcache import Cache
from loguru import logger

@dataclass
class SearchResult:
    """搜索结果数据结构"""
    knowledge_id: str
    title: str
    content_snippet: str
    similarity_score: float
    source_type: str  # 'semantic', 'keyword', 'hybrid'
    metadata: Dict
    full_content: str = ""

@dataclass
class SearchConfig:
    """搜索配置"""
    # 模型配置
    embedding_model: str = "BAAI/bge-large-zh-v1.5"  # 高性能中文模型
    device: str = "auto"  # auto/cpu/cuda
    max_seq_length: int = 512
    batch_size: int = 32
    
    # 搜索配置
    similarity_threshold: float = 0.3
    max_results: int = 10
    chunk_size: int = 300
    chunk_overlap: int = 50
    
    # 性能配置
    enable_gpu: bool = True
    enable_cache: bool = True
    cache_ttl_hours: int = 24
    enable_batch_processing: bool = True
    
    # 索引配置
    index_type: str = "auto"  # "flat", "ivf", "hnsw", "auto"
    nlist: int = 100  # IVF参数
    efConstruction: int = 200  # HNSW参数
    M: int = 16  # HNSW参数

class HighPerformanceSemanticSearch:
    """高性能语义搜索引擎"""
    
    def __init__(self, config: SearchConfig, cache_dir: str = "./cache"):
        self.config = config
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        # 初始化组件
        self.model = None
        self.index = None
        self.knowledge_items = []
        self.id_mapping = {}
        
        # 缓存系统
        if config.enable_cache:
            self.disk_cache = Cache(str(self.cache_dir / "embeddings"))
            self.result_cache = Cache(str(self.cache_dir / "results"))
        else:
            self.disk_cache = None
            self.result_cache = None
        
        # 性能监控
        self.stats = {
            "total_searches": 0,
            "cache_hits": 0,
            "avg_search_time": 0.0,
            "index_size": 0
        }
        
        logger.info(f"🚀 初始化高性能语义搜索引擎")
        logger.info(f"📊 设备: {self._get_device()}")
        logger.info(f"💾 缓存目录: {cache_dir}")
    
    def _get_device(self) -> str:
        """智能设备选择"""
        if self.config.device == "auto":
            if torch.cuda.is_available() and self.config.enable_gpu:
                device = "cuda"
                logger.info(f"🎮 检测到GPU: {torch.cuda.get_device_name()}")
            else:
                device = "cpu"
                logger.info(f"💻 使用CPU: {psutil.cpu_count()}核")
        else:
            device = self.config.device
        
        return device
    
    def initialize_model(self) -> bool:
        """初始化嵌入模型"""
        try:
            device = self._get_device()
            
            logger.info(f"📥 加载嵌入模型: {self.config.embedding_model}")
            start_time = time.time()
            
            # 优先使用BGE模型（更高性能）
            if "bge" in self.config.embedding_model.lower():
                self.model = BGEM3FlagModel(
                    self.config.embedding_model,
                    use_fp16=True if device == "cuda" else False,
                    device=device
                )
                self.model_type = "bge"
                logger.info("🎯 使用BGE高性能模型")
            else:
                # 备选：sentence-transformers
                self.model = SentenceTransformer(
                    self.config.embedding_model,
                    device=device
                )
                self.model_type = "sentence_transformer"
                logger.info("📝 使用Sentence-Transformer模型")
            
            load_time = time.time() - start_time
            logger.success(f"✅ 模型加载完成，耗时: {load_time:.2f}秒")
            
            # 预热模型
            self._warmup_model()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 模型初始化失败: {e}")
            return False
    
    def _warmup_model(self):
        """模型预热，优化首次查询性能"""
        logger.info("🔥 模型预热中...")
        dummy_texts = ["测试文本预热", "模型性能优化", "向量计算预处理"]
        
        start_time = time.time()
        _ = self.get_embeddings(dummy_texts)
        warmup_time = time.time() - start_time
        
        logger.success(f"✅ 模型预热完成，耗时: {warmup_time:.2f}秒")
    
    def get_embeddings(self, texts: Union[str, List[str]], show_progress: bool = False) -> np.ndarray:
        """获取文本嵌入向量（支持批量处理）"""
        if isinstance(texts, str):
            texts = [texts]
        
        # 检查缓存
        cached_embeddings = []
        uncached_texts = []
        uncached_indices = []
        
        if self.disk_cache:
            for i, text in enumerate(texts):
                text_hash = hashlib.md5(text.encode()).hexdigest()
                cached = self.disk_cache.get(f"emb_{text_hash}")
                if cached is not None:
                    cached_embeddings.append((i, cached))
                else:
                    uncached_texts.append(text)
                    uncached_indices.append(i)
        else:
            uncached_texts = texts
            uncached_indices = list(range(len(texts)))
        
        # 计算未缓存的嵌入
        all_embeddings = [None] * len(texts)
        
        # 填充缓存的结果
        for i, emb in cached_embeddings:
            all_embeddings[i] = emb
            self.stats["cache_hits"] += 1
        
        # 批量计算未缓存的嵌入
        if uncached_texts:
            try:
                if self.model_type == "bge":
                    # BGE模型批量处理
                    if self.config.enable_batch_processing and len(uncached_texts) > 1:
                        new_embeddings = self.model.encode(
                            uncached_texts,
                            batch_size=self.config.batch_size,
                            max_length=self.config.max_seq_length
                        )['dense_vecs']
                    else:
                        new_embeddings = []
                        for text in uncached_texts:
                            emb = self.model.encode([text])['dense_vecs'][0]
                            new_embeddings.append(emb)
                        new_embeddings = np.array(new_embeddings)
                else:
                    # Sentence-Transformer批量处理
                    new_embeddings = self.model.encode(
                        uncached_texts,
                        batch_size=self.config.batch_size,
                        show_progress_bar=show_progress,
                        convert_to_numpy=True
                    )
                
                # 填充新计算的结果并缓存
                for i, emb in zip(uncached_indices, new_embeddings):
                    all_embeddings[i] = emb
                    
                    # 缓存结果
                    if self.disk_cache:
                        text_hash = hashlib.md5(texts[i].encode()).hexdigest()
                        self.disk_cache.set(
                            f"emb_{text_hash}", 
                            emb, 
                            expire=self.config.cache_ttl_hours * 3600
                        )
                
            except Exception as e:
                logger.error(f"❌ 嵌入计算失败: {e}")
                raise
        
        result = np.array([emb for emb in all_embeddings if emb is not None])
        return result
    
    def build_index(self, knowledge_items: List[Dict], force_rebuild: bool = False) -> bool:
        """构建高性能FAISS索引"""
        try:
            index_cache_path = self.cache_dir / "faiss_index.pkl"
            metadata_cache_path = self.cache_dir / "index_metadata.json"
            
            # 检查是否可以加载缓存的索引
            if not force_rebuild and index_cache_path.exists() and metadata_cache_path.exists():
                try:
                    logger.info("📥 尝试加载缓存的索引...")
                    with open(metadata_cache_path, 'r', encoding='utf-8') as f:
                        cached_metadata = json.load(f)
                    
                    # 验证数据一致性
                    if cached_metadata.get("total_items") == len(knowledge_items):
                        with open(index_cache_path, 'rb') as f:
                            cache_data = pickle.load(f)
                        
                        self.index = cache_data["index"]
                        self.knowledge_items = cache_data["knowledge_items"]
                        self.id_mapping = cache_data["id_mapping"]
                        
                        logger.success("✅ 成功加载缓存索引")
                        return True
                except Exception as e:
                    logger.warning(f"⚠️ 加载缓存索引失败，重新构建: {e}")
            
            # 构建新索引
            logger.info(f"🏗️ 构建FAISS索引，知识条目数: {len(knowledge_items)}")
            start_time = time.time()
            
            # 准备文本数据
            texts = []
            self.knowledge_items = knowledge_items
            self.id_mapping = {}
            
            for i, item in enumerate(knowledge_items):
                # 组合标题和内容进行嵌入
                title = item.get('title', '')
                content = item.get('content', item.get('full_content', ''))
                combined_text = f"{title}\n{content}"
                texts.append(combined_text)
                self.id_mapping[i] = item.get('id', str(i))
            
            # 批量计算嵌入向量
            logger.info("🔢 计算嵌入向量...")
            embeddings = self.get_embeddings(texts, show_progress=True)
            
            # 选择合适的索引类型
            dimension = embeddings.shape[1]
            num_vectors = embeddings.shape[0]
            
            logger.info(f"📊 向量维度: {dimension}, 向量数量: {num_vectors}")
            
            if self.config.index_type == "auto":
                if num_vectors < 1000:
                    index_type = "flat"
                elif num_vectors < 10000:
                    index_type = "ivf"
                else:
                    index_type = "hnsw"
            else:
                index_type = self.config.index_type
            
            # 创建FAISS索引
            if index_type == "flat":
                # 精确搜索，小数据集最佳
                self.index = faiss.IndexFlatIP(dimension)
                logger.info("🎯 使用精确搜索索引(Flat)")
                
            elif index_type == "ivf":
                # 近似搜索，中等数据集
                nlist = min(self.config.nlist, num_vectors // 10)
                quantizer = faiss.IndexFlatIP(dimension)
                self.index = faiss.IndexIVFFlat(quantizer, dimension, nlist)
                self.index.train(embeddings.astype(np.float32))
                logger.info(f"⚡ 使用IVF索引，聚类数: {nlist}")
                
            elif index_type == "hnsw":
                # HNSW索引，大数据集高性能
                self.index = faiss.IndexHNSWFlat(dimension, self.config.M)
                self.index.hnsw.efConstruction = self.config.efConstruction
                logger.info(f"🚀 使用HNSW索引，M: {self.config.M}, efConstruction: {self.config.efConstruction}")
            
            # 添加向量到索引
            logger.info("📥 添加向量到索引...")
            self.index.add(embeddings.astype(np.float32))
            
            # 缓存索引
            cache_data = {
                "index": self.index,
                "knowledge_items": self.knowledge_items,
                "id_mapping": self.id_mapping
            }
            
            with open(index_cache_path, 'wb') as f:
                pickle.dump(cache_data, f)
            
            metadata = {
                "total_items": len(knowledge_items),
                "dimension": dimension,
                "index_type": index_type,
                "build_time": time.time()
            }
            
            with open(metadata_cache_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            build_time = time.time() - start_time
            self.stats["index_size"] = num_vectors
            
            logger.success(f"✅ 索引构建完成！")
            logger.info(f"⏱️ 构建耗时: {build_time:.2f}秒")
            logger.info(f"📊 索引类型: {index_type}")
            logger.info(f"💾 索引大小: {num_vectors} 向量")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 索引构建失败: {e}")
            return False
    
    def search(self, query: str, top_k: int = None, threshold: float = None) -> List[SearchResult]:
        """高性能语义搜索"""
        if not self.model or not self.index:
            logger.error("❌ 模型或索引未初始化")
            return []
        
        top_k = top_k or self.config.max_results
        threshold = threshold or self.config.similarity_threshold
        
        start_time = time.time()
        
        try:
            # 检查查询结果缓存
            query_hash = hashlib.md5(f"{query}_{top_k}_{threshold}".encode()).hexdigest()
            
            if self.result_cache:
                cached_result = self.result_cache.get(f"search_{query_hash}")
                if cached_result:
                    self.stats["cache_hits"] += 1
                    logger.info(f"💨 缓存命中，查询: '{query[:30]}...'")
                    return cached_result
            
            # 计算查询向量
            query_embedding = self.get_embeddings([query])[0]
            
            # 执行向量搜索
            scores, indices = self.index.search(
                query_embedding.reshape(1, -1).astype(np.float32), 
                top_k * 2  # 搜索更多结果后筛选
            )
            
            # 处理搜索结果
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx == -1 or score < threshold:
                    continue
                
                knowledge_item = self.knowledge_items[idx]
                knowledge_id = self.id_mapping.get(idx, str(idx))
                
                # 提取相关片段
                content_snippet = self._extract_relevant_snippet(
                    knowledge_item.get('content', ''),
                    query,
                    max_length=self.config.chunk_size
                )
                
                result = SearchResult(
                    knowledge_id=knowledge_id,
                    title=knowledge_item.get('title', ''),
                    content_snippet=content_snippet,
                    similarity_score=float(score),
                    source_type='semantic',
                    metadata={
                        'index': int(idx),
                        'search_time': time.time() - start_time,
                        'model': self.config.embedding_model
                    },
                    full_content=knowledge_item.get('content', '')
                )
                results.append(result)
            
            # 限制最终结果数量
            results = results[:top_k]
            
            # 缓存结果
            if self.result_cache:
                self.result_cache.set(
                    f"search_{query_hash}",
                    results,
                    expire=self.config.cache_ttl_hours * 3600
                )
            
            # 更新统计
            self.stats["total_searches"] += 1
            search_time = time.time() - start_time
            self.stats["avg_search_time"] = (
                (self.stats["avg_search_time"] * (self.stats["total_searches"] - 1) + search_time) /
                self.stats["total_searches"]
            )
            
            logger.info(f"🔍 语义搜索完成: '{query[:30]}...' → {len(results)}个结果，耗时: {search_time:.3f}秒")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ 搜索失败: {e}")
            return []
    
    def _extract_relevant_snippet(self, content: str, query: str, max_length: int = 300) -> str:
        """提取最相关的内容片段"""
        if not content or len(content) <= max_length:
            return content
        
        # 简单实现：查找包含查询词的段落
        sentences = content.split('。')
        best_sentence = ""
        max_score = 0
        
        query_words = set(query.lower().split())
        
        for sentence in sentences:
            if len(sentence.strip()) < 10:
                continue
                
            sentence_words = set(sentence.lower().split())
            score = len(query_words & sentence_words)
            
            if score > max_score:
                max_score = score
                best_sentence = sentence
        
        if best_sentence:
            # 扩展上下文
            start_idx = max(0, content.find(best_sentence) - 50)
            end_idx = min(len(content), start_idx + max_length)
            return content[start_idx:end_idx]
        
        # 回退：返回开头部分
        return content[:max_length]
    
    def get_stats(self) -> Dict:
        """获取性能统计信息"""
        return {
            **self.stats,
            "cache_hit_rate": self.stats["cache_hits"] / max(1, self.stats["total_searches"]),
            "memory_usage_mb": psutil.Process().memory_info().rss / 1024 / 1024
        }
    
    def clear_cache(self):
        """清理缓存"""
        if self.disk_cache:
            self.disk_cache.clear()
        if self.result_cache:
            self.result_cache.clear()
        logger.info("🧹 缓存已清理")

# 工厂函数
def create_semantic_search_engine(config_dict: Dict) -> HighPerformanceSemanticSearch:
    """创建语义搜索引擎实例"""
    config = SearchConfig(**config_dict)
    engine = HighPerformanceSemanticSearch(config)
    
    if not engine.initialize_model():
        raise RuntimeError("语义搜索引擎初始化失败")
    
    return engine 