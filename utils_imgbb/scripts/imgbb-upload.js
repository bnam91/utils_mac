const { uploadImageFromFile } = require('../imgbb');
const { selectFileDialog } = require('../modules/file-selector');
const { showUploadSuccess, showUploadError, showUploadComplete } = require('../modules/notification');
const path = require('path');
const { execSync, spawn } = require('child_process');
const os = require('os');

// 클립보드에 복사하는 함수 (플랫폼별 처리)
function copyToClipboard(text) {
    const platform = os.platform();
    try {
        if (platform === 'darwin') {
            // macOS: pbcopy 사용 (stdin으로 직접 전달)
            const pbcopy = spawn('pbcopy', []);
            pbcopy.stdin.write(text);
            pbcopy.stdin.end();
        } else if (platform === 'win32') {
            // Windows: clip 사용
            execSync(`echo ${text} | clip`, { encoding: 'utf8' });
        } else {
            // Linux: xclip 또는 xsel 사용
            try {
                const xclip = spawn('xclip', ['-selection', 'clipboard']);
                xclip.stdin.write(text);
                xclip.stdin.end();
            } catch (e) {
                const xsel = spawn('xsel', ['--clipboard', '--input']);
                xsel.stdin.write(text);
                xsel.stdin.end();
            }
        }
    } catch (error) {
        console.error(`클립보드 복사 실패: ${error.message}`);
    }
}

// 명령줄 인수에서 이미지 파일 경로 가져오기 (없으면 GUI 다이얼로그 열기)
const imagePaths = process.argv.slice(2);

// 이미지 파일 경로 처리
async function getImagePaths() {
    if (imagePaths.length === 0) {
        // GUI 다이얼로그로 파일 선택 (복수 선택 가능)
        console.log('파일 선택 다이얼로그를 엽니다...');
        const selectedPaths = await selectFileDialog();
        return selectedPaths.map(p => p.trim());
    }
    
    // 상대 경로인 경우 현재 작업 디렉토리 기준으로 절대 경로로 변환
    return imagePaths.map(imagePath => 
        path.isAbsolute(imagePath) 
            ? imagePath 
            : path.resolve(process.cwd(), imagePath)
    );
}

// 이미지 업로드 실행
async function uploadImages() {
    try {
        const absolutePaths = await getImagePaths();
        console.log(`선택된 파일 (${absolutePaths.length}개):`);
        absolutePaths.forEach((p, i) => console.log(`  ${i + 1}. ${p}`));
        console.log('');
        
        const uploadedUrls = [];
        const failedFiles = [];
        
        // 각 파일을 순차적으로 업로드
        for (let i = 0; i < absolutePaths.length; i++) {
            const filePath = absolutePaths[i];
            const fileName = path.basename(filePath);
            console.log(`[${i + 1}/${absolutePaths.length}] 업로드 중: ${fileName}`);
            
            try {
                const imageUrl = await uploadImageFromFile(filePath);
                uploadedUrls.push(imageUrl);
                console.log(`  ✓ 업로드 완료: ${imageUrl}`);
                
                // 각 URL을 생성할 때마다 클립보드에 복사
                copyToClipboard(imageUrl);
                console.log(`  ✓ 클립보드에 복사됨`);
                
                // 성공 알림 표시
                showUploadSuccess(fileName, imageUrl);
            } catch (error) {
                console.error(`  ✗ 업로드 실패: ${error.message}`);
                failedFiles.push({ fileName, error: error.message });
                
                // 실패 알림 표시
                showUploadError(fileName, error.message);
            }
            console.log('');
        }
        
        if (uploadedUrls.length === 0) {
            throw new Error('업로드된 이미지가 없습니다.');
        }
        
        console.log('업로드 완료!');
        console.log('업로드된 이미지 URL:');
        uploadedUrls.forEach((url, i) => console.log(`  ${i + 1}. ${url}`));
        
        // 마지막 URL이 클립보드에 남아있음
        console.log(`\n✓ 총 ${uploadedUrls.length}개의 이미지가 업로드되었습니다.`);
        console.log(`✓ 마지막 URL이 클립보드에 저장되어 있습니다.`);
        
        // 전체 업로드 완료 알림 표시
        showUploadComplete(uploadedUrls.length, absolutePaths.length);
        
        return uploadedUrls;
    } catch (error) {
        console.error('오류:', error.message);
        process.exit(1);
    }
}

uploadImages();

