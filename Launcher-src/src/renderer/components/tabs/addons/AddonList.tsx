import { useState } from 'react';
import { ChevronDown, ChevronRight } from 'lucide-react';
import cls from 'classnames';

import { type AddonData } from '~main/types';

import AddonListItem, { type Dependencies } from './AddonListItem';
import AddonItemErrorBoundary from './AddonItemErrorBoundary';

type Props = {
	title: string;
	addons: AddonData[];
	dependencies: Dependencies;
};

const AddonList = ({ title, addons, dependencies }: Props) => {
	const [open, setOpen] = useState(true);
	if (!addons.length) return null;
	return (
		<div>
			<button
				type="button"
				onClick={() => setOpen(o => !o)}
				className="mb-2 flex cursor-pointer items-center gap-1 border-0 bg-transparent p-0"
			>
				{open ? <ChevronDown size={18} /> : <ChevronRight size={18} />}
				<h4 className="tw-color">{title}</h4>
			</button>
			<div
				className={cls(
					'grid grid-cols-[auto_auto_1fr_auto] items-center gap-x-3 gap-y-1',
					!open && 'hidden'
				)}
			>
				{addons.map((addon, i) => {
					const { ref: gitRef, ...rest } = addon;
					return (
						<AddonItemErrorBoundary
							key={`${addon.folder}#${i}`}
							folder={addon.folder}
							row={i}
						>
							<AddonListItem
								row={i}
								dependencies={dependencies}
								gitRef={gitRef}
								{...rest}
							/>
						</AddonItemErrorBoundary>
					);
				})}
			</div>
		</div>
	);
};
export default AddonList;
