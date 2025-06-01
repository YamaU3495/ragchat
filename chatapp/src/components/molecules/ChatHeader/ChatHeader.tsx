import React from 'react';
import Avatar from '../../atoms/Avatar';
import styles from './ChatHeader.module.css';
import { config } from '../../../config';
type ChatHeaderProps = {
  className?: string;
};

const ChatHeader: React.FC<ChatHeaderProps> = ({ className }) => (
  <div className={`${styles.chatHeader}${className ? ' ' + className : ''}`}>
    <span className={styles.logo}>{config.appTitle}</span>
    <span className={styles.avatar}><Avatar src="https://ui-avatars.com/api/?name=User" size={32} /></span>
  </div>
);

export default ChatHeader; 