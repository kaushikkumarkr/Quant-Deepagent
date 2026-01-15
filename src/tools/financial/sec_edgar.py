import os
import glob
from typing import List, Dict, Optional
from sec_edgar_downloader import Downloader
from bs4 import BeautifulSoup
from src.utils.logging import setup_logging
from src.utils.retry import with_retry

logger = setup_logging(__name__)

class SECTool:
    """
    Tool for downloading and processing SEC filings (10-K, 10-Q).
    """
    
    def __init__(self, email: str = "your_email@example.com", company: str = "QuantMind"):
        # SEC requires a User-Agent string with email and company name
        self.downloader = Downloader(company, email, os.path.join(os.getcwd(), "data/sec_filings"))
        self.download_dir = os.path.join(os.getcwd(), "data/sec_filings")

    @with_retry(max_attempts=3)
    def download_filings(self, ticker: str, filing_type: str = "10-K", limit: int = 1) -> List[str]:
        """
        Download the latest filings for a ticker.
        Returns list of absolute paths to downloaded files.
        """
        logger.debug(f"Downloading {limit} {filing_type} filings for {ticker}...")
        try:
            self.downloader.get(filing_type, ticker, limit=limit)
            
            # Find the downloaded files
            # Structure: data/sec_filings/sec-edgar-filings/{ticker}/{filing_type}/{accession_number}/*.txt
            search_path = os.path.join(
                self.download_dir, 
                "sec-edgar-filings", 
                ticker, 
                filing_type, 
                "*", 
                "*.txt" # Usually they are full-submission.txt or similar
            ) # Note: newer versions might download as html, check library behavior. 
              # Standard sec-edgar-downloader downloads HTML/XML usually. 
              # Let's adjust to find *.* and filter
            
            files = glob.glob(search_path)
            # Filter for the main document usually named same as accession
            # For simplicity, we return all found non-image files
            valid_files = [f for f in files if f.endswith(".txt") or f.endswith(".html") or f.endswith(".xml")]
            
            logger.debug(f"Found {len(valid_files)} downloaded files for {ticker}.")
            return valid_files
            
        except Exception as e:
            logger.error(f"Failed to download filings for {ticker}: {e}")
            return []

    def extract_text(self, file_path: str) -> str:
        """
        Extract clean text from an SEC filing (HTML/XML/Text).
        """
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            
            soup = BeautifulSoup(content, "lxml")
            
            # Remove scripts and styles
            for script in soup(["script", "style"]):
                script.decompose()
                
            text = soup.get_text(separator="\n")
            
            # Simple cleaning
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            clean_text = '\n'.join(chunk for chunk in chunks if chunk)
            
            return clean_text
        except Exception as e:
            logger.error(f"Error parsing file {file_path}: {e}")
            return ""
