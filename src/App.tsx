// src/App.tsx
import React, { useState } from 'react';
import Header, { MenuKey } from './components/Header';
import Mypage from './screen/Mypage';
import CardRecommendation from './screen/Card_Recommendation';
import ConsumptionDiary from './screen/Consumption_diary';
import './App.css';

function App() {
  const [activeMenu, setActiveMenu] = useState<MenuKey>('마이페이지');

  const handleMenuClick = (menu: MenuKey) => {
    setActiveMenu(menu);
  };

  return (
    <div className="app-root">
      <Header activeMenu={activeMenu} onMenuClick={handleMenuClick} />

      {activeMenu === '마이페이지' && <Mypage />}
      {activeMenu === '카드 추천' && <CardRecommendation />}
      {activeMenu === '소비일기' && <ConsumptionDiary />}
    </div>
  );
}

export default App;

