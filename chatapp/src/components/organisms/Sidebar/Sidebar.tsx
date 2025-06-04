import React, { useState } from 'react';
import SidebarItem from '../../molecules/SidebarItem/SidebarItem';
import MenuIcon from '@mui/icons-material/Menu';
import EditIcon from '@mui/icons-material/Edit';
import Button from '../../atoms/Button';
import styles from './Sidebar.module.css';
import { IconButton } from '@mui/material';

export type SidebarItemType = {
  label: string;
  active?: boolean;
  onClick?: () => void;
  onDelete?: () => void;
};

type SidebarProps = {
  items: SidebarItemType[];
  className?: string;
  onNewChat?: () => void;
};

const Sidebar: React.FC<SidebarProps> = ({ items, className, onNewChat }) => {
  const [open, setOpen] = useState(true);

  if (!open) {
    return (
      <div className={styles.sidebarHeader} style={{ background: '#181818', height: 48, display: 'flex', alignItems: 'center', padding: '8px 12px' }}>
        <IconButton onClick={() => setOpen(true)} className={styles.sidebarHeaderBtn} title="サイドバー開閉" size="small">
          <MenuIcon style={{ color: '#fff' }} />
        </IconButton>
      </div>
    );
  }

  return (
    <aside className={`${styles.sidebar}${className ? ' ' + className : ''}`}>
      <div className={styles.sidebarHeader}>
        <IconButton onClick={() => setOpen(false)} className={styles.sidebarHeaderBtn} title="サイドバー開閉" size="small">
          <MenuIcon style={{ color: '#fff' }} />
        </IconButton>
        <div style={{ flex: 1 }} />
        <IconButton onClick={onNewChat} className={styles.sidebarHeaderBtn} title="新しいチャット" size="small">
          <EditIcon style={{ color: '#fff' }} />
        </IconButton>
      </div>
      <div className={styles.sidebarItems}>
        {items.map((item, idx) => (
          <SidebarItem
            key={idx}
            label={item.label}
            active={item.active}
            onClick={item.onClick}
            onDelete={item.onDelete}
          />
        ))}
      </div>
    </aside>
  );
};

export default Sidebar; 