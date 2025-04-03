#!/usr/bin/env python3
import os
import re
import boto3
import logging
from datetime import datetime
from dotenv import load_dotenv


# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv('/app/.env')

def generate_presigned_urls():
    """Generate pre-signed URLs for both certificates."""
    try:
        # Configure AWS client
        s3_client = boto3.client('s3',
                                region_name=os.getenv('AWS_REGION', 'us-east-1'),
                                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'))
        
        # Certificate file paths
        cert1_key = os.getenv('CERTIFICATE1_KEY')
        cert2_key = os.getenv('CERTIFICATE2_KEY')
        cert3_key = os.getenv('CERTIFICATE3_KEY')
        bucket_name = os.getenv('S3_BUCKET_NAME')
        
        # Generate URLs with 8-day expiration (691,200 seconds)
        url1 = s3_client.generate_presigned_url('get_object',
                                               Params={'Bucket': bucket_name, 'Key': cert1_key},
                                               ExpiresIn=691200)
        
        url2 = s3_client.generate_presigned_url('get_object',
                                               Params={'Bucket': bucket_name, 'Key': cert2_key},
                                               ExpiresIn=691200)
        
        url3 = s3_client.generate_presigned_url('get_object',
                                               Params={'Bucket': bucket_name, 'Key': cert3_key},
                                               ExpiresIn=691200)
        
        logger.info(f"Generated pre-signed URLs successfully")
        return url1, url2, url3
    
    except Exception as e:
        logger.error(f"Error generating pre-signed URLs: {str(e)}")
        raise

def update_system_message(url1, url2, url3):
    """Update the system_message.txt file with new URLs."""
    try:
        # Paths
        file_path = os.getenv('FILE_PATH')
        
        # Read content from system_message.txt
        with open(file_path, 'r') as file:
            content = file.read()
        
        # Replace URLs using regex
        pattern1 = r'(\* CERTIFICATE 1 LINK: )https[^\n]*'
        pattern2 = r'(\* CERTIFICATE 2 LINK: )https[^\n]*'
        pattern3 = r'(\* CERTIFICATE 3 LINK: )https[^\n]*'
        
        updated_content = re.sub(pattern1, f'\\1{url1}', content)
        updated_content = re.sub(pattern2, f'\\1{url2}', content)
        updated_content = re.sub(pattern3, f'\\1{url3}', content)
        
        # Add or update timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d')
        if '* Last updated:' in updated_content:
            updated_content = re.sub(r'\* Last updated:.*', f'* Last updated: {timestamp}', updated_content)
        else:
            updated_content += f"\n  * Last updated: {timestamp}"
        
        # Write updated content
        with open(file_path, 'w') as file:
            file.write(updated_content)
        
        logger.info(f"Updated system_message.txt with new URLs")
        return file_path
    
    except Exception as e:
        logger.error(f"Error updating system_message.txt: {str(e)}")
        raise


def main():
    try:
        logger.info("Starting certificate link update process")
        
        # Generate pre-signed URLs
        url1, url2, url3 = generate_presigned_urls()
        
        # Update system_message.txt with new URLs
        update_system_message(url1, url2, url3)
        
        logger.info("Certificate link update process completed successfully")
    
    except Exception as e:
        logger.error(f"Error in main process: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main()