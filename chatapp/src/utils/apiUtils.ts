import { config } from '../config';

export const getApiBaseUrl = (): string => {
  const { host, port } = config.api;
  const url = `http://${host}:${port}`;
  
  console.log('API Configuration:', {
    host,
    port,
    url,
    appTitle: config.appTitle
  });
  
  return url;
}; 