import React from 'react';
import DeleteIcon from '@mui/icons-material/Delete';
import styles from './SidebarItem.module.css';
import { IconButton } from '@mui/material';

export type SidebarItemProps = {
  label: string;
  active?: boolean;
  onClick?: () => void;
  onDelete?: () => void;
};

const SidebarItem: React.FC<SidebarItemProps> = ({
  label,
  active = false,
  onClick,
  onDelete,
}) => {
  return (
    <div 
      className={`${styles.sidebarItem} ${active ? styles.active : ''}`}
      onClick={onClick}
      title={label}
    >
      <span className={styles.label}>{label}</span>
      {onDelete && (
        <IconButton 
          aria-label="edit"
          onClick={(e) => {
            e.stopPropagation();
            onDelete();
          }}
          size="small"
        >
          <DeleteIcon style={{ color: '#fff' }}  />
        </IconButton >
      )}
    </div>
  );
};

export default SidebarItem; 