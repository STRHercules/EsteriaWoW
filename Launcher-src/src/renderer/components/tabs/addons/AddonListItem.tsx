import {
	AlertOctagon,
	AlertTriangle,
	DownloadCloud,
	Github,
	HelpCircle,
	Trash2
} from 'lucide-react';
import cls from 'classnames';

import { type AddonData } from '~main/types';
import { api } from '~renderer/utils/api';
import TextButton from '~renderer/components/styled/TextButton';
import { ColoredText } from '~renderer/components/styled/ColoredText';
import IconSpinner from '~renderer/components/styled/IconSpinner';
import DialogButton from '~renderer/components/styled/DialogButton';
import { isNotUndef } from '~common/utils';
import CloseButton from '~renderer/components/styled/CloseButton';
import { useT } from '~renderer/i18n';

import AddonDetail from './AddonDetail';

export type Dependencies = {
	[folder: string]: 'installed' | 'available' | string;
};

export type LocalDependencies = {
	name: string;
	optional: boolean;
	status: 'installed' | 'available' | 'missing' | string;
}[];

type Props = Omit<AddonData, 'ref'> & {
	row: number;
	dependencies: Dependencies;
	gitRef?: string;
};

const toRepoUrl = (git?: string) =>
	git ? git.replace(/\.git$/, '') : undefined;

const AddonListItem = ({ row, dependencies, ...addon }: Props) => {
	const t = useT();
	const update = api.addons.update.useMutation();
	const remove = api.addons.remove.useMutation();
	const openLink = api.general.openLink.useMutation();
	const repoUrl = toRepoUrl(addon.git);

	const localDependencies: LocalDependencies = [
		...(addon.toc?.Dependencies?.split(', ')?.map(d => [d, false] as const) ??
			[]),
		...(addon.toc?.OptionalDeps?.split(', ')?.map(d => [d, true] as const) ??
			[])
	].map<LocalDependencies[number]>(([d, optional]) => ({
		name: d,
		optional,
		status: dependencies[d] ?? 'missing'
	}));

	const warnings = [
		addon.toc && addon.toc?.Interface !== '11200'
			? {
					full: t('addons.warnIncorrectVersionFull', {
						version: addon.toc?.Interface ?? ''
					}),
					short: t('addons.warnIncorrectVersionShort')
			  }
			: undefined,
		localDependencies.some(d => d.status !== 'installed' && !d.optional)
			? {
					full: t('addons.warnMissingDependenciesFull', {
						deps: localDependencies
							.filter(d => d.status !== 'installed' && !d.optional)
							.map(d => d.name)
							.join(', ')
					}),
					short: t('addons.warnMissingDependenciesShort')
			  }
			: undefined
	].filter(isNotUndef);

	return (
		<div className="contents hover-row:bg-purple/30">
			<div
				className="-mx-4 h-full w-[200%]"
				style={{ gridRow: row + 1, gridColumn: '1/4' }}
			/>
			{addon.status === 'fetching' ? (
				<IconSpinner
					className="text-blueGray"
					size={18}
					style={{ gridRow: row + 1, gridColumn: 1 }}
				/>
			) : (
				<DialogButton
					clickAway
					dialog={close => (
						<AddonDetail
							close={close}
							warnings={warnings}
							dependencies={localDependencies}
							{...addon}
						/>
					)}
				>
					{open => (
						<TextButton
							icon={
								addon.status === 'invalid'
									? AlertOctagon
									: warnings.length
									? AlertTriangle
									: HelpCircle
							}
							onClick={open}
							title={t('addons.details')}
							size={18}
							className={cls(
								'-mx-2',
								addon.status === 'invalid'
									? 'text-red'
									: warnings.length
									? 'text-yellow'
									: 'text-blueGray'
							)}
							style={{ gridRow: row + 1, gridColumn: 1 }}
						/>
					)}
				</DialogButton>
			)}

			<div
				className="-ml-2 flex items-center gap-1 whitespace-nowrap"
				style={{ gridRow: row + 1, gridColumn: 2 }}
			>
				<ColoredText>{addon.toc?.Title ?? addon.folder}</ColoredText>
				{repoUrl && (
					<TextButton
						icon={Github}
						size={14}
						title={t('addons.openOnGithub', { url: repoUrl })}
						onClick={() => openLink.mutateAsync(repoUrl)}
						className="!p-1 text-blueGray/60 hocus:text-pink"
					/>
				)}
			</div>

			<ColoredText
				className="s1 py-1 text-blueGray"
				style={{ gridRow: row + 1, gridColumn: 3 }}
			>
				{addon.toc?.Notes ?? addon.description ?? ''}
			</ColoredText>

			<div
				className="-m-2 flex items-center justify-end gap-2"
				style={{ gridRow: row + 1, gridColumn: 4 }}
			>
				{addon.status === 'downloading' ? (
					<>
						<p className="s1 text-blueGray">{addon.progress}</p>
						<IconSpinner size={18} className="text-blueGray" />
					</>
				) : addon.status === 'invalid' ? (
					<p className="s1 text-red">{addon.error}</p>
				) : warnings.length ? (
					<p className="s1 text-yellow">{warnings[0].short}</p>
				) : (
					<p className="s1 text-blueGray/50">
						{addon.status === 'upToDate'
							? t('addons.upToDate')
							: !addon.git
							? t('addons.notVersioned')
							: ''}
					</p>
				)}
				{addon.status === 'outOfDate' && (
					<TextButton
						onClick={() => update.mutateAsync({ toUpdate: [addon.folder] })}
						className="s1 -mx-2 justify-self-end"
					>
						{t('addons.update')}
					</TextButton>
				)}
				{addon.status === 'available' ? (
					<TextButton
						onClick={() => update.mutateAsync({ toUpdate: [addon.folder] })}
						className="text-warmGreen"
						icon={DownloadCloud}
						size={18}
						title={t('addons.download')}
					/>
				) : (
					<DialogButton
						clickAway
						dialog={close => (
							<div className="tw-dialog">
								<CloseButton close={close} />
								<h4 className="tw-color">{t('addons.deleteConfirmTitle')}</h4>
								<hr />
								<p className="text-blueGray">
									{t('addons.deleteConfirmBody', { folder: addon.folder })}
								</p>
								<p className="text-blueGray">
									{t('addons.deleteConfirmFiles')}
								</p>
								<TextButton
									icon={Trash2}
									onClick={async () => {
										await remove.mutateAsync({ toDelete: [addon.folder] });
										close();
									}}
									disabled={remove.isLoading}
									className="self-end text-red"
								>
									{t('addons.delete')}
								</TextButton>
							</div>
						)}
					>
						{open => (
							<TextButton
								onClick={open}
								className="text-red/50"
								icon={Trash2}
								size={18}
								title={t('addons.remove')}
							/>
						)}
					</DialogButton>
				)}
			</div>
		</div>
	);
};

export default AddonListItem;
