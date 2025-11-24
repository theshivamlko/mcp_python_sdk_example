
import os
import json
import logging
from typing import List, Dict, Optional
from firecrawl import FirecrawlApp
from urllib.parse import urlparse
from datetime import datetime
from pathlib import Path
from mcp.server.fastmcp import FastMCP

from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

SCRAPE_DIR = "scraped_content"
METADATA_FILE = Path(SCRAPE_DIR) / "scraped_metadata.json"

mcp = FastMCP("llm_inference")

@mcp.tool()
def scrape_websites(
    websites: Dict[str, str],
    formats: List[str] = ['markdown', 'html'],
    api_key: Optional[str] = None
) -> List[str]:
    """
    Scrape multiple websites using Firecrawl and store their content.
    
    Args:
        websites: Dictionary of provider_name -> URL mappings
        formats: List of formats to scrape ['markdown', 'html'] (default: both)
        api_key: Firecrawl API key (if None, expects environment variable)
        
    Returns:
        List of provider names for successfully scraped websites
    """
    
    if api_key is None:
        api_key = os.getenv('FIRECRAWL_API_KEY')
        if not api_key:
            raise ValueError("API key must be provided or set as FIRECRAWL_API_KEY environment variable")
    
    app = FirecrawlApp(api_key=api_key)
    os.makedirs(SCRAPE_DIR, exist_ok=True)
    try:
        scraped_metadata = json.loads(METADATA_FILE.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        scraped_metadata = {}

    successful_scrapes: List[str] = []

    for provider_name, url in websites.items():
        metadata = {
            "provider_name": provider_name,
            "url": url,
            "domain": urlparse(url).netloc,
            "scraped_at": datetime.utcnow().isoformat(),
            "formats": formats,
            "success": False,
        }

        try:
            logger.info(f"Scraping {provider_name}: {url}")
            scrape_result = app.scrape_url(url, formats=formats).model_dump()

            if scrape_result.get("success", False):
                data = scrape_result.get("data", {}) or {}
                content_files: Dict[str, str] = {}
                for format_type in formats:
                    content = data.get(format_type)
                    if not content:
                        continue
                    filename = f"{provider_name}_{format_type}.txt"
                    file_path = Path(SCRAPE_DIR) / filename
                    file_path.write_text(content, encoding="utf-8")
                    content_files[format_type] = filename

                metadata["content_files"] = content_files
                meta_candidate = data.get("metadata") if isinstance(data, dict) else None
                if isinstance(meta_candidate, dict):
                    meta_info = meta_candidate
                    metadata["title"] = meta_info.get("title")
                    metadata["description"] = meta_info.get("description")
                else:
                    metadata["title"] = scrape_result.get("title")
                    metadata["description"] = scrape_result.get("description")
                metadata["success"] = True
                successful_scrapes.append(provider_name)
            else:
                metadata["error"] = scrape_result.get("error", "Unknown error")
                logger.error(f"Failed to scrape {provider_name}: {metadata['error']}")
        except Exception as exc:
            metadata["error"] = str(exc)
            metadata["success"] = False
            logger.error(f"Exception while scraping {provider_name}: {exc}")

        scraped_metadata[provider_name] = metadata

    METADATA_FILE.write_text(json.dumps(scraped_metadata, indent=2), encoding="utf-8")
    logger.info(f"Scraping complete. Successful providers: {successful_scrapes}")
    return successful_scrapes

@mcp.tool()
def extract_scraped_info(identifier: str) -> str:
    """
    Extract information about a scraped website.
    
    Args:
        identifier: The provider name, full URL, or domain to look for
        
    Returns:
        Formatted JSON string with the scraped information
    """
    
    logger.info(f"Extracting information for identifier: {identifier}")

    try:
        scraped_metadata = json.loads(METADATA_FILE.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return f"There's no saved information related to identifier '{identifier}'."

    identifier_value = identifier.lower()
    for provider_name, metadata in scraped_metadata.items():
        values_to_check = [provider_name, metadata.get("url", ""), metadata.get("domain", "")]
        normalized = [value.lower() for value in values_to_check if isinstance(value, str)]
        if identifier_value not in normalized:
            continue
        result = dict(metadata)
        content_files = metadata.get("content_files") or {}
        if content_files:
            content: Dict[str, str] = {}
            for format_type, filename in content_files.items():
                file_path = Path(SCRAPE_DIR) / filename
                try:
                    content[format_type] = file_path.read_text(encoding="utf-8")
                except FileNotFoundError:
                    content[format_type] = ""
            result["content"] = content
        return json.dumps(result, indent=2)

    return f"There's no saved information related to identifier '{identifier}'."
    

if __name__ == "__main__":
    mcp.run(transport="stdio")