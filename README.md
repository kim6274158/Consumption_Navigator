# Consumption Navigator - Frontend (소비게이터)

개인의 소비 패턴을 분석해 **맞춤형 카드 추천**, **소비 트렌드 분석**, **AI 챗봇**, **소비일기 작성 및 조회 기능**을 제공하는 웹 서비스입니다.  
본 레포지토리는 소비게이터의 **프론트엔드(React + TypeScript)** 코드가 포함되어 있습니다.

---

## 1. 기술 스택

### Frontend
- **Language**: TypeScript  
- **Framework**: React  
- **Bundler / Dev Server**: Vite 또는 CRA  
- **Styling**: CSS (컴포넌트별 세부 스타일 분리)  
- **State 관리**: React Hooks  

---

## 2. 실행 방법

```bash
# 1. 레포지토리 클론
git clone https://github.com/kim6274158/Consumption_Navigator.git
cd Consumption_Navigator

# 2. 프론트엔드 브랜치로 이동
git checkout frontend

# 3. 패키지 설치
npm install

# 4. 개발 서버 실행
npm run dev     # (Vite 기반일 경우)
# 또는
npm start       # (CRA 기반일 경우)

## 3. 폴더 구
Consumption_Navigator/
├── public/                  # 정적 파일 (favicon, index.html 등)
├── src/
│   ├── components/          # UI 컴포넌트
│   │   ├── Header.tsx
│   │   ├── SearchBar.tsx
│   │   ├── ChatBotModal.tsx
│   │   ├── Profile.tsx
│   │   ├── MonthStatus.tsx
│   │   ├── Trend.tsx
│   │   ├── Trend_Consumption.tsx
│   │   ├── LifeStyle.tsx
│   │   ├── Diary.tsx
│   │   └── ...
│   │
│   ├── screen/              # 페이지 단위 구성
│   │   ├── Mypage.tsx
│   │   ├── Card_Recommendation.tsx
│   │   ├── Consumption_diary.tsx
│   │   └── ...
│   │
│   ├── styles/              # CSS 스타일 파일
│   │   ├── Profile.css
│   │   ├── SearchBar.css
│   │   ├── MonthStatus.css
│   │   ├── Trend.css
│   │   ├── Trend_Consumption.css
│   │   ├── LifeStyle.css
│   │   ├── Diary.css
│   │   ├── Card_Recommendation.css
│   │   ├── Mypage.css
│   │   └── ...
│   │
│   ├── images/              # 이미지 리소스
│   │   ├── image_address.ts
│   │   ├── mypage_logo.png
│   │   ├── mypage_profile.png
│   │   ├── mypage_reading_glasses.png
│   │   ├── mypage_life_style.png
│   │   ├── chatbot_icon.png
│   │   ├── chatbot_image_upload.png
│   │   ├── chatbot_send.png
│   │   └── ...
│   │
│   ├── App.tsx              # 전체 라우팅 및 레이아웃
│   ├── main.tsx / index.tsx # 엔트리 포인트
│   └── react-app-env.d.ts   # 타입 정의
│
├── package.json
├── tsconfig.json
├── .gitignore
└── README.md

