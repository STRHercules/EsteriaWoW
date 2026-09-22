export type AddonSource = {
	git: string;
	branch?: string;
	name?: string;
	description?: string;
	ref?: string;
};

export const defaultSources: AddonSource[] = [];
