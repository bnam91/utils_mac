# utils_pdf_tools - PDF/이미지 변환 유틸리티

macOS용 PDF와 이미지 파일을 변환하는 Python 스크립트 모음입니다.

## 설치

```bash
# Python 패키지 설치
pip3 install -r requirements.txt
```

## 사용법

### PDF → JPG 변환
```bash
python3 pdf_to_jpg.py document.pdf              # 단일 파일
python3 pdf_to_jpg.py file1.pdf file2.pdf     # 여러 파일
python3 pdf_to_jpg.py ~/Documents/             # 폴더 (하위 폴더 포함)
```
**출력:** `{원본명}.jpg` 또는 `{원본명}_001.jpg`, `{원본명}_002.jpg` (원본과 같은 폴더)

### PDF → 이미지 분리
```bash
python3 pdf_to_images.py document.pdf          # 단일 PDF
python3 pdf_to_images.py file1.pdf file2.pdf   # 여러 PDF
```
**출력:** `{원본명}_images/` 폴더에 `{원본명}_001.jpg`, `{원본명}_002.jpg` 생성

### 이미지 → PDF 변환
```bash
python3 images_to_pdf.py image.jpg             # 단일 이미지 → image.pdf
python3 images_to_pdf.py img1.jpg img2.png     # 여러 이미지 → {폴더명}_merged.pdf
python3 images_to_pdf.py ~/Pictures/vacation/ # 폴더 → {폴더명}_merged.pdf
```
**출력:** 단일은 `{이미지명}.pdf`, 여러 개/폴더는 `{폴더명}_merged.pdf` (중복 시 `_1`, `_2` 자동 추가)

## 문제 해결
```bash
pip3 install -r requirements.txt       # 패키지 오류 시
```
