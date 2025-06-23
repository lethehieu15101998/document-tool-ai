from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel

from src.models.file_model import UploadResult
from src.models.response import ApiResponse
from src.services.file_service import save_file_to_questions
from src.services.rag.retrieval import query_project_documents
from src.services.rag.utils import analyze_document_from_file
from src.utils.JsonUtil import parse_diagram

router = APIRouter(prefix="/api/v1/files", tags=["Files"])


class AnalyzeRequest(BaseModel):
    file_name: str


class ExtractDocumentRequest(BaseModel):
    content: str


@router.post("/upload")
async def upload(file: UploadFile = File(...)):
    file_name = await save_file_to_questions(file)
    return ApiResponse(
        message="Upload thành công", data=UploadResult(filename=file_name)
    )


@router.post("/analyze_document")
def analyze_document_endpoint(
    request: AnalyzeRequest,
):
    file_name = request.file_name

    result_json_string = analyze_document_from_file(file_name)

    return ApiResponse(message="Upload thành công", data=result_json_string)


@router.post("/extract_info_document/file")
def extract_info_document_from_file_endpoint(
    request: AnalyzeRequest,
):
    file_name = request.file_name

    result_json_string = analyze_document_from_file(file_name)
    result = query_project_documents("project_CMDB", result_json_string)
    return ApiResponse(message="Upload thành công", data=parse_diagram(result))


@router.post("/extract_info_document/text")
def extract_info_document_from_file_endpoint(
    request: ExtractDocumentRequest,
):
    content = request.content
    result = query_project_documents("project_CMDB", content)
    return ApiResponse(message="Upload thành công", data=parse_diagram(result))
