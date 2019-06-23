import axios from 'axios';

export const HTTP = axios.create({
    baseURL: `https://yathinosaur.api.stdlib.com/http-project@dev/receive_roid_events/`
  })


export const HTTP2 = axios.create({
    baseURL: `https://yathinosaur.api.stdlib.com/roid@dev/insert_roid_event/`
  })