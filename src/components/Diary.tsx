import React, { useState, FormEvent } from "react";
import "../styles/Diary.css";

type DiaryEntry = {
  id: number;
  title: string;
  content: string;
  createdAt: Date;
};

const Diary: React.FC = () => {
  const [activeTab, setActiveTab] = useState<"이번주" | "이전달" | "올해">(
    "이번주"
  );
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [entries, setEntries] = useState<DiaryEntry[]>([]);

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();

    // 제목과 내용이 모두 비어 있으면 저장 안 함
    if (!title.trim() && !content.trim()) return;

    const newEntry: DiaryEntry = {
      id: Date.now(),
      title: title.trim() || "제목 없음",
      content: content.trim(),
      createdAt: new Date(),
    };

    // 새 일기를 맨 위에 추가
    setEntries((prev) => [newEntry, ...prev]);

    // 입력칸 초기화
    setTitle("");
    setContent("");
  };

  return (
    <section className="diary">
      {/* 상단 설명 + 타이틀 */}
      <header className="diary__header">
        <p className="diary__description">
          소비 평가를 보고 일기를 작성하면 다음에 알려드릴게요!
        </p>
        <h2 className="diary__title">직접 소비에 대한 감상을 작성해 주세요</h2>
      </header>

      {/* 탭 영역 (이번주 / 이전달 / 올해) - UI만 */}
      <div className="diary__tabs">
        {(["이번주", "이전달", "올해"] as const).map((tab) => (
          <button
            key={tab}
            type="button"
            className={`diary__tab ${
              activeTab === tab ? "diary__tab--active" : ""
            }`}
            onClick={() => setActiveTab(tab)}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* 입력 카드 + 등록 버튼 */}
      <form className="diary__form" onSubmit={handleSubmit}>
        <div className="diary__card diary__card--editor">
          {/* 제목 입력칸 (굵은 텍스트) */}
          <input
            type="text"
            className="diary__input-title"
            placeholder="내용을 입력해 주세요"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
          />

          {/* 내용 입력칸 */}
          <textarea
            className="diary__input-content"
            placeholder="내용을 입력해 주세요"
            value={content}
            onChange={(e) => setContent(e.target.value)}
            rows={3}
          />
        </div>

        {/* 등록하기 버튼 */}
        <button type="submit" className="diary__submit">
          등록하기
        </button>
      </form>

      {/* 저장된 일기 리스트 영역 */}
      <div className="diary__entries">
        {entries.map((entry) => (
          <article key={entry.id} className="diary__card diary__card--entry">
            <h3 className="diary__entry-title">{entry.title}</h3>
            {entry.content && (
              <p className="diary__entry-content">{entry.content}</p>
            )}
          </article>
        ))}
      </div>
    </section>
  );
};

export default Diary;
