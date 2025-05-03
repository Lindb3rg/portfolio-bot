import re
import requests
import subprocess
from typing import Optional, List, Tuple
import os

from dotenv import load_dotenv
import logging


logger = logging.basicConfig(
    level=logging.INFO,  
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='presigned-logs.log',  # Save logs to this file
    filemode='a'  # 'w' to overwrite, 'a' to append
)

load_dotenv()

S3 = os.getenv('S3_BUCKET_NAME').strip()


def _extract_urls(raw_data) -> List[Tuple[str, str]]:
    """Extract S3 URLs and their file paths from the raw data."""
    url_pattern = fr'https://{S3}\.s3\..*?\.amazonaws\.com/([^?]+)\?'
    urls = []
    for url_match in re.finditer(fr'(https://{S3}\.s3\..*?\.amazonaws\.com/[^\s"\']+)', raw_data):
        full_url = url_match.group(1)
        file_path_match = re.search(url_pattern, full_url)
        if file_path_match:
            file_path = file_path_match.group(1)
            urls.append((full_url, file_path))
    
    return urls


def _generate_presigned_url(file_path) -> Optional[str]:
    """Generate a new presigned URL for the given file path."""
    try:
        new_url = subprocess.run(
            ["aws", "s3", "presign", f"s3://{S3}/{file_path}", 
             "--expires-in", "604800"],
            capture_output=True, text=True, check=True
        )
        return new_url.stdout.strip()
    
    except subprocess.CalledProcessError as e:
        logger.error(f"Error generating pre-signed URL: {e}")
        logger.error(f"Error output: {e.stderr}")
        return None
    

def _update_config_file(updated_raw_data) -> None:
    """Update the certificates.md file with new URLs."""
    try:
        
        with open('knowledge-base/certifications/certificates.md', 'w') as f:
            f.write(updated_raw_data)
            
        logger.info("Updated certificates.md with new pre-signed URLs")
    except Exception as e:
        logger.error(f"Error updating certificates.md file: {e}")


def validate_and_update_urls() -> None:
    """Validate URLs in the certificates.md file and update expired ones."""
    try:
        with open('knowledge-base/certifications/certificates.md', 'r') as f:
            raw_data = f.read()
            
        urls = _extract_urls(raw_data)
        updated = False
        
        for url, file_path in urls:
            try:
                response = requests.head(url, timeout=5)
                if response.status_code == 403:
                    if 'application/xml' in response.headers.get('Content-Type', ''):
                        error_response = requests.get(url, timeout=5)
                        if "<Message>Request has expired</Message>" in error_response.text:
                            
                            logger.warning(f"URL for {file_path} has expired. Generating new pre-signed URL...")
                            new_url = _generate_presigned_url(file_path)
                            
                            if new_url:
                                raw_data = raw_data.replace(url, new_url)
                                logger.info(f"Updated URL for {file_path}")
                                updated = True
                                
            except Exception as e:
                logger.error(f"Error checking URL {url}: {e}")
        
        if updated:
            _update_config_file(raw_data)
    except Exception as e:
        logger.error(f"Error in validate_and_update_urls: {e}")
                
                
if __name__ == "__main__":
    validate_and_update_urls()