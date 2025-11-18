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

## 2. 파일구조

Consumption_Navigator/
├─ public/                         # 정적 리소스 (favicon, index.html 등)
├─ src/
│  ├─ components/                  # 재사용 가능한 UI 컴포넌트
│  │   ├─ Profile.tsx              # 마이페이지 상단 프로필 영역
│  │   ├─ SearchBar.tsx            # 메인 검색바 및 챗봇 진입부
│  │   ├─ MonthStatus.tsx          # 이번 달 소비 현황 컴포넌트
│  │   ├─ Trend.tsx                # 소비 트렌드 & 패턴 컴포넌트
│  │   ├─ Diary.tsx                # 소비일기 작성/표시 컴포넌트
│  │   └─ ChatBotModal.tsx         # AI 챗봇 모달
│  ├─ screen/                      # 페이지(화면) 단위 컴포넌트
│  │   ├─ Mypage.tsx               # 마이페이지 메인 화면
│  │   ├─ Card_Recommendation.tsx  # 카드 추천 화면
│  │   └─ Consumption_diary.tsx    # 소비일기 전체 화면
│  ├─ styles/                      # 스타일(CSS) 파일 모음
│  │   ├─ Profile.css
│  │   ├─ SearchBar.css
│  │   ├─ MonthStatus.css
│  │   ├─ Trend.css
│  │   ├─ Diary.css
│  │   ├─ Card_Recommendation.css
│  │   └─ Consumption_diary.css
│  ├─ images/                      # 이미지 에셋
│  │   ├─ image_address.ts         # 이미지 경로를 객체로 관리
│  │   ├─ mypage_logo.png
│  │   ├─ mypage_profile.png
│  │   └─ ...                      # 그 외 카드/아이콘 이미지
│  ├─ App.tsx                      # 루트 App 컴포넌트
│  ├─ main.tsx                     # 진입점(ReactDOM 렌더링)
│  └─ vite-env.d.ts / 기타 설정 파일
├─ package.json                    # 의존성 및 npm script 정의
├─ tsconfig.json                   # TypeScript 설정
├─ .gitignore
└─ README.md

---

## 3. 실행 방법

```bash
1. 레포지토리 클론
git clone https://github.com/kim6274158/Consumption_Navigator.git
cd Consumption_Navigator

2. 프론트엔드 브랜치로 이동
git checkout frontend

3. 패키지 설치
npm install

4. 개발 서버 실행
npm run dev     # (Vite 기반일 경우)
# 또는
npm start       # (CRA 기반일 경우)

