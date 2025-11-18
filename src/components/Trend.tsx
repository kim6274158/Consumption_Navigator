import React from "react";
import IMAGES from "../images/image_address";
import "../styles/Trend.css";

const Trend: React.FC = () => {
  return (
    <section className="trend" aria-label="트렌드 & 패턴">
      <header className="trend__header">
        <div className="trend__headline">
          <h2>트렌드 & 패턴</h2>
        </div>
      </header>

      <div className="trend__card">
        <div className="trend__content">
          {/* 왼쪽: 라이프 스타일 섹션 */}
          <div className="trend__section">
            <div className="trend__section-header">
              <h3 className="trend__section-title">라이프 스타일</h3>
              <p className="trend__section-subtitle">열렬한 모임 예찬자</p>
            </div>

            <div className="trend__stats">
              <div className="trend__stat-item">
                <div className="trend__stat-row">
                  <div className="trend__stat-label-value">
                    <span className="trend__stat-label">상위</span>
                    <span className="trend__stat-value">24%</span>
                  </div>
                  <p className="trend__stat-desc">해당 라이프 스타일 유형 중</p>
                </div>
                <div className="trend__stat-arrow">←</div>
                <div className="trend__stat-row">
                  <div className="trend__stat-label-value">
                    <span className="trend__stat-label">상위</span>
                    <span className="trend__stat-value">16%</span>
                  </div>
                  <p className="trend__stat-desc">주류 비용 잘 지켜도 이렇게</p>
                </div>
              </div>
            </div>

            <div className="trend__image-wrapper">
              <img
                src={IMAGES.mypageLifeStyle}
                alt="라이프 스타일 차트"
                className="trend__image"
              />
            </div>
          </div>

          {/* 오른쪽: 나이 대비 섹션 */}
          <div className="trend__section">
            <div className="trend__section-header">
              <h3 className="trend__section-title">나이 대비</h3>
              <p className="trend__section-subtitle">28살 여성 중</p>
            </div>

            <div className="trend__stats">
              <div className="trend__stat-item">
                <div className="trend__stat-row">
                  <div className="trend__stat-label-value">
                    <span className="trend__stat-label">상위</span>
                    <span className="trend__stat-value">12%</span>
                  </div>
                  <p className="trend__stat-desc">20대 후반 여성 중</p>
                </div>
                <div className="trend__stat-arrow">←</div>
                <div className="trend__stat-row">
                  <div className="trend__stat-label-value">
                    <span className="trend__stat-label">상위</span>
                    <span className="trend__stat-value">9%</span>
                  </div>
                  <p className="trend__stat-desc">주류 비용 잘 지켜도 이렇게</p>
                </div>
              </div>

              <div className="trend__stat-item">
                <div className="trend__stat-row">
                  <div className="trend__stat-label-value">
                    <span className="trend__stat-label">상위</span>
                    <span className="trend__stat-value">50%</span>
                  </div>
                  <p className="trend__stat-desc">20대 후반 중</p>
                </div>
                <div className="trend__stat-arrow">←</div>
                <div className="trend__stat-row">
                  <div className="trend__stat-label-value">
                    <span className="trend__stat-label">상위</span>
                    <span className="trend__stat-value">48%</span>
                  </div>
                  <p className="trend__stat-desc">주류 비용 잘 지켜도 이렇게</p>
                </div>
              </div>

              <div className="trend__stat-item">
                <div className="trend__stat-row">
                  <div className="trend__stat-label-value">
                    <span className="trend__stat-label">상위</span>
                    <span className="trend__stat-value">64%</span>
                  </div>
                  <p className="trend__stat-desc">20대 여성 중</p>
                </div>
                <div className="trend__stat-arrow">←</div>
                <div className="trend__stat-row">
                  <div className="trend__stat-label-value">
                    <span className="trend__stat-label">상위</span>
                    <span className="trend__stat-value">26%</span>
                  </div>
                  <p className="trend__stat-desc">주류 비용 잘 지켜도 이렇게</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Trend;
