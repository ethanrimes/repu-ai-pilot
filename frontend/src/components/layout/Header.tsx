'use client';

import { useAuth } from '@/hooks/useAuth';
import styles from '@/styles/layout.module.css';

export function Header() {
  const { user, logout } = useAuth();

  return (
    <header className={styles.header}>
      <div className={styles.headerContent}>
        <h1 className={styles.logo}>AutoParts Colombia</h1>
        
        {user && (
          <div className={styles.userSection}>
            <span className={styles.userEmail}>{user.email}</span>
            <button onClick={logout} className={styles.logoutButton}>
              Sign Out
            </button>
          </div>
        )}
      </div>
    </header>
  );
}