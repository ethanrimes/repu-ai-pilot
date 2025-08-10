// frontend/src/i18n/config.ts
import { Language } from '@/stores/languageStore';

export interface Translation {
  [key: string]: string | Translation;
}

export interface Translations {
  common: Translation;
  chat: Translation;
  auth: Translation;
  parts: Translation;
}

// Type-safe translation keys with nested structure
export const translationKeys = {
  common: {
    app: {
      name: 'common.app.name',
      tagline: 'common.app.tagline'
    },
    language: {
      label: 'common.language.label',
      spanish: 'common.language.spanish',
      english: 'common.language.english',
      switch: 'common.language.switch'
    },
    navigation: {
      home: 'common.navigation.home',
      chat: 'common.navigation.chat',
      search: 'common.navigation.search',
      profile: 'common.navigation.profile',
      settings: 'common.navigation.settings'
    },
    actions: {
      submit: 'common.actions.submit',
      cancel: 'common.actions.cancel',
      save: 'common.actions.save',
      close: 'common.actions.close',
      edit: 'common.actions.edit',
      delete: 'common.actions.delete',
      confirm: 'common.actions.confirm',
      retry: 'common.actions.retry',
      back: 'common.actions.back',
      next: 'common.actions.next',
      previous: 'common.actions.previous'
    },
    status: {
      loading: 'common.status.loading',
      error: 'common.status.error',
      success: 'common.status.success',
      warning: 'common.status.warning',
      info: 'common.status.info',
      noData: 'common.status.noData',
      noResults: 'common.status.noResults'
    }
  },
  chat: {
    interface: {
      title: 'chat.interface.title',
      subtitle: 'chat.interface.subtitle',
      placeholder: 'chat.interface.placeholder'
    },
    actions: {
      send: 'chat.actions.send',
      clearHistory: 'chat.actions.clearHistory',
      newChat: 'chat.actions.newChat',
      exportChat: 'chat.actions.exportChat',
      shareChat: 'chat.actions.shareChat'
    },
    status: {
      thinking: 'chat.status.thinking',
      typing: 'chat.status.typing',
      searching: 'chat.status.searching',
      connecting: 'chat.status.connecting',
      offline: 'chat.status.offline'
    },
    messages: {
      welcome: 'chat.messages.welcome',
      errorMessage: 'chat.messages.errorMessage',
      networkError: 'chat.messages.networkError',
      rateLimitError: 'chat.messages.rateLimitError',
      sessionExpired: 'chat.messages.sessionExpired'
    },
    empty: {
      title: 'chat.empty.title',
      description: 'chat.empty.description'
    }
  },
  auth: {
    pages: {
      login: {
        title: 'auth.pages.login.title',
        subtitle: 'auth.pages.login.subtitle'
      },
      signup: {
        title: 'auth.pages.signup.title',
        subtitle: 'auth.pages.signup.subtitle'
      }
    },
    form: {
      email: {
        label: 'auth.pages.login.form.email.label',
        placeholder: 'auth.pages.login.form.email.placeholder'
      },
      password: {
        label: 'auth.pages.login.form.password.label',
        placeholder: 'auth.pages.login.form.password.placeholder'
      },
      submitButton: 'auth.pages.login.form.submitButton'
    },
    actions: {
      login: 'auth.actions.login',
      logout: 'auth.actions.logout',
      signup: 'auth.actions.signup',
      forgotPassword: 'auth.actions.forgotPassword',
      resetPassword: 'auth.actions.resetPassword'
    },
    messages: {
      welcome: 'auth.messages.welcome',
      welcomeBack: 'auth.messages.welcomeBack',
      loginSuccess: 'auth.messages.loginSuccess',
      logoutSuccess: 'auth.messages.logoutSuccess',
      loginError: 'auth.messages.loginError',
      signupError: 'auth.messages.signupError',
      sessionExpired: 'auth.messages.sessionExpired'
    }
  }
} as const;

// Async function to load translations
export async function getTranslations(language: Language): Promise<Translations> {
  try {
    const [common, chat, auth, parts] = await Promise.all([
      import(`./locales/${language}/common.json`).then(m => m.default),
      import(`./locales/${language}/chat.json`).then(m => m.default),
      import(`./locales/${language}/auth.json`).then(m => m.default),
      import(`./locales/${language}/parts.json`).then(m => m.default)
    ]);

    return { common, chat, auth, parts };
  } catch (error) {
    console.error(`Failed to load translations for language: ${language}`, error);
    // Fallback to Spanish if loading fails
    if (language !== 'es') {
      return getTranslations('es');
    }
    throw error;
  }
}

// Helper function to get nested translation value with variable interpolation
export function getNestedTranslation(
  translations: Translations, 
  key: string, 
  variables?: Record<string, string | number>
): string {
  const keys = key.split('.');
  let value: any = translations;
  
  for (const k of keys) {
    value = value?.[k];
    if (value === undefined) {
      console.warn(`Translation key not found: ${key}`);
      return key; // Return the key itself as fallback
    }
  }
  
  if (typeof value !== 'string') {
    console.warn(`Translation value is not a string: ${key}`);
    return key;
  }

  // Handle variable interpolation (e.g., "Hello {{name}}")
  if (variables) {
    return value.replace(/\{\{(\w+)\}\}/g, (match, varName) => {
      return variables[varName]?.toString() || match;
    });
  }
  
  return value;
}

// Type-safe translation hook result
export interface UseTranslationsResult {
  t: (key: string, variables?: Record<string, string | number>) => string;
  language: Language;
}

export const supportedLanguages: Language[] = ['es', 'en'];

export const languageNames: Record<Language, string> = {
  es: 'Español',
  en: 'English'
};
