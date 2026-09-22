import {
	createContext,
	useContext,
	useEffect,
	useState,
	type ReactNode
} from 'react';

import { api } from '~renderer/utils/api';

import { translations, type Lang } from './translations';

type Params = Record<string, string | number>;
type Translate = (key: string, params?: Params) => string;

type LocaleCtx = {
	lang: Lang;
	setLang: (lang: Lang) => void;
	t: Translate;
};

const LocaleContext = createContext<LocaleCtx>({
	lang: 'enUS',
	setLang: () => {},
	t: key => key
});

export const LocaleProvider = ({ children }: { children: ReactNode }) => {
	const { data: pref } = api.preferences.get.useQuery();
	const [lang, setLang] = useState<Lang>('enUS');

	useEffect(() => {
		if (pref?.locale) setLang(pref.locale);
	}, [pref?.locale]);

	const t: Translate = (key, params) => {
		let s = translations[lang]?.[key] ?? translations.enUS[key] ?? key;
		if (params)
			for (const [k, v] of Object.entries(params))
				s = s.replace(`{${k}}`, String(v));
		return s;
	};

	return (
		<LocaleContext.Provider value={{ lang, setLang, t }}>
			{children}
		</LocaleContext.Provider>
	);
};

export const useLocale = () => useContext(LocaleContext);
export const useT = () => useContext(LocaleContext).t;
