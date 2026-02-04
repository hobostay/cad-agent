#!/usr/bin/env python3
"""
CAD Agent API Server
现代化 FastAPI 后端，提供 RESTful API 和 WebSocket 聊天接口
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from typing import List, Optional
import json
import asyncio
import os
import sys
from pathlib import Path

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gen_parts import generate_part
from gen_parts_3d import generate_part_3d
from nl_to_spec_llm import parse_with_llm
from core.config import get_config
from core.registry import list_generators, create_generator
import parts  # noqa: F401  # 触发生成器注册
from engineering_validation import validate_part_design, recommend_material

app = FastAPI(
    title="CAD Agent API",
    description="AI 驱动的机械 CAD 参数解析与生成系统",
    version="2.0.0"
)

# 静态资源
app.mount("/static", StaticFiles(directory="static"), name="static")

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== 数据模型 ====================

class GenerateRequest(BaseModel):
    """生成 CAD 请求"""
    part_type: str
    parameters: dict
    output_format: str = "stl"  # stl 或 dxf

class ChatMessage(BaseModel):
    """聊天消息"""
    role: str  # user 或 assistant
    content: str

class ParseRequest(BaseModel):
    """自然语言解析请求"""
    text: str

class PartSpec(BaseModel):
    """零件规格"""
    schema_version: str = "1.0.0"
    part_type: str
    unit: str = "mm"
    base_shape: dict
    holes: List[dict]
    layer: str = "MAIN"

# ==================== WebSocket 连接管理 ====================

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

# ==================== API 路由 ====================

@app.get("/")
async def root():
    """返回前端页面"""
    return FileResponse("templates/index.html")

@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "service": "CAD Agent API"}

@app.get("/api/part-types")
async def get_part_types():
    """获取支持的零件类型"""
    return {
        "categories": {
            "基础零件": ["plate", "bolt", "nut", "washer"],
            "传动零件": ["gear", "sprocket", "pulley", "shaft", "stepped_shaft", "coupling"],
            "支撑零件": ["bearing", "flange", "bracket", "spring"],
            "结构件": ["chassis_frame", "snap_ring", "retainer"]
        }
    }

@app.get("/api/schema")
async def get_parameter_schema():
    """获取所有零件的参数 Schema"""
    schemas = {}
    for part_type in list_generators():
        try:
            gen = create_generator(part_type)
            schemas[part_type] = gen.get_parameter_schema()
        except Exception:
            schemas[part_type] = {}
    return {"success": True, "data": schemas}

@app.post("/api/parse")
async def parse_natural_language(request: ParseRequest):
    """解析自然语言为 CAD 参数（仅返回参数，不生成图纸）"""
    try:
        config = get_config()
        spec, reasoning = parse_with_llm(
            request.text,
            api_key=config.api.api_key,
            base_url=config.api.base_url,
            model=config.api.model,
        )
        return {"success": True, "data": spec, "reasoning": reasoning}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/design")
async def design_part(request: ParseRequest):
    """
    半自动设计：自然语言 -> 参数
    前端可让用户确认参数后再调用 /api/generate
    """
    try:
        config = get_config()
        spec, reasoning = parse_with_llm(
            request.text,
            api_key=config.api.api_key,
            base_url=config.api.base_url,
            model=config.api.model,
        )
        return {"success": True, "data": spec, "reasoning": reasoning}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/generate")
async def generate_cad(request: GenerateRequest):
    """生成 CAD 文件"""
    try:
        spec = {"type": request.part_type, "parameters": request.parameters}

        # 确定文件名和生成函数
        if request.output_format.lower() == "stl":
            filename = f"{request.part_type}_output.stl"
            generate_part_3d(spec, filename)
        else:
            filename = f"{request.part_type}_output.dxf"
            generate_part(spec, filename)

        # 读取文件内容
        with open(filename, 'rb') as f:
            file_data = f.read()

        file_size = os.path.getsize(filename)

        return {
            "success": True,
            "filename": filename,
            "size": file_size,
            "format": request.output_format
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/download/{filename}")
async def download_file(filename: str):
    """下载生成的文件"""
    file_path = Path(filename)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="文件不存在")
    return FileResponse(file_path, filename=filename)

@app.post("/api/validate")
async def validate_design(request: GenerateRequest):
    """验证设计合理性"""
    try:
        valid, messages, recommendations = validate_part_design(
            request.part_type,
            request.parameters
        )
        return {
            "success": True,
            "valid": valid,
            "messages": messages,
            "recommendations": recommendations
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/material")
async def get_material_recommendation(request: GenerateRequest):
    """获取材料推荐"""
    try:
        recommendations = recommend_material(request.part_type, "")
        return {
            "success": True,
            "recommendations": recommendations
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """WebSocket 聊天接口"""
    await manager.connect(websocket)

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            if message.get("type") == "parse":
                # 解析自然语言
                config = get_config()
                spec, reasoning = parse_with_llm(
                    message.get("text", ""),
                    api_key=config.api.api_key,
                    base_url=config.api.base_url,
                    model=config.api.model,
                )

                await websocket.send_json({
                    "type": "parse_result",
                    "data": spec,
                    "reasoning": reasoning
                })

            elif message.get("type") == "chat":
                # 普通聊天
                await websocket.send_json({
                    "type": "chat_response",
                    "message": f"收到: {message.get('text', '')}"
                })

    except WebSocketDisconnect:
        manager.disconnect(websocket)

# ==================== 启动配置 ====================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
