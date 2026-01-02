const { execSync } = require('child_process');
const os = require('os');
const fs = require('fs');
const path = require('path');

/**
 * GUI 파일 선택 다이얼로그 열기 (복수 선택 지원)
 * @param {string} defaultPath - 기본 디렉토리 경로 (선택사항)
 * @returns {Promise<string[]>} 선택된 파일 경로 배열
 */
async function selectFileDialog(defaultPath = null) {
    const platform = os.platform();
    let command;
    let tempScriptPath = null;
    
    // 기본 경로 설정 (없으면 img_input 폴더 사용)
    const imgInputPath = defaultPath || path.join(__dirname, '..', 'img_input');
    
    if (platform === 'darwin') {
        // macOS: AppleScript 사용 (복수 선택 지원)
        const script = `tell application "System Events"
    activate
    set fileList to choose file with prompt "업로드할 이미지 파일을 선택하세요 (Cmd 키로 여러 개 선택 가능)" with multiple selections allowed of type {"public.image"} default location POSIX file "${imgInputPath}"
    set pathList to {}
    repeat with aFile in fileList
        set end of pathList to POSIX path of aFile
    end repeat
    set AppleScript's text item delimiters to "\\n"
    return pathList as text
end tell`;
        tempScriptPath = path.join(os.tmpdir(), `imgbb-select-${Date.now()}.scpt`);
        fs.writeFileSync(tempScriptPath, script, 'utf8');
        command = `osascript "${tempScriptPath}"`;
    } else if (platform === 'win32') {
        // Windows: PowerShell 사용 (복수 선택 지원)
        const escapedPath = imgInputPath.replace(/\\/g, '\\\\');
        command = `powershell -Command "Add-Type -AssemblyName System.Windows.Forms; $dialog = New-Object System.Windows.Forms.OpenFileDialog; $dialog.InitialDirectory = '${escapedPath}'; $dialog.Filter = 'Image Files (*.png;*.jpg;*.jpeg;*.gif;*.bmp)|*.png;*.jpg;*.jpeg;*.gif;*.bmp|All Files (*.*)|*.*'; $dialog.Multiselect = $true; if ($dialog.ShowDialog() -eq 'OK') { $dialog.FileNames -join '|' } else { '' }"`;
    } else {
        // Linux: zenity 사용 (복수 선택 지원)
        command = `zenity --file-selection --title="업로드할 이미지 파일을 선택하세요 (Ctrl 키로 여러 개 선택 가능)" --filename="${imgInputPath}" --file-filter="이미지 파일 | *.png *.jpg *.jpeg *.gif *.bmp" --multiple --separator="|" 2>/dev/null || echo ""`;
    }
    
    try {
        const result = execSync(command, { encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'] }).trim();
        
        // macOS의 경우 임시 스크립트 파일 삭제
        if (tempScriptPath) {
            try {
                fs.unlinkSync(tempScriptPath);
            } catch (e) {
                // 삭제 실패는 무시
            }
        }
        
        if (!result || result === '') {
            throw new Error('파일이 선택되지 않았습니다.');
        }
        
        // 결과를 배열로 변환 (플랫폼별 구분자 처리)
        let filePaths = [];
        if (platform === 'darwin') {
            // macOS: AppleScript는 줄바꿈으로 구분된 경로 반환
            filePaths = result.split('\n').filter(p => p.trim() !== '');
        } else {
            // Windows/Linux: | 구분자 사용
            filePaths = result.split('|').filter(p => p.trim() !== '');
        }
        
        return filePaths;
    } catch (error) {
        // 에러 발생 시에도 임시 파일 삭제 시도
        if (tempScriptPath) {
            try {
                fs.unlinkSync(tempScriptPath);
            } catch (e) {
                // 삭제 실패는 무시
            }
        }
        throw new Error(`파일 선택 다이얼로그 오류: ${error.message}`);
    }
}

module.exports = {
    selectFileDialog
};

