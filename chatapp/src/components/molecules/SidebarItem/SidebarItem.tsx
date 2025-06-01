import React from 'react';
import DeleteIcon from '@mui/icons-material/Delete';
import styles from './SidebarItem.module.css';
import Button from '../../atoms/Button';

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
        <Button
          className={styles.deleteButton}
          onClick={(e) => {
            e.stopPropagation();
            onDelete();
          }}
          title="削除"
        >
          <DeleteIcon fontSize="small" />
        </Button>
      )}
    </div>
  );
};

export default SidebarItem; 