import React from "react";
import "./Consumption_diary.css";
import "../styles/MonthStatus.css"; // MonthStatus 스타일 그대로 재사용
import IMAGES from "../images/image_address";
import Diary from "../components/Diary"; // ★ 새로 추가

const ConsumptionDiary: React.FC = () => {
  return (
    <div className="consumption-diary-main">
      <div className="consumption-diary-content">
        {/* 올해의 현황 + 범례 */}
        <section className="section-center">
          <div className="consumption-overview section-inner">
            <h2 className="consumption-overview__title">올해의 현황</h2>
            <p className="consumption-overview__subtitle">
              그래도 목표와 소비액의 격차가 많이 줄었어요.
            </p>
            <p className="consumption-overview__description">
              성공 확률이 8% 정도 올라가요!
            </p>

            <div className="consumption-overview__legend">
              <div className="legend-item">
                <img
                  src={IMAGES.targetConsumptionTotalIcon}
                  alt="목표 소비 총액 아이콘"
                />
                <span>실제 소비액</span>
              </div>
              <div className="legend-item">
                <img
                  src={IMAGES.targetConsumptionAmountIcon}
                  alt="현재 소비 금액 아이콘"
                />
                <span>목표 소비액의 총합</span>
              </div>
              <div className="legend-item">
                <img
                  src={IMAGES.goalAchievementRateIcon}
                  alt="성공 확률 아이콘"
                />
                <span>목표 달성률 80% 이상 성공 유무 </span>
              </div>
            </div>
          </div>
        </section>

        {/* 그래프 이미지 */}
        <section className="section-center">
          <img
            src={IMAGES.graphImage}
            alt="올해 소비 추이 그래프"
            className="consumption-graph"
          />
        </section>

        {/* ============================== */}
        {/* 11월 지출 요약 - MonthStatus 스타일 */}
        {/* ============================== */}
        <section className="consumption-month-status-section">
          <section className="month-status" aria-label="이번 달 현황">
            <div className="month-status__summary-card">
              {/* 상단 헤더 (11월 + 설명) */}
              <div className="month-status__summary-heading">
                <div className="month-status__summary-month">
                  <span>11월</span>
                </div>
                <p className="month-status__summary-copy">
                  지출을 평가해볼까요? 소비습관, AI가 제시해 드립니다.
                </p>
              </div>

              {/* 지표 4개 */}
              <div className="month-status__summary-grid">
                {/* 지출 건수 */}
                <article className="month-status__summary-item">
                  <p className="month-status__summary-label">지출 건수</p>
                  <div className="month-status__summary-value-row">
                    <p className="month-status__summary-value">
                      <span>16</span>
                      <span className="month-status__summary-unit">건</span>
                    </p>
                    <p className="month-status__summary-target">
                      <span>/</span>
                      <span>28</span>
                    </p>
                  </div>
                </article>

                {/* 지출 금액 */}
                <article className="month-status__summary-item">
                  <p className="month-status__summary-label">지출 금액</p>
                  <div className="month-status__summary-value-row">
                    <p className="month-status__summary-value">
                      <span>3,000,000</span>
                      <span className="month-status__summary-unit">원</span>
                    </p>
                    <p className="month-status__summary-target">
                      <span>/</span>
                      <span>2,000,000</span>
                    </p>
                  </div>
                </article>

                {/* 가장 컸던 지출 항목 */}
                <article className="month-status__summary-item">
                  <p className="month-status__summary-label">
                    가장 컸던 지출 항목
                  </p>
                  <p className="month-status__highlight">주류</p>
                </article>

                {/* 급상승 항목 */}
                <article className="month-status__summary-item">
                  <p className="month-status__summary-label">급상승 항목</p>
                  <p className="month-status__highlight">카페</p>
                </article>
              </div>
            </div>
          </section>
        </section>

        {/* ============================== */}
        {/* AI 일기 - MonthStatus 소비 평가 스타일 재사용 */}
        {/* ============================== */}
        <section className="consumption-month-status-section">
          <section className="month-status">
            <section className="month-status__insight" aria-label="AI 일기">
              <header className="month-status__insight-header">
                <p className="month-status__insight-title">AI 일기</p>
                <p className="month-status__insight-sub">
                  1주차인 것에 비해서는 많이 절약하셨어요
                </p>
              </header>

              <div className="month-status__insight-cards">
                {/* AI 분석 카드 */}
                <article className="month-status__insight-card month-status__insight-card--alert">
                  <span className="month-status__insight-tag">나쁜습관</span>
                  <p className="month-status__insight-message">
                    1주차에만 소비를 줄여도 목표 달성 난이도가 줄어들어요.
                  </p>
                </article>

                {/* 제안 카드 */}
                <article className="month-status__insight-card month-status__insight-card--suggestion">
                  <span className="month-status__insight-tag">
                    이렇게 개선해 보는 것은 어떠세요
                  </span>
                  <p className="month-status__insight-message">
                    1주차에만 소비를 줄여도 목표 달성 난이도가 줄어들어요.
                  </p>
                  <p className="month-status__insight-helper">
                    1주차에 12만원만 덜 써도 이번 달 목표 성공 확률이 대폭
                    올라가요.
                  </p>
                </article>
              </div>
            </section>
          </section>
        </section>

        {/* ============================== */}
        {/* ✏️ 새로 만든 일기 컴포넌트 (화면 맨 아래) */}
        {/* ============================== */}
        <section className="section-center">
          <Diary />
        </section>
      </div>
    </div>
  );
};

export default ConsumptionDiary;

