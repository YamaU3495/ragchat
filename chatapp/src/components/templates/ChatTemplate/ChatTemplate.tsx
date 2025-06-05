import React, { useState,useEffect } from 'react';
import Sidebar from '../../organisms/Sidebar/Sidebar';
import ChatArea from '../../organisms/ChatArea/ChatArea';
import ChatInput from '../../organisms/ChatInput/ChatInput';
import ChatHeader from '../../molecules/ChatHeader/ChatHeader';
import styles from './ChatTemplate.module.css';
import Alert from '@mui/material/Alert';
import Snackbar from '@mui/material/Snackbar';

import type { SidebarItemType } from '../../organisms/Sidebar/Sidebar';
import type { MessageType } from '../../organisms/ChatArea/ChatArea';

type ChatTemplateProps = {
  sidebarItems: SidebarItemType[];
  messages: MessageType[];
  inputValue: string;
  onInputChange: (e: React.ChangeEvent<HTMLTextAreaElement>) => void;
  onSend: () => void;
  onEdit?: (index: number, newMessage: string) => void;
  onDeleteAndSend?: (index: number, newMessage: string) => void;
  onNewChat?: () => void;
  loading?: boolean;
  error?: string;
  onErrorClose: () => void;
};

const ChatTemplate: React.FC<ChatTemplateProps> = ({ 
  sidebarItems, 
  messages, 
  inputValue, 
  onInputChange, 
  onSend, 
  onEdit, 
  onDeleteAndSend,
  onNewChat, 
  loading,
  error,
  onErrorClose
}) => {
  const [showError, setShowError] = useState(!!error);
  
  useEffect(() => {
    setShowError(!!error);
  }, [error]);

  const handleCloseError = () => {
    setShowError(false);
    onErrorClose();
  };

  return (
    <div className={styles.appRoot}>
      <Sidebar items={sidebarItems} onNewChat={onNewChat} />
      <div className={styles.chatMain}>
        <ChatHeader className={styles.fullWidth} />
        <ChatArea messages={messages} className={styles.fullWidth} onEdit={onEdit} onDeleteAndSend={onDeleteAndSend} loading={loading}/>
        <ChatInput value={inputValue} onChange={onInputChange} onSend={onSend} className={styles.fullWidth} loading={loading} />
      </div>
      <Snackbar 
        open={showError} 
        autoHideDuration={6000} 
        onClose={handleCloseError}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert onClose={handleCloseError} severity="error" variant="filled">
          {error}
        </Alert>
      </Snackbar>
    </div>
  );
};

export default ChatTemplate;