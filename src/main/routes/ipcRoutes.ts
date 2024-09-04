import { ipcMain, Notification } from 'electron';
import path from 'path';
import { spawn } from 'child_process';
import { startObs } from '../../js-script/app';

const isDebug =
  process.env.NODE_ENV === 'development' || process.env.DEBUG_PROD === 'true';

export const setupIpcRoutes = () => {
  ipcMain.on('ipc-example', async (event, arg) => {
    const msgTemplate = (pingPong: string) => `IPC test: ${pingPong}`;
    console.log(msgTemplate(arg));
    event.reply('ipc-example', msgTemplate('pong'));
  });

  ipcMain.on('run-python-script', (event) => {
    try {
      const exePath = path.join(
        __dirname,
        '..',
        '..',
        // '..',
        // '..',  removes one path for running the app using pnpm dev

        'compiled-scripts',
        'py-script.exe',
      );
      if (isDebug) {
        console.log('Logging the path now');
        console.log(exePath);
      }

      const py = spawn(exePath, {
        env: { ...process.env }, // pass env variables to the Python script
      });
      py.stdout.on('data', (data) => {
        console.log(`stdout: ${data}`);
        event.reply('python-script-output', data.toString());
      });

      py.stderr.on('data', (data) => {
        console.error(`stderr: ${data}`);
        event.reply('python-script-error', data.toString());
      });

      py.on('close', (code) => {
        console.log(`child process exited with code ${code}`);
        console.log('Python script exited');
        event.reply('python-script-close', code);
      });
    } catch (err) {
      console.log(err);
    }
  });

  ipcMain.on('display-notification', async (event, message) => {
    function showNotification() {
      new Notification({
        title: 'Error encountered!',
        body: `${message}`,
      }).show();
    }

    showNotification();
  });

  ipcMain.on('change-game', async (event, game) => {
    try {
      // Set the environment variable
      console.log(`Game changed to ${game}`);
      process.env.CURRENT_GAME = game;
      const response = await fetch('http://localhost:4609/change-game');

      if (!response.ok) {
        console.log('Failed to change the game');
      } else {
        console.log(`Game changed to ${game}`);
      }
    } catch (error) {
      console.error('Error occurred while changing the game:', error);
    }
  });

  ipcMain.on('select-download-directory', async (event, message) => {
    var remote = require('remote');
    var dialog = remote.require('electron').dialog;

    var path = dialog.showOpenDialog({
      properties: ['openDirectory'],
    });
  });

  // Handler from MainContainer.tsx to send env variables
  ipcMain.handle('get-env-vars', () => {
    console.log('get-env-variables route called');
    console.log(process.env.CURRENT_GAME);

    return process.env.CURRENT_GAME;
  });
};