#!/usr/bin/env python3
from pdf2image import convert_from_path
from pathlib import Path
import sys
import os

# notification 모듈 임포트
from notification import format_size, show_conversion_notification

PDF_EXT = {".pdf"}

def iter_files(paths):
    for p in map(Path, paths):
        if p.is_dir():
            for f in p.rglob("*"):
                if f.is_file() and f.suffix.lower() in PDF_EXT:
                    yield f
        elif p.is_file() and p.suffix.lower() in PDF_EXT:
            yield p

def extract_images_from_pdf(src: Path, output_dir: Path, format="jpg"):
    """PDF에서 각 페이지를 이미지로 추출"""
    try:
        images = convert_from_path(str(src), dpi=200)
    except Exception as e:
        raise Exception(f"PDF 읽기 실패: {e}")
    
    created_files = []
    total_size = 0
    
    # 출력 디렉토리 생성
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 각 페이지를 이미지로 저장
    for i, im in enumerate(images, start=1):
        # 파일명: 원본이름_001.jpg 형식
        if format.lower() == "png":
            dst = output_dir / (src.stem + f"_{i:03d}.png")
            im.save(dst, format="PNG", optimize=True)
        else:  # 기본값: JPG
            dst = output_dir / (src.stem + f"_{i:03d}.jpg")
            im.convert("RGB").save(dst, format="JPEG", quality=92, optimize=True)
        
        # 생성된 파일 정보 수집
        file_size = os.path.getsize(dst)
        created_files.append({
            'path': dst,
            'size': file_size
        })
        total_size += file_size
    
    return {
        'success': True,
        'source': src,
        'pages': len(images),
        'files': created_files,
        'total_size': total_size
    }

def main(argv):
    if len(argv) < 2:
        print("No input paths")
        return 1

    # 출력: 원본 파일과 같은 레벨에 {원본파일명}_images 폴더 생성
    total_processed = 0
    total_success = 0
    total_failed = 0
    total_size = 0  # 전체 생성된 파일의 총 용량
    file_sizes = []  # 각 파일의 용량 저장 (평균 계산용)
    created_folder_names = []  # 생성된 폴더명 리스트
    
    for src in iter_files(argv[1:]):
        total_processed += 1
        try:
            # 출력 폴더: 원본파일명_images
            output_dir = src.parent / (src.stem + "_images")
            
            result = extract_images_from_pdf(src, output_dir)
            total_success += 1
            total_size += result['total_size']  # 성공한 파일의 용량 누적
            file_sizes.append(result['total_size'])  # 개별 용량 저장
            created_folder_names.append(output_dir.name)  # 생성된 폴더명 저장
            
            # 상세 결과 출력
            print(f"\n✓ 성공: {src.name}")
            print(f"  원본: {src}")
            print(f"  페이지 수: {result['pages']}페이지")
            print(f"  출력 폴더: {output_dir}")
            print(f"  생성된 파일:")
            for file_info in result['files']:
                print(f"    - {file_info['path'].name} ({format_size(file_info['size'])})")
            print(f"  총 용량: {format_size(result['total_size'])}")
            
        except Exception as e:
            total_failed += 1
            print(f"\n✗ 실패: {src.name}")
            print(f"  원본: {src}")
            print(f"  오류: {e}")
    
    # 전체 요약 출력
    print(f"\n{'='*50}")
    print(f"처리 완료: 총 {total_processed}개 파일")
    print(f"  성공: {total_success}개")
    print(f"  실패: {total_failed}개")
    print(f"{'='*50}")
    
    # macOS 시스템 알림(토스트 메시지) 표시
    show_conversion_notification(
        total_processed=total_processed,
        total_success=total_success,
        total_failed=total_failed,
        total_size=total_size,
        file_sizes=file_sizes,
        conversion_type="PDF → 이미지 분리",
        file_names=created_folder_names
    )

    return 0 if total_failed == 0 else 1

if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

