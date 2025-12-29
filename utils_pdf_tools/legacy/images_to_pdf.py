#!/usr/bin/env python3
from PIL import Image
from pathlib import Path
import sys
import os

# notification 모듈 임포트
from notification import format_size, show_conversion_notification

IMG_EXT = {".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff", ".bmp", ".heic"}

def iter_files(paths):
    """파일과 폴더를 구분하여 처리"""
    for p in map(Path, paths):
        if p.is_dir():
            # 폴더인 경우: 해당 폴더의 직접적인 이미지 파일만 (하위 폴더 제외)
            for f in p.iterdir():
                if f.is_file() and f.suffix.lower() in IMG_EXT:
                    yield f, p  # (파일경로, 소속폴더) 튜플 반환
        elif p.is_file() and p.suffix.lower() in IMG_EXT:
            # 파일인 경우: 파일과 그 파일이 속한 폴더 반환
            yield p, p.parent

def get_unique_filename(output_path: Path):
    """중복 파일명이 있으면 번호를 추가하여 고유한 파일명 생성"""
    if not output_path.exists():
        return output_path
    
    # 파일명과 확장자 분리
    stem = output_path.stem
    suffix = output_path.suffix
    parent = output_path.parent
    
    # 번호 추가하여 고유한 파일명 찾기
    counter = 1
    while True:
        new_name = f"{stem}_{counter}{suffix}"
        new_path = parent / new_name
        if not new_path.exists():
            return new_path
        counter += 1

def convert_images_to_pdf(image_paths, output_path: Path):
    """여러 이미지를 하나의 PDF로 변환 및 합치기"""
    if not image_paths:
        raise Exception("이미지 파일이 없습니다.")
    
    images = []
    total_size = 0
    
    # 모든 이미지 로드
    for img_path in sorted(image_paths):  # 파일명 순서로 정렬
        try:
            with Image.open(img_path) as im:
                # 투명 PNG 등은 RGB로 변환
                if im.mode in ("RGBA", "LA"):
                    bg = Image.new("RGB", im.size, (255, 255, 255))
                    bg.paste(im, mask=im.split()[-1])
                    im = bg
                elif im.mode != "RGB":
                    im = im.convert("RGB")
                
                images.append(im.copy())
                total_size += os.path.getsize(img_path)
        except Exception as e:
            raise Exception(f"이미지 로드 실패 ({img_path.name}): {e}")
    
    if not images:
        raise Exception("변환 가능한 이미지가 없습니다.")
    
    # 첫 번째 이미지의 크기에 맞춰 모든 이미지 리사이즈 (선택사항)
    # 필요시 주석 해제하여 사용
    # first_size = images[0].size
    # images = [img.resize(first_size, Image.Resampling.LANCZOS) if img.size != first_size else img for img in images]
    
    # PDF로 저장
    try:
        images[0].save(
            output_path,
            "PDF",
            resolution=200.0,
            save_all=True,
            append_images=images[1:] if len(images) > 1 else []
        )
    except Exception as e:
        raise Exception(f"PDF 저장 실패: {e}")
    
    pdf_size = os.path.getsize(output_path)
    
    return {
        'success': True,
        'source_count': len(image_paths),
        'pages': len(images),
        'output': output_path,
        'pdf_size': pdf_size,
        'total_input_size': total_size
    }

def main(argv):
    if len(argv) < 2:
        print("No input paths")
        return 1

    # 출력: 원본 파일과 같은 레벨에 PDF 생성
    total_processed = 0
    total_success = 0
    total_failed = 0
    total_pdf_size = 0  # 전체 생성된 PDF의 총 용량
    pdf_sizes = []  # 각 PDF의 용량 저장 (평균 계산용)
    created_pdf_names = []  # 생성된 PDF 파일명 리스트
    
    # 입력 파일들을 그룹화 (같은 폴더의 파일들은 하나의 PDF로 합치기)
    file_groups = {}
    
    for img_path, folder in iter_files(argv[1:]):
        # 같은 폴더의 파일들을 그룹화
        if folder not in file_groups:
            file_groups[folder] = []
        file_groups[folder].append(img_path)
    
    # 각 폴더별로 PDF 생성
    for folder, image_paths in file_groups.items():
        # 이미지가 없으면 스킵
        if not image_paths:
            continue
            
        total_processed += 1
        try:
            # 출력 파일명: 폴더명_merged.pdf 또는 첫 번째 이미지명.pdf
            if len(image_paths) == 1:
                # 단일 이미지인 경우
                output_name = image_paths[0].stem + ".pdf"
            else:
                # 여러 이미지인 경우
                output_name = folder.name + "_merged.pdf" if folder.name else "merged.pdf"
            
            output_path = folder / output_name
            # 중복 파일명 처리
            output_path = get_unique_filename(output_path)
            
            result = convert_images_to_pdf(image_paths, output_path)
            total_success += 1
            total_pdf_size += result['pdf_size']
            pdf_sizes.append(result['pdf_size'])
            created_pdf_names.append(output_path.name)  # 생성된 PDF 파일명 저장
            
            # 상세 결과 출력
            print(f"\n✓ 성공: {len(image_paths)}개 이미지 → PDF")
            print(f"  입력 폴더/파일:")
            if len(image_paths) == 1:
                print(f"    - {image_paths[0].name}")
            else:
                print(f"    폴더: {folder}")
                for img_path in image_paths:
                    print(f"      - {img_path.name}")
            print(f"  출력: {output_path}")
            print(f"  페이지 수: {result['pages']}페이지")
            print(f"  PDF 용량: {format_size(result['pdf_size'])}")
            print(f"  입력 총 용량: {format_size(result['total_input_size'])}")
            
        except Exception as e:
            total_failed += 1
            print(f"\n✗ 실패: {len(image_paths)}개 이미지 처리 실패")
            print(f"  폴더: {folder}")
            print(f"  오류: {e}")
    
    # 전체 요약 출력
    print(f"\n{'='*50}")
    print(f"처리 완료: 총 {total_processed}개 그룹")
    print(f"  성공: {total_success}개")
    print(f"  실패: {total_failed}개")
    print(f"{'='*50}")
    
    # macOS 시스템 알림(토스트 메시지) 표시
    show_conversion_notification(
        total_processed=total_processed,
        total_success=total_success,
        total_failed=total_failed,
        total_size=total_pdf_size,
        file_sizes=pdf_sizes,
        conversion_type="이미지 → PDF 변환",
        file_names=created_pdf_names
    )

    return 0 if total_failed == 0 else 1

if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

