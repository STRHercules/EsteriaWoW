import { useForm } from 'react-hook-form';
import { useEffect } from 'react';

import { PreferencesSchema } from '~common/schemas';
import zodResolver from '~renderer/utils/zodResolver';
import { api } from '~renderer/utils/api';
import { useT } from '~renderer/i18n';

import TextButton from './styled/TextButton';
import FilePickerInput from './form/FilePickerInput';
import CloseButton from './styled/CloseButton';

type Props = { close: () => void };

const ClientDirDialog = ({ close }: Props) => {
	const t = useT();
	const { data: pref } = api.preferences.get.useQuery();
	const setPref = api.preferences.set.useMutation();
	const isValidClientDir = api.preferences.isValidClientDir.useQuery(
		pref?.clientDir,
		{ enabled: !!pref?.isPortable }
	);

	const verify = api.updater.verify.useMutation();

	const {
		register,
		handleSubmit,
		watch,
		formState,
		setValue,
		setError,
		reset
	} = useForm({
		defaultValues: { clientDir: pref?.clientDir ?? '' },
		resolver: zodResolver(PreferencesSchema.pick({ clientDir: true }))
	});

	useEffect(() => {
		pref && reset(pref);
	}, [reset, pref]);

	if (pref?.isPortable) {
		return (
			<form className="tw-dialog">
				<CloseButton close={close} />
				<h2 className="color mb-2 text-xl">
					{t('prefs.installLocationTitle')}
				</h2>
				<p>{t('prefs.portableInfo')}</p>
				{!isValidClientDir.isLoading && !isValidClientDir.data && (
					<p>
						<span className="text-secondary">{t('prefs.errorLabel')}</span>
						{t('prefs.wowExeNotFound', { exe: 'WoW.exe' })}
					</p>
				)}
			</form>
		);
	}

	return (
		<form
			className="tw-dialog"
			onSubmit={handleSubmit(async ({ clientDir }) => {
				try {
					await setPref.mutateAsync({ clientDir });
					verify.mutate();
					close();
				} catch (e) {
					setError('clientDir', {
						message: e instanceof Error ? e.message : JSON.stringify(e)
					});
				}
			})}
		>
			<CloseButton
				close={() => {
					reset();
					close();
				}}
			/>
			<h3 className="tw-color">{t('prefs.installLocationTitle')}</h3>
			<hr />

			<p className="text-blueGray">{t('prefs.selectDirectory')}</p>
			<p className="text-blueGray">{t('prefs.upgradeExisting')}</p>
			<div className="flex items-center gap-3">
				<label htmlFor="clientDir">{t('prefs.installDirectory')}</label>
				<FilePickerInput
					{...register('clientDir')}
					title={watch('clientDir') ?? undefined}
					setValue={v =>
						setValue('clientDir', v, {
							shouldTouch: true,
							shouldDirty: true,
							shouldValidate: true
						})
					}
					options={{ properties: ['openDirectory', 'createDirectory'] }}
				/>
			</div>
			{formState.errors.clientDir && (
				<p className="text-secondary text-sm">
					{formState.errors.clientDir.message}
				</p>
			)}

			<TextButton
				type="submit"
				loading={formState.isSubmitting}
				className="self-end text-green"
			>
				{t('prefs.confirm')}
			</TextButton>
		</form>
	);
};

export default ClientDirDialog;
