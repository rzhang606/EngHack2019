import axios from 'axios';

export const HTTP = axios.create({
    baseURL: `https://yathinosaur.api.stdlib.com/http-project@dev/receive_events/`
  })