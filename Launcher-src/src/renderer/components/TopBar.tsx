import { Settings, Minus, X } from 'lucide-react';
import { useState } from 'react';

import { api } from '~renderer/utils/api';
import { useT } from '~renderer/i18n';

import DialogButton from './styled/DialogButton';
import PreferencesDialog from './PreferencesDialog';
import TextButton from './styled/TextButton';
import LanguageDropdown from './LanguageDropdown';

const TopBar = () => {
	const t = useT();
	const [safeToQuit, setSafeToQuit] = useState(true);
	api.updater.observe.useSubscription(undefined, {
		onData: ({ state }) =>
			setSafeToQuit(state !== 'verifying' && state !== 'updating')
	});

	const minimize = api.general.minimize.useMutation();
	const quit = api.general.quit.useMutation();
	return (
		<div
			style={{ WebkitAppRegion: 'drag' } as React.CSSProperties}
			className="absolute left-0 right-0 top-0 flex justify-end pr-2 pt-2 opacity-50"
		>
			<div
				style={{ WebkitAppRegion: 'no-drag' } as React.CSSProperties}
				className="flex items-center"
			>
				<LanguageDropdown />
				<DialogButton dialog={close => <PreferencesDialog close={close} />}>
					{open => (
						<TextButton
							icon={Settings}
							title={t('topbar.settings')}
							onClick={open}
							size={16}
							className="!p-1"
						/>
					)}
				</DialogButton>
				<TextButton
					icon={Minus}
					title={t('topbar.minimize')}
					onClick={() => minimize.mutateAsync()}
					size={16}
					className="!p-1"
				/>
				<DialogButton
					dialog={close => (
						<div className="tw-dialog">
							<h3 className="tw-color">{t('quit.title')}</h3>
							<hr />
							<p className="text-blueGray">{t('quit.warn')}</p>
							<div className="flex gap-2 self-end">
								<TextButton onClick={close}>{t('quit.return')}</TextButton>
								<TextButton
									onClick={() => quit.mutateAsync()}
									className="text-red"
								>
									{t('topbar.quit')}
								</TextButton>
							</div>
						</div>
					)}
				>
					{open => (
						<TextButton
							icon={X}
							title={t('topbar.quit')}
							onClick={() => (!safeToQuit ? open() : quit.mutateAsync())}
							size={16}
							className="!p-1 hocus:text-red"
						/>
					)}
				</DialogButton>
			</div>
		</div>
	);
};

export default TopBar;
