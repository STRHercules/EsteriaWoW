import { useState } from 'react';

import { api } from '~renderer/utils/api';
import { useT } from '~renderer/i18n';

import Button from './styled/Button';

type Status =
	| { state: 'idle'; currentVersion: string }
	| { state: 'checking'; currentVersion: string }
	| { state: 'unavailable'; currentVersion: string }
	| { state: 'available'; currentVersion: string; nextVersion: string }
	| {
			state: 'downloading';
			currentVersion: string;
			nextVersion: string;
			progress: number;
	  }
	| { state: 'ready'; currentVersion: string; nextVersion: string }
	| { state: 'error'; currentVersion: string; message: string };

const SelfUpdateBanner = () => {
	const t = useT();
	const [status, setStatus] = useState<Status>({
		state: 'idle',
		currentVersion: ''
	});
	api.selfUpdater.observe.useSubscription(undefined, {
		onData: setStatus
	});
	const install = api.selfUpdater.install.useMutation();

	if (
		status.state === 'idle' ||
		status.state === 'checking' ||
		status.state === 'unavailable'
	) {
		return null;
	}

	const tone = status.state === 'error' ? 'border-red/40' : 'border-tw/40';
	const label =
		status.state === 'error'
			? t('misc.selfUpdateCheckFailed', { message: status.message })
			: status.state === 'available'
			? t('misc.selfUpdateAvailable', {
					version: status.nextVersion
			  })
			: status.state === 'downloading'
			? t('misc.selfUpdateDownloading', {
					version: status.nextVersion,
					percent: Math.round(status.progress * 100)
			  })
			: status.state === 'ready'
			? t('misc.selfUpdateReady', { version: status.nextVersion })
			: '';

	return (
		<div
			className={`relative z-10 flex items-center gap-3 rounded-md border ${tone} bg-black/60 px-4 py-2 text-sm`}
		>
			<span className="flex-grow break-all">{label}</span>
			{status.state === 'ready' && (
				<Button
					primary
					onClick={() => install.mutateAsync()}
					disabled={install.isLoading}
				>
					{t('misc.selfUpdateInstallNow')}
				</Button>
			)}
		</div>
	);
};

export default SelfUpdateBanner;
