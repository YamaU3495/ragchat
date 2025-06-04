import React, { useState, useRef, useEffect } from 'react';
import styles from './MessageBubble.module.css';
import ReactMarkdown from 'react-markdown';
import TextArea from '../../atoms/TextArea';
import chatInputStyles from '../../organisms/ChatInput/ChatInput.module.css';
import Button from '../../atoms/Button';
import EditIcon from '@mui/icons-material/Edit';
import { Avatar, IconButton, Tooltip } from '@mui/material';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import remarkGfm from 'remark-gfm'
import hljs from 'highlight.js';
import 'highlight.js/styles/github.css';
import PersonIcon from '@mui/icons-material/Person';
import SmartToyOutlinedIcon from '@mui/icons-material/SmartToyOutlined';
import { grey } from '@mui/material/colors';

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
  const [copied, setCopied] = useState(false);
  
  useEffect(() => {
    hljs.initHighlighting();
    hljs.initHighlighting.called = false;
  });

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

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(message);
      setCopied(true);
      setTimeout(() => setCopied(false), 1200);
    } catch (e) {
      // fallback or error handling
      throw new Error('コピーに失敗しました')
    }
  };

  return (
    <div className={[
      styles.messageRow,
      isUser ? styles.messageRowUser : styles.messageRowAi,
      className
    ].filter(Boolean).join(' ')}>
      {!isUser && (
        <Avatar sx={{ bgcolor: grey[700] }}>
          <SmartToyOutlinedIcon />
        </Avatar>
      )}
      <div>
        <div className={[
          styles.messageBubble,
          isUser ? styles.messageBubbleUser : styles.messageBubbleAi
        ].join(' ')}>
          <div style={{ display: 'flex' }}>
            {userName && <div className={styles.messageMeta} style={{ textAlign: 'left', marginBottom: 4 }}>{userName}</div>}
            <Tooltip title={copied ? 'コピーしました' : 'コピー'} placement="top" arrow>
              <IconButton size="small" onClick={handleCopy} style={{ marginLeft: 4 }}>
                <ContentCopyIcon fontSize="small" color={copied ? 'success' : 'inherit'} />
              </IconButton>
            </Tooltip>
            {isUser && onEdit && typeof index === 'number' && !isEditing && (
              <IconButton 
                aria-label="edit"
                onClick={handleEdit}
              >
                <EditIcon/>
              </IconButton >
            )}
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
                style={{ resize: 'none', overflow: 'hidden', width: '100%', boxSizing: 'border-box', padding: 1, margin: '16px 0px' }}
                backgroundColor='#fff'
                autoResize={true}
              />
              <div className={styles.editButtons}>
                <Button 
                  variant="outlined" 
                  onClick={handleSave}
                  size="small"
                  disableElevation
                >
                  送信する
                </Button>
                <Button 
                  variant="outlined"
                  onClick={handleCancel}
                  size="small"
                  disableElevation
                >
                  キャンセル
                </Button>
              </div>
            </div>
          ) : (
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{message}</ReactMarkdown>
          )}
          {time && <div className={styles.messageMeta}>{time}</div>}
        </div>
      </div>
      {isUser && (
        <Avatar sx={{ bgcolor: grey[700] }}>
          <PersonIcon />
        </Avatar>
      )}
    </div>
  );
};

export default MessageBubble; 