import React from 'react';
import MessageBubble from '../../molecules/MessageBubble/MessageBubble';
import styles from './ChatArea.module.css';
import CircularProgress from '@mui/material/CircularProgress';

export type MessageType = {
  message: string;
  isUser?: boolean;
  avatarSrc?: string;
  userName?: string;
  time?: string;
};

type ChatAreaProps = {
  messages: MessageType[];
  className?: string;
  onEdit?: (index: number, newMessage: string) => void;
  loading?: boolean;
};

const ChatArea: React.FC<ChatAreaProps> = ({ messages, className, onEdit, loading }) => (
  <div className={`${styles.chatArea}${className ? ' ' + className : ''}`}> 
    <div className={styles.chatAreaInner}>
      {messages.map((msg, idx) => (
        <MessageBubble key={idx} {...msg} index={idx} onEdit={onEdit} />
      ))}
      {loading && (
        <div style={{ display: 'flex', justifyContent: 'center', margin: '16px 0' }}>
          <CircularProgress />
        </div>
      )}
    </div>
  </div>
);

export default ChatArea; 