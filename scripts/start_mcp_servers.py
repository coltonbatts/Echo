#!/usr/bin/env python3
"""
Script to start all MCP servers for Echo platform.

This script starts the file operations, web search, and system utilities MCP servers
in the background and provides a way to stop them all.
"""

import subprocess
import time
import signal
import sys
import os
from typing import List
import psutil

# MCP server configurations
MCP_SERVERS = [
    {
        "name": "Calculator Server",
        "script": "sample_mcp_server.py",
        "port": 8001,
        "description": "Basic calculator operations"
    },
    {
        "name": "File Operations Server", 
        "script": "mcp_servers/file_server.py",
        "port": 8002,
        "description": "File system operations"
    },
    {
        "name": "Web Search Server",
        "script": "mcp_servers/web_server.py", 
        "port": 8003,
        "description": "Web search and fetching capabilities"
    },
    {
        "name": "System Utilities Server",
        "script": "mcp_servers/system_server.py",
        "port": 8004,
        "description": "System information and process management"
    }
]

class MCPServerManager:
    def __init__(self):
        self.processes: List[subprocess.Popen] = []
        self.running = False
        
    def start_server(self, server_config: dict) -> subprocess.Popen:
        """Start a single MCP server"""
        script_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), server_config["script"])
        
        if not os.path.exists(script_path):
            print(f"Warning: Script {script_path} not found, skipping {server_config['name']}")
            return None
            
        print(f"Starting {server_config['name']} on port {server_config['port']}...")
        
        try:
            # Start the server process
            process = subprocess.Popen([
                sys.executable, script_path
            ], 
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env={**os.environ, "PORT": str(server_config["port"])}
            )
            
            # Give it a moment to start
            time.sleep(1)
            
            # Check if process is still running
            if process.poll() is None:
                print(f"✅ {server_config['name']} started successfully (PID: {process.pid})")
                return process
            else:
                stdout, stderr = process.communicate()
                print(f"❌ {server_config['name']} failed to start")
                if stderr:
                    print(f"Error: {stderr.decode()}")
                return None
                
        except Exception as e:
            print(f"❌ Failed to start {server_config['name']}: {e}")
            return None
    
    def start_all_servers(self):
        """Start all MCP servers"""
        print("🚀 Starting Echo MCP servers...\n")
        
        for server_config in MCP_SERVERS:
            process = self.start_server(server_config)
            if process:
                self.processes.append(process)
        
        if self.processes:
            print(f"\n✅ Started {len(self.processes)} MCP servers successfully")
            print("\nServer URLs:")
            for i, server_config in enumerate(MCP_SERVERS):
                if i < len(self.processes):
                    print(f"  - {server_config['name']}: http://localhost:{server_config['port']}")
            
            print(f"\nUpdate your .env file with:")
            server_urls = [f"http://localhost:{server['port']}" for server in MCP_SERVERS]
            print(f"MCP_SERVER_URLS={','.join(server_urls)}")
            
            self.running = True
            return True
        else:
            print("❌ No servers started successfully")
            return False
    
    def stop_all_servers(self):
        """Stop all running MCP servers"""
        print("\n🛑 Stopping MCP servers...")
        
        for process in self.processes:
            try:
                if process.poll() is None:  # Process is still running
                    print(f"Stopping process {process.pid}...")
                    process.terminate()
                    
                    # Wait up to 5 seconds for graceful shutdown
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        print(f"Force killing process {process.pid}...")
                        process.kill()
                        process.wait()
                        
            except Exception as e:
                print(f"Error stopping process: {e}")
        
        self.processes.clear()
        self.running = False
        print("✅ All MCP servers stopped")
    
    def check_server_health(self):
        """Check health of all running servers"""
        import httpx
        import asyncio
        
        async def check_health():
            print("\n🔍 Checking server health...")
            
            async with httpx.AsyncClient(timeout=5) as client:
                for server_config in MCP_SERVERS:
                    url = f"http://localhost:{server_config['port']}/tools"
                    try:
                        response = await client.get(url)
                        if response.status_code == 200:
                            tools = response.json()
                            tool_count = len(tools) if isinstance(tools, list) else 0
                            print(f"✅ {server_config['name']}: {tool_count} tools available")
                        else:
                            print(f"⚠️ {server_config['name']}: HTTP {response.status_code}")
                    except Exception as e:
                        print(f"❌ {server_config['name']}: {e}")
        
        asyncio.run(check_health())
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print(f"\nReceived signal {signum}")
        self.stop_all_servers()
        sys.exit(0)
    
    def run_interactive(self):
        """Run in interactive mode with commands"""
        # Set up signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        if not self.start_all_servers():
            return
        
        print("\n📝 Commands:")
        print("  'health' - Check server health")
        print("  'list' - List running servers")  
        print("  'stop' - Stop all servers")
        print("  'restart' - Restart all servers")
        print("  'quit' - Exit")
        
        try:
            while self.running:
                command = input("\nEnter command: ").strip().lower()
                
                if command == 'health':
                    self.check_server_health()
                elif command == 'list':
                    self.list_servers()
                elif command == 'stop':
                    self.stop_all_servers()
                    break
                elif command == 'restart':
                    self.stop_all_servers()
                    time.sleep(2)
                    self.start_all_servers()
                elif command in ['quit', 'exit', 'q']:
                    break
                elif command == 'help':
                    print("\n📝 Commands:")
                    print("  'health' - Check server health")
                    print("  'list' - List running servers")
                    print("  'stop' - Stop all servers") 
                    print("  'restart' - Restart all servers")
                    print("  'quit' - Exit")
                else:
                    print("Unknown command. Type 'help' for available commands.")
                    
        except EOFError:
            pass
        finally:
            self.stop_all_servers()
    
    def list_servers(self):
        """List status of all servers"""
        print("\n📋 Server Status:")
        for i, server_config in enumerate(MCP_SERVERS):
            if i < len(self.processes):
                process = self.processes[i]
                status = "Running" if process.poll() is None else "Stopped"
                pid = process.pid if process.poll() is None else "N/A"
                print(f"  {server_config['name']}: {status} (PID: {pid})")
            else:
                print(f"  {server_config['name']}: Not started")

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Echo MCP Server Manager")
    parser.add_argument("--daemon", action="store_true", help="Run in daemon mode")
    parser.add_argument("--check-health", action="store_true", help="Check server health and exit")
    parser.add_argument("--stop", action="store_true", help="Stop running servers")
    
    args = parser.parse_args()
    
    manager = MCPServerManager()
    
    if args.check_health:
        manager.check_server_health()
        return
    
    if args.stop:
        # Find and stop any running MCP servers
        print("🔍 Looking for running MCP servers...")
        killed_any = False
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info['cmdline'] or []
                if any('mcp_server' in arg or 'sample_mcp_server' in arg for arg in cmdline):
                    print(f"Stopping process {proc.info['pid']}: {' '.join(cmdline)}")
                    proc.terminate()
                    killed_any = True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        if not killed_any:
            print("No running MCP servers found")
        else:
            print("✅ Stopped running MCP servers")
        return
    
    if args.daemon:
        # Start servers and exit
        if manager.start_all_servers():
            print("\n🏁 Servers started in daemon mode. Use --stop to stop them.")
        else:
            sys.exit(1)
    else:
        # Interactive mode
        manager.run_interactive()

if __name__ == "__main__":
    main()