import json
import os
import time
from ocr.upstage_ocr_ultra_fast import extract_text_optimized_global as extract_text_from_image_optimized
from utils.s3_utils import download_s3_files
from config.settings import TMP_DIR
import logging
import tempfile
import shutil

logger = logging.getLogger(__name__)

def process_contract_images_from_s3(bucket: str, s3_keys: list[str], output_path: str):
    """
    🚀 최적화된 OCR 배치 처리 (전처리 최소화 + HTML 모드)
    이미지 전처리는 건너뛰고 직접 OCR 처리하여 속도 향상
    """
    start_time = time.time()
    logger.info(f"🚀 최적화된 OCR 배치 처리 시작 - 총 {len(s3_keys)}개 이미지")
    
    merged_result = {
        "pages": [],
        "full_html": "",
        "processing_info": {
            "total_pages": len(s3_keys),
            "processed_pages": 0,
            "failed_pages": 0,
            "start_time": start_time,
            "mode": "optimized_no_preprocess"
        }
    }

    # 임시 디렉토리 생성
    temp_dir = None
    try:
        temp_dir = tempfile.mkdtemp(prefix="ocr_optimized_", dir=TMP_DIR)
        local_image_dir = os.path.join(temp_dir, "images")
        os.makedirs(local_image_dir, exist_ok=True)
        
        logger.info(f"📁 임시 디렉토리 생성: {temp_dir}")

        # S3 다운로드
        download_start = time.time()
        try:
            local_image_paths = download_s3_files(bucket, s3_keys, local_image_dir)
            download_time = time.time() - download_start
            logger.info(f"📥 S3 다운로드 완료: {download_time:.2f}초")
        except Exception as e:
            logger.error(f"❌ S3 다운로드 실패: {str(e)}")
            raise Exception(f"S3 다운로드 실패: {str(e)}")

        # 최적화된 OCR 처리 (전처리 없이)
        ocr_start = time.time()
        processed_count = 0
        failed_count = 0
        
        for idx, path in enumerate(local_image_paths):
            page_start = time.time()
            logger.info(f"[{idx+1}/{len(local_image_paths)}] 🚀 OCR 처리 (전처리 없음): {os.path.basename(path)}")
            
            try:
                # 🚀 전처리 건너뛰고 바로 OCR (HTML 모드)
                ocr_single_start = time.time()
                result = extract_text_from_image_optimized(path)  # HTML 추출
                ocr_single_time = time.time() - ocr_single_start
                
                page_time = time.time() - page_start
                logger.info(f"   ✅ 페이지 {idx+1} 완료: {page_time:.2f}초 (OCR: {ocr_single_time:.2f}초)")
                
                # 결과 처리
                if "content" in result and "html" in result["content"]:
                    page_html = result["content"]["html"]
                    
                    merged_result["pages"].append({
                        "page": idx + 1,
                        "html": page_html,
                        "processing_time": page_time,
                        "file_name": os.path.basename(path),
                        "mode": "optimized_no_preprocess"
                    })
                    merged_result["full_html"] += f"\n<!-- Page {idx+1} -->\n" + page_html
                    processed_count += 1
                else:
                    logger.warning(f"   ⚠️ 예상치 못한 응답 형식: {result}")
                    raise Exception("OCR 응답에서 HTML 콘텐츠를 찾을 수 없습니다.")
                
            except Exception as e:
                logger.error(f"   ❌ OCR 처리 실패: {str(e)}")
                failed_count += 1
                
                merged_result["pages"].append({
                    "page": idx + 1,
                    "html": "",
                    "error": str(e),
                    "file_name": os.path.basename(path),
                    "mode": "failed"
                })

        ocr_time = time.time() - ocr_start
        logger.info(f"🔍 OCR 처리 완료: {ocr_time:.2f}초 (성공: {processed_count}, 실패: {failed_count})")

        # 처리 정보 업데이트
        merged_result["processing_info"].update({
            "processed_pages": processed_count,
            "failed_pages": failed_count,
            "processing_time": ocr_time,
            "download_time": download_time
        })

        # 파일 저장
        save_start = time.time()
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(merged_result, f, ensure_ascii=False, indent=2)
            save_time = time.time() - save_start
            
            total_time = time.time() - start_time
            logger.info(f"💾 파일 저장 완료: {save_time:.2f}초")
            logger.info(f"🎉 전처리 없는 최적화 처리 완료: {total_time:.2f}초")
            logger.info(f"   - S3 다운로드: {download_time:.2f}초 ({download_time/total_time*100:.1f}%)")
            logger.info(f"   - OCR 처리: {ocr_time:.2f}초 ({ocr_time/total_time*100:.1f}%)")
            logger.info(f"   - 파일 저장: {save_time:.2f}초 ({save_time/total_time*100:.1f}%)")
            
            if processed_count == 0:
                raise Exception("모든 페이지의 OCR 처리에 실패했습니다.")
            elif failed_count > 0:
                logger.warning(f"⚠️ {failed_count}개 페이지 처리 실패. 부분적 결과를 반환합니다.")
                
        except Exception as e:
            logger.error(f"❌ 파일 저장 실패: {str(e)}")
            raise Exception(f"OCR 결과 저장 실패: {str(e)}")
            
    except Exception as e:
        logger.error(f"❌ 최적화된 OCR 배치 처리 실패: {str(e)}")
        raise
        
    finally:
        # 임시 디렉토리 정리
        if temp_dir and os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
                logger.info(f"🧹 임시 디렉토리 정리 완료: {temp_dir}")
            except Exception as cleanup_error:
                logger.warning(f"⚠️ 임시 디렉토리 정리 실패: {cleanup_error}")
