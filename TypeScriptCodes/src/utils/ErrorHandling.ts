export enum ErrorSeverity {
    DEBUG = 'DEBUG',
    INFO = 'INFO',
    WARNING = 'WARNING',
    ERROR = 'ERROR',
    CRITICAL = 'CRITICAL'
}

export interface ErrorContext {
    timestamp: Date;
    severity: ErrorSeverity;
    component: string;
    message: string;
    stackTrace?: string;
    additionalData?: Record<string, any>;
}

export class KAPESITError extends Error {
    public severity: ErrorSeverity;
    public component: string;
    public timestamp: Date;
    public stackTrace: string;
    public additionalData?: Record<string, any>;

    constructor(
        message: string,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        component: string = 'UNKNOWN',
        additionalData?: Record<string, any>
    ) {
        super(message);
        this.name = 'KAPESITError';
        this.severity = severity;
        this.component = component;
        this.timestamp = new Date();
        this.stackTrace = this.stack || '';
        this.additionalData = additionalData;
    }

    toJSON(): ErrorContext {
        return {
            timestamp: this.timestamp,
            severity: this.severity,
            component: this.component,
            message: this.message,
            stackTrace: this.stackTrace,
            additionalData: this.additionalData
        };
    }
}

export class ErrorHandler {
    private static instance: ErrorHandler;
    private errorHistory: ErrorContext[] = [];
    private errorStats: Map<string, number> = new Map();

    private constructor() {
        this.setupGlobalErrorHandler();
    }

    static getInstance(): ErrorHandler {
        if (!ErrorHandler.instance) {
            ErrorHandler.instance = new ErrorHandler();
        }
        return ErrorHandler.instance;
    }

    static createError(
        message: string,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        component: string = 'UNKNOWN',
        additionalData?: Record<string, any>
    ): KAPESITError {
        const error = new KAPESITError(message, severity, component, additionalData);
        ErrorHandler.getInstance().handleError(error);
        return error;
    }

    private setupGlobalErrorHandler(): void {
        process.on('uncaughtException', (error: Error) => {
            this.handleError(
                new KAPESITError(
                    error.message,
                    ErrorSeverity.CRITICAL,
                    'GLOBAL',
                    { originalError: error }
                )
            );
        });

        process.on('unhandledRejection', (reason: any) => {
            this.handleError(
                new KAPESITError(
                    reason?.message || 'Unhandled Promise rejection',
                    ErrorSeverity.CRITICAL,
                    'GLOBAL',
                    { reason }
                )
            );
        });
    }

    handleError(error: KAPESITError): void {
        // Log error
        this.logError(error);

        // Update statistics
        this.updateErrorStats(error);

        // Store in history
        this.errorHistory.push(error.toJSON());

        // Clean up old errors (keep last 1000)
        if (this.errorHistory.length > 1000) {
            this.errorHistory.shift();
        }

        // Send alerts for critical errors
        if (error.severity === ErrorSeverity.CRITICAL) {
            this.sendAlert(error);
        }
    }

    private logError(error: KAPESITError): void {
        const logMessage = `[${error.timestamp.toISOString()}] ${error.severity} - ${error.component}: ${error.message}`;
        
        switch (error.severity) {
            case ErrorSeverity.DEBUG:
                console.debug(logMessage);
                break;
            case ErrorSeverity.INFO:
                console.info(logMessage);
                break;
            case ErrorSeverity.WARNING:
                console.warn(logMessage);
                break;
            case ErrorSeverity.ERROR:
            case ErrorSeverity.CRITICAL:
                console.error(logMessage);
                if (error.stackTrace) {
                    console.error(error.stackTrace);
                }
                break;
        }
    }

    private updateErrorStats(error: KAPESITError): void {
        const key = `${error.component}:${error.severity}`;
        this.errorStats.set(key, (this.errorStats.get(key) || 0) + 1);
    }

    private async sendAlert(error: KAPESITError): Promise<void> {
        // Implement alert sending logic (email, Slack, etc.)
        console.error('CRITICAL ERROR ALERT:', error.toJSON());
    }

    getErrorHistory(): ErrorContext[] {
        return [...this.errorHistory];
    }

    getErrorStats(): Record<string, number> {
        return Object.fromEntries(this.errorStats);
    }

    clearErrorHistory(): void {
        this.errorHistory = [];
        this.errorStats.clear();
    }
} 