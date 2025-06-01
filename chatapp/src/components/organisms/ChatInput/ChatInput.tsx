import React, { useRef } from 'react';
import TextArea from '../../atoms/TextArea';
import Button from '../../atoms/Button';
import styles from './ChatInput.module.css';
import SendIcon from '@mui/icons-material/Send';

type ChatInputProps = {
  value: string;
  onChange: (e: React.ChangeEvent<HTMLTextAreaElement>) => void;
  onSend: () => void;
  className?: string;
  loading?: boolean;
};

const ChatInput: React.FC<ChatInputProps> = ({ value, onChange, onSend, className, loading }) => {
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendAndReset();
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = (textarea.scrollHeight > textarea.offsetHeight ? textarea.scrollHeight : textarea.scrollHeight) + 'px';
      if (e.target.value === '' || e.target.value.split('\n').length === 1) {
        textarea.style.height = '';
      }
    }
    onChange(e);
  };

  const handleSendAndReset = () => {
    onSend();
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = '';
    }
  };

  return (
    <div className={`${styles.chatInputArea}${className ? ' ' + className : ''}`}>
      <TextArea
        ref={textareaRef}
        value={value}
        onChange={handleChange}
        onKeyDown={handleKeyDown}
        placeholder="メッセージを入力..."
        className={styles.chatInputBox}
        rows={1}
        style={{ resize: 'none', overflow: 'hidden' }}
        autoResize
      />
      <Button
        onClick={handleSendAndReset}
        className={styles.chatSendBtn}
        type="button"
        disabled={loading}
      >
        <SendIcon style={{ fontSize: 22 }} />
      </Button>
    </div>
  );
};

export default ChatInput; 