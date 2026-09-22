import { Check, X } from 'lucide-react';
import { useEffect, useState } from 'react';

import CloseButton from '~renderer/components/styled/CloseButton';
import IconSpinner from '~renderer/components/styled/IconSpinner';
import TextButton from '~renderer/components/styled/TextButton';
import { api } from '~renderer/utils/api';
import { useT } from '~renderer/i18n';

const useDebounced = (value: string, delay: number) => {
	const [debouncedValue, setDebouncedValue] = useState(value);
	useEffect(() => {
		const timeout = setTimeout(() => setDebouncedValue(value), delay);
		return () => clearTimeout(timeout);
	}, [value, delay]);

	return debouncedValue;
};

const CustomAddonDialog = ({ close }: { close: () => void }) => {
	const t = useT();
	const [url, setUrl] = useState('');
	const debouncedUrl = useDebounced(url, 500);
	const response = api.addons.checkGitUrl.useQuery(debouncedUrl, {
		enabled: !!debouncedUrl
	});
	const update = api.addons.install.useMutation();

	return (
		<div className="tw-dialog">
			<CloseButton close={close} />
			<h3 className="tw-color">{t('addons.installAddon')}</h3>
			<hr />
			{response.data ? (
				<img
					src={response.data?.preview}
					alt={t('addons.previewAlt')}
					className="w-full"
				/>
			) : (
				<div className="flex h-[191px] w-full items-center justify-center bg-darkPurple">
					{response.isFetching && <IconSpinner />}
				</div>
			)}
			<div className="flex items-center gap-1 border-b border-blueGray bg-darkGray/70 p-1 hocus:border-orange">
				<input
					className="w-full cursor-text bg-inherit"
					value={url}
					onChange={e => setUrl(e.target.value)}
				/>
				{response.isFetching ? (
					<IconSpinner size={18} />
				) : response.data ? (
					<Check size={18} />
				) : (
					<X size={18} />
				)}
			</div>
			<div className="flex items-center justify-end gap-2">
				<p className="s1 text-blueGray">
					{response.data
						? t('addons.readyToInstall')
						: t('addons.invalidGitUrl')}
				</p>
				<TextButton
					onClick={() => {
						if (!response.data) return;
						update.mutateAsync(response.data);
						close();
						setUrl('');
					}}
					className={response.data ? 'text-warmGreen' : 'text-blueGray'}
					disabled={!response.data || response.isLoading}
				>
					{t('addons.install')}
				</TextButton>
			</div>
		</div>
	);
};

export default CustomAddonDialog;
