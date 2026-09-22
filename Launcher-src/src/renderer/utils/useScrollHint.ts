import { useLayoutEffect, useRef } from 'react';

const FADE_PX = 24;

const setScrollHint = (tar: HTMLElement) => {
	const top = tar.scrollTop > 0 && tar.scrollHeight !== tar.clientHeight;
	const bottom = tar.scrollTop < tar.scrollHeight - tar.offsetHeight;

	const topStr = top ? 'true' : 'false';
	const bottomStr = bottom ? 'true' : 'false';
	if (topStr === tar.dataset.top && bottomStr === tar.dataset.bottom) return;

	tar.dataset.top = topStr;
	tar.dataset.bottom = bottomStr;

	if (!top && !bottom) {
		tar.style.webkitMaskImage = '';
		return;
	}

	tar.style.webkitMaskImage = `linear-gradient(${
		top ? `transparent, black calc(${FADE_PX}px)` : ''
	}${top && bottom ? ', ' : ''}${
		bottom ? `black calc(100% - ${FADE_PX}px), transparent` : ''
	})`;
};

const useScrollHint = <T extends HTMLElement>() => {
	const ref = useRef<T>(null);
	useLayoutEffect(() => {
		const current = ref.current;
		if (!current) return;

		let scheduled = false;
		const schedule = () => {
			if (scheduled) return;
			scheduled = true;
			requestAnimationFrame(() => {
				scheduled = false;
				setScrollHint(current);
			});
		};

		schedule();

		const observer = new ResizeObserver(schedule);
		observer.observe(current);
		current.addEventListener('scroll', schedule, { passive: true });
		window.addEventListener('resize', schedule);

		return () => {
			observer.disconnect();
			current?.removeEventListener('scroll', schedule);
			window.removeEventListener('resize', schedule);
		};
	}, []);

	return ref;
};

export default useScrollHint;
