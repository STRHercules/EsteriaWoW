import { useEffect } from 'react';

const allowedElements = ['INPUT', 'TEXTAREA'];

const isClipboardShortcut = (e: KeyboardEvent) =>
	(e.ctrlKey || e.metaKey) &&
	['a', 'c', 'v', 'x'].includes(e.key.toLowerCase());

const usePreventDefaultEvents = () => {
	useEffect(() => {
		const disableKeyboardEvents = (e: KeyboardEvent) => {
			if (allowedElements.includes((e.target as HTMLElement).tagName)) return;
			if (isClipboardShortcut(e)) return;
			e.preventDefault();
		};

		window.addEventListener('keydown', disableKeyboardEvents, true);
		window.addEventListener('keyup', disableKeyboardEvents, true);

		return () => {
			window.removeEventListener('keydown', disableKeyboardEvents, true);
			window.removeEventListener('keyup', disableKeyboardEvents, true);
		};
	}, []);
};

export default usePreventDefaultEvents;
