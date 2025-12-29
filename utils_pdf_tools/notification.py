#!/usr/bin/env python3
"""macOS 시스템 알림(토스트 메시지) 모듈"""
import subprocess

def show_notification(title, message, subtitle="", sound="Glass"):
    """macOS 시스템 알림(토스트) 표시
    
    알림의 "보기" 버튼은 macOS가 자동으로 처리합니다.
    
    Args:
        title: 알림 제목
        message: 알림 메시지 본문
        subtitle: 알림 부제목 (선택사항)
        sound: 알림 사운드 (기본값: "Glass")
    """
    try:
        # 특수 문자 이스케이프 처리
        title = title.replace('"', '\\"')
        message = message.replace('"', '\\"')
        subtitle = subtitle.replace('"', '\\"')
        
        script = f'''
        display notification "{message}" with title "{title}" subtitle "{subtitle}" sound name "{sound}"
        '''
        subprocess.run(['osascript', '-e', script], check=False, capture_output=True)
    except Exception:
        pass  # 알림 실패해도 계속 진행

def format_size(size_bytes):
    """바이트를 읽기 쉬운 형식으로 변환"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

def show_conversion_notification(
    total_processed,
    total_success,
    total_failed,
    total_size,
    file_sizes,
    conversion_type="변환",
    file_names=None
):
    """변환 작업 완료 알림 표시
    
    Args:
        total_processed: 처리된 총 파일/그룹 수
        total_success: 성공한 파일/그룹 수
        total_failed: 실패한 파일/그룹 수
        total_size: 생성된 파일의 총 용량
        file_sizes: 각 파일의 용량 리스트 (평균 계산용)
        conversion_type: 변환 타입 (예: "PDF → JPG 변환", "이미지 → PDF 변환")
        file_names: 생성된 파일명 리스트 (선택사항)
    """
    if total_processed == 0:
        return
    
    # 평균 용량 계산
    avg_size = total_size / len(file_sizes) if file_sizes else 0
    
    # 파일명 정보 생성
    file_info = ""
    if file_names:
        if len(file_names) == 1:
            file_info = f" | 파일: {file_names[0]}"
        elif len(file_names) <= 3:
            file_info = f" | 파일: {', '.join(file_names)}"
        else:
            file_info = f" | 파일: {', '.join(file_names[:2])} 외 {len(file_names)-2}개"
    
    if total_failed == 0:
        # 모두 성공
        if total_success == 1:
            # 단일 파일인 경우 개별 용량 표시
            message = f"용량: {format_size(total_size)}{file_info}"
        else:
            # 여러 파일인 경우 총 용량, 평균 용량 표시
            message = f"총 용량: {format_size(total_size)} | 평균: {format_size(avg_size)}{file_info}"
        
        show_notification(
            title=f"{conversion_type} 완료",
            subtitle=f"{total_success}개 처리 성공",
            message=message,
            sound="Glass"
        )
    elif total_success == 0:
        # 모두 실패
        show_notification(
            title=f"{conversion_type} 실패",
            subtitle=f"{total_failed}개 처리 실패",
            message="모든 처리에 실패했습니다.",
            sound="Basso"
        )
    else:
        # 일부 성공/실패
        if total_success == 1:
            message = f"생성된 파일 용량: {format_size(total_size)}{file_info}"
        else:
            message = f"총 용량: {format_size(total_size)} | 평균: {format_size(avg_size)}{file_info}"
        
        show_notification(
            title=f"{conversion_type} 완료",
            subtitle=f"성공: {total_success}개, 실패: {total_failed}개",
            message=message,
            sound="Submarine"
        )

