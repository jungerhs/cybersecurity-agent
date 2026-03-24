import { useState, useEffect } from 'react';
import { api } from './api';
import ChatInterface from './components/ChatInterface';
import Sidebar from './components/Sidebar';
import './App.css';

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

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isInitialized, setIsInitialized] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null);

  useEffect(() => {
    checkHealth();
  }, []);

  const checkHealth = async () => {
    try {
      const health = await api.healthCheck();
      setIsInitialized(health.initialized);
      if (health.initialized) {
        const status = await api.getStatus();
        setSystemStatus(status);
      }
    } catch (error) {
      console.error('Health check failed:', error);
    }
  };

  const handleInitialize = async (forceRebuild = false) => {
    setIsLoading(true);
    try {
      const result = await api.initializeSystem(forceRebuild);
      
      if (result.success) {
        setIsInitialized(true);
        setSystemStatus(result.status);
        addSystemMessage('系统初始化成功！');
      } else {
        addSystemMessage(`初始化失败：${result.error}`);
      }
    } catch (error: any) {
      addSystemMessage(`初始化失败：${error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleQuery = async (question: string, useWebSearch: boolean) => {
    if (!question.trim()) return;

    addUserMessage(question);
    setIsLoading(true);

    try {
      const result = await api.query(question, true, useWebSearch);
      
      if (result.success) {
        addAssistantMessage(result.answer);
      } else {
        addSystemMessage(`查询失败：${result.error}`);
      }
    } catch (error: any) {
      addSystemMessage(`查询失败：${error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const addUserMessage = (content: string) => {
    const message: Message = {
      id: Date.now().toString(),
      type: 'user',
      content,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, message]);
  };

  const addAssistantMessage = (content: string) => {
    const message: Message = {
      id: Date.now().toString(),
      type: 'assistant',
      content,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, message]);
  };

  const addSystemMessage = (content: string) => {
    const message: Message = {
      id: Date.now().toString(),
      type: 'system',
      content,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, message]);
  };

  const handleReset = async () => {
    if (!confirm('确定要重置系统吗？这将清除所有数据。')) return;

    setIsLoading(true);
    try {
      await api.resetSystem();
      setIsInitialized(false);
      setSystemStatus(null);
      setMessages([]);
      addSystemMessage('系统已重置');
    } catch (error: any) {
      addSystemMessage(`重置失败：${error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRefreshStatus = async () => {
    try {
      const status = await api.getStatus();
      setSystemStatus(status);
    } catch (error: any) {
      console.error('Failed to refresh status:', error);
    }
  };

  return (
    <div className="app">
      <Sidebar
        systemStatus={systemStatus}
        onInitialize={handleInitialize}
        onReset={handleReset}
        onRefreshStatus={handleRefreshStatus}
        isLoading={isLoading}
      />
      
      <main className="app-main">
        <ChatInterface
          messages={messages}
          isLoading={isLoading}
          onQuery={handleQuery}
          systemStatus={systemStatus}
          isInitialized={isInitialized}
        />
      </main>
    </div>
  );
}

export default App;
