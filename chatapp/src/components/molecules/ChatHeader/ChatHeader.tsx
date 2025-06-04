import React from 'react';
import styles from './ChatHeader.module.css';
import { config } from '../../../config';
import { Avatar } from '@mui/material';
import PersonIcon from '@mui/icons-material/Person';

type ChatHeaderProps = {
  className?: string;
};

const ChatHeader: React.FC<ChatHeaderProps> = ({ className }) => (
  <div className={`${styles.chatHeader}${className ? ' ' + className : ''}`}>
    <span className={styles.logo}>{config.appTitle}</span>
    <span className={styles.avatar}>
        <Avatar>
          <PersonIcon />
        </Avatar>
    </span>
  </div>
);

export default ChatHeader; 