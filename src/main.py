# src/main.py

import os

from llama_index.core import Settings
from llama_index.llms.google_genai import GoogleGenAI

from src.config import DATA_DIR
from src.ingestion import ingest_documents_for_project
from src.retrieval import query_project_documents
from src.utils import create_project_directories

# AIzaSyA1ajYrmy98W5akyLuwiJXD48ki6hcvGLA
os.environ["GOOGLE_API_KEY"] = "AIzaSyCZrpTENz0lFppSPShEt5WumxlgIlM46fA"
llm = GoogleGenAI(model="gemini-2.0-flash-exp", api_key="AIzaSyCZrpTENz0lFppSPShEt5WumxlgIlM46fA")
Settings.llm = llm

def run_ingestion_process(project_id: str, project_name: str):
    """Chạy quá trình ingest tài liệu cho một dự án."""
    print(f"\n--- Bắt đầu quá trình Ingest cho dự án: '{project_name}' ---")
    create_project_directories(project_name)
    ingest_documents_for_project(project_id, project_name)
    print(f"--- Quá trình Ingest cho dự án: '{project_name}' hoàn tất ---")

def run_query_process(project_name: str, query: str):
    """Chạy quá trình truy vấn cho một dự án."""
    print(f"\n--- Bắt đầu quá trình Query cho dự án: '{project_name}' ---")
    response = query_project_documents(project_name, query)
    print(f"--- Câu trả lời cho dự án '{project_name}': ---")
    print(response)
    print(f"--- Quá trình Query cho dự án: '{project_name}' hoàn tất ---")

if __name__ == "__main__":
    # --- Ví dụ sử dụng ---

    # 1. Thiết lập dự án đầu tiên
    project_A_id = "PROJ-001"
    project_A_name = "project_A"
    
    # Tạo một file dummy trong data/project_A để test
    # project_A_data_path = os.path.join(DATA_DIR, project_A_name)
    # os.makedirs(project_A_data_path, exist_ok=True)
    # with open(os.path.join(project_A_data_path, "requirements_design.txt"), "w", encoding="utf-8") as f:
    #     f.write("Yêu cầu 1: Hệ thống phải có chức năng đăng nhập an toàn với xác thực 2 yếu tố.\n")
    #     f.write("Yêu cầu 2: Module quản lý người dùng cần cho phép admin thêm, sửa, xóa người dùng và phân quyền.\n")
    #     f.write("Yêu cầu 3: Thiết kế cơ sở dữ liệu phải hỗ trợ mở rộng cho các module mới.\n")
    #     f.write("Yêu cầu 4: Giao diện người dùng phải thân thiện và dễ sử dụng trên cả mobile và desktop.\n")
    #     f.write("Yêu cầu 5: Hệ thống cần tích hợp API bên thứ ba để xử lý thanh toán.\n")
    #     f.write("Yêu cầu 6: Test run againe.\n")

    # Chạy ingest lần đầu cho Project A (sẽ xử lý và tạo cache/index)
    run_ingestion_process("CMDB_01", "project_CMDB")

    # 3. Chạy truy vấn cho Project A
    # query_A = "Là người có vai trò nhập liệu thông tin CI trên hệ thống CMDB, tôi muốn có giao diện quản trị (hiển thị, nhập liệu) thông tin CI để thực hiện nhập liệu, hiển thị thống kê CI."
    # run_query_process("project_CMDB", query_A)

    # # 4. Chạy truy vấn cho Project B
    # query_B = "Báo cáo bảo mật nói gì về các lỗ hổng và giải pháp?"
    # run_query_process(project_B_name, query_B)

    # 5. Thử truy vấn một dự án không tồn tại hoặc chưa được ingest
    # print("\n--- Thử truy vấn một dự án không tồn tại ---")
    # response_non_existent = query_project_documents("non_existent_project", "Câu hỏi bất kỳ?")
    # print(response_non_existent)