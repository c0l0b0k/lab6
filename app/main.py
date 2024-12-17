from pathlib import Path

from fastapi import HTTPException, status, Depends, Body, FastAPI
from typing import *

from starlette.responses import FileResponse, HTMLResponse
from starlette.staticfiles import StaticFiles

from .auth import get_current_user
from .database.Neo4jDatabase import Neo4jDatabase
import logging
from .config import *
import mimetypes
from app.models import GraphSegment

logging.basicConfig(level=logging.DEBUG)

app = FastAPI()

# Конфигурация подключения к базе данных Neo4j
db = Neo4jDatabase(uri=NEO4J_URI, user=NEO4J_USER, password=NEO4J_PASSWORD, database=NE04J_DATABASE)


# Статические файлы с корректным MIME-типом для JS
@app.get("/static/{file_path:path}")
async def serve_static_file(file_path: str):
    file_path = f"app/static/{file_path}"
    # Определение MIME-типа для файла
    mime_type, _ = mimetypes.guess_type(file_path)

    # Если это JavaScript файл, устанавливаем MIME-тип application/javascript
    if file_path.endswith('.js'):
        mime_type = "application/javascript"

    return FileResponse(file_path, media_type=mime_type)


app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/", response_class=HTMLResponse)
def read_root():
    html_path = Path("app/templates/index.html")
    return html_path.read_text(encoding="utf-8")


@app.get("/nodes/")
def get_all_nodes():
    return db.get_all_nodes()

@app.get("/nodes/{node_id}")
def get_node_with_relations(node_id: str):
    node_data = db.get_nodes_by_id(node_id)
    if not node_data:
        raise HTTPException(status_code=404, detail="Node not found")
    return node_data

@app.post("/add/nodes/", dependencies=[Depends(get_current_user)])
def add_graph_segment(segment: GraphSegment):
    return db.add_graph_segment(segment)




