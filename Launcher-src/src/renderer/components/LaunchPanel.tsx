import { useState, type ReactElement } from 'react';
import cls from 'classnames';
import log from 'electron-log/renderer';

import { type UpdaterStatus } from '~main/types';
import { formatFileSize } from '~common/utils';
import { api } from '~renderer/utils/api';
import { useT } from '~renderer/i18n';

import Button from './styled/Button';
import DialogButton from './styled/DialogButton';
import ClientDirDialog from './ClientDirDialog';

const formatDuration = (seconds: number) => {
	const s = Math.max(0, Math.round(seconds));
	if (s < 60) return `${s}s`;
	const m = Math.floor(s / 60);
	const rem = s % 60;
	if (m < 60) return rem ? `${m}m ${rem}s` : `${m}m`;
	const h = Math.floor(m / 60);
	const minRem = m % 60;
	return minRem ? `${h}h ${minRem}m` : `${h}h`;
};

const formatPercent = (progress: number) => `${(progress * 100).toFixed(1)}%`;

const ProgressDetails = ({ status }: { status: UpdaterStatus }) => {
	const t = useT();
	const { bytesDone, bytesTotal, bytesPerSecond, etaSeconds, progress } =
		status;
	if (bytesTotal === undefined || bytesDone === undefined) return null;

	const pct =
		progress !== undefined && progress >= 0 ? formatPercent(progress) : '—';

	return (
		<p className="s1 text-blueGray">
			<span className="tw-color">{pct}</span>
			<span>
				{' '}
				· {formatFileSize(bytesDone)} / {formatFileSize(bytesTotal)}
			</span>
			{bytesPerSecond !== undefined && bytesPerSecond > 0 && (
				<span> · {formatFileSize(bytesPerSecond)}/s</span>
			)}
			<span>
				{' · '}
				{etaSeconds !== undefined
					? `~${formatDuration(etaSeconds)} ${t('launch.remaining')}`
					: t('launch.calculating')}
			</span>
		</p>
	);
};

const LaunchPanel = () => {
	const t = useT();
	const [status, setStatus] = useState<UpdaterStatus>({ state: 'verifying' });
	api.updater.observe.useSubscription(undefined, {
		onData: setStatus,
		onError: err => log.error('Updater subscription error:', err)
	});

	const { data: pref } = api.preferences.get.useQuery();

	const verify = api.updater.verify.useMutation();
	const update = api.updater.update.useMutation();
	const start = api.launcher.start.useMutation();

	const props: Record<
		UpdaterStatus['state'],
		{ button: ReactElement; helperText?: ReactElement }
	> = {
		verifying: { button: <Button disabled>{t('launch.verifying')}</Button> },
		serverUnreachable: {
			button: pref?.version ? (
				<Button onClick={() => start.mutateAsync()}>{t('launch.play')}</Button>
			) : (
				<Button onClick={() => verify.mutateAsync()}>
					{t('launch.retry')}
				</Button>
			),
			helperText: (
				<div className="-mb-2">
					<p>
						<span className="text-orange">{t('launch.errorLabel')}</span>{' '}
						{t('launch.serverFail')}
					</p>
					<p className="s1 text-blueGray">
						{pref?.version
							? t('launch.localVersion', { version: pref.version })
							: t('launch.tryLater')}
					</p>
				</div>
			)
		},
		noClient: {
			button: (
				<DialogButton
					clickAway
					dialog={close => <ClientDirDialog close={close} />}
				>
					{open => (
						<Button primary onClick={open}>
							{t('launch.install')}
						</Button>
					)}
				</DialogButton>
			)
		},
		updateAvailable: {
			button: (
				<Button onClick={() => update.mutateAsync()}>
					{t('launch.update')}
				</Button>
			),
			helperText: (
				<div className="-mb-2 flex flex-col gap-1">
					<p>{t('launch.updateAvailable')}</p>
					<p className="s1 text-blueGray">
						{status.progress !== undefined &&
							status.bytesDone !== undefined &&
							status.bytesTotal !== undefined && (
								<>
									<span className="tw-color">
										{formatPercent(status.progress)}
									</span>
									<span>
										{' '}
										· {formatFileSize(status.bytesDone)} /{' '}
										{formatFileSize(status.bytesTotal)} {t('launch.onDisk')} ·{' '}
									</span>
								</>
							)}
						<span className="break-all">{status.message}</span>{' '}
						{t('launch.remaining')}
					</p>
				</div>
			)
		},
		updating: {
			button: <Button disabled>{t('launch.updating')}</Button>,
			helperText: (
				<div className="-mb-2 flex flex-col gap-1">
					{status.message && (
						<p className="s1 truncate text-blueGray">{status.message}</p>
					)}
					<ProgressDetails status={status} />
				</div>
			)
		},
		upToDate: {
			button: (
				<Button primary onClick={() => start.mutateAsync()}>
					{t('launch.play')}
				</Button>
			),
			helperText: (
				<div className="-mb-2">
					<p>{t('launch.upToDate')}</p>
					<p className="s1 text-blueGray">
						{t('launch.version', { version: pref?.version ?? '' })}
					</p>
				</div>
			)
		},
		failed: {
			button: (
				<Button onClick={() => verify.mutateAsync()}>
					{t('launch.retry')}
				</Button>
			),
			helperText: (
				<div className="-mb-2">
					<p>
						<span className="text-orange">{t('launch.errorLabel')}</span>{' '}
						{status.message}
					</p>
					<p className="s1 text-blueGray">{t('launch.verifyHint')}</p>
				</div>
			)
		}
	};

	return (
		<div className="flex gap-3">
			<div className="flex flex-grow flex-col justify-end gap-3">
				{props[status.state].helperText ??
					(status.message && (
						<p className="s1 -mb-2 text-blueGray">{status.message}</p>
					))}
				{start.data && !start.data.ok && start.data.error && (
					<p className="s1 -mb-2 text-orange">{start.data.error}</p>
				)}
				<div className="tw-loading-wrapper">
					{status.progress !== undefined && (
						<div
							className={cls('tw-loading', {
								'tw-loading-unknown': status.progress === -1
							})}
							style={
								status.progress !== -1
									? {
											clipPath: `inset(0 ${
												100 - Math.ceil(Math.abs(status.progress) * 100)
											}% 0 0)`
									  }
									: undefined
							}
						/>
					)}
				</div>
			</div>
			{props[status.state].button}
		</div>
	);
};

export default LaunchPanel;
