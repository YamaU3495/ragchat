interface ApiConfig {
  host: string;
  port: string;
}

interface Config {
  api: ApiConfig;
  appTitle: string;
}

// グローバル設定から読み込み
const getGlobalConfig = (): Config => {
  // @ts-ignore - window.__APP_CONFIG__は動的に追加される
  const globalConfig = window.__APP_CONFIG__;
  
  return {
    api: {
      host: globalConfig.api.host || '',
      port: globalConfig.api.port || ''
    },
    appTitle: globalConfig.appTitle || 'LocalRAG Chat'
  };
};

export const config: Config = getGlobalConfig(); 