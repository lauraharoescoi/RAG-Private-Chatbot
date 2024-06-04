export const environment = {
  production: true,
  apiUrl: 'http://localhost:6000'
};

const conversation = {
  get_conversation: environment.apiUrl + '/conversation/:conversationId',
  post_conversation: environment.apiUrl + '/conversation/:conversationId',
  update_conversation_name: environment.apiUrl + '/conversation/name/:conversationId',
  get_conversations: environment.apiUrl + '/conversation'

};

const files = {
  upload: environment.apiUrl + '/files/upload'
};

export const SERVER_URLS = { conversation, files };