from PIL import Image, ImageEnhance, ImageFilter
import io
import os

def optimize_image_for_ocr(image_path: str, max_size: tuple = (1920, 1920), quality: int = 85) -> str:
    """
    🎯 OCR을 위한 이미지 최적화
    - 파일 크기 최적화 (네트워크 전송 속도 향상)
    - 해상도 최적화 (처리 속도 향상)
    - 품질 최적화 (인식 정확도 유지)
    """
    
    with Image.open(image_path) as img:
        original_size = img.size
        original_format = img.format
        
        # 1. 크기 최적화 (너무 큰 이미지는 OCR 속도 저하)
        if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            print(f"📏 이미지 크기 최적화: {original_size} → {img.size}")
        
        # 2. 컬러 모드 최적화
        if img.mode in ('RGBA', 'LA', 'P'):
            # 투명도가 있는 이미지를 RGB로 변환
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
            img = background
            print(f"🎨 컬러 모드 최적화: {original_format} → RGB")
        
        # 3. 파일 형식 최적화 (JPEG 압축으로 파일 크기 감소)
        optimized_path = image_path.replace(os.path.splitext(image_path)[1], '_optimized.jpg')
        
        img.save(optimized_path, 'JPEG', quality=quality, optimize=True)
        
        # 파일 크기 비교
        original_size_mb = os.path.getsize(image_path) / (1024 * 1024)
        optimized_size_mb = os.path.getsize(optimized_path) / (1024 * 1024)
        
        print(f"💾 파일 크기 최적화: {original_size_mb:.2f}MB → {optimized_size_mb:.2f}MB ({(1-optimized_size_mb/original_size_mb)*100:.1f}% 감소)")
        
        return optimized_path

def enhance_image_for_ocr(image_path: str) -> str:
    """
    ✨ OCR 정확도 향상을 위한 이미지 개선
    - 대비 향상
    - 선명도 향상
    - 노이즈 제거
    """
    
    with Image.open(image_path) as img:
        # 1. 대비 향상 (텍스트와 배경 구분 개선)
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.2)  # 20% 대비 향상
        
        # 2. 선명도 향상 (텍스트 경계 개선)
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(1.1)  # 10% 선명도 향상
        
        # 3. 노이즈 제거 (스캔 품질 개선)
        img = img.filter(ImageFilter.MedianFilter(size=3))
        
        enhanced_path = image_path.replace(os.path.splitext(image_path)[1], '_enhanced.jpg')
        img.save(enhanced_path, 'JPEG', quality=90)
        
        print(f"✨ 이미지 품질 개선 완료: {enhanced_path}")
        return enhanced_path

def preprocess_image_for_ocr(image_path: str, optimize: bool = True, enhance: bool = False) -> str:
    """
    🔄 OCR 전처리 통합 함수
    """
    processed_path = image_path
    
    if optimize:
        processed_path = optimize_image_for_ocr(processed_path)
    
    if enhance:
        processed_path = enhance_image_for_ocr(processed_path)
    
    return processed_path

def cleanup_processed_images(original_path: str):
    """
    🧹 처리된 임시 이미지 파일 정리
    """
    base_path = os.path.splitext(original_path)[0]
    temp_files = [
        f"{base_path}_optimized.jpg",
        f"{base_path}_enhanced.jpg"
    ]
    
    for temp_file in temp_files:
        if os.path.exists(temp_file):
            os.remove(temp_file)
            print(f"🗑️ 임시 파일 삭제: {temp_file}") 