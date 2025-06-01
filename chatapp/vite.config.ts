import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig(({ mode }) => {
  // 環境変数を読み込む
  const env = loadEnv(mode, process.cwd(), '');
  
  return {
    plugins: [react()],
    // 環境変数をクライアントに公開
    define: {
      'import.meta.env.VITE_API_HOST': JSON.stringify(env.VITE_API_HOST),
      'import.meta.env.VITE_API_PORT': JSON.stringify(env.VITE_API_PORT),
      'import.meta.env.VITE_APP_TITLE': JSON.stringify(env.VITE_APP_TITLE)
    }
  };
});