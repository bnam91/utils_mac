const { execSync, spawn } = require('child_process');
const os = require('os');
const path = require('path');

/**
 * 플랫폼별 토스트 알림 표시
 * @param {string} title - 알림 제목
 * @param {string} message - 알림 메시지
 * @param {string} type - 알림 타입 ('success', 'error', 'info')
 */
function showNotification(title, message, type = 'info') {
    const platform = os.platform();
    
    try {
        if (platform === 'darwin') {
            // macOS: osascript를 사용한 알림
            const iconMap = {
                'success': '✓',
                'error': '✗',
                'info': 'ℹ'
            };
            const icon = iconMap[type] || 'ℹ';
            
            // AppleScript에서 특수문자 이스케이프 처리
            const escapeAppleScript = (str) => {
                return str.replace(/\\/g, '\\\\')
                          .replace(/"/g, '\\"')
                          .replace(/\n/g, '\\n');
            };
            
            const escapedTitle = escapeAppleScript(title);
            const escapedMessage = escapeAppleScript(message);
            
            // AppleScript를 사용하여 알림 표시
            const script = `display notification "${escapedMessage}" with title "${escapedTitle}" subtitle "${icon}" sound name "Glass"`;
            execSync(`osascript -e '${script}'`, { encoding: 'utf8', stdio: 'ignore' });
        } else if (platform === 'win32') {
            // Windows: PowerShell을 사용한 알림
            const iconMap = {
                'success': 'Information',
                'error': 'Error',
                'info': 'Information'
            };
            const icon = iconMap[type] || 'Information';
            
            // PowerShell을 사용하여 알림 표시 (Windows 10+)
            const psScript = `
                [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
                $template = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]::ToastText02)
                $textNodes = $template.GetElementsByTagName("text")
                $textNodes.Item(0).AppendChild($template.CreateTextNode("${title}")) | Out-Null
                $textNodes.Item(1).AppendChild($template.CreateTextNode("${message}")) | Out-Null
                $toast = [Windows.UI.Notifications.ToastNotification]::new($template)
                [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("ImgBB Uploader").Show($toast)
            `;
            
            try {
                execSync(`powershell -Command "${psScript}"`, { encoding: 'utf8', stdio: 'ignore' });
            } catch (e) {
                // PowerShell 실패 시 기본 msg 명령어 사용
                execSync(`msg * "${title}: ${message}"`, { encoding: 'utf8', stdio: 'ignore' });
            }
        } else {
            // Linux: notify-send 사용
            const iconMap = {
                'success': 'dialog-information',
                'error': 'dialog-error',
                'info': 'dialog-information'
            };
            const icon = iconMap[type] || 'dialog-information';
            
            execSync(`notify-send "${title}" "${message}" --icon=${icon}`, { encoding: 'utf8', stdio: 'ignore' });
        }
    } catch (error) {
        // 알림 실패 시 콘솔에만 출력 (앱 동작에는 영향 없음)
        console.error(`알림 표시 실패: ${error.message}`);
    }
}

/**
 * 업로드 성공 알림
 * @param {string} fileName - 업로드된 파일명
 * @param {string} url - 업로드된 이미지 URL
 */
function showUploadSuccess(fileName, url) {
    const shortUrl = url.length > 50 ? url.substring(0, 47) + '...' : url;
    showNotification(
        '업로드 성공',
        `${fileName}\n${shortUrl}`,
        'success'
    );
}

/**
 * 업로드 실패 알림
 * @param {string} fileName - 업로드 실패한 파일명
 * @param {string} errorMessage - 에러 메시지
 */
function showUploadError(fileName, errorMessage) {
    const shortMessage = errorMessage.length > 50 ? errorMessage.substring(0, 47) + '...' : errorMessage;
    showNotification(
        '업로드 실패',
        `${fileName}\n${shortMessage}`,
        'error'
    );
}

/**
 * 전체 업로드 완료 알림
 * @param {number} successCount - 성공한 파일 수
 * @param {number} totalCount - 전체 파일 수
 */
function showUploadComplete(successCount, totalCount) {
    if (successCount === totalCount) {
        showNotification(
            '업로드 완료',
            `총 ${successCount}개 파일 업로드 완료\n클립보드에 URL이 복사되었습니다.`,
            'success'
        );
    } else {
        showNotification(
            '업로드 완료',
            `${successCount}/${totalCount}개 파일 업로드 완료`,
            'info'
        );
    }
}

module.exports = {
    showNotification,
    showUploadSuccess,
    showUploadError,
    showUploadComplete
};

