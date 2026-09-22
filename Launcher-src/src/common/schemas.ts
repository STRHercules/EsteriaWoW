import { z } from 'zod';

const f = {
	boolean: (defaultValue?: boolean) =>
		z.boolean().nullish().default(!!defaultValue)
};

export const HardwareInfoSchema = z.object({
	totalRamMb: z.number(),
	cpuCores: z.number(),
	cpuModel: z.string(),
	gpuModel: z.string(),
	vramMb: z.number().nullable(),
	vramSource: z.enum(['registry', 'wmi', 'none']),
	detectedAt: z.string(),
	schemaVersion: z.number()
});
export type HardwareInfo = z.infer<typeof HardwareInfoSchema>;

export const PreferencesSchema = z.object({
	isPortable: z.boolean().optional(),
	clientDir: z.string().optional(),
	version: z.string().optional(),
	minimizeToTrayOnPlay: f.boolean(true),
	cleanWdb: f.boolean(true),
	locale: z
		.enum(['enUS', 'deDE', 'zhCN', 'esES', 'ptBR', 'ruRU'])
		.default('enUS'),
	localePatchLetter: z.string().optional(),
	localePatchLocale: z.string().optional(),
	rememberPosition: f.boolean(),
	windowPosition: z
		.object({
			x: z.number(),
			y: z.number(),
			width: z.number(),
			height: z.number()
		})
		.nullish(),
	hardware: HardwareInfoSchema.optional()
});
export type PreferencesSchema = z.infer<typeof PreferencesSchema>;

export const TocDataSchema = z.object({
	Interface: z.string(),
	Title: z.string(),
	Author: z.string(),
	Notes: z.string(),
	Version: z.string(),
	Dependencies: z.string().optional(),
	OptionalDeps: z.string().optional()
});

export type TocData = z.infer<typeof TocDataSchema>;

export const AddonDataSchema = z.object({
	status: z.enum([
		'available',
		'fetching',
		'unknown',
		'upToDate',
		'outOfDate',
		'downloading',
		'invalid'
	]),
	git: z.string().optional(),
	toc: TocDataSchema.optional(),
	description: z.string().optional(),
	error: z.string().optional(),
	branch: z.string().optional(),
	ref: z.string().optional(),
	folder: z.string(),
	progress: z.string().optional(),
	preview: z.string().optional()
});

export type AddonData = z.infer<typeof AddonDataSchema>;

export const NewsItemSchema = z.object({
	id: z.string(),
	title: z.string(),
	date: z.string(),
	body: z.string(),
	url: z.string().url().optional(),
	author: z.string().nullish()
});
export type NewsItem = z.infer<typeof NewsItemSchema>;

export const NewsFeedSchema = z.object({
	items: z.array(NewsItemSchema)
});
export type NewsFeed = z.infer<typeof NewsFeedSchema>;

export const ForumAnnouncementSchema = z.object({
	id: z.string(),
	title: z.string(),
	author: z.string().nullish(),
	date: z.string(),
	url: z.string().url(),
	html: z.string()
});
export type ForumAnnouncement = z.infer<typeof ForumAnnouncementSchema>;
