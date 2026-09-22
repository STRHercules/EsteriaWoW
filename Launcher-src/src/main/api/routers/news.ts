import fetch from 'node-fetch';
import Logger from 'electron-log/main';

import { EsteriaConfig } from '~common/config';
import { NewsFeedSchema, type NewsItem } from '~common/schemas';

import { createTRPCRouter, publicProcedure } from '../trpc';

const FETCH_TIMEOUT_MS = 8_000;

const fetchNews = async (): Promise<NewsItem[]> => {
	if (!EsteriaConfig.newsUrl) return [];
	const url = EsteriaConfig.newsUrl;
	const controller = new AbortController();
	const t = setTimeout(() => controller.abort(), FETCH_TIMEOUT_MS);
	try {
		const res = await fetch(url, { signal: controller.signal });
		if (!res.ok) throw Error(`HTTP ${res.status}`);
		const parsed = NewsFeedSchema.safeParse(await res.json());
		if (!parsed.success) {
			Logger.error('News feed failed schema validation', parsed.error.flatten());
			throw Error('Malformed news feed');
		}
		return parsed.data.items;
	} finally {
		clearTimeout(t);
	}
};

export const newsRouter = createTRPCRouter({
	list: publicProcedure.query(async () => {
		try {
			return await fetchNews();
		} catch (e) {
			Logger.error('Failed to fetch news', e);
			throw e;
		}
	})
});
