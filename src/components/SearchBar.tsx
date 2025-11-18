import React, { useState, KeyboardEvent } from "react";
import IMAGES from "../images/image_address";
import ChatBotModal from "./ChatBotModal";
import "../styles/SearchBar.css";

const SearchBar: React.FC = () => {
  const [query, setQuery] = useState("");
  const [isChatBotOpen, setIsChatBotOpen] = useState(false);

  const openChatBot = () => {
    setIsChatBotOpen(true);
  };

  const closeChatBot = () => {
    setIsChatBotOpen(false);
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      e.preventDefault();
      openChatBot();
    }
  };

  const handleIconClick = () => {
    openChatBot();
  };

  return (
    <>
      <div className="searchbar">
        <input
          className="searchbar-input"
          type="text"
          placeholder="모르시는 항목은 챗봇에게 여쭤보세요."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
        />

        <button
          type="button"
          className="searchbar-icon-button"
          onClick={handleIconClick}
        >
          <img
            src={IMAGES.mypageReadingGlasses} // ✅ 수정된 부분
            alt="검색 아이콘"
            className="searchbar-icon"
          />
        </button>
      </div>

      <ChatBotModal isOpen={isChatBotOpen} onClose={closeChatBot} />
    </>
  );
};

export default SearchBar;
