declare module '*.module.css' {
  const classes: { [key: string]: string };
  export default classes;
}

// グローバル設定の型定義
interface Window {
  __APP_CONFIG__: {
    api: {
      host: string;
      port: string;
    };
    appTitle: string;
  };
} 