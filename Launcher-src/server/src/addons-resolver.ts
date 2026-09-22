import fs from 'fs-extra';
import path from 'path';

import { defaultSources, type AddonSource } from './addons-sources.js';

const CACHE_TTL_MS = 60 * 60 * 1000;
const FETCH_CONCURRENCY = 8;
const FETCH_TIMEOUT_MS = 10_000;
const SOURCES_OVERRIDE_PATH = process.env.ADDONS_SOURCES_PATH ?? '';

export type TocData = Record<string, string>;

export type ResolvedAddon = {
	name: string;
	owner: string;
	git: string;
	branch?: string;
	ref?: string;
	toc?: TocData;
	description?: string;
	lastUpdated?: string;
	stars?: number;
};

type CacheEntry = { at: number; data: ResolvedAddon[] };
let cache: CacheEntry | undefined;
let inFlight: Promise<ResolvedAddon[]> | undefined;

const normalizeColorCodes = (s: string): string =>
	s.replace(/\|C(?=[0-9a-fA-F]{8})/g, '|c').replace(/\|R/g, '|r');

const parseToc = (content: string): TocData =>
	content
		.split('\n')
		.filter(l => l.startsWith('## '))
		.map(l => l.slice(3))
		.map(l => {
			const idx = l.indexOf(':');
			if (idx === -1) return null;
			return [l.slice(0, idx).trim(), l.slice(idx + 1).trim()] as const;
		})
		.filter((e): e is readonly [string, string] => !!e)
		.reduce<TocData>((acc, [k, v]) => {
			acc[k] = normalizeColorCodes(v);
			return acc;
		}, {});

const fetchWithTimeout = async (url: string, init?: RequestInit) => {
	const controller = new AbortController();
	const t = setTimeout(() => controller.abort(), FETCH_TIMEOUT_MS);
	try {
		return await fetch(url, { ...init, signal: controller.signal });
	} finally {
		clearTimeout(t);
	}
};

type RepoMeta = {
	description?: string;
	defaultBranch?: string;
	lastUpdated?: string;
	stars?: number;
};

type RawMeta = {
	description?: string | null;
	default_branch?: string;
	pushed_at?: string | null;
	updated_at?: string | null;
	last_activity_at?: string | null;
	stargazers_count?: number | null;
	stars_count?: number | null;
	star_count?: number | null;
};

type Provider = {
	apiUrl: (owner: string, repo: string) => string;
	apiHeaders: () => Record<string, string>;
	mapMeta: (json: RawMeta) => RepoMeta;
	tocUrl: (owner: string, repo: string, ref: string, name: string) => string;
};

const githubProvider: Provider = {
	apiUrl: (o, r) => `https://api.github.com/repos/${o}/${r}`,
	apiHeaders: () => ({
		Accept: 'application/vnd.github+json',
		...(process.env.GITHUB_TOKEN && {
			Authorization: `Bearer ${process.env.GITHUB_TOKEN}`
		})
	}),
	mapMeta: j => ({
		description: j.description ?? undefined,
		defaultBranch: j.default_branch,
		lastUpdated: j.pushed_at ?? undefined,
		stars: j.stargazers_count ?? undefined
	}),
	tocUrl: (o, r, ref, name) =>
		`https://raw.githubusercontent.com/${o}/${r}/${ref}/${name}.toc`
};

const gitlabProvider: Provider = {
	apiUrl: (o, r) =>
		'https://gitlab.com/api/v4/projects/' + encodeURIComponent(o + '/' + r),
	apiHeaders: () => ({ Accept: 'application/json' }),
	mapMeta: j => ({
		description: j.description ?? undefined,
		defaultBranch: j.default_branch,
		lastUpdated: j.last_activity_at ?? undefined,
		stars: j.star_count ?? undefined
	}),
	tocUrl: (o, r, ref, name) =>
		'https://gitlab.com/' +
		o +
		'/' +
		r +
		'/-/raw/' +
		encodeURIComponent(ref) +
		'/' +
		encodeURIComponent(name) +
		'.toc'
};

const CODEBERG_API = 'https://codeberg.org/api/v1';
const codebergProvider: Provider = {
	apiUrl: (o, r) => `${CODEBERG_API}/repos/${o}/${r}`,
	apiHeaders: () => ({ Accept: 'application/json' }),
	mapMeta: j => ({
		description: j.description ?? undefined,
		defaultBranch: j.default_branch,
		lastUpdated: j.updated_at ?? undefined,
		stars: j.stars_count ?? undefined
	}),
	tocUrl: (o, r, ref, name) =>
		`${CODEBERG_API}/repos/${o}/${r}/raw/${name}.toc?ref=${encodeURIComponent(
			ref
		)}`
};

const parseGitUrl = (
	git: string
): { owner: string; repo: string; provider: Provider } => {
	const gh = git.match(/github\.com\/([^/]+)\/([^/]+?)(?:\.git)?$/);
	if (gh && gh[1] && gh[2]) {
		return { owner: gh[1], repo: gh[2], provider: githubProvider };
	}
	const gitlab = git.match(/gitlab\.com\/([^/]+)\/([^/]+?)(?:\.git)?$/);
	if (gitlab && gitlab[1] && gitlab[2]) {
		return { owner: gitlab[1], repo: gitlab[2], provider: gitlabProvider };
	}
	const codeberg = git.match(/codeberg\.org\/([^/]+)\/([^/]+?)(?:\.git)?$/);
	if (codeberg && codeberg[1] && codeberg[2]) {
		return {
			owner: codeberg[1],
			repo: codeberg[2],
			provider: codebergProvider
		};
	}
	throw Error(`Unsupported git URL: ${git}`);
};

const REQUIRED_TOC_KEYS = ['Interface'];

const tryFetchToc = async (
	provider: Provider,
	owner: string,
	repo: string,
	name: string,
	ref: string
): Promise<TocData | undefined> => {
	const res = await fetchWithTimeout(
		provider.tocUrl(owner, repo, ref, name)
	).catch(() => null);
	if (!res?.ok) return undefined;
	const parsed = parseToc(await res.text());
	return REQUIRED_TOC_KEYS.every(k => typeof parsed[k] === 'string')
		? parsed
		: undefined;
};

const resolveOne = async (src: AddonSource): Promise<ResolvedAddon | null> => {
	try {
		const { owner, repo, provider } = parseGitUrl(src.git);
		const name = src.name ?? repo;

		const apiRes = await fetchWithTimeout(provider.apiUrl(owner, repo), {
			headers: provider.apiHeaders()
		}).catch(() => null);

		let meta: RepoMeta | undefined;
		if (apiRes?.ok) meta = provider.mapMeta((await apiRes.json()) as RawMeta);

		const candidates = src.ref
			? [src.ref]
			: src.branch
			? [src.branch]
			: [
					...new Set(
						[meta?.defaultBranch, 'main', 'master'].filter(
							(b): b is string => !!b
						)
					)
			  ];

		let toc: TocData | undefined;
		let resolvedRef: string | undefined;
		for (const ref of candidates) {
			toc = await tryFetchToc(provider, owner, repo, name, ref);
			if (toc) {
				resolvedRef = ref;
				break;
			}
		}

		const effectiveBranch = src.ref
			? undefined
			: src.branch ?? resolvedRef ?? meta?.defaultBranch;

		let description = meta?.description ?? undefined;
		const lastUpdated = meta?.lastUpdated;
		const stars = meta?.stars;

		if (src.description) {
			description = src.description;
			if (toc) toc = { ...toc, Notes: src.description };
		}

		const result: ResolvedAddon = { name, owner, git: src.git };
		if (effectiveBranch !== undefined) result.branch = effectiveBranch;
		if (src.ref !== undefined) result.ref = src.ref;
		if (toc !== undefined) result.toc = toc;
		if (description !== undefined) result.description = description;
		if (lastUpdated !== undefined) result.lastUpdated = lastUpdated;
		if (stars !== undefined) result.stars = stars;
		return result;
	} catch (e) {
		console.error(`Failed to resolve ${src.git}:`, e);
		return null;
	}
};

const poolMap = async <T, R>(
	items: T[],
	concurrency: number,
	fn: (item: T) => Promise<R>
): Promise<R[]> => {
	const results: R[] = new Array(items.length);
	let idx = 0;
	const worker = async () => {
		while (true) {
			const i = idx++;
			if (i >= items.length) return;
			const item = items[i];
			if (item === undefined) return;
			results[i] = await fn(item);
		}
	};
	await Promise.all(Array.from({ length: concurrency }, worker));
	return results;
};

const loadSources = async (): Promise<AddonSource[]> => {
	if (!SOURCES_OVERRIDE_PATH) return defaultSources;
	try {
		if (await fs.pathExists(SOURCES_OVERRIDE_PATH)) {
			const override = (await fs.readJSON(
				SOURCES_OVERRIDE_PATH
			)) as AddonSource[];
			if (Array.isArray(override) && override.length > 0) {
				console.log(
					`Using addon sources override from ${SOURCES_OVERRIDE_PATH}`
				);
				return override;
			}
		}
	} catch (e) {
		console.error(
			`Failed to read override at ${SOURCES_OVERRIDE_PATH}, using defaults:`,
			e
		);
	}
	return defaultSources;
};

const buildList = async (): Promise<ResolvedAddon[]> => {
	const sources = await loadSources();
	console.log(
		`Resolving metadata for ${sources.length} addons (concurrency=${FETCH_CONCURRENCY})...`
	);
	const t0 = Date.now();
	const results = await poolMap(sources, FETCH_CONCURRENCY, resolveOne);
	const ok = results.filter((r): r is ResolvedAddon => r !== null);
	ok.sort((a, b) => a.name.localeCompare(b.name));
	console.log(
		`Resolved ${ok.length}/${sources.length} addons in ${Date.now() - t0}ms`
	);
	return ok;
};

export const getAddons = async (force = false): Promise<ResolvedAddon[]> => {
	if (!force && cache && Date.now() - cache.at < CACHE_TTL_MS) {
		return cache.data;
	}
	if (inFlight) return inFlight;
	inFlight = buildList()
		.then(data => {
			cache = { at: Date.now(), data };
			return data;
		})
		.finally(() => {
			inFlight = undefined;
		});
	return inFlight;
};

export const warmUp = () => {
	getAddons().catch(e => console.error('Addon resolver warm-up failed:', e));
};
