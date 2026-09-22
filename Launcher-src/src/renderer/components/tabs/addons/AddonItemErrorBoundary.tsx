import { Component, type ErrorInfo, type ReactNode } from 'react';
import log from 'electron-log/renderer';

type Props = { children: ReactNode; folder: string; row: number };
type State = { hasError: boolean; message?: string };

class AddonItemErrorBoundary extends Component<Props, State> {
	state: State = { hasError: false };

	static getDerivedStateFromError(error: Error): State {
		return { hasError: true, message: error.message };
	}

	componentDidCatch(error: Error, info: ErrorInfo) {
		log.error(
			`[AddonListItem] crash row=${this.props.row} folder=${this.props.folder}:`,
			error,
			info
		);
	}

	render() {
		if (!this.state.hasError) return this.props.children;
		return (
			<div
				className="contents"
				style={{ gridRow: this.props.row + 1 }}
			>
				<div style={{ gridRow: this.props.row + 1, gridColumn: '1/5' }} className="-mx-4 px-4 py-1 text-red s1">
					Failed to render &quot;{this.props.folder}&quot;: {this.state.message ?? 'unknown error'}
				</div>
			</div>
		);
	}
}

export default AddonItemErrorBoundary;
