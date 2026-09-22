import DOMPurify from 'dompurify';
import { AlertTriangle, ExternalLink, RefreshCw } from 'lucide-react';
import { useCallback, useMemo } from 'react';

import { api } from '~renderer/utils/api';
import { useT } from '~renderer/i18n';
import useScrollHint from '~renderer/utils/useScrollHint';
import Parchment from '~renderer/assets/parchment.jpg';

import IconSpinner from './styled/IconSpinner';
import TextButton from './styled/TextButton';

const SANITIZE_CONFIG = {
	ALLOWED_TAGS: [
		'b', 'strong', 'i', 'em', 'u', 's', 'strike', 'a', 'ul', 'ol', 'li',
		'blockquote', 'cite', 'span', 'div', 'img', 'br', 'p', 'code', 'pre',
		'dl', 'dt', 'dd', 'hr', 'sub', 'sup', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
		'table', 'thead', 'tbody', 'tr', 'td', 'th'
	],
	ALLOWED_ATTR: ['href', 'src', 'alt', 'title', 'class', 'style'],
	ALLOWED_URI_REGEXP: /^(?:https?:|mailto:)/i,
	FORBID_TAGS: ['script', 'iframe', 'object', 'embed', 'form', 'input', 'style', 'link', 'meta']
};

const LIGHT_NAMED = new Set([
	'white', 'snow', 'ivory', 'floralwhite', 'ghostwhite', 'seashell', 'beige',
	'linen', 'cornsilk', 'lightyellow', 'lightgoldenrodyellow', 'lemonchiffon',
	'yellow', 'aqua', 'cyan', 'lime', 'aquamarine', 'azure', 'mintcream',
	'honeydew', 'lavender', 'lavenderblush', 'aliceblue', 'whitesmoke',
	'gainsboro', 'silver', 'lightgray', 'lightgrey', 'antiquewhite', 'papayawhip',
	'blanchedalmond', 'bisque', 'moccasin', 'navajowhite', 'peachpuff', 'khaki',
	'wheat', 'greenyellow', 'chartreuse', 'springgreen', 'palegoldenrod', 'gold'
]);

const LIGHT_THRESHOLD = 165;

const SAFE_STYLE_PROPS = new Set([
	'color',
	'background-color',
	'font-weight',
	'font-style',
	'text-decoration',
	'text-align',
	'font-size'
]);

const colorIsTooLight = (raw: string): boolean => {
	const v = raw.trim().toLowerCase();
	const lum = (r: number, g: number, b: number) => 0.2126 * r + 0.7152 * g + 0.0722 * b;

	const hex = v.match(/^#([0-9a-f]{3}|[0-9a-f]{6})$/);
	if (hex) {
		const h =
			hex[1].length === 3
				? hex[1]
						.split('')
						.map(c => c + c)
						.join('')
				: hex[1];
		return (
			lum(
				parseInt(h.slice(0, 2), 16),
				parseInt(h.slice(2, 4), 16),
				parseInt(h.slice(4, 6), 16)
			) > LIGHT_THRESHOLD
		);
	}
	const rgb = v.match(/^rgba?\(\s*(\d+)[\s,]+(\d+)[\s,]+(\d+)/);
	if (rgb) return lum(+rgb[1], +rgb[2], +rgb[3]) > LIGHT_THRESHOLD;

	return LIGHT_NAMED.has(v);
};

const clampFontSize = (val: string): string => {
	const m = val.match(/^(\d+(?:\.\d+)?)(px|pt|%|em|rem)$/i);
	if (!m) return val;
	const n = parseFloat(m[1]);
	const unit = m[2].toLowerCase();
	const max = unit === 'px' ? 28 : unit === 'pt' ? 21 : unit === '%' ? 200 : 2;
	return `${Math.min(n, max)}${unit}`;
};

DOMPurify.addHook('afterSanitizeAttributes', node => {
	if (node.tagName === 'IMG') node.setAttribute('loading', 'lazy');

	const style = node.getAttribute('style');
	if (!style) return;

	const kept: string[] = [];
	for (const decl of style.split(';')) {
		const idx = decl.indexOf(':');
		if (idx < 0) continue;
		const prop = decl.slice(0, idx).trim().toLowerCase();
		let val = decl.slice(idx + 1).trim();
		if (!val || !SAFE_STYLE_PROPS.has(prop)) continue;

		if (prop === 'color' && colorIsTooLight(val)) continue;
		if (prop === 'font-size') val = clampFontSize(val);
		kept.push(`${prop}:${val}`);
	}

	if (kept.length) node.setAttribute('style', kept.join(';'));
	else node.removeAttribute('style');
});

const formatDate = (raw: string) => {
	const d = new Date(raw);
	if (Number.isNaN(d.getTime())) return raw;
	return d.toLocaleDateString(undefined, {
		year: 'numeric',
		month: 'short',
		day: 'numeric'
	});
};

const ForumAnnouncementPanel = () => {
	const t = useT();
	const openLink = api.general.openLink.useMutation();
	const query = api.forum.latestAnnouncement.useQuery(undefined, {
		staleTime: 10 * 60 * 1000,
		refetchOnWindowFocus: false,
		retry: 1
	});
	const scrollRef = useScrollHint<HTMLDivElement>();

	const data = query.data;
	const safeHtml = useMemo(
		() => (data ? DOMPurify.sanitize(data.html, SANITIZE_CONFIG) : ''),
		[data]
	);

	const onBodyClick = useCallback(
		(e: React.MouseEvent<HTMLDivElement>) => {
			const anchor = (e.target as HTMLElement).closest('a[href]');
			if (!anchor) return;
			e.preventDefault();
			const href = anchor.getAttribute('href');
			if (href) openLink.mutateAsync(href);
		},
		[openLink]
	);

	return (
		<aside
			className="parchment-post flex min-h-0 flex-grow flex-col gap-3"
			style={{ backgroundImage: `url(${Parchment})` }}
		>
			<div className="flex items-start justify-between gap-2">
				<h4 className="parchment-post-title min-w-0 flex-1 break-words">
					{data?.title ?? t('forum.title')}
				</h4>
				<TextButton
					icon={RefreshCw}
					size={18}
					className="-mr-2 -mt-1 shrink-0"
					loading={query.isFetching}
					onClick={() => query.refetch()}
					title={t('misc.refresh')}
				/>
			</div>

			{data?.author && (
				<span className="parchment-post-meta">
					{t('misc.newsByAuthor', { author: data.author })} · {formatDate(data.date)}
				</span>
			)}

			<hr />

			<div
				ref={scrollRef}
				className="relative -mx-4 flex min-h-0 flex-grow flex-col overflow-y-auto overflow-x-hidden px-4"
			>
				{query.isLoading ? (
					<div className="flex flex-grow flex-col items-center justify-center gap-2">
						<IconSpinner className="parchment-post-muted" />
						<p className="parchment-post-muted italic">{t('forum.loading')}</p>
					</div>
				) : query.isError ? (
					<div className="flex flex-grow flex-col items-center justify-center gap-3">
						<AlertTriangle size={32} className="text-red" />
						<p className="parchment-post-muted italic">{t('forum.error')}</p>
						<TextButton
							icon={RefreshCw}
							size={18}
							onClick={() => query.refetch()}
						>
							{t('misc.tryAgain')}
						</TextButton>
					</div>
				) : !data ? (
					<div className="flex flex-grow flex-col items-center justify-center">
						<p className="parchment-post-muted italic">{t('forum.empty')}</p>
					</div>
				) : (
					<div
						className="parchment-post-body"
						onClick={onBodyClick}
						dangerouslySetInnerHTML={{ __html: safeHtml }}
					/>
				)}
			</div>

			{data && (
				<TextButton
					icon={ExternalLink}
					size={14}
					className="-ml-2 self-start"
					onClick={() => openLink.mutateAsync(data.url)}
				>
					{t('forum.readFullPost')}
				</TextButton>
			)}
		</aside>
	);
};

export default ForumAnnouncementPanel;
