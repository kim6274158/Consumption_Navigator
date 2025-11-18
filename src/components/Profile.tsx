import React from "react";
import IMAGES from "../images/image_address";
import "../styles/Profile.css";

const Profile: React.FC = () => {
  return (
    <section className="profile-container" aria-label="마이페이지 프로필">
      {/* 왼쪽 프로필 영역 */}
      <div className="profile-left">
        <div className="profile-avatar">
          <img src={IMAGES.mypageProfile} alt="마이페이지 프로필 이미지" />
        </div>

        <div className="profile-info">
          <h1 className="profile-title">
            안녕하세요. <span className="profile-title-name">지유빈</span> 고객님
          </h1>

          <p className="profile-subcopy">현명한 소비습관, Ai가 제시해 드립니다.</p>

          <button type="button" className="profile-action-btn">
            개인정보 수정
          </button>
        </div>
      </div>

      {/* 오른쪽 목표 소비 영역 */}
      <aside className="profile-budget" aria-label="소비 목표 정보">
        <div className="profile-budget-top">
          <button type="button" className="profile-period-btn">
            <span className="profile-period-text">이번주</span>
            <span className="profile-period-arrow" aria-hidden="true" />
          </button>

          <div className="profile-budget-title">
            <span className="profile-budget-label">소비목표금액</span>
          </div>
        </div>

        <div
          className="profile-budget-amount"
          aria-label="소비 목표 금액 14만 5천원"
        >
          14만5천원
        </div>

        <div className="profile-budget-meta">
          <span className="profile-meta-label">지난 주 대비</span>

          <div className="profile-meta-row">
            <span className="profile-meta-title">예산 초과 항목</span>
            <span className="profile-meta-value profile-meta-value--danger">
              <span className="profile-meta-sign">+</span> 2개
            </span>
          </div>

          <div className="profile-meta-row">
            <span className="profile-meta-title">소비한 금액</span>
            <span className="profile-meta-value profile-meta-value--info">
              <span className="profile-meta-sign">-</span> 6만원
            </span>
          </div>
        </div>
      </aside>
    </section>
  );
};

export default Profile;