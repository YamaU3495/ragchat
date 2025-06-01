import React, { useState, useEffect } from 'react';
import ChatTemplate from '../templates/ChatTemplate/ChatTemplate';
import { getCookie, setCookie } from '../../utils/cookieUtils';
import { getApiBaseUrl } from '../../utils/apiUtils';
import type { MessageType } from '../organisms/ChatArea/ChatArea';
import type { SidebarItemType } from '../organisms/Sidebar/Sidebar';

type Session = {
  id: string;
  createdAt: string;
  label: string;
};

const ChatPage: React.FC = () => {
  const [messages, setMessages] = useState<MessageType[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string>();
  const [sessions, setSessions] = useState<Session[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);

  // セッション一覧をクッキーから取得する関数
  const loadSessionsFromCookie = () => {
    const savedSessions = getCookie('sessions');
    if (savedSessions) {
      try {
        const parsedSessions = JSON.parse(savedSessions);
        setSessions(parsedSessions);
        if (parsedSessions.length > 0) {
          handleSessionSelect(parsedSessions[0].id);
        }
      } catch (error) {
        console.error('保存されたセッション一覧の解析に失敗しました:', error);
        setSessions([]); // 解析に失敗した場合は空の配列を設定
      }
    } else {
      setSessions([]); // クッキーにデータがない場合は空の配列を設定
    }
  };

  // 会話履歴を取得する関数
  const fetchConversationHistory = async (sessionId: string) => {
    setLoading(true);
    try {
      const response = await fetch(`${getApiBaseUrl()}/api/chat/history/${sessionId}`);
      if (!response.ok) {
        throw new Error('会話履歴の取得に失敗しました');
      }
      const data = await response.json();
      
      // データの検証
      if (!data || !Array.isArray(data.messages)) {
        throw new Error('会話履歴の形式が不正です');
      }

      // メッセージが空の場合
      if (data.messages.length === 0) {
        setMessages([]);
        setErrorMessage('会話履歴が存在しません');
        return;
      }

      const formattedMessages = data.messages.map((msg: any) => {
        if (!msg.content || typeof msg.content !== 'string') {
          throw new Error('メッセージの形式が不正です');
        }
        return {
          message: msg.content,
          isUser: msg.role === 'user'
        };
      });

      setMessages(formattedMessages);
    } catch (error) {
      console.error('会話履歴の取得に失敗しました:', error);
      setErrorMessage(error instanceof Error ? error.message : '会話履歴の取得に失敗しました');
      setMessages([]); // エラー時はメッセージをクリア
    } finally {
      setLoading(false);
    }
  };

  // セッション選択時の処理
  const handleSessionSelect = (sessionId: string) => {
    setActiveSessionId(sessionId);
    fetchConversationHistory(sessionId);
  };

  // コンポーネントマウント時にクッキーからセッション一覧を取得
  useEffect(() => {
    loadSessionsFromCookie();
  }, []);

  const handleSend = async () => {
    if (!inputValue.trim()) return;

    setLoading(true);
    try {
      const response = await fetch(`${getApiBaseUrl()}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          content: inputValue,
          session_id: activeSessionId 
        }),
      });

      if (!response.ok) {
        let errorMessage = 'エラーが発生しました';
        
        if (response.status === 422) {
          const errorData = await response.json();
          errorMessage = errorData.detail || '入力内容が不正です';
        } else if (response.status === 404) {
          errorMessage = 'リソースが見つかりません';
        } else if (response.status === 500) {
          errorMessage = 'サーバーエラーが発生しました';
        }
        
        throw new Error(errorMessage);
      }

      const data = await response.json();
      
      // 新しいメッセージを追加
      const newMessages = [
        ...messages,
        { message: inputValue, isUser: true },
        { message: data.response, isUser: false }
      ];
      setMessages(newMessages);

      // 新しいセッションを作成
      if (!activeSessionId) {
        const newSession: Session = {
          id: data.session_id,
          createdAt: new Date().toISOString(),
          label: inputValue.slice(0, 20) + '...'
        };

        const updatedSessions = [...sessions, newSession];
        setSessions(updatedSessions);
        setCookie('sessions', JSON.stringify(updatedSessions));
      }

      setInputValue('');
    } catch (error) {
      console.error('エラーが発生しました:', error);
      let errorMessage = 'エラーが発生しました';
      
      if (error instanceof TypeError && error.message === 'Failed to fetch') {
        errorMessage = 'サーバーに接続できません。サーバーが起動しているか確認してください。';
      } else if (error instanceof Error) {
        errorMessage = error.message;
      }
      
      setErrorMessage(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInputValue(e.target.value);
  };

  const handleNewChat = () => {
    setMessages([]);
    setInputValue('');
    setActiveSessionId(null);
  };

  const handleDeleteSession = (sessionId: string) => {
    const updatedSessions = sessions.filter(session => session.id !== sessionId);
    setSessions(updatedSessions);
    setCookie('sessions', JSON.stringify(updatedSessions));

    if (activeSessionId === sessionId) {
      if (updatedSessions.length > 0) {
        handleSessionSelect(updatedSessions[0].id);
      } else {
        handleNewChat();
      }
    }
  };

  const handleEditMessage = async (index: number, newMessage: string) => {
    if (!activeSessionId) return;

    const updatedMessages = [...messages];
    updatedMessages[index] = { ...updatedMessages[index], message: newMessage };
    setMessages(updatedMessages);

    try {
      const response = await fetch(`${getApiBaseUrl()}/api/chat/edit/${activeSessionId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message_index: index,
          new_content: newMessage
        }),
      });

      if (!response.ok) {
        throw new Error('メッセージの編集に失敗しました');
      }
    } catch (error) {
      console.error('メッセージの編集に失敗しました:', error);
      setErrorMessage(error instanceof Error ? error.message : 'メッセージの編集に失敗しました');
      // エラー時は元のメッセージに戻す
      setMessages(messages);
    }
  };

  // サイドバーアイテムを生成
  const sidebarItems: SidebarItemType[] = sessions.map(session => ({
    label: session.label,
    active: session.id === activeSessionId,
    onClick: () => handleSessionSelect(session.id),
    onDelete: () => handleDeleteSession(session.id)
  }));

  return (
    <ChatTemplate
      sidebarItems={sidebarItems}
      messages={messages}
      inputValue={inputValue}
      onInputChange={handleInputChange}
      onSend={handleSend}
      onEdit={handleEditMessage}
      onNewChat={handleNewChat}
      loading={loading}
      error={errorMessage}
      onErrorClose={() => setErrorMessage(undefined)}
    />
  );
};

export default ChatPage; 