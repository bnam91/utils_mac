const path = require('path');
const os = require('os');
const fs = require('fs');
// 프로젝트 내부 .env 파일 우선, 없으면 기본 경로 사용
const envPath = path.join(__dirname, '.env');
const defaultEnvPath = path.join(os.homedir(), 'Documents', 'github_cloud', 'api_keys', '.env');
require('dotenv').config({ path: fs.existsSync(envPath) ? envPath : defaultEnvPath });
const axios = require('axios');
const FormData = require('form-data');

/**
 * ImgBB API를 사용한 이미지 업로드 함수
 * @param {string} imgBase64 - base64로 인코딩된 이미지 데이터
 * @returns {Promise<string>} 업로드된 이미지의 URL
 */
async function uploadImageToImgbb(imgBase64) {
    const url = "https://api.imgbb.com/1/upload";
    const imgbbApiKey = process.env.IMGBB_API_KEY; // 환경 변수에서 API 키 가져오기
    
    if (!imgbbApiKey) {
        throw new Error("IMGBB_API_KEY 환경 변수가 설정되지 않았습니다.");
    }

    const formData = new FormData();
    formData.append('key', imgbbApiKey);
    formData.append('image', imgBase64);

    try {
        const response = await axios.post(url, formData, {
            headers: formData.getHeaders()
        });

        if (response.status === 200) {
            if (response.data && response.data.data && response.data.data.url) {
                return response.data.data.url;
            } else {
                throw new Error("예상치 못한 응답 형식입니다.");
            }
        } else {
            throw new Error(`이미지 업로드 중 오류 발생: ${response.status}`);
        }
    } catch (error) {
        if (error.response) {
            throw new Error(`요청 중 오류 발생: ${error.response.status} - ${error.response.statusText}`);
        } else if (error.request) {
            throw new Error(`요청 중 오류 발생: 네트워크 오류`);
        } else {
            throw new Error(`요청 중 오류 발생: ${error.message}`);
        }
    }
}

/**
 * 파일에서 이미지를 읽어서 base64로 변환하고 업로드하는 함수
 * @param {string} imagePath - 이미지 파일 경로
 * @returns {Promise<string>} 업로드된 이미지의 URL
 */
async function uploadImageFromFile(imagePath) {
    try {
        // 파일을 읽어서 base64로 인코딩
        const imageBuffer = fs.readFileSync(imagePath);
        const imgBase64 = imageBuffer.toString('base64');
        
        console.log("이미지가 base64로 변환되었습니다.");
        
        // 이미지 업로드
        const imageUrl = await uploadImageToImgbb(imgBase64);
        
        if (imageUrl) {
            console.log(`이미지가 성공적으로 업로드되었습니다. URL: ${imageUrl}`);
            return imageUrl;
        } else {
            console.log("이미지 업로드에 실패했습니다.");
            return null;
        }
    } catch (error) {
        throw new Error(`파일 읽기 오류: ${error.message}`);
    }
}

/**
 * Buffer에서 이미지를 업로드하는 함수
 * @param {Buffer} imageBuffer - 이미지 버퍼
 * @returns {Promise<string>} 업로드된 이미지의 URL
 */
async function uploadImageFromBuffer(imageBuffer) {
    try {
        const imgBase64 = imageBuffer.toString('base64');
        console.log("이미지 버퍼가 base64로 변환되었습니다.");
        
        const imageUrl = await uploadImageToImgbb(imgBase64);
        
        if (imageUrl) {
            console.log(`이미지가 성공적으로 업로드되었습니다. URL: ${imageUrl}`);
            return imageUrl;
        } else {
            console.log("이미지 업로드에 실패했습니다.");
            return null;
        }
    } catch (error) {
        throw new Error(`버퍼 처리 오류: ${error.message}`);
    }
}

module.exports = {
    uploadImageToImgbb,
    uploadImageFromFile,
    uploadImageFromBuffer
};

