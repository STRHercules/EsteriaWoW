const trimTrailingSlashes = (value: string) => value.replace(/\/+$/, '');

export const EsteriaConfig = {
	serverUrl: trimTrailingSlashes(
		import.meta.env.MAIN_VITE_SERVER_URL || 'http://127.0.0.1:7384'
	),
	clientVersion: import.meta.env.MAIN_VITE_CLIENT_VERSION || 'live',
	realmList: import.meta.env.MAIN_VITE_REALM_LIST || '127.0.0.1',
	patchList: import.meta.env.MAIN_VITE_PATCH_LIST || '127.0.0.1',
	realmName: import.meta.env.MAIN_VITE_REALM_NAME || 'Esteria',
	newsUrl: import.meta.env.MAIN_VITE_NEWS_URL || '',
	forumUrl: import.meta.env.MAIN_VITE_FORUM_URL || ''
} as const;
