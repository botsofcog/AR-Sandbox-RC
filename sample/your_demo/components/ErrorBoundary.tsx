import React, { Component, ErrorInfo as ReactErrorInfo, ReactNode } from 'react';
import { ErrorInfo } from '../types';
import { ErrorDisplay } from './ErrorDisplay';
import { Logger } from '../services/logger';

interface Props {
  children: ReactNode;
}

interface State {
  errorInfo: ErrorInfo | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    errorInfo: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    // Update state so the next render will show the fallback UI.
    return {
      errorInfo: {
        error,
        context: 'A critical rendering error occurred in the application.',
        troubleshooting: ['Try reloading the page.', 'If the problem persists, copy the debug info and report the issue.'],
      },
    };
  }

  public componentDidCatch(error: Error, errorInfo: ReactErrorInfo) {
    // You can also log the error to an error reporting service
    Logger.error('Uncaught error:', error, errorInfo);
  }

  public render() {
    if (this.state.errorInfo) {
      // You can render any custom fallback UI
      return (
        <ErrorDisplay
          errorInfo={this.state.errorInfo}
          onDismiss={() => this.setState({ errorInfo: null })}
          appState={{ note: 'App state not available due to render error.' }}
        />
      );
    }

    return this.props.children;
  }
}
