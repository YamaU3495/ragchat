import React, { useState, useRef } from 'react';
import Avatar from '../../atoms/Avatar';
import styles from './MessageBubble.module.css';
import ReactMarkdown from 'react-markdown';
import TextArea from '../../atoms/TextArea';
import chatInputStyles from '../../organisms/ChatInput/ChatInput.module.css';
import Button from '../../atoms/Button';
import EditIcon from '@mui/icons-material/Edit';

type MessageBubbleProps = {
  message: string;
  isUser?: boolean;
  avatarSrc?: string;
  userName?: string;
  time?: string;
  className?: string;
  onEdit?: (index: number, newMessage: string) => void;
  index?: number;
};

const MessageBubble: React.FC<MessageBubbleProps> = ({ message, isUser = false, avatarSrc, userName, time, className, onEdit, index }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editValue, setEditValue] = useState(message);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleEdit = () => {
    setIsEditing(true);
    setTimeout(() => {
      textareaRef.current?.focus();
    }, 0);
  };

  const handleSave = () => {
    if (onEdit && typeof index === 'number') {
      onEdit(index, editValue);
    }
    setIsEditing(false);
  };

  const handleCancel = () => {
    setEditValue(message);
    setIsEditing(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSave();
    }
  };

  return (
    <div className={[
      styles.messageRow,
      isUser ? styles.messageRowUser : styles.messageRowAi,
      className
    ].filter(Boolean).join(' ')}>
      {!isUser && (
        <Avatar src={avatarSrc || 'https://ui-avatars.com/api/?name=AI'} size={36} />
      )}
      <div>
        <div className={[
          styles.messageBubble,
          isUser ? styles.messageBubbleUser : styles.messageBubbleAi
        ].join(' ')}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            {userName && <div className={styles.messageMeta} style={{ textAlign: 'left', marginBottom: 4 }}>{userName}</div>}
          </div>
          {isEditing ? (
            <div className={styles.editContainer}>
              <TextArea
                ref={textareaRef}
                value={editValue}
                onChange={(e) => setEditValue(e.target.value)}
                onKeyDown={handleKeyDown}
                className={chatInputStyles.chatInputBox}
                rows={1}
                style={{ resize: 'none', overflow: 'hidden', width: '100%', boxSizing: 'border-box',padding: 1,margin: '16px 0px'}}
                backgroundColor={isUser ? '#dcf2ff' : '#fff'}
                autoResize={true}
              />
              <div className={styles.editButtons}>
                <Button onClick={handleSave} className={styles.editButton}>送信する</Button>
                <Button onClick={handleCancel} className={styles.editButton}>キャンセルする</Button>
              </div>
            </div>
          ) : (
            <ReactMarkdown>{message}</ReactMarkdown>
          )}
          {time && <div className={styles.messageMeta}>{time}</div>}
        </div>
        <div style={{display: 'flex', justifyContent: 'flex-end'}}>
          {isUser && onEdit && typeof index === 'number' && !isEditing && (
            <Button
              style={{ background: 'none', border: 'none', color: '#888', cursor: 'pointer', fontSize: 14 }}
              onClick={handleEdit}
              className={styles.editButtonOutside}
              title="編集"
            >
              <EditIcon style={{ fontSize: 23 }} />
            </Button>
          )}
        </div>
      </div>
      {isUser && (
        <Avatar src={avatarSrc || 'https://ui-avatars.com/api/?name=User'} size={36} />
      )}
    </div>
  );
};

export default MessageBubble; 