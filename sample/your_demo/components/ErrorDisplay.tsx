
import React, { useState } from 'react';
import { ErrorInfo } from '../types';
import { Logger } from '../services/logger';

interface ErrorDisplayProps {
    errorInfo: ErrorInfo;
    onDismiss: () => void;
    appState: object;
}

const ReloadIcon: React.FC<{className?: string}> = ({className}) => (
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className={className}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0l3.181 3.183a8.25 8.25 0 0011.664 0l3.181-3.183m-11.664 0l3.181-3.183a8.25 8.25 0 00-11.664 0l3.181 3.183" />
    </svg>
);

const ClipboardIcon: React.FC<{className?: string}> = ({className}) => (
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className={className}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M15.666 3.888A2.25 2.25 0 0013.5 2.25h-3c-1.03 0-1.9.693-2.166 1.638m7.332 0c.055.194.084.4.084.612v3.042m-7.416 0v3.042c0 .212.03.418.084.612m7.332 0c.646.049 1.288.11 1.927.184 1.1.128 1.907 1.077 1.907 2.185V19.5a2.25 2.25 0 01-2.25 2.25H6.75A2.25 2.25 0 014.5 19.5V6.257c0-1.108.806-2.057 1.907-2.185a48.208 48.208 0 011.927-.184" />
    </svg>
);


export const ErrorDisplay: React.FC<ErrorDisplayProps> = ({ errorInfo, onDismiss, appState }) => {
    const [copied, setCopied] = useState(false);

    const handleCopyDebugInfo = () => {
        const debugInfo = {
            error: {
                name: errorInfo.error.name,
                message: errorInfo.error.message,
                stack: errorInfo.error.stack,
            },
            context: errorInfo.context,
            appState: appState,
            timestamp: new Date().toISOString(),
            userAgent: navigator.userAgent,
        };

        try {
            const jsonString = JSON.stringify(debugInfo, null, 2);
            navigator.clipboard.writeText(jsonString);
            Logger.info('Copied debug info to clipboard.');
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        } catch (e) {
            Logger.error('Failed to copy debug info.', e);
        }
    };
    
    return (
        <div className="fixed inset-0 bg-gray-900/80 backdrop-blur-sm flex items-center justify-center z-50 p-4" role="dialog" aria-modal="true" aria-labelledby="error-title" aria-describedby="error-context">
            <div className="w-full max-w-2xl bg-gray-800 border border-red-500/50 rounded-lg shadow-2xl shadow-red-500/20 text-gray-200">
                <div className="p-6 border-b border-gray-700">
                    <h2 id="error-title" className="text-2xl font-bold text-red-400">An Error Occurred</h2>
                    <p id="error-context" className="mt-1 text-gray-400">{errorInfo.context}</p>
                </div>
                <div className="p-6 max-h-[50vh] overflow-y-auto">
                    {errorInfo.troubleshooting && (
                        <div className='mb-6'>
                            <h3 className="font-semibold text-gray-300 mb-2">Troubleshooting Steps:</h3>
                            <ul className="list-disc list-inside space-y-1 text-sm text-gray-400">
                                {errorInfo.troubleshooting.map((step, i) => <li key={i}>{step}</li>)}
                            </ul>
                        </div>
                    )}

                    <div>
                        <h3 className="font-semibold text-gray-300 mb-2">Error Details:</h3>
                        <pre className="text-xs bg-gray-900/70 p-3 rounded-md text-red-300 whitespace-pre-wrap break-words">
                            <code>{errorInfo.error.name}: {errorInfo.error.message}</code>
                        </pre>
                    </div>
                </div>

                <div className="p-4 bg-gray-800/50 border-t border-gray-700 flex justify-between items-center">
                    <button onClick={handleCopyDebugInfo} className="flex items-center gap-2 px-4 py-2 text-xs font-semibold text-cyan-200 bg-cyan-800/50 hover:bg-cyan-700/50 rounded-md transition-colors">
                        <ClipboardIcon className="w-4 h-4" />
                        {copied ? 'Copied!' : 'Copy Debug Info'}
                    </button>
                    <div className="flex items-center gap-3">
                         <button onClick={() => window.location.reload()} className="flex items-center gap-2 px-4 py-2 text-xs font-semibold text-yellow-200 bg-yellow-800/50 hover:bg-yellow-700/50 rounded-md transition-colors">
                            <ReloadIcon className="w-4 h-4" />
                            Reload Page
                        </button>
                        <button onClick={onDismiss} className="px-4 py-2 text-xs font-semibold text-gray-200 bg-gray-700 hover:bg-gray-600 rounded-md transition-colors">
                            Dismiss
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};
