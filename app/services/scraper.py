import httpx
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re

class ScraperService:
    @staticmethod
    def is_url(text: str) -> bool:
        """
        Check if the text is a valid HTTP/HTTPS URL.
        """
        text = text.strip()
        # Basic check to avoid parsing long text blocks
        if " " in text or "\n" in text:
            return False
            
        try:
            parsed = urlparse(text)
            return parsed.scheme in ("http", "https") and bool(parsed.netloc)
        except Exception:
            return False

    @classmethod
    async def scrape_url(cls, url: str) -> str:
        """
        Asynchronously fetch and extract main readable text from a URL.
        """
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        try:
            async with httpx.AsyncClient(timeout=6.0, follow_redirects=True) as client:
                response = await client.get(url, headers=headers)
                
                if response.status_code != 200:
                    raise Exception(f"HTTP error {response.status_code} loading URL.")
                    
                html_content = response.text
                
                # Parse HTML
                soup = BeautifulSoup(html_content, "html.parser")
                
                # Remove non-readable elements
                for element in soup(["script", "style", "header", "footer", "nav", "aside", "form", "iframe"]):
                    element.decompose()
                    
                # Get text
                text = soup.get_text(separator=" ")
                
                # Clean up whitespace
                text = re.sub(r'\s+', ' ', text).strip()
                
                # Limit size to prevent hitting LLM token limits (approx 10,000 characters)
                if len(text) > 10000:
                    text = text[:10000] + "... [Text truncated for analysis]"
                    
                if not text:
                    raise Exception("Scraped page content is empty or unreadable.")
                    
                return text
                
        except httpx.RequestError as e:
            raise Exception(f"Network error trying to access the URL: {str(e)}")
        except Exception as e:
            raise Exception(f"Failed to scrape webpage: {str(e)}")
