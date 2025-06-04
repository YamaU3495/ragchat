import React from 'react';
import ChatPage from './components/pages/ChatPage';
import { ThemeProvider, THEME_ID, createTheme } from '@mui/material/styles';
const materialTheme = createTheme({
  palette: {
    primary: {
      light: '#757ce8',
      main: '#3f50b5',
      dark: '#002884',
      contrastText: '#fff',
    },
    secondary: {
      light: '#ff7961',
      main: '#ff002d',
      dark: '#ba000d',
      contrastText: '#fff',
    },
  },
});


function App() {
  return (
    <ThemeProvider theme={{[THEME_ID]: materialTheme}}>
      <ChatPage />
    </ThemeProvider>
  );
}

export default App;
