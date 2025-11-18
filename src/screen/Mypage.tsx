import React from "react";
import SearchBar from "../components/SearchBar";
import Profile from "../components/Profile";
import MonthStatus from "../components/MonthStatus";
import Trend from "../components/Trend";
import "./Mypage.css";

const Mypage: React.FC = () => {
  return (
    <main className="mypage-main">
      <div className="mypage-content">
        <section className="mypage-search-section">
          <SearchBar />
        </section>
        <section className="mypage-profile-section">
          <Profile />
        </section>
        <section className="mypage-month-status-section">
          <MonthStatus />
        </section>
        <section className="mypage-trend-section">
          <Trend />
        </section>
      </div>
    </main>
  );
};

export default Mypage;


