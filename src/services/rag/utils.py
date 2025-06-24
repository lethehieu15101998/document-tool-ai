# src/utils.py

import json
import os

import nest_asyncio
from llama_index.core import Document, Settings, SimpleDirectoryReader
from llama_index.core.prompts import RichPromptTemplate
from llama_index.llms.google_genai import GoogleGenAI
from llama_index.readers.file import (
    CSVReader,
    DocxReader,
    PDFReader,
    UnstructuredReader,
)
from llama_parse import LlamaParse

from src.config.config import CACHE_DIR, DATA_DIR, QUESTIONS_DIR, VECTOR_STORES_DIR

nest_asyncio.apply()

os.environ["GOOGLE_API_KEY"] = "AIzaSyCZrpTENz0lFppSPShEt5WumxlgIlM46fA"
llm = GoogleGenAI(
    model="gemini-2.0-flash", api_key="AIzaSyCZrpTENz0lFppSPShEt5WumxlgIlM46fA"
)
Settings.llm = llm


def create_project_directories(project_name: str):
    """
    Tạo cấu trúc thư mục cần thiết cho một dự án cụ thể.
    """
    project_data_path = os.path.join(DATA_DIR, project_name)
    project_pipeline_cache_path = os.path.join(
        CACHE_DIR, f"{project_name}_pipeline_cache"
    )
    project_vector_store_path = os.path.join(
        VECTOR_STORES_DIR, f"{project_name}_vector_store"
    )

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


def analyze_document_from_file(file_name: str) -> str:
    file_path = os.path.join(QUESTIONS_DIR, file_name)
    """
    Đọc nội dung từ một file, phân tích bằng LLM và trả về kết quả
    tổng hợp dưới dạng chuỗi JSON.

    Args:
        file_path (str): Đường dẫn đến file tài liệu cần phân tích.

    Returns:
        str: Chuỗi JSON chứa kết quả phân tích và tổng hợp từ LLM.
             Trả về thông báo lỗi nếu có vấn đề.
    """

    # --- 1. Kiểm tra sự tồn tại của file ---
    if not os.path.exists(file_path):
        return json.dumps(
            {"error": f"Không tìm thấy file tại đường dẫn: {file_path}"},
            ensure_ascii=False,
        )

    analysis_prompt_template = RichPromptTemplate(
        """
        Bạn là một trợ lý AI phân tích tài liệu chuyên nghiệp và cực kỳ tỉ mỉ.
        Mục tiêu của bạn là phân tích sâu tài liệu được cung cấp và trình bày TẤT CẢ kết quả bằng tiếng Việt, gom gọn vào một trường duy nhất trong định dạng JSON.
        Sử dụng Markdown bên trong trường đó để cấu trúc thông tin một cách rõ ràng và giữ lại các đặc tả chi tiết quan trọng.

        ---------------------
        **Tài liệu cần phân tích:**
        {{ document_content }}
        ---------------------

        **Yêu cầu phân tích và tổng hợp chi tiết:**
        1.  **Tóm tắt Tổng quan Tài liệu:** Cung cấp một cái nhìn tổng thể về mục đích và bối cảnh của tài liệu.
        2.  **Đặc tả Yêu cầu Chính:**
            * **Mục đích Yêu cầu (CARD):** Nêu rõ mục đích chính của yêu cầu theo góc nhìn của người dùng (user persona).
            * **Tiêu chí Nghiệm thu (CONVERSATION):**
                * Trích xuất và liệt kê từng kịch bản (Scenario) với các điều kiện (Given, When) và kết quả mong muốn (Then) chi tiết.
                * Trình bày mỗi kịch bản một cách rõ ràng để người đọc có thể hình dung luồng kiểm thử.
            * **Mô tả Yêu cầu Chi tiết (CONVERSATION):**
                * Trích xuất các thông tin cụ thể về **các trường trên lưới dữ liệu** (tên trường, mô tả, kiểu dữ liệu, bắt buộc/không) và ghi chú liên quan.
                * Trích xuất các thông tin cụ thể về **các trường trên Popup Thêm mới/Chỉnh sửa** (tên trường, mô tả, kiểu dữ liệu, cho phép chỉnh sửa, bắt buộc/không) và ghi chú liên quan.
                * Chú ý đến các đặc tả về luồng thao tác nghiệp vụ, kiểm tra trùng lặp, tự động sinh ID, xóa mềm, v.v.

        **ĐỊNH DẠNG ĐẦU RA BẮT BUỘC:**
        Kết quả trả về phải hoàn toàn tuân thủ đúng định dạng JSON mẫu ở dưới đây. Không thêm chú thích, không giải thích thêm ngoài JSON. Câu trả lời phải là tiếng việt, chỉ trả lời trong phạm vi của nội dung câu hỏi, không trả lời ngoài phạm vi

        ```json
        {
        "detailed_analysis": "### 1. Tóm tắt Tổng quan Tài liệu:\n[Nội dung tóm tắt tổng quan, tập trung vào mục đích chính và đối tượng người dùng]\n\n### 2. Đặc tả Yêu cầu Chính:\n\n#### 2.1. Mục đích Yêu cầu (CARD):\n- Là người [Vai trò người dùng], tôi muốn [Mục tiêu của yêu cầu].\n\n#### 2.2. "
        }
        ```
       
        """
    )

    try:
        documents = SimpleDirectoryReader(input_files=[file_path]).load_data()
        # llama_parse_parser = LlamaParse(
        #     api_key="llx-5Zz21yq5EUt8k7iwrMKsNhwfhNb3VRCbabnys84XYHsnJ30u",  # Thay bằng API key Llama Cloud của bạn
        #     result_type="markdown",
        #     verbose=True,
        # )
        # file_extractor = {
        #     ".pdf": llama_parse_parser,
        #     ".docx": llama_parse_parser,  # LlamaParse hỗ trợ DOCX
        #     ".doc": llama_parse_parser,  # LlamaParse hỗ trợ DOC (định dạng cũ của Word)
        #     ".pptx": llama_parse_parser,  # LlamaParse hỗ trợ PPTX
        #     ".xlsx": llama_parse_parser,  # LlamaParse hỗ trợ XLSX
        #     ".csv": llama_parse_parser,  # LlamaParse hỗ trợ CSV
        #     ".txt": llama_parse_parser,  # LlamaParse cũng có thể xử lý TXT
        # }
        # documents = SimpleDirectoryReader(
        #     input_files=[file_path], file_extractor=file_extractor
        # ).load_data()

        # Lấy nội dung văn bản từ Document đầu tiên
        document_content_string = " . ".join([doc.text for doc in documents])
    except Exception as e:
        return json.dumps(
            {"error": f"Lỗi khi đọc nội dung file '{file_path}': {e}"},
            ensure_ascii=False,
        )

    # --- 4. Format prompt với nội dung tài liệu ---
    messages = analysis_prompt_template.format_messages(
        document_content=document_content_string
    )

    # --- 5. Gọi LLM và lấy kết quả ---
    try:
        print(f"Đang gửi nội dung file '{file_path}' tới LLM để phân tích...")
        # Gọi chat API
        response = llm.chat(messages)

        # Trích xuất nội dung từ phản hồi của LLM
        # Cách trích xuất có thể khác nhau tùy thuộc vào thư viện bạn dùng (openai trực tiếp hay llama_index wrapper)
        # Nếu dùng openai client:
        result_content = response.message.content
        # Nếu dùng llama_index.llms.openai/google:
        # result_content = response.message.content

        return result_content

    except Exception as e:
        return json.dumps(
            {
                "error": f"Lỗi khi gọi LLM: {e}. Vui lòng kiểm tra API Key, kết nối mạng và tên model."
            },
            ensure_ascii=False,
        )


def analyze_document_from_content_no_rag(content: str) -> str:

    analysis_prompt_template = RichPromptTemplate(
        """
        Bạn là một trợ lý AI phân tích tài liệu chuyên nghiệp và cực kỳ tỉ mỉ.
        Mục tiêu của bạn là phân tích sâu tài liệu được cung cấp và trình bày TẤT CẢ kết quả bằng tiếng Việt

        ---------------------
        **Tài liệu cần phân tích:**
        {{ document_content }}
        ---------------------

          Dựa vào yêu cầu đề bài, hãy thực hiện:
                    1. Viết một đoạn mô tả relationship Diagram của các bảng liên quan đến chức năng. Hãy dựa vào ngữ cảnh lấy thông tin chi tiết tên các bảng, các trường, kiểu dữ liệu tương ứng từng bảng.
              
                    2. Mô tả luồng xử lý của chức năng này  hoặc sơ đồ luồng để sinh ra biểu đồ active diagram và sequence diagram. Nếu không đủ thông tin, có thể suy luận hợp lý, không được bịa".

                    Kết quả trả về phải hoàn toàn tuân thủ đúng định dạng JSON mẫu ở dưới đây. Không thêm chú thích, không giải thích thêm ngoài JSON. Phải trả lời bằng tiếng việt:
                    {
                      "relationshipDiagramDescription": "...",
                      "functionDiagramDescription": "..."
                    }
        """
    )

    # --- 4. Format prompt với nội dung tài liệu ---
    messages = analysis_prompt_template.format_messages(document_content=content)

    # --- 5. Gọi LLM và lấy kết quả ---
    try:

        response = llm.chat(messages)

        result_content = response.message.content

        return result_content

    except Exception as e:
        return json.dumps(
            {
                "error": f"Lỗi khi gọi LLM: {e}. Vui lòng kiểm tra API Key, kết nối mạng và tên model."
            },
            ensure_ascii=False,
        )
