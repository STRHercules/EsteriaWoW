import { useEffect, useRef, useState } from 'react';
import { Globe } from 'lucide-react';
import { createPortal } from 'react-dom';
import cls from 'classnames';

import { api } from '~renderer/utils/api';
import { useLocale } from '~renderer/i18n';
import { type Lang } from '~renderer/i18n/translations';

const LOCALES: { value: Lang; code: string; label: string }[] = [
	{ value: 'enUS', code: 'En', label: 'English' },
	{ value: 'deDE', code: 'De', label: 'Deutsch' },
	{ value: 'zhCN', code: 'Zh', label: '中文' },
	{ value: 'esES', code: 'Es', label: 'Español' },
	{ value: 'ptBR', code: 'Pt', label: 'Português' },
	{ value: 'ruRU', code: 'Ru', label: 'Русский' }
];

const LanguageDropdown = () => {
	const { lang, setLang, t } = useLocale();
	const setPref = api.preferences.set.useMutation();
	const code = LOCALES.find(l => l.value === lang)?.code ?? 'En';

	const [open, setOpen] = useState(false);
	const [pos, setPos] = useState<{ top: number; right: number }>();
	const btnRef = useRef<HTMLButtonElement>(null);

	const toggle = () => {
		const r = btnRef.current?.getBoundingClientRect();
		if (r) setPos({ top: r.bottom + 4, right: window.innerWidth - r.right });
		setOpen(o => !o);
	};

	useEffect(() => {
		if (!open) return;
		const close = () => setOpen(false);
		window.addEventListener('click', close);
		return () => window.removeEventListener('click', close);
	}, [open]);

	const pick = (v: Lang) => {
		setLang(v);
		setPref.mutate({ locale: v });
		setOpen(false);
	};

	return (
		<>
			<button
				ref={btnRef}
				type="button"
				title={t('topbar.language')}
				onClick={e => {
					e.stopPropagation();
					toggle();
				}}
				className="bg-transparent flex cursor-pointer items-center border-0 px-1 text-[12px] tracking-wide hocus:text-orange"
			>
				<Globe size={14} />
				{code}
			</button>
			{open &&
				pos &&
				createPortal(
					<div
						onClick={e => e.stopPropagation()}
						style={{ top: pos.top, right: pos.right }}
						className="fixed z-50 flex flex-col border border-blueGray/30 bg-darkGray py-1 shadow-[0_8px_20px_rgba(0,0,0,0.5)]"
					>
						{LOCALES.map(l => (
							<button
								key={l.value}
								type="button"
								title={l.label}
								onClick={() => pick(l.value)}
								className={cls(
									'bg-transparent cursor-pointer border-0 px-3 py-1 text-center text-[12px] hocus:bg-orange/20',
									l.value === lang ? 'text-warmGreen' : 'text-white'
								)}
							>
								{l.code}
							</button>
						))}
					</div>,
					document.body
				)}
		</>
	);
};

export default LanguageDropdown;
