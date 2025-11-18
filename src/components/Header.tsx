// src/components/Header.tsx
import React from 'react';
import IMAGES from '../images/image_address';
import '../styles/Header.css';

export type MenuKey = '소비분석' | '재무관리' | '소비일기' | '카드 추천' | '마이페이지';

interface HeaderProps {
  activeMenu: MenuKey;
  onMenuClick?: (menu: MenuKey) => void;
}

const menuList: MenuKey[] = ['소비분석', '재무관리', '소비일기', '카드 추천', '마이페이지'];

const Header: React.FC<HeaderProps> = ({ activeMenu, onMenuClick }) => {
  return (
    <header className="mypage-header">
      <div className="mypage-header-inner">
        {/* 로고 */}
        <div className="header-logo-wrapper">
          <img
            src={IMAGES.mypageLogo}
            alt="O!ALL 로고"
            className="header-logo"
          />
        </div>

        {/* 메뉴 */}
        <nav className="header-nav">
          {menuList.map((menu) => (
            <button
              key={menu}
              type="button"
              className={
                'header-menu-button' +
                (activeMenu === menu ? ' header-menu-button--active' : '')
              }
              onClick={() => onMenuClick && onMenuClick(menu)}
            >
              <span className="header-menu-text">{menu}</span>
            </button>
          ))}
        </nav>
      </div>
    </header>
  );
};

export default Header;

