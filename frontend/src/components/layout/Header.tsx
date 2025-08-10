'use client';

import { useAuth } from '@/hooks/useAuth';
import { useTranslations } from '@/hooks/useLanguage';
import { LanguageToggle } from '@/components/chat/LanguageToggle';
import styles from '@/styles/layout.module.css';

export function Header() {
  const { user, logout } = useAuth();
  const { t } = useTranslations();

  return (
    <header className={styles.header}>
      <div className={styles.headerContent}>
        <h1 className={styles.logo}>{t('common.app.name')}</h1>
        
        <div className={styles.headerActions}>
          <LanguageToggle />
          {user && (
            <div className={styles.userSection}>
              <span className={styles.userEmail}>{user.email}</span>
              <button onClick={logout} className={styles.logoutButton}>
                {t('auth.actions.logout')}
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}