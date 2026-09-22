import { useT } from '~renderer/i18n';

import TextButton from './styled/TextButton';
import { TabNames, type TabType } from './TabsPanel';

type Props = {
	activeTab?: TabType;
	setActiveTab: (tab?: TabType) => void;
};

const Header = ({ activeTab, setActiveTab }: Props) => {
	const t = useT();
	return (
		<div className="-mb-3 flex select-none items-center gap-1">
			<button
				onClick={() => setActiveTab(undefined)}
				className="z-10 -my-3 mx-3 flex w-[180px] cursor-pointer flex-col items-start leading-none"
				aria-label="Esteria home"
			>
				<span className="font-sans text-2xl font-bold tracking-[0.28em] text-orange">
					ESTERIA
				</span>
				<span className="mt-1 pl-1 text-[10px] uppercase tracking-[0.42em] text-white/70">
					WotLK 3.3.5a
				</span>
			</button>
			{TabNames.map(tab => (
				<TextButton
					key={tab}
					onClick={() => setActiveTab(tab)}
					active={activeTab === tab}
					className="uppercase"
				>
					{t(`tab.${tab}`)}
				</TextButton>
			))}
		</div>
	);
};

export default Header;
