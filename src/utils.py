# src/utils.py

import os

from src.config import CACHE_DIR, DATA_DIR, VECTOR_STORES_DIR


def create_project_directories(project_name: str):
    """
    Tạo cấu trúc thư mục cần thiết cho một dự án cụ thể.
    """
    project_data_path = os.path.join(DATA_DIR, project_name)
    project_pipeline_cache_path = os.path.join(CACHE_DIR, f"{project_name}_pipeline_cache")
    project_vector_store_path = os.path.join(VECTOR_STORES_DIR, f"{project_name}_vector_store")

    os.makedirs(project_data_path, exist_ok=True)
    os.makedirs(project_pipeline_cache_path, exist_ok=True)
    os.makedirs(project_vector_store_path, exist_ok=True)

def get_project_paths(project_name: str):
    """
    Trả về các đường dẫn liên quan đến một dự án.
    """
    return {
        "data": os.path.join(DATA_DIR, project_name),
        "pipeline_cache": os.path.join(CACHE_DIR, f"{project_name}_pipeline_cache"),
        "vector_store": os.path.join(VECTOR_STORES_DIR, f"{project_name}_vector_store"),
    }