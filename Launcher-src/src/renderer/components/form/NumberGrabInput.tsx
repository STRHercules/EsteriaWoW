import cls from 'classnames';
import { type ChangeEvent, type FocusEvent, type HTMLProps, forwardRef } from 'react';

type Props = Omit<
	HTMLProps<HTMLInputElement>,
	'value' | 'min' | 'max' | 'step'
> & {
	setValue: (v: number) => void;
	min?: number;
	max?: number;
	step?: number;
	sensitivity?: number;
};
const NumberGrabInput = forwardRef<HTMLInputElement, Props>(
	(
		{
			setValue,
			className,
			max = Infinity,
			min = -Infinity,
			step: _step,
			sensitivity: _sensitivity,
			type: _ignored,
			onChange,
			onBlur,
			...props
		},
		ref
	) => (
		<input
			ref={ref}
			type="text"
			inputMode="numeric"
			{...props}
			onChange={(e: ChangeEvent<HTMLInputElement>) => {
				const n = Number(e.currentTarget.value);
				if (Number.isFinite(n) && n > max) {
					e.currentTarget.value = String(max);
				}
				onChange?.(e);
			}}
			onBlur={(e: FocusEvent<HTMLInputElement>) => {
				const n = Number(e.currentTarget.value);
				const clamped = Math.max(
					Math.min(Number.isFinite(n) ? n : min, max),
					min
				);
				setValue(clamped);
				onBlur?.(e);
			}}
			onWheel={e => !e.shiftKey && e.currentTarget.blur()}
			className={cls(
				className,
				'w-[70px] cursor-text border-b border-blueGray bg-inherit p-1 text-center hocus:border-orange'
			)}
		/>
	)
);
export default NumberGrabInput;
