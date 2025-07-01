const getTimestamp = () => new Date().toISOString();

export const Logger = {
  info: (message: string, ...optionalParams: any[]) => {
    console.info(`[INFO] [${getTimestamp()}]: ${message}`, ...optionalParams);
  },
  warn: (message: string, ...optionalParams: any[]) => {
    console.warn(`[WARN] [${getTimestamp()}]: ${message}`, ...optionalParams);
  },
  error: (message: string, ...optionalParams: any[]) => {
    console.error(`[ERROR] [${getTimestamp()}]: ${message}`, ...optionalParams);
  },
};
