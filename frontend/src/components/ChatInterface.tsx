import React from 'react';
import ReactMarkdown from 'react-markdown';
import './ChatInterface.css';

interface Message {
  id: string;
  type: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
}

interface SystemStatus {
  is_initialized: boolean;
  vector_store: {
    document_count: number;
    status: string;
  };
  tools: Array<{
    name: string;
    description: string;
  }>;
}

interface ChatInterfaceProps {
  messages: Message[];
  isLoading: boolean;
  onQuery: (question: string, useWebSearch: boolean) => void;
  systemStatus: SystemStatus | null;
  isInitialized: boolean;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({
  messages,
  isLoading,
  onQuery,
  systemStatus,
  isInitialized
}) => {
  const [inputValue, setInputValue] = React.useState('');
  const [useWebSearch, setUseWebSearch] = React.useState(true);
  const messagesEndRef = React.useRef<HTMLDivElement>(null);

  React.useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputValue.trim() && !isLoading) {
      onQuery(inputValue, useWebSearch);
      setInputValue('');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const exampleQuestions = [
    'SQL 注入攻击原理与防御',
    'XSS 攻击类型和防护',
    'OWASP Top 10 2024',
    '安全代码审查方法'
  ];

  return (
    <div className="chat-interface">
      {!isInitialized || messages.length === 0 ? (
        <div className="welcome-screen">
          <div className="welcome-content">
            <div className="welcome-icon">
              <svg width="80" height="80" viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="40" cy="40" r="36" stroke="#3B82F6" strokeWidth="3" fill="#EFF6FF"/>
                <path d="M32 28L38 34L48 24" stroke="#3B82F6" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </div>
            <h2>您好！我是网络安全知识助手</h2>
            <p>我可以帮您解答各种网络安全问题，包括：</p>
            
            <div className="example-questions">
              {exampleQuestions.map((question, index) => (
                <button
                  key={index}
                  className="example-question"
                  onClick={() => onQuery(question)}
                  disabled={!isInitialized}
                >
                  {question}
                </button>
              ))}
            </div>

            {!isInitialized && (
              <div className="init-hint">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
                  <line x1="12" y1="9" x2="12" y2="13"/>
                  <line x1="12" y1="17" x2="12.01" y2="17"/>
                </svg>
                <span>建议先上传安全文档以获得更精准的本地知识检索效果</span>
              </div>
            )}
          </div>
        </div>
      ) : (
        <div className="messages-container">
          <div className="messages-list">
            {messages.map((message) => (
              <div key={message.id} className={`message message-${message.type}`}>
                <div className="message-avatar">
                  {message.type === 'user' ? (
                    <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
                      <circle cx="16" cy="16" r="16" fill="#3B82F6"/>
                      <path d="M16 10C14.3431 10 13 11.3431 13 13C13 14.6569 14.3431 16 16 16C17.6569 16 19 14.6569 19 13C19 11.3431 17.6569 10 16 10ZM16 18C13.7909 18 12 19.7909 12 22H20C20 19.7909 18.2091 18 16 18Z" fill="white"/>
                    </svg>
                  ) : (
                    <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
                      <circle cx="16" cy="16" r="16" fill="#10B981"/>
                      <path d="M12 16L15 19L20 13" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                    </svg>
                  )}
                </div>
                <div className="message-body">
                  <div className="message-header">
                    <span className="message-name">
                      {message.type === 'user' ? '您' : '助手'}
                    </span>
                    <span className="message-time">
                      {message.timestamp.toLocaleTimeString()}
                    </span>
                  </div>
                  <div className="message-content">
                    {message.type === 'assistant' ? (
                      <ReactMarkdown>{message.content}</ReactMarkdown>
                    ) : (
                      <div className="message-text">{message.content}</div>
                    )}
                  </div>
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="message message-assistant">
                <div className="message-avatar">
                  <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
                    <circle cx="16" cy="16" r="16" fill="#10B981"/>
                    <path d="M12 16L15 19L20 13" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                </div>
                <div className="message-body">
                  <div className="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </div>
      )}

      <form className="input-form" onSubmit={handleSubmit}>
        <div className="input-container">
          <textarea
            className="message-input"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="请输入您的网络安全问题..."
            rows={1}
            disabled={isLoading || !isInitialized}
          />
          <button
            type="submit"
            className="send-button"
            disabled={!inputValue.trim() || isLoading || !isInitialized}
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="22" y1="2" x2="11" y2="13"/>
              <polygon points="22 2 15 22 11 13 2 9 22 2"/>
            </svg>
          </button>
        </div>
        <div className="input-footer">
          <label className="web-search-toggle">
            <input
              type="checkbox"
              checked={useWebSearch}
              onChange={(e) => setUseWebSearch(e.target.checked)}
              disabled={isLoading || !isInitialized}
            />
            <span>启用网络搜索</span>
          </label>
          <span className="hint">按 Enter 发送，Shift + Enter 换行</span>
        </div>
      </form>
    </div>
  );
};

export default ChatInterface;
