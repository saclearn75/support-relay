/** Console logger that keeps diagnostics readable by dropping high-volume traces. */
export const diagnosticLogger = {
  debug: () => undefined,
  info: (message: string, context?: Record<string, unknown>) =>
    console.log(`[band] ${message}`, context ?? ""),
  warn: (message: string, context?: Record<string, unknown>) =>
    console.warn(`[band warning] ${message}`, context ?? ""),
  error: (message: string, context?: Record<string, unknown>) =>
    console.error(`[band error] ${message}`, context ?? ""),
};
