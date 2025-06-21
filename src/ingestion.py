# src/ingestion.py

import os

from llama_index.core import (SimpleDirectoryReader, StorageContext,
                              VectorStoreIndex, load_index_from_storage,
                              load_indices_from_storage)
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.storage.docstore import SimpleDocumentStore
from llama_index.core.storage.index_store import SimpleIndexStore
from llama_index.core.vector_stores import SimpleVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

from src.config import CHUNK_OVERLAP, CHUNK_SIZE, EMBED_MODEL_NAME
from src.utils import get_project_paths

# Khởi tạo embedding model (sẽ được sử dụng xuyên suốt)
# Đặt biến global hoặc truyền vào hàm để tránh khởi tạo lại nhiều lần
embedding_model = HuggingFaceEmbedding(model_name=EMBED_MODEL_NAME)

def ingest_documents_for_project(project_id: str, project_name: str):
    """
    Thực hiện quá trình ingest tài liệu cho một dự án cụ thể,
    sử dụng cache cho pipeline và lưu trữ vector store riêng.
    """
    project_paths = get_project_paths(project_name)
    data_path = project_paths["data"]
    pipeline_cache_path = project_paths["pipeline_cache"]
    vector_store_path = project_paths["vector_store"]

    if not os.path.exists(data_path) or not os.listdir(data_path):
        print(f"Không tìm thấy tài liệu trong '{data_path}' cho dự án '{project_name}'. Bỏ qua quá trình ingest.")
        return None

    # 1. Khởi tạo Ingestion Pipeline
    pipeline = IngestionPipeline(
        transformations=[
            SentenceSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP),
            embedding_model,
        ]
    )

    # 2. Thử tải trạng thái pipeline từ cache
    try:
        pipeline.load(pipeline_cache_path)
        print(f"Đã tải trạng thái IngestionPipeline từ cache cho dự án '{project_name}'.")
    except Exception:
        print(f"Không tìm thấy cache IngestionPipeline cho dự án '{project_name}'. Tạo pipeline mới.")

    # 3. Đọc tài liệu
    documents = SimpleDirectoryReader(input_dir=data_path).load_data()

    # 4. Gán metadata cho từng tài liệu
    for doc in documents:
        doc.metadata["project_id"] = project_id
        doc.metadata["project_name"] = project_name

    # 5. Chạy pipeline để ingest các tài liệu và nhận về các nodes
    # pipeline.run sẽ tự động bỏ qua các tài liệu đã được xử lý nếu cache hoạt động tốt
    print(f"Bắt đầu xử lý và tạo nodes cho dự án '{project_name}'...")
    nodes = pipeline.run(documents=documents, show_progress=True)
    print(f"Đã hoàn thành xử lý nodes cho dự án '{project_name}'.")

    # 6. Lưu trạng thái pipeline sau khi chạy để cache cho lần sau
    pipeline.persist(pipeline_cache_path)
    print(f"Đã lưu trạng thái IngestionPipeline vào cache cho dự án '{project_name}'.")

    # 7. Lưu trữ các nodes vào Vector Store riêng cho dự án
    index = None
    try:
        # Tải index từ storage nếu đã tồn tại
        # vector_store = SimpleVectorStore.from_persist_dir(vector_store_path)
        # storage_context = StorageContext.from_defaults(vector_store=vector_store)
        storage_context = StorageContext.from_defaults(
            docstore=SimpleDocumentStore.from_persist_dir(persist_dir=vector_store_path),
            vector_store=SimpleVectorStore.from_persist_dir(
                persist_dir=vector_store_path
            ),
            index_store=SimpleIndexStore.from_persist_dir(persist_dir=vector_store_path),
        )
        print("vafo ddaya ")
        index = load_index_from_storage(
            storage_context=storage_context,
            index_id="61a6fbb0-4597-4e71-a9e0-51a3e087352c",  # <- truyền vào đây
        )
        print(f"Đã tải index cho dự án '{project_name}' từ '{vector_store_path}'")

        # Cập nhật index với các nodes mới/thay đổi
        if nodes: # Chỉ chèn nếu có nodes mới được tạo ra
            for node in nodes:
                index.insert(node)
            print(f"Đã thêm các nodes mới vào index cho dự án '{project_name}'")
        else:
            print(f"Không có nodes mới để thêm vào index cho dự án '{project_name}'.")

    except Exception as e:
        # Nếu không có index, tạo mới từ tất cả các nodes đã ingest
        print(f"Không tìm thấy index cho dự án '{project_name}' từ '{vector_store_path}'. Tạo index mới.")
        # print(f"Chi tiết lỗi: {e}")
        if nodes:
            storage_context = StorageContext.from_defaults(vector_store=SimpleVectorStore())
            index = VectorStoreIndex(nodes=nodes, storage_context=storage_context, embed_model=embedding_model, show_progress=True)
        else:
            print(f"Không có nodes để tạo index mới cho dự án '{project_name}'.")
            return None # Không có nodes thì không tạo index
    
    if index:
        index.storage_context.persist(persist_dir=vector_store_path)
        print(f"Đã lưu/cập nhật index cho dự án '{project_name}' vào '{vector_store_path}'")

    return index