#!/usr/bin/env python3
from pathlib import Path
import sys
import os

# 스크립트 디렉토리를 Python 경로에 추가 (notification 모듈 import를 위해)
script_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(script_dir))

from pdf2image import convert_from_path
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

def convert_one(src: Path):
    # PDF의 각 페이지를 이미지로 변환
    try:
        images = convert_from_path(str(src), dpi=200)
    except Exception as e:
        raise Exception(f"PDF 읽기 실패: {e}")
    
    created_files = []
    total_size = 0
    output_dir = None
    
    # 단일 페이지: 원본과 같은 폴더에 저장
    # 여러 페이지: {원본명}_images 폴더에 저장
    if len(images) == 1:
        # 단일 페이지인 경우
        dst = src.parent / (src.stem + ".jpg")
        im = images[0]
        im.convert("RGB").save(dst, format="JPEG", quality=92, optimize=True)
        
        file_size = os.path.getsize(dst)
        created_files.append({
            'path': dst,
            'size': file_size
        })
        total_size += file_size
    else:
        # 여러 페이지인 경우: 폴더에 저장
        output_dir = src.parent / (src.stem + "_images")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        for i, im in enumerate(images, start=1):
            # 파일명: 원본이름_001.jpg 형식
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
        'total_size': total_size,
        'output_dir': output_dir if len(images) > 1 else None
    }

def main(argv):
    # 디버깅: 모든 입력 정보 출력
    print("=" * 50, file=sys.stderr)
    print("디버깅 정보:", file=sys.stderr)
    print(f"argv: {argv}", file=sys.stderr)
    print(f"argv 길이: {len(argv)}", file=sys.stderr)
    print(f"stdin.isatty(): {sys.stdin.isatty()}", file=sys.stderr)
    
    # 명령줄 인자 또는 stdin에서 경로 받기
    paths = []
    
    # 명령줄 인자가 있으면 사용
    if len(argv) >= 2:
        print(f"명령줄 인자로 받은 경로들: {argv[1:]}", file=sys.stderr)
        paths = argv[1:]
    # stdin에서 경로 읽기 (단축어에서 사용 시)
    elif not sys.stdin.isatty():
        try:
            # stdin 읽기 (한 번만 읽을 수 있음)
            stdin_input = sys.stdin.read()
            print(f"stdin 원본 내용: {repr(stdin_input)}", file=sys.stderr)
            print(f"stdin 길이: {len(stdin_input)}", file=sys.stderr)
            
            if stdin_input and stdin_input.strip():
                print(f"stdin 처리 전: {repr(stdin_input.strip())}", file=sys.stderr)
                # 줄바꿈으로 구분된 경로들 처리
                for line in stdin_input.strip().split('\n'):
                    line = line.strip()
                    if line:
                        print(f"처리 중인 줄: {repr(line)}", file=sys.stderr)
                        # 파일 경로인지 확인
                        p = Path(line)
                        print(f"  경로 존재 여부: {p.exists()}", file=sys.stderr)
                        if p.exists():
                            paths.append(line)
                            print(f"  ✓ 경로 추가: {line}", file=sys.stderr)
                        elif line.startswith('/'):  # 절대 경로인 경우
                            paths.append(line)
                            print(f"  ✓ 절대 경로로 추가: {line}", file=sys.stderr)
                        else:
                            print(f"  ✗ 경로 무시: {line}", file=sys.stderr)
        except Exception as e:
            print(f"stdin 읽기 오류: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)
    
    print(f"최종 경로 리스트: {paths}", file=sys.stderr)
    print("=" * 50, file=sys.stderr)
    
    if not paths:
        print("No input paths", file=sys.stderr)
        return 1

    # 출력: 원본 파일과 같은 레벨에 JPG 생성
    total_processed = 0
    total_success = 0
    total_failed = 0
    total_size = 0  # 전체 생성된 파일의 총 용량
    file_sizes = []  # 각 파일의 용량 저장 (평균 계산용)
    created_file_names = []  # 생성된 JPG 파일명 리스트
    
    for src in iter_files(paths):
        total_processed += 1
        try:
            result = convert_one(src)
            total_success += 1
            total_size += result['total_size']  # 성공한 파일의 용량 누적
            file_sizes.append(result['total_size'])  # 개별 용량 저장
            
            # 생성된 파일명/폴더명 저장
            if result['output_dir']:
                # 여러 페이지인 경우 폴더명 저장
                created_file_names.append(result['output_dir'].name)
            elif result['files']:
                # 단일 페이지인 경우 파일명 저장
                created_file_names.append(result['files'][0]['path'].name)
            
            # 상세 결과 출력
            print(f"\n✓ 성공: {src.name}")
            print(f"  원본: {src}")
            print(f"  페이지 수: {result['pages']}페이지")
            if result['output_dir']:
                print(f"  출력 폴더: {result['output_dir']}")
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
        conversion_type="PDF → JPG 변환",
        file_names=created_file_names
    )

    return 0 if total_failed == 0 else 1

if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

