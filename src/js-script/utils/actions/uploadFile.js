const fs = require('fs');

const pathToVideo = 'C:\\Users\\salim\\Videos\\test.mp4';

async function uploadFile(filePath) {
  try {
    const currentGame = process.env.CURRENT_GAME || 'KOF XIII';
    const currentUser = process.env.CURRENT_USER || 'SalimOfShadow';
    const fileName = `${currentGame.replace(/_/g, '')} Match Replay | ${currentUser}`;
    const currentEnv = process.env.CURRENT_ENV || 'dev';
    const endpointURL =
      currentEnv === 'dev'
        ? 'http://localhost:3001'
        : 'https://salimkof.pro:3001';

    console.log(`About to upload a file from this path : ${filePath}`);
    const file = await fs.openAsBlob(filePath);
    const formData = new FormData();
    formData.set('currentGame', currentGame);
    formData.set('currentUser', currentUser);
    formData.set('replay', file);
    const response = await fetch(`${endpointURL}/recieve-video`, {
      method: 'POST',
      body: formData,
    });
    if (response.ok) {
      console.log('File uploaded successfully');
      return true;
    } else {
      console.error('Upload failed with status:', response.status);
      return false;
    }
  } catch (err) {
    console.log(err);
  }
}
uploadFile(pathToVideo);
module.exports = { uploadFile };
// ONLY WORKS WHEN HARDCODING THE SAME EXACT PATH