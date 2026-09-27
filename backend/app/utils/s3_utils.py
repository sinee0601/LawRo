"""
AWS S3 Utilities
Functions for uploading/downloading files to/from S3
"""

import json
import logging
import os
from typing import List, Optional
from uuid import uuid4

import boto3
from botocore.exceptions import ClientError, NoCredentialsError, PartialCredentialsError

from ..config import settings

logger = logging.getLogger(__name__)

# S3 client
_s3_client = None


def get_s3_client():
    """Get or initialize S3 client"""
    global _s3_client

    if _s3_client is not None:
        return _s3_client

    try:
        _s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        logger.info("S3 client initialized successfully")
        return _s3_client
    except (NoCredentialsError, PartialCredentialsError) as e:
        logger.error(f"AWS credentials error: {e}")
        return None
    except Exception as e:
        logger.error(f"S3 client initialization failed: {e}")
        return None


def upload_image_to_s3(
    bucket: str,
    file,
    user_id: str,
    contract_id: str,
    custom_filename: Optional[str] = None
) -> str:
    """
    Upload image to S3

    Args:
        bucket: S3 bucket name
        file: File object to upload
        user_id: User ID
        contract_id: Contract ID
        custom_filename: Custom filename (optional)

    Returns:
        str: S3 object key

    Raises:
        Exception: If upload fails
    """
    s3 = get_s3_client()
    if not s3:
        raise Exception("S3 client not initialized. Check AWS credentials.")

    try:
        # Generate filename
        if custom_filename:
            key = f"user_{user_id}/contracts/{contract_id}/{custom_filename}"
        else:
            ext = file.filename.split(".")[-1] if file.filename and "." in file.filename else "jpg"
            key = f"user_{user_id}/contracts/{contract_id}/contract_{uuid4().hex[:8]}.{ext}"

        logger.info(f"Uploading to S3: {key}")

        # Reset file pointer
        file.file.seek(0)

        # Check file size
        file_content = file.file.read()
        file_size = len(file_content)

        if file_size == 0:
            raise Exception(f"File is empty: {file.filename}")

        logger.info(f"File size: {file_size} bytes")

        # Reset file pointer
        file.file.seek(0)

        # Upload to S3
        s3.upload_fileobj(
            file.file,
            bucket,
            key,
            ExtraArgs={
                "ContentType": file.content_type or "image/jpeg",
                "Metadata": {
                    "user_id": user_id,
                    "contract_id": contract_id,
                    "original_filename": file.filename or "unknown",
                    "file_size": str(file_size)
                }
            }
        )

        logger.info(f"S3 upload successful: {key}")
        return key

    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_msg = f"S3 upload failed (ClientError): {error_code} - {e.response['Error']['Message']}"
        logger.error(error_msg)
        raise Exception(error_msg)
    except Exception as e:
        error_msg = f"S3 upload failed: {str(e)}"
        logger.error(error_msg)
        raise Exception(error_msg)


def download_s3_files(
    bucket_name: str,
    s3_keys: List[str],
    local_dir: Optional[str] = None
) -> List[str]:
    """
    Download files from S3

    Args:
        bucket_name: S3 bucket name
        s3_keys: List of S3 object keys to download
        local_dir: Local directory to save files (default: ./tmp)

    Returns:
        list: List of local file paths

    Raises:
        Exception: If download fails
    """
    s3 = get_s3_client()
    if not s3:
        raise Exception("S3 client not initialized.")

    if local_dir is None:
        local_dir = "./tmp"

    try:
        os.makedirs(local_dir, exist_ok=True)
        local_paths = []

        for s3_key in s3_keys:
            try:
                filename = os.path.basename(s3_key)
                local_path = os.path.join(local_dir, filename)

                logger.info(f"Downloading from S3: {s3_key} -> {local_path}")

                s3.download_file(bucket_name, s3_key, local_path)
                local_paths.append(local_path)

                logger.info(f"S3 download successful: {filename}")

            except ClientError as e:
                error_code = e.response['Error']['Code']
                if error_code == 'NoSuchKey':
                    logger.error(f"S3 file not found: {s3_key}")
                    raise Exception(f"File not found in S3: {s3_key}")
                else:
                    logger.error(f"S3 download failed: {s3_key}, error: {error_code}")
                    raise Exception(f"S3 download failed: {error_code}")
            except Exception as e:
                logger.error(f"Download failed: {s3_key}, error: {str(e)}")
                raise Exception(f"File download failed: {s3_key} - {str(e)}")

        return local_paths

    except Exception as e:
        logger.error(f"S3 download processing failed: {str(e)}")
        raise


def upload_json_to_s3(bucket: str, key: str, data: dict):
    """
    Upload JSON data to S3

    Args:
        bucket: S3 bucket name
        key: S3 object key
        data: Dictionary data to upload

    Raises:
        Exception: If upload fails
    """
    s3 = get_s3_client()
    if not s3:
        raise Exception("S3 client not initialized.")

    try:
        logger.info(f"Uploading JSON to S3: {key}")

        json_content = json.dumps(data, ensure_ascii=False, indent=2)

        s3.put_object(
            Bucket=bucket,
            Key=key,
            Body=json_content.encode('utf-8'),
            ContentType="application/json",
            Metadata={
                "data_type": "json",
                "content_length": str(len(json_content))
            }
        )

        logger.info(f"JSON upload successful: {key}")

    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_msg = f"JSON upload failed (ClientError): {error_code}"
        logger.error(error_msg)
        raise Exception(error_msg)
    except Exception as e:
        error_msg = f"JSON upload failed: {str(e)}"
        logger.error(error_msg)
        raise Exception(error_msg)


def test_s3_connection(bucket_name: str) -> bool:
    """
    Test S3 connection and permissions

    Args:
        bucket_name: Bucket name to test

    Returns:
        bool: Connection success status
    """
    s3 = get_s3_client()
    if not s3:
        logger.error("S3 client not initialized.")
        return False

    try:
        logger.info(f"Testing S3 connection: {bucket_name}")

        # Check bucket existence
        s3.head_bucket(Bucket=bucket_name)

        logger.info(f"S3 connection test successful: {bucket_name}")
        return True

    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '404':
            logger.error(f"S3 bucket does not exist: {bucket_name}")
        elif error_code == '403':
            logger.error(f"S3 bucket access denied: {bucket_name}")
        else:
            logger.error(f"S3 connection error: {error_code}")
        return False
    except Exception as e:
        logger.error(f"S3 connection test failed: {str(e)}")
        return False


def list_s3_files(bucket_name: str, prefix: str) -> List[str]:
    """
    List files in S3 bucket with given prefix

    Args:
        bucket_name: S3 bucket name
        prefix: Object key prefix

    Returns:
        list: List of S3 object keys
    """
    s3 = get_s3_client()
    if not s3:
        raise Exception("S3 client not initialized.")

    try:
        logger.info(f"Listing S3 objects: {prefix}")

        paginator = s3.get_paginator("list_objects_v2")
        s3_keys = []

        for page in paginator.paginate(Bucket=bucket_name, Prefix=prefix):
            contents = page.get("Contents", [])
            for obj in contents:
                key = obj["Key"]
                # Filter image files only
                if key.lower().endswith(('.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp')):
                    s3_keys.append(key)

        logger.info(f"Found {len(s3_keys)} image files")
        return s3_keys

    except Exception as e:
        logger.error(f"Failed to list S3 objects: {e}")
        raise
