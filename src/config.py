# src/config.py

import os

# Cấu hình đường dẫn gốc
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # Thư mục gốc của dự án

# Đường dẫn dữ liệu và lưu trữ
DATA_DIR = os.path.join(BASE_DIR, "data")
CACHE_DIR = os.path.join(BASE_DIR, "cache")
VECTOR_STORES_DIR = os.path.join(BASE_DIR, "vector_stores")

# Cấu hình mô hình
EMBED_MODEL_NAME = "BAAI/bge-small-en-v1.5"
RERANK_MODEL_NAME = "cross-encoder/ms-marco-TinyBERT-L-2"
RERANK_TOP_N = 10 # Số lượng node giữ lại sau rerank
RETRIEVAL_TOP_K = 10 # Số lượng node ban đầu lấy ra trước khi rerank

# Cấu hình Node Parser (SentenceSplitter)
CHUNK_SIZE = 1024
CHUNK_OVERLAP = 20