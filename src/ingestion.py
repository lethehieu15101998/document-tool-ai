import os

from llama_index.core import (SimpleDirectoryReader, StorageContext,
                              VectorStoreIndex, load_index_from_storage)
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.storage.docstore import SimpleDocumentStore
from llama_index.core.storage.index_store import SimpleIndexStore
from llama_index.core.vector_stores import SimpleVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

from src.config import CHUNK_OVERLAP, CHUNK_SIZE, EMBED_MODEL_NAME
from src.utils import get_project_paths

embedding_model = HuggingFaceEmbedding(model_name=EMBED_MODEL_NAME)
PROJECT_INDEX_ID = "61a6fbb0-4597-4e71-a9e0-51a3e087352c"

def ingest_documents_for_project(project_id: str, project_name: str):
    project_paths = get_project_paths(project_name)
    data_path = project_paths["data"]
    pipeline_cache_path = project_paths["pipeline_cache"]
    vector_store_path = project_paths["vector_store"]

    if not os.path.exists(data_path) or not os.listdir(data_path):
        print(f"Không tìm thấy tài liệu trong '{data_path}' cho dự án '{project_name}'. Bỏ qua.")
        return None

    # Load hoặc tạo docstore
    docstore_path = os.path.join(vector_store_path, "docstore.json")
    if os.path.exists(docstore_path):
        docstore = SimpleDocumentStore.from_persist_path(docstore_path)
        print("Đã load docstore từ cache.")
    else:
        docstore = SimpleDocumentStore()
        print("Tạo mới docstore.")

    # 1. Khởi tạo pipeline và gắn docstore
    pipeline = IngestionPipeline(
        transformations=[
            SentenceSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP),
            embedding_model,
        ],
        docstore=docstore,
    )

    # 2. Load pipeline cache nếu có
    try:
        pipeline.load(pipeline_cache_path)
        print(f"Đã tải pipeline từ cache cho dự án '{project_name}'.")
    except Exception:
        print(f"Không có cache pipeline cho dự án '{project_name}', sẽ tạo mới.")

    # 3. Load documents với filename_as_id
    documents = SimpleDirectoryReader(input_dir=data_path, filename_as_id=True).load_data()

    # 4. Gán thêm metadata
    for doc in documents:
        doc.metadata["project_id"] = project_id
        doc.metadata["project_name"] = project_name

    # 5. Chạy pipeline
    print(f"Bắt đầu xử lý documents cho dự án '{project_name}'...")
    nodes = pipeline.run(documents=documents, show_progress=True)
    print(f"Đã ingest {len(nodes)} nodes cho dự án '{project_name}'.")

    # 6. Persist pipeline (kèm cả docstore)
    pipeline.persist(pipeline_cache_path)
    print(f"Đã lưu pipeline vào '{pipeline_cache_path}'.")

    # 7. Load hoặc tạo index
    try:
        if not os.path.exists(vector_store_path) or not os.listdir(vector_store_path):
            raise FileNotFoundError("Vector store không tồn tại hoặc trống.")

        storage_context = StorageContext.from_defaults(persist_dir=vector_store_path)
        print("Đã load StorageContext.")

        index = load_index_from_storage(
            storage_context=storage_context,
            embed_model=embedding_model,
            index_id=PROJECT_INDEX_ID,
        )
        print(f"Đã load index '{PROJECT_INDEX_ID}'.")

        if nodes:
            for node in nodes:
                index.insert(node)
            print("Đã thêm nodes vào index.")

    except Exception as e:
        print(f"Lỗi khi load index, sẽ tạo mới: {e}")
        if not nodes:
            print("Không có nodes để tạo index.")
            return None

        new_docstore = SimpleDocumentStore()
        new_vector_store = SimpleVectorStore()
        new_index_store = SimpleIndexStore()
        storage_context = StorageContext.from_defaults(
            docstore=new_docstore,
            vector_store=new_vector_store,
            index_store=new_index_store,
        )
        index = VectorStoreIndex(
            nodes=nodes,
            storage_context=storage_context,
            embed_model=embedding_model,
            show_progress=True
        )
        index.set_index_id(PROJECT_INDEX_ID)
        index.storage_context.persist(persist_dir=vector_store_path)
        print(f"Đã tạo index mới với ID '{PROJECT_INDEX_ID}'.")

    return index
