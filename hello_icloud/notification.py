#!/usr/bin/env python3
"""
시스템 알림창을 띄우는 스크립트
macOS에서 "hellow icloud!" 메시지를 알림으로 표시합니다.
"""

import subprocess
import sys


def show_notification(title=None, message="hello icloud!", sound="default"):
    """
    macOS 시스템 알림을 표시합니다.
    
    Args:
        title: 알림 제목 (None이면 제목 없이 표시, 기본값: None)
        message: 알림 메시지 (기본값: "hello icloud!")
        sound: 알림 소리 (기본값: "default")
    """
    if title:
        applescript = f'''
        display notification "{message}" with title "{title}" sound name "{sound}"
        '''
    else:
        applescript = f'''
        display notification "{message}" sound name "{sound}"
        '''
    
    try:
        subprocess.run(
            ["osascript", "-e", applescript],
            check=True,
            capture_output=True
        )
        print(f"알림이 표시되었습니다: {message}")
    except subprocess.CalledProcessError as e:
        print(f"알림 표시 중 오류 발생: {e}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print("osascript를 찾을 수 없습니다. macOS가 아닌 것 같습니다.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    show_notification(message="hello icloud!")

