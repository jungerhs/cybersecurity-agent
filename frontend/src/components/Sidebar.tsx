import React, { useState } from 'react';
import { api } from '../api';
import './Sidebar.css';

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

interface SidebarProps {
  systemStatus: SystemStatus | null;
  onInitialize: (forceRebuild?: boolean) => void;
  onReset: () => void;
  onRefreshStatus: () => void;
  isLoading: boolean;
}

const Sidebar: React.FC<SidebarProps> = ({
  systemStatus,
  onInitialize,
  onReset,
  onRefreshStatus,
  isLoading
}) => {
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    if (!systemStatus?.is_initialized) {
      alert('请先初始化系统再上传文档');
      return;
    }

    setIsUploading(true);
    setUploadProgress(0);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await api.uploadDocument(formData);
      
      if (response.success) {
        alert(`文档上传成功！添加了 ${response.added_count} 个文档块`);
        onRefreshStatus();
      } else {
        alert(`上传失败：${response.error}`);
      }
    } catch (error: any) {
      alert(`上传失败：${error.message}`);
    } finally {
      setIsUploading(false);
      setUploadProgress(0);
    }
  };

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="logo">
          <svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect width="40" height="40" rx="8" fill="#3B82F6"/>
            <path d="M12 20L18 26L28 14" stroke="white" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
          <div className="logo-text">
            <h1>网络安全知识问答助手</h1>
            <p>基于 RAG 和 Agent 技术的智能安全知识平台</p>
          </div>
        </div>
      </div>

      <div className="sidebar-content">
        <div className="knowledge-base-card">
          <div className="card-header">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/>
              <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>
            </svg>
            <h2>知识库文档</h2>
          </div>
          <p className="card-description">上传安全文档以构建本地知识库</p>
          
          <div className="upload-section">
            <label className="upload-button">
              <input
                type="file"
                accept=".pdf,.md,.txt,.doc,.docx"
                onChange={handleFileUpload}
                disabled={isLoading || isUploading || !systemStatus?.is_initialized}
                style={{ display: 'none' }}
              />
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                <polyline points="17 8 12 3 7 8"/>
                <line x1="12" y1="3" x2="12" y2="15"/>
              </svg>
              {isUploading ? '上传中...' : '上传文档'}
            </label>

            {isUploading && (
              <div className="upload-progress">
                <div className="progress-bar">
                  <div 
                    className="progress-fill" 
                    style={{ width: `${uploadProgress}%` }}
                  />
                </div>
                <span className="progress-text">正在上传并处理文档...</span>
              </div>
            )}
            
            <div className="upload-hint">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                <polyline points="14 2 14 8 20 8"/>
                <line x1="16" y1="13" x2="8" y2="13"/>
                <line x1="16" y1="17" x2="8" y2="17"/>
                <polyline points="10 9 9 9 8 9"/>
              </svg>
              <span>{systemStatus?.vector_store?.document_count || 0} 个文档</span>
              <p>支持 PDF、MD、TXT 等格式</p>
            </div>
          </div>
        </div>

        <div className="security-tips-card">
          <div className="card-header">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
              <line x1="12" y1="9" x2="12" y2="13"/>
              <line x1="12" y1="17" x2="12.01" y2="17"/>
            </svg>
            <h2>安全提示</h2>
          </div>
          <ul className="tips-list">
            <li>本系统仅供学习和研究使用</li>
            <li>漏洞细节已自动脱敏</li>
            <li>请勿用于非法活动</li>
            <li>遵守相关法律法规</li>
          </ul>
        </div>

        <div className="system-status-card">
          <div className="status-row">
            <span className="status-label">系统状态</span>
            <span className={`status-indicator ${systemStatus?.is_initialized ? 'online' : 'offline'}`}>
              {systemStatus?.is_initialized ? '已就绪' : '未初始化'}
            </span>
          </div>
          {systemStatus?.is_initialized && (
            <>
              <div className="status-row">
                <span className="status-label">文档数量</span>
                <span className="status-value">{systemStatus.vector_store?.document_count || 0}</span>
              </div>
              <div className="status-row">
                <span className="status-label">可用工具</span>
                <span className="status-value">{systemStatus.tools?.length || 0}</span>
              </div>
            </>
          )}
        </div>
      </div>

      <div className="sidebar-footer">
        <button
          className="action-button"
          onClick={() => onInitialize(false)}
          disabled={isLoading}
        >
          {isLoading ? '初始化中...' : '初始化系统'}
        </button>
        <button
          className="action-button secondary"
          onClick={() => onInitialize(true)}
          disabled={isLoading}
        >
          重建系统
        </button>
        <button
          className="action-button danger"
          onClick={onReset}
          disabled={isLoading}
        >
          重置系统
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;
