import type { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.techz.client.manager',
  appName: 'Client Manager',
  webDir: 'dist',

  // server: { 
  //   //URL de VITE
  //   url: 'http://192.168.0.192:5173',
  //   cleartext: true, //Permite conexiones no seguras
  // },

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
      resize: 'none' as any,
      style: 'dark' as any,
      resizeOnFullScreen: false,
    },
    StatusBar: {
      style: 'DARK' as any,
      backgroundColor: '#121212',
      overlaysWebView: true,
    },
  },
};

export default config;
