import { config } from '../config';

export const getApiBaseUrl = (): string => {
  const { host, port } = config.api;
  
  // ホストが空の場合は相対パスを使用
  if (!host) {
    return '/api';
  }
  
  // 完全なURLを構築
  const protocol = (import.meta as any).env?.DEV ? 'http' : 'https';
  const url = port ? `${protocol}://${host}:${port}` : `${protocol}://${host}`;
  
  console.log('API Configuration:', {
    host,
    port,
    url,
    appTitle: config.appTitle,
    isDev: (import.meta as any).env?.DEV
  });
  
  return url;
}; 