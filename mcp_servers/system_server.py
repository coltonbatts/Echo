"""MCP Server for System Utilities

Provides tools for system information, process management, and basic system operations.
Includes security restrictions to prevent harmful operations.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import uvicorn
import os
import subprocess
import psutil
import platform
import time
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import shutil

app = FastAPI(title="System Utilities MCP Server", version="1.0.0")

# Security: Define allowed commands and operations
ALLOWED_COMMANDS = {
    "ls", "dir", "pwd", "whoami", "date", "uptime", "df", "free",
    "ps", "top", "netstat", "ping", "traceroute", "curl", "wget",
    "git", "npm", "pip", "python", "node", "java", "docker"
}

BLOCKED_PATTERNS = [
    "rm", "del", "format", "mkfs", "dd", "sudo", "su", "chmod 777",
    "shutdown", "reboot", "halt", "init", ">", ">>", "|", "&", ";",
    "eval", "exec", "system", "shell"
]

def is_command_safe(command: str) -> tuple[bool, str]:
    """Check if a command is safe to execute"""
    command_lower = command.lower().strip()
    
    # Check for blocked patterns
    for pattern in BLOCKED_PATTERNS:
        if pattern in command_lower:
            return False, f"Command contains blocked pattern: {pattern}"
    
    # Check if command starts with allowed command
    cmd_parts = command_lower.split()
    if not cmd_parts:
        return False, "Empty command"
    
    base_cmd = cmd_parts[0]
    if base_cmd not in ALLOWED_COMMANDS:
        return False, f"Command '{base_cmd}' is not in allowed list"
    
    return True, "Command is safe"

@app.get("/tools")
async def list_tools():
    return [
        {
            "name": "system_info",
            "description": "Get system information (OS, CPU, memory, disk)",
            "parameters": {}
        },
        {
            "name": "process_list",
            "description": "List running processes",
            "parameters": {
                "filter": "string - Filter processes by name (optional)",
                "limit": "integer - Limit number of results (default: 20)"
            }
        },
        {
            "name": "execute_command",
            "description": "Execute a safe system command",
            "parameters": {
                "command": "string - Command to execute (restricted for security)",
                "timeout": "integer - Timeout in seconds (default: 30)"
            }
        },
        {
            "name": "disk_usage",
            "description": "Get disk usage information",
            "parameters": {
                "path": "string - Path to check (default: current directory)"
            }
        },
        {
            "name": "memory_info",
            "description": "Get detailed memory usage information",
            "parameters": {}
        },
        {
            "name": "network_info",
            "description": "Get network interface information",
            "parameters": {}
        },
        {
            "name": "environment_vars",
            "description": "Get environment variables (filtered for security)",
            "parameters": {
                "filter": "string - Filter variables by name pattern (optional)"
            }
        },
        {
            "name": "check_service",
            "description": "Check if a service/process is running",
            "parameters": {
                "service_name": "string - Name of the service to check"
            }
        },
        {
            "name": "system_metrics",
            "description": "Get current system performance metrics",
            "parameters": {}
        }
    ]

@app.get("/tools/{tool_name}/schema")
async def tool_schema(tool_name: str):
    schemas = {
        "system_info": {
            "type": "object",
            "properties": {},
            "required": []
        },
        "process_list": {
            "type": "object",
            "properties": {
                "filter": {"type": "string", "description": "Filter processes by name"},
                "limit": {"type": "integer", "default": 20, "minimum": 1, "maximum": 100}
            },
            "required": []
        },
        "execute_command": {
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "Command to execute"},
                "timeout": {"type": "integer", "default": 30, "minimum": 1, "maximum": 300}
            },
            "required": ["command"]
        },
        "disk_usage": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "default": ".", "description": "Path to check"}
            },
            "required": []
        },
        "memory_info": {
            "type": "object",
            "properties": {},
            "required": []
        },
        "network_info": {
            "type": "object",
            "properties": {},
            "required": []
        },
        "environment_vars": {
            "type": "object",
            "properties": {
                "filter": {"type": "string", "description": "Filter pattern for variable names"}
            },
            "required": []
        },
        "check_service": {
            "type": "object",
            "properties": {
                "service_name": {"type": "string", "description": "Service name to check"}
            },
            "required": ["service_name"]
        },
        "system_metrics": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
    
    if tool_name not in schemas:
        raise HTTPException(status_code=404, detail="Tool not found")
    return schemas[tool_name]

# Pydantic models
class ProcessListRequest(BaseModel):
    filter: Optional[str] = None
    limit: int = 20

class ExecuteCommandRequest(BaseModel):
    command: str
    timeout: int = 30

class DiskUsageRequest(BaseModel):
    path: str = "."

class EnvironmentVarsRequest(BaseModel):
    filter: Optional[str] = None

class CheckServiceRequest(BaseModel):
    service_name: str

@app.post("/tools/system_info/execute")
async def execute_system_info(payload: dict = {}):
    try:
        system_info = {
            "platform": {
                "system": platform.system(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor(),
                "python_version": platform.python_version()
            },
            "cpu": {
                "count": psutil.cpu_count(),
                "count_logical": psutil.cpu_count(logical=True),
                "usage_percent": psutil.cpu_percent(interval=1),
                "frequency": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
            },
            "memory": {
                "total": psutil.virtual_memory().total,
                "available": psutil.virtual_memory().available,
                "used": psutil.virtual_memory().used,
                "percent": psutil.virtual_memory().percent
            },
            "disk": {
                "total": psutil.disk_usage('/').total,
                "used": psutil.disk_usage('/').used,
                "free": psutil.disk_usage('/').free,
                "percent": psutil.disk_usage('/').percent
            },
            "boot_time": datetime.fromtimestamp(psutil.boot_time()).isoformat(),
            "timestamp": datetime.now().isoformat()
        }
        
        return {"result": system_info}
        
    except Exception as e:
        return {"error": f"Failed to get system info: {str(e)}"}

@app.post("/tools/process_list/execute")
async def execute_process_list(payload: ProcessListRequest):
    try:
        processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status', 'create_time']):
            try:
                proc_info = proc.info
                
                # Apply filter if specified
                if payload.filter and payload.filter.lower() not in proc_info['name'].lower():
                    continue
                
                processes.append({
                    "pid": proc_info['pid'],
                    "name": proc_info['name'],
                    "cpu_percent": proc_info['cpu_percent'],
                    "memory_percent": proc_info['memory_percent'],
                    "status": proc_info['status'],
                    "created": datetime.fromtimestamp(proc_info['create_time']).isoformat()
                })
                
                if len(processes) >= payload.limit:
                    break
                    
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        
        # Sort by CPU usage
        processes.sort(key=lambda x: x['cpu_percent'] or 0, reverse=True)
        
        return {"result": {"processes": processes, "count": len(processes)}}
        
    except Exception as e:
        return {"error": f"Failed to list processes: {str(e)}"}

@app.post("/tools/execute_command/execute")
async def execute_execute_command(payload: ExecuteCommandRequest):
    # Security check
    is_safe, reason = is_command_safe(payload.command)
    if not is_safe:
        return {"error": f"Command rejected: {reason}"}
    
    try:
        # Execute command with timeout
        result = subprocess.run(
            payload.command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=payload.timeout,
            cwd=os.getcwd()
        )
        
        return {
            "result": {
                "command": payload.command,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "success": result.returncode == 0,
                "execution_time": payload.timeout  # Approximate
            }
        }
        
    except subprocess.TimeoutExpired:
        return {"error": f"Command timed out after {payload.timeout} seconds"}
    except Exception as e:
        return {"error": f"Failed to execute command: {str(e)}"}

@app.post("/tools/disk_usage/execute")
async def execute_disk_usage(payload: DiskUsageRequest):
    try:
        if not os.path.exists(payload.path):
            return {"error": "Path does not exist"}
        
        usage = psutil.disk_usage(payload.path)
        
        # Get disk partitions for additional info
        partitions = []
        for partition in psutil.disk_partitions():
            try:
                partition_usage = psutil.disk_usage(partition.mountpoint)
                partitions.append({
                    "device": partition.device,
                    "mountpoint": partition.mountpoint,
                    "fstype": partition.fstype,
                    "total": partition_usage.total,
                    "used": partition_usage.used,
                    "free": partition_usage.free,
                    "percent": partition_usage.percent
                })
            except PermissionError:
                continue
        
        return {
            "result": {
                "path": payload.path,
                "total": usage.total,
                "used": usage.used,
                "free": usage.free,
                "percent": usage.percent,
                "partitions": partitions
            }
        }
        
    except Exception as e:
        return {"error": f"Failed to get disk usage: {str(e)}"}

@app.post("/tools/memory_info/execute")
async def execute_memory_info(payload: dict = {}):
    try:
        virtual_mem = psutil.virtual_memory()
        swap_mem = psutil.swap_memory()
        
        memory_info = {
            "virtual_memory": {
                "total": virtual_mem.total,
                "available": virtual_mem.available,
                "used": virtual_mem.used,
                "free": virtual_mem.free,
                "percent": virtual_mem.percent,
                "active": getattr(virtual_mem, 'active', None),
                "inactive": getattr(virtual_mem, 'inactive', None),
                "buffers": getattr(virtual_mem, 'buffers', None),
                "cached": getattr(virtual_mem, 'cached', None)
            },
            "swap_memory": {
                "total": swap_mem.total,
                "used": swap_mem.used,
                "free": swap_mem.free,
                "percent": swap_mem.percent,
                "sin": swap_mem.sin,
                "sout": swap_mem.sout
            }
        }
        
        return {"result": memory_info}
        
    except Exception as e:
        return {"error": f"Failed to get memory info: {str(e)}"}

@app.post("/tools/network_info/execute")
async def execute_network_info(payload: dict = {}):
    try:
        network_info = {
            "interfaces": {},
            "connections": [],
            "stats": {}
        }
        
        # Network interfaces
        for interface, addrs in psutil.net_if_addrs().items():
            network_info["interfaces"][interface] = []
            for addr in addrs:
                network_info["interfaces"][interface].append({
                    "family": str(addr.family),
                    "address": addr.address,
                    "netmask": addr.netmask,
                    "broadcast": addr.broadcast
                })
        
        # Network statistics
        net_stats = psutil.net_if_stats()
        for interface, stats in net_stats.items():
            network_info["stats"][interface] = {
                "isup": stats.isup,
                "duplex": str(stats.duplex),
                "speed": stats.speed,
                "mtu": stats.mtu
            }
        
        # Network connections (limited for security)
        connections = psutil.net_connections(kind='inet')[:10]  # Limit to 10
        for conn in connections:
            network_info["connections"].append({
                "status": conn.status,
                "local_address": f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else None,
                "remote_address": f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else None,
                "type": str(conn.type)
            })
        
        return {"result": network_info}
        
    except Exception as e:
        return {"error": f"Failed to get network info: {str(e)}"}

@app.post("/tools/environment_vars/execute")
async def execute_environment_vars(payload: EnvironmentVarsRequest):
    try:
        # Security: Filter out sensitive environment variables
        sensitive_patterns = ['key', 'secret', 'token', 'password', 'pwd', 'auth']
        
        env_vars = {}
        for key, value in os.environ.items():
            # Skip sensitive variables
            if any(pattern.lower() in key.lower() for pattern in sensitive_patterns):
                env_vars[key] = "[REDACTED]"
                continue
            
            # Apply filter if specified
            if payload.filter and payload.filter.lower() not in key.lower():
                continue
            
            env_vars[key] = value
        
        return {
            "result": {
                "environment_variables": env_vars,
                "count": len(env_vars),
                "filtered": bool(payload.filter)
            }
        }
        
    except Exception as e:
        return {"error": f"Failed to get environment variables: {str(e)}"}

@app.post("/tools/check_service/execute")
async def execute_check_service(payload: CheckServiceRequest):
    try:
        service_found = False
        service_info = []
        
        # Check running processes for service name
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'status']):
            try:
                proc_info = proc.info
                if (payload.service_name.lower() in proc_info['name'].lower() or
                    any(payload.service_name.lower() in arg.lower() 
                        for arg in proc_info['cmdline'] if arg)):
                    
                    service_found = True
                    service_info.append({
                        "pid": proc_info['pid'],
                        "name": proc_info['name'],
                        "status": proc_info['status'],
                        "cmdline": ' '.join(proc_info['cmdline'][:3])  # Limit cmdline
                    })
                    
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return {
            "result": {
                "service_name": payload.service_name,
                "running": service_found,
                "processes": service_info,
                "count": len(service_info)
            }
        }
        
    except Exception as e:
        return {"error": f"Failed to check service: {str(e)}"}

@app.post("/tools/system_metrics/execute")
async def execute_system_metrics(payload: dict = {}):
    try:
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "cpu": {
                "usage_percent": psutil.cpu_percent(interval=1),
                "per_cpu": psutil.cpu_percent(interval=1, percpu=True),
                "load_average": os.getloadavg() if hasattr(os, 'getloadavg') else None
            },
            "memory": {
                "virtual_percent": psutil.virtual_memory().percent,
                "swap_percent": psutil.swap_memory().percent
            },
            "disk": {
                "usage_percent": psutil.disk_usage('/').percent,
                "io_counters": psutil.disk_io_counters()._asdict() if psutil.disk_io_counters() else None
            },
            "network": {
                "io_counters": psutil.net_io_counters()._asdict() if psutil.net_io_counters() else None
            },
            "process_count": len(psutil.pids()),
            "boot_time": datetime.fromtimestamp(psutil.boot_time()).isoformat()
        }
        
        return {"result": metrics}
        
    except Exception as e:
        return {"error": f"Failed to get system metrics: {str(e)}"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8004)