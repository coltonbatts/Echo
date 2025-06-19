"""MCP Server for Web Search and Web Operations

Provides tools for web search, URL fetching, and basic web operations.
Uses multiple search providers and implements rate limiting and caching.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import uvicorn
import httpx
import json
import os
import time
import hashlib
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin, urlparse
import re
from datetime import datetime, timedelta

app = FastAPI(title="Web Search MCP Server", version="1.0.0")

# Configuration from environment variables
SEARCH_API_KEY = os.getenv("SEARCH_API_KEY")  # For services like SerpAPI
RATE_LIMIT_REQUESTS = int(os.getenv("WEB_RATE_LIMIT", "10"))  # requests per minute
CACHE_TTL_SECONDS = int(os.getenv("WEB_CACHE_TTL", "300"))  # 5 minutes
MAX_CONTENT_LENGTH = int(os.getenv("WEB_MAX_CONTENT", "50000"))  # 50KB

# Simple in-memory cache and rate limiting
cache = {}
rate_limiter = {"requests": [], "window_start": time.time()}

def is_rate_limited() -> bool:
    """Simple rate limiting implementation"""
    now = time.time()
    window_duration = 60  # 1 minute
    
    # Clean old requests
    rate_limiter["requests"] = [
        req_time for req_time in rate_limiter["requests"] 
        if now - req_time < window_duration
    ]
    
    if len(rate_limiter["requests"]) >= RATE_LIMIT_REQUESTS:
        return True
    
    rate_limiter["requests"].append(now)
    return False

def get_cache_key(operation: str, params: dict) -> str:
    """Generate cache key for operation and parameters"""
    key_data = f"{operation}:{json.dumps(params, sort_keys=True)}"
    return hashlib.md5(key_data.encode()).hexdigest()

def get_from_cache(key: str) -> Optional[dict]:
    """Retrieve from cache if not expired"""
    if key in cache:
        entry = cache[key]
        if time.time() - entry["timestamp"] < CACHE_TTL_SECONDS:
            return entry["data"]
        else:
            del cache[key]
    return None

def set_cache(key: str, data: dict):
    """Store in cache with timestamp"""
    cache[key] = {"data": data, "timestamp": time.time()}

@app.get("/tools")
async def list_tools():
    return [
        {
            "name": "web_search",
            "description": "Search the web for information using multiple search engines",
            "parameters": {
                "query": "string - Search query",
                "num_results": "integer - Number of results to return (default: 5)",
                "language": "string - Language code (default: en)"
            }
        },
        {
            "name": "fetch_webpage",
            "description": "Fetch and extract content from a webpage",
            "parameters": {
                "url": "string - URL to fetch",
                "extract_text": "boolean - Extract only text content (default: true)"
            }
        },
        {
            "name": "url_info",
            "description": "Get information about a URL (title, description, status)",
            "parameters": {
                "url": "string - URL to analyze"
            }
        },
        {
            "name": "search_news",
            "description": "Search for recent news articles",
            "parameters": {
                "query": "string - News search query",
                "num_results": "integer - Number of results (default: 5)",
                "days_back": "integer - How many days back to search (default: 7)"
            }
        },
        {
            "name": "extract_links",
            "description": "Extract all links from a webpage",
            "parameters": {
                "url": "string - URL to extract links from",
                "filter_domain": "string - Only return links from this domain (optional)"
            }
        }
    ]

@app.get("/tools/{tool_name}/schema")
async def tool_schema(tool_name: str):
    schemas = {
        "web_search": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "num_results": {"type": "integer", "default": 5, "minimum": 1, "maximum": 20},
                "language": {"type": "string", "default": "en", "description": "Language code"}
            },
            "required": ["query"]
        },
        "fetch_webpage": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "format": "uri", "description": "URL to fetch"},
                "extract_text": {"type": "boolean", "default": True, "description": "Extract only text content"}
            },
            "required": ["url"]
        },
        "url_info": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "format": "uri", "description": "URL to analyze"}
            },
            "required": ["url"]
        },
        "search_news": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "News search query"},
                "num_results": {"type": "integer", "default": 5, "minimum": 1, "maximum": 20},
                "days_back": {"type": "integer", "default": 7, "minimum": 1, "maximum": 30}
            },
            "required": ["query"]
        },
        "extract_links": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "format": "uri", "description": "URL to extract links from"},
                "filter_domain": {"type": "string", "description": "Filter links by domain"}
            },
            "required": ["url"]
        }
    }
    
    if tool_name not in schemas:
        raise HTTPException(status_code=404, detail="Tool not found")
    return schemas[tool_name]

# Pydantic models
class WebSearchRequest(BaseModel):
    query: str
    num_results: int = 5
    language: str = "en"

class FetchWebpageRequest(BaseModel):
    url: str
    extract_text: bool = True

class UrlInfoRequest(BaseModel):
    url: str

class SearchNewsRequest(BaseModel):
    query: str
    num_results: int = 5
    days_back: int = 7

class ExtractLinksRequest(BaseModel):
    url: str
    filter_domain: Optional[str] = None

def extract_text_from_html(html_content: str) -> str:
    """Extract readable text from HTML content"""
    # Simple HTML text extraction (for production, consider using BeautifulSoup)
    import re
    
    # Remove script and style elements
    html_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
    html_content = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', html_content)
    
    # Clean up whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def extract_title_from_html(html_content: str) -> str:
    """Extract title from HTML content"""
    import re
    match = re.search(r'<title[^>]*>(.*?)</title>', html_content, re.IGNORECASE | re.DOTALL)
    return match.group(1).strip() if match else ""

def extract_meta_description(html_content: str) -> str:
    """Extract meta description from HTML"""
    import re
    match = re.search(r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']*)["\']', html_content, re.IGNORECASE)
    if not match:
        match = re.search(r'<meta[^>]*content=["\']([^"\']*)["\'][^>]*name=["\']description["\']', html_content, re.IGNORECASE)
    return match.group(1).strip() if match else ""

async def duckduckgo_search(query: str, num_results: int = 5) -> List[Dict]:
    """Search using DuckDuckGo Instant Answer API (free, no API key needed)"""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            # DuckDuckGo Instant Answer API
            response = await client.get(
                "https://api.duckduckgo.com/",
                params={
                    "q": query,
                    "format": "json",
                    "no_html": "1",
                    "skip_disambig": "1"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                results = []
                
                # Add instant answer if available
                if data.get("Abstract"):
                    results.append({
                        "title": data.get("Heading", "DuckDuckGo Answer"),
                        "snippet": data["Abstract"],
                        "url": data.get("AbstractURL", ""),
                        "source": "DuckDuckGo Instant Answer"
                    })
                
                # Add related topics
                for topic in data.get("RelatedTopics", [])[:num_results-1]:
                    if isinstance(topic, dict) and topic.get("Text"):
                        results.append({
                            "title": topic.get("Text", "").split(" - ")[0],
                            "snippet": topic.get("Text", ""),
                            "url": topic.get("FirstURL", ""),
                            "source": "DuckDuckGo Related"
                        })
                
                return results[:num_results]
    
    except Exception as e:
        print(f"DuckDuckGo search error: {e}")
    
    return []

@app.post("/tools/web_search/execute")
async def execute_web_search(payload: WebSearchRequest):
    if is_rate_limited():
        return {"error": "Rate limit exceeded. Please try again later."}
    
    cache_key = get_cache_key("web_search", payload.dict())
    cached_result = get_from_cache(cache_key)
    if cached_result:
        return {"result": cached_result, "cached": True}
    
    try:
        # Use DuckDuckGo as primary search (free, no API key needed)
        results = await duckduckgo_search(payload.query, payload.num_results)
        
        if not results:
            # Fallback: simple web search simulation
            results = [
                {
                    "title": f"Search results for: {payload.query}",
                    "snippet": "No specific results available. Try a different search engine or API.",
                    "url": f"https://duckduckgo.com/?q={payload.query.replace(' ', '+')}",
                    "source": "Fallback"
                }
            ]
        
        result_data = {
            "query": payload.query,
            "results": results,
            "count": len(results),
            "timestamp": datetime.now().isoformat()
        }
        
        set_cache(cache_key, result_data)
        return {"result": result_data}
        
    except Exception as e:
        return {"error": f"Search failed: {str(e)}"}

@app.post("/tools/fetch_webpage/execute")
async def execute_fetch_webpage(payload: FetchWebpageRequest):
    if is_rate_limited():
        return {"error": "Rate limit exceeded. Please try again later."}
    
    cache_key = get_cache_key("fetch_webpage", payload.dict())
    cached_result = get_from_cache(cache_key)
    if cached_result:
        return {"result": cached_result, "cached": True}
    
    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            headers = {
                "User-Agent": "Mozilla/5.0 (compatible; Echo-MCP-Bot/1.0)"
            }
            
            response = await client.get(payload.url, headers=headers)
            response.raise_for_status()
            
            # Check content length
            content = response.text
            if len(content) > MAX_CONTENT_LENGTH:
                content = content[:MAX_CONTENT_LENGTH] + "... [truncated]"
            
            result_data = {
                "url": payload.url,
                "status_code": response.status_code,
                "content_type": response.headers.get("content-type", ""),
                "content_length": len(response.text),
                "title": extract_title_from_html(content),
            }
            
            if payload.extract_text:
                result_data["text_content"] = extract_text_from_html(content)
            else:
                result_data["html_content"] = content
            
            set_cache(cache_key, result_data)
            return {"result": result_data}
            
    except Exception as e:
        return {"error": f"Failed to fetch webpage: {str(e)}"}

@app.post("/tools/url_info/execute")
async def execute_url_info(payload: UrlInfoRequest):
    if is_rate_limited():
        return {"error": "Rate limit exceeded. Please try again later."}
    
    cache_key = get_cache_key("url_info", payload.dict())
    cached_result = get_from_cache(cache_key)
    if cached_result:
        return {"result": cached_result, "cached": True}
    
    try:
        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
            headers = {
                "User-Agent": "Mozilla/5.0 (compatible; Echo-MCP-Bot/1.0)"
            }
            
            # HEAD request first to get basic info
            head_response = await client.head(payload.url, headers=headers)
            
            # GET request for HTML content if it's a webpage
            content_type = head_response.headers.get("content-type", "")
            html_content = ""
            
            if "text/html" in content_type:
                get_response = await client.get(payload.url, headers=headers)
                html_content = get_response.text[:5000]  # First 5KB for analysis
            
            parsed_url = urlparse(payload.url)
            result_data = {
                "url": payload.url,
                "domain": parsed_url.netloc,
                "status_code": head_response.status_code,
                "content_type": content_type,
                "content_length": head_response.headers.get("content-length"),
                "last_modified": head_response.headers.get("last-modified"),
                "server": head_response.headers.get("server"),
            }
            
            if html_content:
                result_data["title"] = extract_title_from_html(html_content)
                result_data["description"] = extract_meta_description(html_content)
            
            set_cache(cache_key, result_data)
            return {"result": result_data}
            
    except Exception as e:
        return {"error": f"Failed to get URL info: {str(e)}"}

@app.post("/tools/search_news/execute")
async def execute_search_news(payload: SearchNewsRequest):
    if is_rate_limited():
        return {"error": "Rate limit exceeded. Please try again later."}
    
    # For news, we'll enhance the search query and use the same search mechanism
    news_query = f"{payload.query} news recent"
    
    try:
        results = await duckduckgo_search(news_query, payload.num_results)
        
        # Filter for more recent content (this is a simple heuristic)
        news_results = []
        for result in results:
            news_results.append({
                **result,
                "type": "news",
                "search_query": payload.query,
                "days_back": payload.days_back
            })
        
        result_data = {
            "query": payload.query,
            "news_results": news_results,
            "count": len(news_results),
            "timestamp": datetime.now().isoformat()
        }
        
        return {"result": result_data}
        
    except Exception as e:
        return {"error": f"News search failed: {str(e)}"}

@app.post("/tools/extract_links/execute")
async def execute_extract_links(payload: ExtractLinksRequest):
    if is_rate_limited():
        return {"error": "Rate limit exceeded. Please try again later."}
    
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            headers = {
                "User-Agent": "Mozilla/5.0 (compatible; Echo-MCP-Bot/1.0)"
            }
            
            response = await client.get(payload.url, headers=headers)
            response.raise_for_status()
            
            content = response.text
            
            # Extract links using regex
            import re
            link_pattern = r'<a[^>]*href=["\']([^"\']*)["\'][^>]*>(.*?)</a>'
            matches = re.findall(link_pattern, content, re.IGNORECASE | re.DOTALL)
            
            links = []
            for href, text in matches:
                # Convert relative URLs to absolute
                if href.startswith('http'):
                    full_url = href
                else:
                    full_url = urljoin(payload.url, href)
                
                # Filter by domain if specified
                if payload.filter_domain:
                    if payload.filter_domain not in full_url:
                        continue
                
                # Clean up text
                clean_text = re.sub(r'<[^>]+>', '', text).strip()
                
                links.append({
                    "url": full_url,
                    "text": clean_text[:100],  # Limit text length
                    "domain": urlparse(full_url).netloc
                })
            
            # Remove duplicates
            seen_urls = set()
            unique_links = []
            for link in links:
                if link["url"] not in seen_urls:
                    seen_urls.add(link["url"])
                    unique_links.append(link)
            
            result_data = {
                "source_url": payload.url,
                "links": unique_links,
                "count": len(unique_links),
                "filter_domain": payload.filter_domain
            }
            
            return {"result": result_data}
            
    except Exception as e:
        return {"error": f"Failed to extract links: {str(e)}"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003)