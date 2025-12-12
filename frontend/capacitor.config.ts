import type { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.techz.clientmanager',
  appName: 'Client Manager',
  webDir: 'dist',

  server: { 
    //URL de VITE
    url: 'http://192.168.1.113:5173',
    cleartext: true, //Permite conexiones no seguras
  },

  android: {
    buildOptions: {
      keystorePath: '',
      keystoreAlias: ''
    }
  },
  plugins: {
    SplashScreen: {
      launchShowDuration: 2000,
      backgroundColor: '#121212',
      showSpinner: true,
      androidSpinnerStyle: 'large',
      spinnerColor: '#2196F3',
      splashFullScreen: true,
      splashImmersive: true,
    },
    Keyboard: {
      resize: 'body' as any,
      style: 'dark' as any,
      resizeOnFullScreen: true,
    },
    StatusBar: {
      style: 'DARK' as any,
      backgroundColor: '#121212',
      overlaysWebView: true,
    },
  },
};

export default config;
