"""MCP Server for File Operations

Provides tools for file system operations including reading, writing, listing directories,
and basic file management. All operations are sandboxed to prevent security issues.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import uvicorn
import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import mimetypes
import base64

app = FastAPI(title="File Operations MCP Server", version="1.0.0")

# Security: Define allowed base directories (can be configured via env)
ALLOWED_BASE_DIRS = [
    os.path.expanduser("~/Documents"),
    os.path.expanduser("~/Desktop"),
    "/tmp",
    os.getcwd()  # Current working directory
]

def is_path_allowed(path: str) -> bool:
    """Check if a path is within allowed directories"""
    try:
        abs_path = os.path.abspath(path)
        return any(abs_path.startswith(os.path.abspath(base)) for base in ALLOWED_BASE_DIRS)
    except:
        return False

@app.get("/tools")
async def list_tools():
    return [
        {
            "name": "read_file",
            "description": "Read contents of a text file",
            "parameters": {
                "file_path": "string - Path to the file to read"
            }
        },
        {
            "name": "write_file", 
            "description": "Write content to a file (creates or overwrites)",
            "parameters": {
                "file_path": "string - Path to the file to write",
                "content": "string - Content to write to the file"
            }
        },
        {
            "name": "list_directory",
            "description": "List files and directories in a given path",
            "parameters": {
                "directory_path": "string - Path to the directory to list",
                "include_hidden": "boolean - Whether to include hidden files (default: false)"
            }
        },
        {
            "name": "create_directory",
            "description": "Create a new directory",
            "parameters": {
                "directory_path": "string - Path of the directory to create"
            }
        },
        {
            "name": "delete_file",
            "description": "Delete a file",
            "parameters": {
                "file_path": "string - Path to the file to delete"
            }
        },
        {
            "name": "file_info",
            "description": "Get information about a file or directory",
            "parameters": {
                "path": "string - Path to the file or directory"
            }
        },
        {
            "name": "search_files",
            "description": "Search for files by name pattern",
            "parameters": {
                "directory_path": "string - Directory to search in",
                "pattern": "string - File name pattern (supports wildcards)",
                "recursive": "boolean - Search recursively in subdirectories (default: false)"
            }
        }
    ]

@app.get("/tools/{tool_name}/schema")
async def tool_schema(tool_name: str):
    schemas = {
        "read_file": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "Path to the file to read"}
            },
            "required": ["file_path"]
        },
        "write_file": {
            "type": "object", 
            "properties": {
                "file_path": {"type": "string", "description": "Path to the file to write"},
                "content": {"type": "string", "description": "Content to write to the file"}
            },
            "required": ["file_path", "content"]
        },
        "list_directory": {
            "type": "object",
            "properties": {
                "directory_path": {"type": "string", "description": "Path to the directory to list"},
                "include_hidden": {"type": "boolean", "default": False, "description": "Include hidden files"}
            },
            "required": ["directory_path"]
        },
        "create_directory": {
            "type": "object",
            "properties": {
                "directory_path": {"type": "string", "description": "Path of the directory to create"}
            },
            "required": ["directory_path"]
        },
        "delete_file": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "Path to the file to delete"}
            },
            "required": ["file_path"]
        },
        "file_info": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Path to the file or directory"}
            },
            "required": ["path"]
        },
        "search_files": {
            "type": "object",
            "properties": {
                "directory_path": {"type": "string", "description": "Directory to search in"},
                "pattern": {"type": "string", "description": "File name pattern (supports wildcards)"},
                "recursive": {"type": "boolean", "default": False, "description": "Search recursively"}
            },
            "required": ["directory_path", "pattern"]
        }
    }
    
    if tool_name not in schemas:
        raise HTTPException(status_code=404, detail="Tool not found")
    return schemas[tool_name]

# Pydantic models for request payloads
class ReadFileRequest(BaseModel):
    file_path: str

class WriteFileRequest(BaseModel):
    file_path: str
    content: str

class ListDirectoryRequest(BaseModel):
    directory_path: str
    include_hidden: bool = False

class CreateDirectoryRequest(BaseModel):
    directory_path: str

class DeleteFileRequest(BaseModel):
    file_path: str

class FileInfoRequest(BaseModel):
    path: str

class SearchFilesRequest(BaseModel):
    directory_path: str
    pattern: str
    recursive: bool = False

@app.post("/tools/read_file/execute")
async def execute_read_file(payload: ReadFileRequest):
    if not is_path_allowed(payload.file_path):
        return {"error": "Access denied: Path not allowed"}
    
    try:
        if not os.path.exists(payload.file_path):
            return {"error": "File not found"}
        
        if not os.path.isfile(payload.file_path):
            return {"error": "Path is not a file"}
        
        # Check if file is binary
        mime_type, _ = mimetypes.guess_type(payload.file_path)
        is_binary = mime_type and not mime_type.startswith('text/')
        
        if is_binary:
            with open(payload.file_path, 'rb') as f:
                content = base64.b64encode(f.read()).decode('utf-8')
            return {"result": {"content": content, "encoding": "base64", "mime_type": mime_type}}
        else:
            with open(payload.file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return {"result": {"content": content, "encoding": "utf-8"}}
        
    except Exception as e:
        return {"error": f"Failed to read file: {str(e)}"}

@app.post("/tools/write_file/execute")
async def execute_write_file(payload: WriteFileRequest):
    if not is_path_allowed(payload.file_path):
        return {"error": "Access denied: Path not allowed"}
    
    try:
        # Create parent directories if they don't exist
        os.makedirs(os.path.dirname(payload.file_path), exist_ok=True)
        
        with open(payload.file_path, 'w', encoding='utf-8') as f:
            f.write(payload.content)
        
        return {"result": f"Successfully wrote {len(payload.content)} characters to {payload.file_path}"}
        
    except Exception as e:
        return {"error": f"Failed to write file: {str(e)}"}

@app.post("/tools/list_directory/execute")
async def execute_list_directory(payload: ListDirectoryRequest):
    if not is_path_allowed(payload.directory_path):
        return {"error": "Access denied: Path not allowed"}
    
    try:
        if not os.path.exists(payload.directory_path):
            return {"error": "Directory not found"}
        
        if not os.path.isdir(payload.directory_path):
            return {"error": "Path is not a directory"}
        
        items = []
        for item in os.listdir(payload.directory_path):
            if not payload.include_hidden and item.startswith('.'):
                continue
                
            item_path = os.path.join(payload.directory_path, item)
            is_dir = os.path.isdir(item_path)
            size = os.path.getsize(item_path) if not is_dir else None
            
            items.append({
                "name": item,
                "type": "directory" if is_dir else "file",
                "size": size,
                "path": item_path
            })
        
        items.sort(key=lambda x: (x["type"] == "file", x["name"].lower()))
        return {"result": {"items": items, "count": len(items)}}
        
    except Exception as e:
        return {"error": f"Failed to list directory: {str(e)}"}

@app.post("/tools/create_directory/execute")
async def execute_create_directory(payload: CreateDirectoryRequest):
    if not is_path_allowed(payload.directory_path):
        return {"error": "Access denied: Path not allowed"}
    
    try:
        os.makedirs(payload.directory_path, exist_ok=True)
        return {"result": f"Successfully created directory: {payload.directory_path}"}
        
    except Exception as e:
        return {"error": f"Failed to create directory: {str(e)}"}

@app.post("/tools/delete_file/execute")
async def execute_delete_file(payload: DeleteFileRequest):
    if not is_path_allowed(payload.file_path):
        return {"error": "Access denied: Path not allowed"}
    
    try:
        if not os.path.exists(payload.file_path):
            return {"error": "File not found"}
        
        if os.path.isdir(payload.file_path):
            return {"error": "Cannot delete directory with delete_file tool"}
        
        os.remove(payload.file_path)
        return {"result": f"Successfully deleted file: {payload.file_path}"}
        
    except Exception as e:
        return {"error": f"Failed to delete file: {str(e)}"}

@app.post("/tools/file_info/execute")
async def execute_file_info(payload: FileInfoRequest):
    if not is_path_allowed(payload.path):
        return {"error": "Access denied: Path not allowed"}
    
    try:
        if not os.path.exists(payload.path):
            return {"error": "Path not found"}
        
        stat = os.stat(payload.path)
        is_dir = os.path.isdir(payload.path)
        
        info = {
            "path": payload.path,
            "type": "directory" if is_dir else "file",
            "size": stat.st_size,
            "modified": stat.st_mtime,
            "created": stat.st_ctime,
            "permissions": oct(stat.st_mode)[-3:]
        }
        
        if not is_dir:
            mime_type, _ = mimetypes.guess_type(payload.path)
            info["mime_type"] = mime_type
        
        return {"result": info}
        
    except Exception as e:
        return {"error": f"Failed to get file info: {str(e)}"}

@app.post("/tools/search_files/execute")
async def execute_search_files(payload: SearchFilesRequest):
    if not is_path_allowed(payload.directory_path):
        return {"error": "Access denied: Path not allowed"}
    
    try:
        import fnmatch
        
        if not os.path.exists(payload.directory_path):
            return {"error": "Directory not found"}
        
        matches = []
        
        if payload.recursive:
            for root, dirs, files in os.walk(payload.directory_path):
                for file in files:
                    if fnmatch.fnmatch(file, payload.pattern):
                        full_path = os.path.join(root, file)
                        matches.append({
                            "name": file,
                            "path": full_path,
                            "directory": root
                        })
        else:
            for item in os.listdir(payload.directory_path):
                if fnmatch.fnmatch(item, payload.pattern):
                    full_path = os.path.join(payload.directory_path, item)
                    if os.path.isfile(full_path):
                        matches.append({
                            "name": item,
                            "path": full_path,
                            "directory": payload.directory_path
                        })
        
        return {"result": {"matches": matches, "count": len(matches)}}
        
    except Exception as e:
        return {"error": f"Failed to search files: {str(e)}"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)