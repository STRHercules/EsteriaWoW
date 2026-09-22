import AddonsTab from './tabs/AddonsTab';
import NewsTab from './tabs/NewsTab';
import TabErrorBoundary from './TabErrorBoundary';

const Tabs = {
	'news': NewsTab,
	'addons': AddonsTab
} as const;

export const TabNames = Object.keys(Tabs) as TabType[];

export type TabType = keyof typeof Tabs;

type Props = { activeTab?: TabType };

const TabsPanel = ({ activeTab }: Props) => {
	const tab: TabType = activeTab ?? 'news';
	const Component = Tabs[tab];
	return (
		<TabErrorBoundary key={tab} tabName={tab}>
			<Component />
		</TabErrorBoundary>
	);
};

export default TabsPanel;
