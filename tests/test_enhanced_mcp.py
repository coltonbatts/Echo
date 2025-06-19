"""
Tests for enhanced MCP functionality including intelligent tool selection,
parallel execution, and new MCP servers.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
import json

# Import the modules to test
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.enhanced_mcp_client import EnhancedMCPClient, ToolInfo, ExecutionResult, ServerHealth
from backend.intelligent_tool_selector import IntelligentToolSelector, ToolMatch, IntentPattern
from backend.main import extract_parameters_from_message

class TestEnhancedMCPClient:
    """Test the enhanced MCP client functionality"""
    
    @pytest.fixture
    def client(self):
        """Create a test MCP client"""
        with patch('backend.enhanced_mcp_client.MCP_SERVER_URLS', ["http://test:8001", "http://test:8002"]):
            return EnhancedMCPClient()
    
    @pytest.fixture
    def sample_tool(self):
        """Create a sample tool for testing"""
        return ToolInfo(
            name="test_tool",
            description="A test tool for calculations",
            parameters={"expression": {"type": "string"}},
            server_url="http://test:8001",
            category="computation",
            tags=["math", "calculator"]
        )
    
    @pytest.mark.asyncio
    async def test_server_health_check(self, client):
        """Test server health checking"""
        with patch('httpx.AsyncClient') as mock_client:
            # Mock successful response
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json.return_value = [{"name": "test_tool"}]
            mock_response.raise_for_status = MagicMock()
            
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            health = await client.check_server_health("http://test:8001")
            
            assert health.is_healthy == True
            assert health.url == "http://test:8001"
            assert "test_tool" in health.capabilities
    
    @pytest.mark.asyncio
    async def test_tool_discovery_with_metadata(self, client):
        """Test enhanced tool discovery with metadata"""
        mock_tools_data = [
            {
                "name": "calculator",
                "description": "Perform mathematical calculations",
                "parameters": {"expression": "string"}
            },
            {
                "name": "web_search", 
                "description": "Search the web for information",
                "parameters": {"query": "string"}
            }
        ]
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_tools_data
            mock_response.raise_for_status = MagicMock()
            
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            tools = await client.discover_tools_from_server("http://test:8001")
            
            assert len(tools) == 2
            assert tools[0].name == "calculator"
            assert tools[0].category == "computation"
            assert "math" in tools[0].tags
            
            assert tools[1].name == "web_search"
            assert tools[1].category == "web_operations"
            assert "web" in tools[1].tags
    
    @pytest.mark.asyncio
    async def test_parallel_tool_execution(self, client):
        """Test parallel execution of multiple tools"""
        tool_requests = [
            ("http://test:8001", "calculator", {"expression": "2+2"}),
            ("http://test:8001", "web_search", {"query": "test"})
        ]
        
        # Mock the individual execution method
        async def mock_execute(server_url, tool_name, params):
            if tool_name == "calculator":
                return ExecutionResult(
                    tool_name="calculator",
                    server_url=server_url,
                    parameters=params,
                    result={"result": 4},
                    success=True,
                    execution_time=0.5,
                    timestamp=datetime.now()
                )
            else:
                return ExecutionResult(
                    tool_name="web_search",
                    server_url=server_url,
                    parameters=params,
                    result={"result": "search results"},
                    success=True,
                    execution_time=1.0,
                    timestamp=datetime.now()
                )
        
        client.execute_tool_with_retry = AsyncMock(side_effect=mock_execute)
        
        results = await client.execute_multiple_tools(tool_requests)
        
        assert len(results) == 2
        assert results[0].tool_name == "calculator"
        assert results[0].success == True
        assert results[0].result["result"] == 4
        
        assert results[1].tool_name == "web_search"
        assert results[1].success == True
    
    def test_tool_categorization(self, client):
        """Test automatic tool categorization"""
        test_cases = [
            ("file_reader", "Read files from disk", "file_operations"),
            ("web_search", "Search the internet", "web_operations"),
            ("system_info", "Get system information", "system_operations"),
            ("calculator", "Perform mathematical calculations", "computation"),
            ("unknown_tool", "Does something unknown", "general")
        ]
        
        for name, description, expected_category in test_cases:
            category = client._categorize_tool(name, description)
            assert category == expected_category
    
    def test_tag_extraction(self, client):
        """Test tag extraction from tool descriptions"""
        test_cases = [
            ("async_processor", "Asynchronous data processing", ["async", "data"]),
            ("secure_storage", "Secure file storage system", ["secure", "data"]),
            ("realtime_monitor", "Real-time system monitoring", ["realtime", "network"]),
            ("ai_classifier", "AI-powered text classification", ["ai"])
        ]
        
        for name, description, expected_tags in test_cases:
            tags = client._extract_tags(name, description)
            for expected_tag in expected_tags:
                assert expected_tag in tags

class TestIntelligentToolSelector:
    """Test the intelligent tool selection system"""
    
    @pytest.fixture
    def selector(self):
        """Create a test tool selector"""
        return IntelligentToolSelector()
    
    @pytest.fixture
    def sample_tools(self):
        """Create sample tools for testing"""
        return [
            ToolInfo(
                name="read_file",
                description="Read contents of a file",
                parameters={"file_path": "string"},
                server_url="http://test:8002",
                category="file_operations",
                tags=["file", "read"]
            ),
            ToolInfo(
                name="web_search",
                description="Search the web for information",
                parameters={"query": "string"},
                server_url="http://test:8003",
                category="web_operations", 
                tags=["web", "search"]
            ),
            ToolInfo(
                name="calculator",
                description="Perform mathematical calculations",
                parameters={"expression": "string"},
                server_url="http://test:8001",
                category="computation",
                tags=["math", "calculate"]
            )
        ]
    
    def test_entity_extraction(self, selector):
        """Test entity extraction from user messages"""
        test_cases = [
            ("Read the file /path/to/file.txt", ["file_path"]),
            ("Search for information about Python", ["search_query"]),
            ("Calculate 2 + 2 * 3", ["math_expression", "number"]),
            ("Open https://example.com", ["url"]),
            ("Check if nginx process is running", ["process_name"])
        ]
        
        for message, expected_entities in test_cases:
            entities = selector.extract_entities(message)
            for entity_type in expected_entities:
                assert entity_type in entities
    
    def test_intent_detection(self, selector):
        """Test intent detection from user messages"""
        test_cases = [
            ("Read the contents of config.txt", "file_read"),
            ("Search for Python tutorials", "web_search"),
            ("Calculate the sum of 10 and 20", "calculation"),
            ("Get system information", "system_info"),
            ("Find all .py files in the directory", "file_search")
        ]
        
        for message, expected_intent in test_cases:
            entities = selector.extract_entities(message)
            intents = selector.detect_intent(message, entities)
            
            assert len(intents) > 0
            top_intent, confidence = intents[0]
            assert top_intent == expected_intent
            assert confidence > 0
    
    def test_semantic_similarity(self, selector, sample_tools):
        """Test semantic similarity calculation"""
        test_cases = [
            ("read a file", sample_tools[0], True),  # file tool should match
            ("search the web", sample_tools[1], True),  # web tool should match
            ("do math calculation", sample_tools[2], True),  # calculator should match
            ("cook dinner", sample_tools[0], False)  # no tool should match well
        ]
        
        for message, tool, should_match in test_cases:
            similarity = selector.calculate_semantic_similarity(message, tool)
            if should_match:
                assert similarity > 0.3  # Should have reasonable similarity
            else:
                assert similarity < 0.2  # Should have low similarity
    
    @pytest.mark.asyncio
    async def test_tool_selection_integration(self, selector, sample_tools):
        """Test end-to-end tool selection"""
        # Mock the client's tool discovery
        async def mock_discover_tools():
            return {"http://test:8001": sample_tools}
        
        selector.client.discover_all_tools = mock_discover_tools
        
        test_cases = [
            ("Read the file config.txt", "read_file"),
            ("Search for Python tutorials", "web_search"), 
            ("Calculate 15 + 25", "calculator")
        ]
        
        for message, expected_tool in test_cases:
            matches = await selector.select_tools(message, max_tools=3)
            
            assert len(matches) > 0
            top_match = matches[0]
            assert top_match.tool.name == expected_tool
            assert top_match.confidence > 0.5
            assert len(top_match.reasons) > 0

class TestParameterExtraction:
    """Test parameter extraction from user messages"""
    
    def test_file_path_extraction(self):
        """Test extraction of file paths"""
        tool = ToolInfo(
            name="read_file",
            description="Read a file",
            parameters={"file_path": "string"},
            server_url="http://test:8002",
            category="file_operations"
        )
        
        match = ToolMatch(
            tool=tool,
            confidence=0.8,
            reasons=["test"],
            entities={"file_path": ["/path/to/file.txt"]}
        )
        
        message = "Read the file /path/to/file.txt"
        params = extract_parameters_from_message(message, match)
        
        assert params["file_path"] == "/path/to/file.txt"
    
    def test_search_query_extraction(self):
        """Test extraction of search queries"""
        tool = ToolInfo(
            name="web_search",
            description="Search the web",
            parameters={"query": "string"},
            server_url="http://test:8003",
            category="web_operations"
        )
        
        match = ToolMatch(
            tool=tool,
            confidence=0.8,
            reasons=["test"],
            entities={"search_query": ["Python tutorials"]}
        )
        
        message = "Search for Python tutorials"
        params = extract_parameters_from_message(message, match)
        
        assert params["query"] == "Python tutorials"
    
    def test_math_expression_extraction(self):
        """Test extraction of mathematical expressions"""
        tool = ToolInfo(
            name="calculator",
            description="Calculate expressions",
            parameters={"expression": "string"},
            server_url="http://test:8001",
            category="computation"
        )
        
        match = ToolMatch(
            tool=tool,
            confidence=0.8,
            reasons=["test"],
            entities={"math_expression": ["2 + 2"]}
        )
        
        message = "Calculate 2 + 2"
        params = extract_parameters_from_message(message, match)
        
        assert "2 + 2" in params["expression"]

class TestMCPServerEndpoints:
    """Test MCP server endpoint functionality"""
    
    @pytest.mark.asyncio
    async def test_file_server_endpoints(self):
        """Test file server tool listing"""
        # This would require running the actual file server
        # For now, just test the structure
        from mcp_servers.file_server import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        response = client.get("/tools")
        
        assert response.status_code == 200
        tools = response.json()
        assert isinstance(tools, list)
        assert len(tools) > 0
        
        # Check for expected tools
        tool_names = [tool["name"] for tool in tools]
        expected_tools = ["read_file", "write_file", "list_directory", "search_files"]
        for expected_tool in expected_tools:
            assert expected_tool in tool_names
    
    @pytest.mark.asyncio
    async def test_web_server_endpoints(self):
        """Test web server tool listing"""
        from mcp_servers.web_server import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        response = client.get("/tools")
        
        assert response.status_code == 200
        tools = response.json()
        assert isinstance(tools, list)
        assert len(tools) > 0
        
        # Check for expected tools
        tool_names = [tool["name"] for tool in tools]
        expected_tools = ["web_search", "fetch_webpage", "url_info"]
        for expected_tool in expected_tools:
            assert expected_tool in tool_names
    
    @pytest.mark.asyncio 
    async def test_system_server_endpoints(self):
        """Test system server tool listing"""
        from mcp_servers.system_server import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        response = client.get("/tools")
        
        assert response.status_code == 200
        tools = response.json()
        assert isinstance(tools, list)
        assert len(tools) > 0
        
        # Check for expected tools
        tool_names = [tool["name"] for tool in tools]
        expected_tools = ["system_info", "process_list", "memory_info"]
        for expected_tool in expected_tools:
            assert expected_tool in tool_names

if __name__ == "__main__":
    pytest.main([__file__, "-v"])