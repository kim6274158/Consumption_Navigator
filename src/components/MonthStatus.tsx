import React from "react";
import "../styles/MonthStatus.css";

type SummaryMetric = {
  label: string;
  current: string;
  currentUnit?: string;
  targetPrefix?: string;
  targetValue?: string;
  targetUnit?: string;
};

type InsightCard = {
  id: string;
  tone: "alert" | "suggestion";
  tag: string;
  message: string;
  highlight?: string;
  messageEnd?: string;
  helper?: string;
};

const summaryMetrics: SummaryMetric[] = [
  {
    label: "지출 건수",
    current: "16",
    currentUnit: "건",
    targetPrefix: "/",
    targetValue: "28",
  },
  {
    label: "지출 금액",
    current: "3,000,000",
    targetPrefix: "/",
    targetValue: "2,000,000",
  },
];

const highlightMetrics = [
  {
    label: "가장 컸던 지출 항목",
    value: "주류",
  },
  {
    label: "급상승 항목",
    value: "카페",
  },
];

const insights: InsightCard[] = [
  {
    id: "habit",
    tone: "alert",
    tag: "나쁜 습관",
    message: "1주차에 소비의",
    highlight: "60%",
    messageEnd: "를 하는 경향이 있어요.",
  },
  {
    id: "suggestion",
    tone: "suggestion",
    tag: "이렇게 개선해 보는 것은 어떠세요",
    message: "1주차에 카페 항목 소비를 6만원 정도 더 많이 설정해 보세요.",
    helper: "성공 확률이 30% 정도 올라가요!",
  },
];

const MonthStatus: React.FC = () => {
  return (
    <section className="month-status" aria-label="이번 달 현황">
      <header className="month-status__header">
        <div className="month-status__headline">
          <h2>이번 달 현황</h2>
        </div>
      </header>

      <div className="month-status__summary-card">
        <div className="month-status__summary-heading">
          <div className="month-status__summary-month">
            <span>11월</span>
          </div>
          <p className="month-status__summary-copy">
            지출을 평가해 볼까요? 소비습관, Ai가 제시해 드립니다.
          </p>
        </div>

        <div className="month-status__summary-grid">
          {summaryMetrics.map((metric) => (
            <article className="month-status__summary-item" key={metric.label}>
              <p className="month-status__summary-label">{metric.label}</p>
              <div className="month-status__summary-value-row">
                <p className="month-status__summary-value">
                  <span>{metric.current}</span>
                  {metric.currentUnit && (
                    <span className="month-status__summary-unit">
                      {metric.currentUnit}
                    </span>
                  )}
                </p>
                {metric.targetValue && (
                  <p className="month-status__summary-target">
                    {metric.targetPrefix && (
                      <span>{metric.targetPrefix}&nbsp;</span>
                    )}
                    <span>{metric.targetValue}</span>
                    {/* 목표 값에는 단위 표시하지 않음 (건, 원 제거) */}
                  </p>
                )}
              </div>
            </article>
          ))}

          {highlightMetrics.map((metric) => (
            <article className="month-status__summary-item" key={metric.label}>
              <p className="month-status__summary-label">{metric.label}</p>
              <p className="month-status__highlight">{metric.value}</p>
            </article>
          ))}
        </div>
      </div>

      <section className="month-status__insight" aria-label="소비 평가">
        <header className="month-status__insight-header">
          <p className="month-status__insight-title">소비 평가</p>
          <p className="month-status__insight-sub">
            이번달에는 바쁘셨을 꺼라 믿어요!
          </p>
        </header>

        <div className="month-status__insight-cards">
          {insights.map((card) => (
            <article
              key={card.id}
              className={`month-status__insight-card month-status__insight-card--${card.tone}`}
            >
              <span className="month-status__insight-tag">{card.tag}</span>
              <p className="month-status__insight-message">
                {card.message}
                {card.highlight && (
                  <span className="month-status__insight-highlight">
                    {card.highlight}
                  </span>
                )}
                {card.messageEnd}
              </p>
              {card.helper && (
                <p className="month-status__insight-helper">{card.helper}</p>
              )}
            </article>
          ))}
        </div>
      </section>
    </section>
  );
};

export default MonthStatus;
