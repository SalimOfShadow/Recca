import FormData from 'form-data';
import fs from 'fs';
import axios from 'axios'; // Import axios
import { Notification } from 'electron';

export async function uploadFile(filePath: string) {
  try {
    const currentPlatform = process.env.CURRENT_PLATFORM || 'youtube';
    const currentGame = process.env.CURRENT_GAME || 'KOF XIII';
    const currentUser = process.env.CURRENT_USERNAME || 'Guest';
    const visibility = process.env.VISIBILITY || 'public';
    const fileName = `${currentGame.replace(/_/g, '')} Match Replay | ${currentUser}`;

    const currentEnv = process.env.NODE_ENV;
    // const endpointURL = 'https://salimkof.pro:6001';
    const endpointURL = 'http://localhost:6001';
    // const endpointURL = currentEnv === 'production'
    //   ? 'https://salimkof.pro:3001'
    //   : 'http://localhost:3001'

    console.log(`About to upload a file from this path : ${filePath}`);
    const dataStream = fs.createReadStream(filePath);

    // Prepare form data
    const formData = new FormData();
    formData.append('currentGame', currentGame);
    formData.append('currentUser', currentUser);
    formData.append('visibility', visibility);
    formData.append('platform', currentPlatform);
    formData.append('replay', dataStream, fileName);

    // Get headers for form data (necessary for axios)
    const formHeaders = formData.getHeaders();

    // Send the request with axios
    const response = await axios.post(
      `${endpointURL}/api/v1/recieve-video`,
      formData,
      {
        headers: {
          ...formHeaders,
        },
        timeout: 1000 * 60 * 7, // Times out the request after 7 minutes
      },
    );

    if (response.status === 200) {
      console.log('File uploaded successfully');
      return true;
    } else {
      new Notification({
        title: 'Failed to upload the replay.',
        body: `Please ensure your connection is stable.`,
      }).show();
      console.error('Upload failed with status:', response.status);
      return false;
    }
  } catch (err) {
    console.log(err);
  }
}
