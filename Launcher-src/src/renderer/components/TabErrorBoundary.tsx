import { AlertTriangle, RefreshCw } from 'lucide-react';
import { Component, type ErrorInfo, type ReactNode } from 'react';
import log from 'electron-log/renderer';

import { useT } from '~renderer/i18n';

import TextButton from './styled/TextButton';

type Props = {
	tabName: string;
	children: ReactNode;
};

type State = {
	error?: Error;
	componentStack?: string;
};

type FallbackProps = {
	tabName: string;
	error: Error;
	componentStack?: string;
	onReset: () => void;
};

const TabErrorFallback = ({
	tabName,
	error,
	componentStack,
	onReset
}: FallbackProps) => {
	const t = useT();
	return (
		<div className="tw-surface flex min-h-0 flex-grow flex-col gap-3">
			<div className="flex items-center gap-2">
				<AlertTriangle size={22} className="text-red" />
				<h4 className="text-red">{t('misc.tabCrashed', { tab: tabName })}</h4>
			</div>
			<hr />
			<p className="text-white">
				{error.name}: {error.message}
			</p>
			{componentStack && (
				<pre className="s1 max-h-[200px] overflow-auto whitespace-pre-wrap text-blueGray">
					{componentStack.trim()}
				</pre>
			)}
			<hr />
			<TextButton
				icon={RefreshCw}
				onClick={onReset}
				className="self-end text-warmGreen"
			>
				{t('misc.tryAgain')}
			</TextButton>
		</div>
	);
};

class TabErrorBoundary extends Component<Props, State> {
	state: State = {};

	static getDerivedStateFromError(error: Error): State {
		return { error };
	}

	componentDidCatch(error: Error, info: ErrorInfo) {
		log.error(`Tab "${this.props.tabName}" crashed:`, error, info);
		this.setState({ error, componentStack: info.componentStack ?? undefined });
	}

	componentDidUpdate(prevProps: Props) {
		if (prevProps.tabName !== this.props.tabName) {
			this.setState({ error: undefined, componentStack: undefined });
		}
	}

	#reset = () => this.setState({ error: undefined, componentStack: undefined });

	render() {
		if (!this.state.error) return this.props.children;
		const { error, componentStack } = this.state;
		return (
			<TabErrorFallback
				tabName={this.props.tabName}
				error={error}
				componentStack={componentStack}
				onReset={this.#reset}
			/>
		);
	}
}

export default TabErrorBoundary;
