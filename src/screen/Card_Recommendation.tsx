import React, { useState } from "react";
import IMAGES from "../images/image_address";
import "./Card_Recommendation.css";

type Benefit = {
  icon: string;
  label: string;
};

type CardInfo = {
  id: string;
  name: string;
  issuer: string;
  summary: string;
  image: string;
  isAiPick?: boolean;
  benefits: Benefit[];
};

/* 상단 AI Pick 신용카드 2개 */
const featuredCreditCards: CardInfo[] = [
  {
    id: "hyundai-z-work",
    name: "현대카드 Z work Edition 2",
    issuer: "현대카드",
    summary:
      "대중교통, 택시, 편의점 등 직장인들이 필수 이용하는 카테고리에 할인 혜택이 있습니다.",
    image: IMAGES.hyundaiCardZ,
    isAiPick: true,
    benefits: [
      { icon: IMAGES.discountBus, label: "교통비 할인" },
      { icon: IMAGES.cashBackIcon, label: "캐시백" },
    ],
  },
  {
    id: "hyundai-m",
    name: "현대카드 M",
    issuer: "현대카드",
    summary:
      "최대 50만 포인트를 먼저 받아 사용하고 카드를 이용하며 M포인트를 적립할 수 있는 카드입니다.",
    image: IMAGES.hyundaiCardM,
    isAiPick: true,
    benefits: [
      { icon: IMAGES.discountBus, label: "교통비 할인" },
      { icon: IMAGES.discountShopping, label: "쇼핑 할인" },
    ],
  },
];

/* 하단 신용카드 리스트 (4개) */
const creditCardList: CardInfo[] = [
  {
    id: "every-mile-skypass",
    name: "카드의정석 EVERY MILE SKYPASS",
    issuer: "우리카드",
    summary: "사용금액별 0.6~0.3% 적립",
    image: IMAGES.everyMileSkypass,
    benefits: [{ icon: IMAGES.discountBus, label: "교통비 할인" }],
  },
  {
    id: "naver-pay-money",
    name: "네이버페이 머니카드",
    issuer: "네이버페이",
    summary: "사용금액별 해외 온/오프라인 3% 적립",
    image: IMAGES.naverPayMoneyCard,
    benefits: [{ icon: IMAGES.discountShopping, label: "쇼핑 할인" }],
  },
  {
    id: "shinhan-mr-life",
    name: "신한카드 Mr.Life",
    issuer: "신한카드",
    summary: "사용금액별 최대 29망원 캐시백 적립",
    image: IMAGES.shinhanMrLife,
    benefits: [
      { icon: IMAGES.discountCafe, label: "쇼핑 할인" },
      { icon: IMAGES.cashBackIcon, label: "캐시백" },
    ],
  },
  {
    id: "samsung-taptap-o",
    name: "삼성카드 taptap O",
    issuer: "삼성카드",
    summary: "사용금액별 최대92만원 혜택 적립",
    image: IMAGES.samsungTaptapO,
    benefits: [
      { icon: IMAGES.discountCafe, label: "카페 할인" },
      { icon: IMAGES.discountBus, label: "교통비 할인" },
    ],
  },
];

/* 하단 체크카드 리스트 (4개) */
const checkCardList: CardInfo[] = [
  {
    id: "one-check",
    name: "ONE 체크카드",
    issuer: "케이뱅크",
    summary: "사용금액별 최대 1.1% 적립.",
    image: IMAGES.oneCheckCard,
    benefits: [{ icon: IMAGES.discountBus, label: "교통비 할인" }],
  },
  {
    id: "shinhan-hey-young",
    name: "신한카드 Hey Young",
    issuer: "신한카드",
    summary: "사용금액별 최대29망원 캐시백 적립",
    image: IMAGES.shinhanHeyYoung,
    benefits: [
      { icon: IMAGES.discountShopping, label: "쇼핑 할인" },
      { icon: IMAGES.discountBus, label: "공과금 할인" },
    ],
  },
  {
    id: "tossbank-check",
    name: "토스뱅크 체크카드",
    issuer: "토스뱅크",
    summary: "사용액별 월 최대 35,000원 적립",
    image: IMAGES.tossbankCheckCard,
    benefits: [{ icon: IMAGES.cashBackIcon, label: "캐시백" }],
  },
  {
    id: "mobilience-card",
    name: "모빌리언스카드",
    issuer: "KG모빌리언스",
    summary: "사용액별 KFC 10% 즉시할인 적립",
    image: IMAGES.mobilienceCard,
    benefits: [
      { icon: IMAGES.discountCafe, label: "카페 할인" },
      { icon: IMAGES.discountBus, label: "교통비 할인" },
    ],
  },
];

const CardRecommendation: React.FC = () => {
  const [activeTab, setActiveTab] = useState<"credit" | "check">("credit");

  return (
    <main className="card-recommendation">
      <section className="card-recommendation__inner">
        {/* 상단 타이틀 */}
        <h1 className="card-recommendation__title">
          이 카드가 잘 어울리실 꺼 같아요.
        </h1>

        {/* 상단 AI Pick 신용카드 2개 */}
        <section className="card-recommendation__featured">
          <div className="card-recommendation__featured-list">
            {featuredCreditCards.map((card) => (
              <article
                key={card.id}
                className="card-item card-item--featured"
              >
                <div className="card-item__image-wrapper">
                  <img
                    src={card.image}
                    alt={card.name}
                    className="card-item__image card-item__image--featured"
                  />
                  {card.isAiPick && (
                    <img
                      src={IMAGES.cardAiPick}
                      alt="AI Pick"
                      className="card-item__ai-badge"
                    />
                  )}
                </div>

                <div className="card-item__body card-item__body--featured">
                  <h2 className="card-item__name card-item__name--featured">
                    {card.name}
                  </h2>
                  <p className="card-item__summary card-item__summary--featured">
                    {card.summary}
                  </p>

                  <div className="card-item__benefits-row">
                    {card.benefits.map((b) => (
                      <div
                        key={b.label}
                        className="card-benefit card-benefit--featured"
                      >
                        <div className="card-benefit__icon">
                          <img src={b.icon} alt={b.label} />
                        </div>
                        <span className="card-benefit__label">
                          {b.label}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </article>
            ))}
          </div>
        </section>

        {/* 신용 / 체크 탭 버튼 */}
        <section className="card-recommendation__tabs">
          <button
            type="button"
            className={
              "card-tab" +
              (activeTab === "credit" ? " card-tab--active" : "")
            }
            onClick={() => setActiveTab("credit")}
          >
            신용 카드
          </button>
          <button
            type="button"
            className={
              "card-tab" +
              (activeTab === "check" ? " card-tab--active" : "")
            }
            onClick={() => setActiveTab("check")}
          >
            체크 카드
          </button>
        </section>

        {/* 하단 카드 리스트: 탭에 따라 신용 / 체크 전환 */}
        {activeTab === "credit" ? (
          /* ---------------------------
             신용카드 리스트
             --------------------------- */
          <section className="card-recommendation__list">
            {creditCardList.map((card) => (
              <article
                key={card.id}
                className="card-item card-item--list"
              >
                <div className="card-item__image-wrapper card-item__image-wrapper--list">
                  <img
                    src={card.image}
                    alt={card.name}
                    className="card-item__image card-item__image--list"
                  />
                </div>

                <div className="card-item__body card-item__body--list">
                  <h2 className="card-item__name">{card.name}</h2>
                  <p className="card-item__issuer">
                    발급처&nbsp;{card.issuer}
                  </p>
                  <p className="card-item__summary">{card.summary}</p>

                  <div className="card-item__benefits-row card-item__benefits-row--list">
                    {card.benefits.map((b) => (
                      <div
                        key={b.label}
                        className="card-benefit card-benefit--list"
                      >
                        <div className="card-benefit__icon">
                          <img src={b.icon} alt={b.label} />
                        </div>
                        <span className="card-benefit__label">
                          {b.label}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </article>
            ))}
          </section>
        ) : (
          /* ---------------------------
             체크카드 리스트
             (신용카드와 동일 레이아웃, 데이터만 다름)
             --------------------------- */
          <section className="card-recommendation__list">
            {checkCardList.map((card) => (
              <article
                key={card.id}
                className="card-item card-item--list"
              >
                <div className="card-item__image-wrapper card-item__image-wrapper--list">
                  <img
                    src={card.image}
                    alt={card.name}
                    className="card-item__image card-item__image--list"
                  />
                </div>

                <div className="card-item__body card-item__body--list">
                  <h2 className="card-item__name">{card.name}</h2>
                  <p className="card-item__issuer">
                    발급처&nbsp;{card.issuer}
                  </p>
                  <p className="card-item__summary">{card.summary}</p>

                  <div className="card-item__benefits-row card-item__benefits-row--list">
                    {card.benefits.map((b) => (
                      <div
                        key={b.label}
                        className="card-benefit card-benefit--list"
                      >
                        <div className="card-benefit__icon">
                          <img src={b.icon} alt={b.label} />
                        </div>
                        <span className="card-benefit__label">
                          {b.label}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </article>
            ))}
          </section>
        )}
      </section>
    </main>
  );
};

export default CardRecommendation;
