import boto3
import os
import json
import logging
from uuid import uuid4
from botocore.exceptions import ClientError, NoCredentialsError, PartialCredentialsError
from config.settings import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION, TMP_DIR

# 로깅 설정
logger = logging.getLogger(__name__)

# S3 클라이언트 초기화
try:
    s3 = boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION
    )
    logger.info("✅ S3 클라이언트 초기화 성공")
except (NoCredentialsError, PartialCredentialsError) as e:
    logger.error(f"❌ AWS 인증 정보 오류: {e}")
    s3 = None
except Exception as e:
    logger.error(f"❌ S3 클라이언트 초기화 실패: {e}")
    s3 = None

# ✅ 1. 이미지 업로드 (사용자 → S3)
def upload_image_to_s3(bucket: str, file, user_id: str, contract_id: str, custom_filename: str = None) -> str:
    """
    이미지를 S3에 업로드
    
    Args:
        bucket: S3 버킷 이름
        file: 업로드할 파일 객체
        user_id: 사용자 ID
        contract_id: 계약서 ID
        custom_filename: 사용자 지정 파일명 (선택사항)
    
    Returns:
        str: S3 객체 키
    
    Raises:
        Exception: 업로드 실패 시
    """
    if not s3:
        raise Exception("S3 클라이언트가 초기화되지 않았습니다. AWS 인증 정보를 확인해주세요.")
    
    try:
        # 파일명 생성
        if custom_filename:
            key = f"user_{user_id}/contracts/{contract_id}/{custom_filename}"
        else:
            ext = file.filename.split(".")[-1] if file.filename and "." in file.filename else "jpg"
            key = f"user_{user_id}/contracts/{contract_id}/contract_{uuid4().hex[:8]}.{ext}"

        logger.info(f"📤 S3 업로드 시작: {key}")
        
        # 파일 포인터를 처음으로 되돌리기
        file.file.seek(0)
        
        # 파일 내용 크기 확인
        file_content = file.file.read()
        file_size = len(file_content)
        
        if file_size == 0:
            raise Exception(f"파일이 비어있습니다: {file.filename}")
        
        logger.info(f"📊 파일 크기: {file_size} bytes")
        
        # 파일 포인터를 다시 처음으로 되돌리기
        file.file.seek(0)
        
        # S3에 업로드
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
                    "upload_timestamp": str(int(file_size))  # 크기를 메타데이터로 저장
                }
            }
        )
        
        logger.info(f"✅ S3 업로드 성공: {key}")
        return key

    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_msg = f"S3 업로드 실패 (ClientError): {error_code} - {e.response['Error']['Message']}"
        logger.error(f"❌ {error_msg}")
        raise Exception(error_msg)
    except Exception as e:
        error_msg = f"S3 업로드 실패: {str(e)}"
        logger.error(f"❌ {error_msg}")
        raise Exception(error_msg)

# ✅ 2. 이미지 다운로드 (S3 → 임시 디렉토리)
def download_s3_files(bucket_name: str, s3_keys: list[str], local_dir: str = None) -> list[str]:
    """
    S3에서 파일들을 다운로드
    
    Args:
        bucket_name: S3 버킷 이름
        s3_keys: 다운로드할 S3 객체 키 리스트
        local_dir: 저장할 로컬 디렉토리 (기본값: TMP_DIR)
    
    Returns:
        list[str]: 다운로드된 로컬 파일 경로 리스트
    
    Raises:
        Exception: 다운로드 실패 시
    """
    if not s3:
        raise Exception("S3 클라이언트가 초기화되지 않았습니다.")
    
    if local_dir is None:
        local_dir = TMP_DIR
    
    try:
        os.makedirs(local_dir, exist_ok=True)
        local_paths = []

        for s3_key in s3_keys:
            try:
                filename = os.path.basename(s3_key)
                local_path = os.path.join(local_dir, filename)
                
                logger.info(f"📥 S3 다운로드 시작: {s3_key} -> {local_path}")
                
                s3.download_file(bucket_name, s3_key, local_path)
                local_paths.append(local_path)
                
                logger.info(f"✅ S3 다운로드 성공: {filename}")
                
            except ClientError as e:
                error_code = e.response['Error']['Code']
                if error_code == 'NoSuchKey':
                    logger.error(f"❌ S3 파일 없음: {s3_key}")
                    raise Exception(f"S3에서 파일을 찾을 수 없습니다: {s3_key}")
                else:
                    logger.error(f"❌ S3 다운로드 실패: {s3_key}, 오류: {error_code}")
                    raise Exception(f"S3 다운로드 실패: {error_code}")
            except Exception as e:
                logger.error(f"❌ 다운로드 실패: {s3_key}, 오류: {str(e)}")
                raise Exception(f"파일 다운로드 실패: {s3_key} - {str(e)}")

        return local_paths
        
    except Exception as e:
        logger.error(f"❌ S3 다운로드 처리 실패: {str(e)}")
        raise

# ✅ 3. JSON 데이터 업로드 (사용자 → S3)
def upload_json_to_s3(bucket: str, key: str, data: dict):
    """
    JSON 데이터를 S3에 업로드
    
    Args:
        bucket: S3 버킷 이름
        key: S3 객체 키
        data: 업로드할 딕셔너리 데이터
    
    Raises:
        Exception: 업로드 실패 시
    """
    if not s3:
        raise Exception("S3 클라이언트가 초기화되지 않았습니다.")
    
    try:
        logger.info(f"📤 JSON 업로드 시작: {key}")
        
        json_content = json.dumps(data, ensure_ascii=False, indent=2)
        
        s3.put_object(
            Bucket=bucket,
            Key=key,
            Body=json_content.encode('utf-8'),
            ContentType="application/json",
            Metadata={
                "data_type": "json",
                "upload_timestamp": str(int(len(json_content)))
            }
        )
        
        logger.info(f"✅ JSON 업로드 성공: {key}")
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_msg = f"JSON 업로드 실패 (ClientError): {error_code}"
        logger.error(f"❌ {error_msg}")
        raise Exception(error_msg)
    except Exception as e:
        error_msg = f"JSON 업로드 실패: {str(e)}"
        logger.error(f"❌ {error_msg}")
        raise Exception(error_msg)

# ✅ 4. S3 연결 테스트
def test_s3_connection(bucket_name: str) -> bool:
    """
    S3 연결 및 권한 테스트
    
    Args:
        bucket_name: 테스트할 버킷 이름
    
    Returns:
        bool: 연결 성공 여부
    """
    if not s3:
        logger.error("❌ S3 클라이언트가 초기화되지 않았습니다.")
        return False
    
    try:
        logger.info(f"🔍 S3 연결 테스트 시작: {bucket_name}")
        
        # 버킷 존재 여부 확인
        s3.head_bucket(Bucket=bucket_name)
        
        logger.info(f"✅ S3 연결 테스트 성공: {bucket_name}")
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '404':
            logger.error(f"❌ S3 버킷이 존재하지 않음: {bucket_name}")
        elif error_code == '403':
            logger.error(f"❌ S3 버킷 접근 권한 없음: {bucket_name}")
        else:
            logger.error(f"❌ S3 연결 오류: {error_code}")
        return False
    except Exception as e:
        logger.error(f"❌ S3 연결 테스트 실패: {str(e)}")
        return False