from fastapi import APIRouter, Query

from src.services.rag.retrieval import query_project_documents

router = APIRouter()


@router.get("/query")
def query(project: str = Query(...), q: str = Query(...)):
    return {"result": query_project_documents(project, q)}
