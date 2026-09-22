import cls from 'classnames';
import { type ReactNode } from 'react';

import TextButton from '../styled/TextButton';

const Checkbox = () => (
	<svg
		width={16}
		height={16}
		viewBox="0 0 12 12"
		fill="none"
		xmlns="http://www.w3.org/2000/svg"
		className="shrink-0"
	>
		<rect
			x="1"
			y="1"
			width="10"
			height="10"
			rx="1"
			stroke="currentColor"
			strokeWidth="1.5"
		/>
		<rect x="3.5" y="3.5" width="5" height="5" fill="white" />
	</svg>
);

type Props = {
	label?: ReactNode;
	value: boolean;
	setValue: (v: boolean) => void;
	disabled?: boolean;
	className?: cls.Value;
};

const CheckboxInput = ({
	label,
	value,
	setValue,
	disabled,
	className
}: Props) => (
	<TextButton
		onClick={() => !disabled && setValue(!value)}
		icon={Checkbox}
		className={cls(
			'!items-start text-left text-blueGray',
			{ '[&_*]:fill-none': !value, 'pointer-events-none opacity-40': disabled },
			className
		)}
	>
		{label}
	</TextButton>
);

export default CheckboxInput;
