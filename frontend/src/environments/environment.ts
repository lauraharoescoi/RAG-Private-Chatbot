// The file contents for the current environment will overwrite these during build.
// The build system defaults to the dev environment which uses `environment.ts`, but if you do
// `ng build --env=prod` then `environment.prod.ts` will be used instead.
// The list of which env maps to which file can be found in `.angular-cli.json`.

export const environment = {
  production: false,
  apiUrl: 'http://backend:6000'
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