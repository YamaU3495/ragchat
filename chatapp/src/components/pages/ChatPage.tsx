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

      const formattedMessages: MessageType[] = data.messages.map((msg: any) => {
        if (!msg.content || typeof msg.content !== 'string') {
          throw new Error('メッセージの形式が不正です');
        }
        return {
          message: msg.content,
          isUser: msg.role === 'user',
          no: msg.no,
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
    const originalMessages = [...messages]; // 現在のメッセージを保存
    try {
      const newMessage: MessageType = {
        message: inputValue,
        isUser: true,
        no: messages.length+1,
      };
      setMessages(prevMessages => [...prevMessages, newMessage]);
      setInputValue('');

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
      
      const aiMessage: MessageType = {
        message: data.content,
        isUser: false,
        no: data.no,
      };
      setMessages(prevMessages => [...prevMessages, aiMessage]);

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
        setActiveSessionId(data.session_id);
      }
    } catch (error) {
      console.error('エラーが発生しました:', error);
      let errorMessage = 'エラーが発生しました';
      
      if (error instanceof TypeError && error.message === 'Failed to fetch') {
        errorMessage = 'サーバーに接続できません。サーバーが起動しているか確認してください。';
      } else if (error instanceof Error) {
        errorMessage = error.message;
      }
      
      setErrorMessage(errorMessage);
      setMessages(originalMessages); // エラー時に元のメッセージに戻す
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

  // Add a new handler for delete-and-send
  const handleDeleteAndSend = async (index: number, newMessage: string) => {
    if (!activeSessionId) return;
    setLoading(true);
    try {
      // Delete messages after the edited message (index)
      var sortedMessaged = messages.sort((a, b) => {
        if (a.no == null) return 1;
        if (b.no == null) return -1;
        return a.no - b.no;
      });
      const startIndex=sortedMessaged.findIndex(msg=>msg.no==sortedMessaged[index].no);
      // APIに送信する前にメッセージを削除する
      for (let i = startIndex; i < messages.length; i++) {
        sortedMessaged = sortedMessaged.filter(msg=>msg.no!=messages[i].no);
      }
      setMessages([...sortedMessaged, {message:newMessage,isUser:true,no: messages[index].no}]);

      // メッセージを削除する
      for (let i = startIndex; i < messages.length; i++) {
        const deleteRes = await fetch(`${getApiBaseUrl()}/api/chat/message/${activeSessionId}/${messages[i].no}`, {
          method: 'DELETE',
        });
        if (!deleteRes.ok) {
          throw new Error('メッセージの削除に失敗しました');
        }
      }
      // Send the new message
      const sendRes = await fetch(`${getApiBaseUrl()}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          content: newMessage,
          session_id: activeSessionId,
        }),
      });
      if (!sendRes.ok) {
        throw new Error('新しいメッセージの送信に失敗しました');
      }
      const data = await sendRes.json();
      // Fetch updated history again to include the new message
      await fetchConversationHistory(activeSessionId);
      setInputValue('');
    } catch (error) {
      console.error('削除と送信でエラー:', error);
      setErrorMessage(error instanceof Error ? error.message : '削除と送信でエラーが発生しました');
    } finally {
      setLoading(false);
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
      onDeleteAndSend={handleDeleteAndSend}
      onNewChat={handleNewChat}
      loading={loading}
      error={errorMessage}
      onErrorClose={() => setErrorMessage(undefined)}
    />
  );
};

export default ChatPage; 