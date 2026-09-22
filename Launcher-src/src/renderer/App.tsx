import { useState } from 'react';

import { api } from './utils/api';
import PageBackground from './assets/background.png';
import Header from './components/Header';
import LaunchPanel from './components/LaunchPanel';
import SelfUpdateBanner from './components/SelfUpdateBanner';
import TabsPanel, { type TabType } from './components/TabsPanel';
import TopBar from './components/TopBar';
import IconSpinner from './components/styled/IconSpinner';
import usePreventDefaultEvents from './utils/usePreventDefaultEvents';

const App = () => {
	const { isLoading } = api.preferences.get.useQuery();
	const { data: appVersion } = api.general.appVersion.useQuery();

	const [activeTab, setActiveTab] = useState<TabType>();

	usePreventDefaultEvents();

	return (
		<div
			className="relative flex grow flex-col gap-3 overflow-hidden bg-cover bg-top bg-no-repeat p-[44px]"
			style={{ backgroundImage: `url(${PageBackground})` }}
		>
			<TopBar />
			<SelfUpdateBanner />
			<Header {...{ activeTab, setActiveTab }} />

			{isLoading ? (
				<div className="flex flex-grow items-center justify-center">
					<IconSpinner />
				</div>
			) : (
				<>
					<TabsPanel activeTab={activeTab} />
					<LaunchPanel />
				</>
			)}

			{appVersion && (
				<span className="pointer-events-none absolute bottom-2 right-3 select-none font-mono text-[10px] uppercase tracking-wider text-white/40">
					v{appVersion}
				</span>
			)}

		</div>
	);
};

export default App;
