import { useT } from '~renderer/i18n';

const ComingSoonTab = () => {
	const t = useT();
	return (
		<div className="tw-surface flex flex-grow flex-col items-center justify-center gap-2">
			<p className="italic text-blueGray">{t('misc.comingSoon')}</p>
		</div>
	);
};

export default ComingSoonTab;
