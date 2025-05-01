import re
import requests
import subprocess
from typing import List, Optional, Tuple
from dotenv import load_dotenv
import os
from utils.logger import logger
from utils.decorators import timer



load_dotenv()

S3 = os.getenv('S3_BUCKET_NAME').strip()

from config.config import CERTIFICATIONS

class CertificateTool:
    def __init__(self):
        self.raw_data = CERTIFICATIONS
        self.s3_bucket = S3
        self.expiry_seconds = 604800  # 7 days
    
    
    @timer
    def _extract_urls(self) -> List[Tuple[str, str]]:
        
        url_pattern = fr'https://{self.s3_bucket}\.s3\..*?\.amazonaws\.com/([^?]+)\?'
        urls = []
        for url_match in re.finditer(fr'(https://{self.s3_bucket}\.s3\..*?\.amazonaws\.com/[^\s"\']+)', self.raw_data):
            full_url = url_match.group(1)
            file_path_match = re.search(url_pattern, full_url)
            if file_path_match:
                file_path = file_path_match.group(1)
                urls.append((full_url, file_path))
        
        return urls
    
    @timer
    def validate_and_update_urls(self) -> None:

        urls = self._extract_urls()
        updated = False
        
        for url, file_path in urls:
            try:
                response = requests.head(url, timeout=5)
                if response.status_code == 403:
                    if 'application/xml' in response.headers.get('Content-Type', ''):
                        error_response = requests.get(url, timeout=5)
                        if "<Message>Request has expired</Message>" in error_response.text:
                            
                            logger.warning(f"URL for {file_path} has expired. Generating new pre-signed URL...")
                            new_url = self._generate_presigned_url(file_path)
                            
                            if new_url:
                                self.raw_data = self.raw_data.replace(url, new_url)
                                updated = True
                                logger.info(f"Updated URL for {file_path}")
                                
            except Exception as e:
                logger.error(f"Error checking URL {url}: {e}")
        
        if updated:
            self._update_config_file()
    
    @timer
    def _generate_presigned_url(self, file_path: str) -> Optional[str]:
        try:
            result = subprocess.run(
                ["aws", "s3", "presign", f"s3://{self.s3_bucket}/{file_path}", 
                 "--expires-in", str(self.expiry_seconds)],
                capture_output=True, text=True, check=True
            )
            
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            logger.error(f"Error generating pre-signed URL: {e}")
            logger.error(f"Error output: {e.stderr}")
            return None
    @timer
    def _update_config_file(self) -> None:
        try:
            with open('config/config.py', 'r') as f:
                config_content = f.read()
            
            pattern = r'(CERTIFICATIONS\s*=\s*""")(.*?)(""")'
            new_config = re.sub(pattern, f'\\1{self.raw_data}\\3', 
                               config_content, flags=re.DOTALL)
            
            with open('config/config.py', 'w') as f:
                f.write(new_config)
                
            logger.info("Updated config.py with new pre-signed URLs")
        except Exception as e:
            logger.error(f"Error updating config file: {e}")
    
    @timer
    def get_filtered_certificates(self, keyword: str = None) -> str:
        
        if keyword == None:
            self.validate_and_update_urls()
            return self.raw_data
            
        
        self.validate_and_update_urls()
        keyword = keyword.lower()
        content_match = re.search(r'<static_context>(.*?)</static_context>', 
                                 self.raw_data, re.DOTALL)
        
        if not content_match:
            return "<static_context>\nNo certificate information found.\n</static_context>"
            
        content = content_match.group(1)
        cert_entries = re.split(r'\n(?=- )', content)
        matching_entries = [entry for entry in cert_entries 
                           if keyword in entry.lower()]
        
        if not matching_entries:
            return f"<static_context>\nNo certificates found matching '{keyword}'.\n</static_context>"
        
        result = "<static_context>\n" + "\n".join(matching_entries) + "\n</static_context>"
        return result