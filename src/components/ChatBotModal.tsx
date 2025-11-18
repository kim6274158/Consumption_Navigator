// C:\Users\kim62\front_end\src\components\ChatBotModal.tsx
import React, { useState, useRef, useEffect } from "react";
import IMAGES from "../images/image_address";
import "../styles/ChatBotModal.css";

interface ChatBotModalProps {
  isOpen: boolean;
  onClose: () => void;
}

interface Message {
  id: number;
  text: string;
  isBot: boolean;
  timestamp: Date;
  imageUrl?: string;
}

const ChatBotModal: React.FC<ChatBotModalProps> = ({ isOpen, onClose }) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      text: "안녕하세요. 어떤 것이 궁금하신가요?",
      isBot: true,
      timestamp: new Date(),
    },
  ]);

  const [inputText, setInputText] = useState("");
  const [selectedImage, setSelectedImage] = useState<string | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  useEffect(() => {
    if (isOpen && messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages, isOpen]);

  const handleSendMessage = () => {
    // 텍스트와 이미지 둘 다 비어 있으면 전송 X
    if (inputText.trim() === "" && !selectedImage) return;

    const newMessage: Message = {
      id: messages.length + 1,
      text: inputText,
      isBot: false,
      timestamp: new Date(),
      imageUrl: selectedImage ?? undefined,
    };

    setMessages((prev) => [...prev, newMessage]);
    setInputText("");
    setSelectedImage(null);

    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }

    // 현재는 고정 답변
    setTimeout(() => {
      const botResponse: Message = {
        id: newMessage.id + 1,
        text: `영수증 내용을 보면 총 217,000원을 지출했고, 구성은 아래와 같습니다.

생삼겹살 25인분 — 175,000원
맥주 4개 — 12,000원
음료수 1개 — 4,000원
밥+된장 13개 — 26,000원

✔︎ 어디서 소비를 줄일 수 있을까?
1) 가장 조정 여지가 큰 항목: 생삼겹살(175,000원)
전체 지출의 80% 이상을 차지.
인분 수가 많기 때문에,
주문을 한 번에 하지 말고 추가 주문 방식으로 조절하기
인분 수를 10~20%만 줄여도 지출 절감 효과가 큼.

2) 음료(맥주·음료) 줄이기
맥주·음료는 합쳐서 16,000원이지만
외식에서 가장 줄이기 쉬운 ‘부가 비용’.
술이나 음료를 줄이거나 물로 대체하면
즉각적 절감 효과가 있음.

3) 밥+된장 13개(26,000원)
1인당 거의 1세트씩 주문한 것으로 보임.
실제로는 고기 남는 양에 따라
밥+된장을 전원 주문하지 않고
2~3개 공유도 가능.`,
        isBot: true,
        timestamp: new Date(),
      };


      setMessages((prev) => [...prev, botResponse]);
    }, 600);
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleImageButtonClick = () => {
    fileInputRef.current?.click();
  };

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const imageUrl = URL.createObjectURL(file);
    setSelectedImage(imageUrl);
  };

  if (!isOpen) return null;

  return (
    <div className="chatbot-modal-backdrop" onClick={onClose}>
      <div
        className="chatbot-modal-container"
        onClick={(e) => e.stopPropagation()}
      >
        {/* 헤더 */}
        <div className="chatbot-modal-header">
          <h2 className="chatbot-modal-title">Chat Bot</h2>
          <button
            type="button"
            className="chatbot-modal-close-button"
            onClick={onClose}
            aria-label="닫기"
          >
            <svg
              width="32"
              height="32"
              viewBox="0 0 32 32"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                d="M8 8L24 24M24 8L8 24"
                stroke="#5E5E5E"
                strokeWidth="2"
                strokeLinecap="round"
              />
            </svg>
          </button>
        </div>

        {/* 메시지 영역 */}
        <div className="chatbot-modal-messages">
          <div className="chatbot-message-container">
            {/* 첫 챗봇 메시지 */}
            <div className="chatbot-message-bot">
              <div className="chatbot-avatar">
                <img
                  src={IMAGES.chatbotIcon}
                  alt="챗봇 아이콘"
                  className="chatbot-avatar-image"
                />
              </div>
              <div className="chatbot-message-bubble bot">
                <div className="chatbot-message-name">OLLA</div>
                <div className="chatbot-message-text">
                  안녕하세요. 어떤 것이 궁금하신가요?
                </div>
              </div>
            </div>

            {/* 나머지 메시지들 */}
            {messages
              .filter((msg) => msg.id !== 1)
              .map((message) => {
                if (message.isBot) {
                  return (
                    <div key={message.id} className="chatbot-message-bot">
                      <div className="chatbot-avatar">
                        <img
                          src={IMAGES.chatbotIcon}
                          alt="챗봇 아이콘"
                          className="chatbot-avatar-image"
                        />
                      </div>
                      <div className="chatbot-message-bubble bot">
                        <div className="chatbot-message-name">OLLA</div>
                        <div className="chatbot-message-text">
                          {message.text}
                        </div>
                      </div>
                    </div>
                  );
                }

                // 사용자 메시지: 텍스트 + 이미지가 하나의 그룹에서 가까이 붙어 나오도록
                return (
                  <div key={message.id} className="chatbot-message-user-group">
                    {message.text && (
                      <div className="chatbot-message-bubble user user-text-bubble">
                        <div className="chatbot-message-text">
                          {message.text}
                        </div>
                      </div>
                    )}
                    {message.imageUrl && (
                      <div className="chatbot-message-bubble user user-image-bubble">
                        <img
                          src={message.imageUrl}
                          alt="사용자 업로드 이미지"
                          className="chatbot-message-image"
                        />
                      </div>
                    )}
                  </div>
                );
              })}

            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* 입력 영역 */}
        <div className="chatbot-modal-input-container">
          <button
            type="button"
            className="chatbot-input-image-button"
            aria-label="이미지 업로드"
            onClick={handleImageButtonClick}
          >
            <img
              src={IMAGES.chatbotImageUpload}
              alt="이미지 업로드"
              className="chatbot-input-image-icon"
            />
          </button>

          {/* 숨겨진 파일 input */}
          <input
            type="file"
            accept="image/*"
            ref={fileInputRef}
            style={{ display: "none" }}
            onChange={handleImageChange}
          />

          {/* 입력 + 미리보기 */}
          <div className="chatbot-input-main">
            {/* GPT처럼 입력창 위에 떠 있는 미리보기 (absolute라서 버튼 위치 안 밀어냄) */}
            {selectedImage && (
              <div className="chatbot-image-preview">
                <img
                  src={selectedImage}
                  alt="업로드 이미지 미리보기"
                  className="chatbot-image-preview-img"
                />
                <button
                  type="button"
                  className="chatbot-image-preview-remove"
                  onClick={() => setSelectedImage(null)}
                  aria-label="이미지 제거"
                >
                  ×
                </button>
              </div>
            )}

            <div className="chatbot-input-wrapper">
              <input
                type="text"
                className="chatbot-input"
                placeholder="모르시는 항목은 챗봇에게 여쭤보세요."
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                onKeyPress={handleKeyPress}
              />

              <button
                type="button"
                className="chatbot-input-send-button"
                onClick={handleSendMessage}
                aria-label="전송"
              >
                <img
                  src={IMAGES.chatbotSend}
                  alt="전송"
                  className="chatbot-input-send-icon"
                />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatBotModal;

