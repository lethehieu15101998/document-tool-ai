# src/retrieval.py

import os

from llama_index.core import (StorageContext, get_response_synthesizer,
                              load_index_from_storage)
from llama_index.core.postprocessor import SentenceTransformerRerank
from llama_index.core.prompts import RichPromptTemplate
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.vector_stores import SimpleVectorStore

from src.config import (EMBED_MODEL_NAME, RERANK_MODEL_NAME, RERANK_TOP_N,
                        RETRIEVAL_TOP_K)
from src.ingestion import \
    embedding_model  # Import embedding_model từ ingestion.py
from src.utils import get_project_paths

# src/retrieval.py





def retriver_query(project_name: str):
    """
    Truy vấn tài liệu của một dự án cụ thể, áp dụng retrieval và reranking.
    """
    project_paths = get_project_paths(project_name)

    vector_store_path = project_paths["vector_store"]

    # Kiểm tra thư mục chứa index
    if not os.path.exists(vector_store_path) or not os.listdir(vector_store_path):
        return f"Không tìm thấy dữ liệu đã được xử lý cho dự án '{project_name}'. Vui lòng ingest tài liệu trước."

    # 1. Tải index từ thư mục lưu trữ
    try:
        storage_context = StorageContext.from_defaults(persist_dir=vector_store_path)
        index = load_index_from_storage(
            storage_context=storage_context,
            embed_model=embedding_model
        )
        print(f"✅ Đã tải index cho dự án '{project_name}' từ '{vector_store_path}'")
    except Exception as e:
        print(f"❌ Lỗi khi tải index cho dự án '{project_name}': {e}")
        return "Xin lỗi, có lỗi xảy ra khi tải dữ liệu dự án."

    # 2. Tạo retriever
    retriever = VectorIndexRetriever(
        index=index,
        similarity_top_k=RETRIEVAL_TOP_K,
    )

    # 3. Tạo reranker
    rerank_postprocessor = SentenceTransformerRerank(
        model=RERANK_MODEL_NAME,
        top_n=RERANK_TOP_N
    )

    # 4. Khởi tạo query engine
    query_engine = RetrieverQueryEngine(
        retriever=retriever,
        response_synthesizer=get_response_synthesizer(),
        node_postprocessors=[rerank_postprocessor]
    )
    


    # # 5. Truy vấn
    # print(f"🔍 Đang truy vấn dự án '{project_name}' với câu hỏi: '{query_text}'...")
    # response = query_engine.query(query_text)

    return query_engine


def query_project_documents(project_name: str, query_text: str) -> str:
    # Prompt bạn yêu cầu
    function_prompt = RichPromptTemplate(
        """
        Bạn là một kỹ sư phần mềm cao cấp chuyên mô hình hóa chức năng hệ thống.

        ---------------------
        Thông tin nội bộ dự án (context) được trích xuất từ tài liệu:
        {{context_str}}
        ---------------------

        Yêu cầu của người dùng:
        "{{query_str}}"

        Hãy thực hiện:
        1. Viết một đoạn mô tả relationship Diagram của các bảng liên quan đến chức năng. Hãy dựa vào ngữ cảnh lấy thông tin chi tiết tên các bảng, các trường, kiểu dữ liệu tương ứng từng bảng.
        . Nếu ngữ cảnh cung cấp không đủ thông tin, có thể suy luận hợp lý từ context đưa vào không đựa bịa".
        2. Mô tả luồng xử lý của chức năng này  hoặc sơ đồ luồng để sinh ra biểu đồ active diagram và sequence diagram. Nếu không đủ thông tin, có thể suy luận hợp lý từ context đưa vào không được bịa".

        Kết quả trả về phải hoàn toàn tuân thủ đúng định dạng JSON ở dưới đây:
        {
          "relationshipDiagramDescription": "...",
          "functionDiagramDescription": "..."
        }
        câu trả lời chỉ được là tiếng việt. Không thêm chú thích, không giải thích thêm.
        """
    )
    

    # Tạo query_engine từ project name
    query_engine = retriver_query(project_name)

    query_engine.update_prompts({
        "response_synthesizer:text_qa_template": function_prompt,
    })

    prompts_dict = query_engine.get_prompts()
    for k, p in prompts_dict.items():
        print(p.get_template())

    response = query_engine.query(query_text)

    return response.response