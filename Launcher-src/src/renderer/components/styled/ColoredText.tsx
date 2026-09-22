type Run = { text: string; color?: string };

const tokenize = (s: string): Run[] => {
	const runs: Run[] = [];
	const re = /\|c([0-9a-fA-F]{8})|\|r/g;
	let i = 0;
	let color: string | undefined;
	let m: RegExpExecArray | null;
	while ((m = re.exec(s)) !== null) {
		if (m.index > i) runs.push({ text: s.slice(i, m.index), color });
		if (m[0].toLowerCase() === '|r') {
			color = undefined;
		} else if (m[1]) {
			color = `#${m[1].slice(2).toLowerCase()}`;
		}
		i = re.lastIndex;
	}
	if (i < s.length) runs.push({ text: s.slice(i), color });
	return runs.filter(r => r.text.length > 0);
};

export const stripColorCodes = (s: string) =>
	tokenize(s)
		.map(r => r.text)
		.join('');

export const ColoredText = ({
	children,
	className,
	style
}: {
	children: string;
	className?: string;
	style?: React.CSSProperties;
}) => {
	const runs = tokenize(children);
	return (
		<p className={className} style={style}>
			{runs.map((r, i) =>
				r.color ? (
					<span
						key={i}
						className="text-size-inherit text-inherit"
						style={{ color: r.color }}
					>
						{r.text}
					</span>
				) : (
					<span key={i}>{r.text}</span>
				)
			)}
		</p>
	);
};
