interface ApiConfig {
  host: string;
  port: string;
}

interface Config {
  api: ApiConfig;
  appTitle: string;
}

export const config: Config = {
  api: {
    host: import.meta.env.VITE_API_HOST,
    port: import.meta.env.VITE_API_PORT
  },
  appTitle: import.meta.env.VITE_APP_TITLE
}; 