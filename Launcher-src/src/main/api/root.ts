import { createTRPCRouter } from './trpc';
import { addonsRouter } from './routers/addonts';
import { launcherRouter } from './routers/launcher';
import { updaterRouter } from './routers/updater';
import { generalRouter } from './routers/general';
import { preferencesRouter } from './routers/preferences';
import { newsRouter } from './routers/news';
import { forumRouter } from './routers/forum';
import { selfUpdaterRouter } from './routers/selfUpdater';

export const appRouter = createTRPCRouter({
	addons: addonsRouter,
	general: generalRouter,
	preferences: preferencesRouter,
	launcher: launcherRouter,
	updater: updaterRouter,
	news: newsRouter,
	forum: forumRouter,
	selfUpdater: selfUpdaterRouter
});

export type AppRouter = typeof appRouter;
