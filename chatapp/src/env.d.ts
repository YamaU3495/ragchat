/// <reference types="vite/client" />

interface ImportMetaEnv {
  // カスタム環境変数（VITE_で始まるもの）
  readonly VITE_API_HOST?: string
  readonly VITE_API_PORT?: string
  readonly VITE_APP_TITLE?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}

// グローバルな型定義
interface Window {
  __API_HOST__: string;
  __API_PORT__: string;
} 