import * as yaml from 'js-yaml';
import * as fs from 'fs';
import * as path from 'path';
import { ErrorHandler, ErrorSeverity } from './ErrorHandling';

export interface ServerConfig {
    host: string;
    port: number;
    maxConnections: number;
    connectionTimeout: number;
    pingInterval: number;
    pingTimeout: number;
}

export interface SecurityConfig {
    quantumKeyLength: number;
    sessionKeyLength: number;
    jwtSecret: string;
    jwtExpiry: number;
    allowedOrigins: string[];
    rateLimit: {
        requestsPerMinute: number;
        burstSize: number;
    };
}

export interface MessageQueueConfig {
    maxRetries: number;
    retryDelay: number;
    maxQueueSize: number;
    cleanupInterval: number;
    messageTTL: number;
    priorityLevels: Array<{
        name: string;
        value: number;
    }>;
}

export interface PerformanceConfig {
    maxMessageSize: number;
    compressionThreshold: number;
    batchSize: number;
    workerCount: number;
    bufferSize: number;
}

export interface LoggingConfig {
    level: string;
    file: string;
    maxSize: number;
    backupCount: number;
    format: string;
}

export interface MonitoringConfig {
    enabled: boolean;
    metricsInterval: number;
    alertThresholds: {
        latencyMs: number;
        errorRate: number;
        queueSize: number;
    };
    alertChannels: Array<{
        type: string;
        recipients?: string[];
        webhook?: string;
    }>;
}

export interface FeatureFlags {
    quantumEncryption: boolean;
    messageCompression: boolean;
    messageBatching: boolean;
    rateLimiting: boolean;
    monitoring: boolean;
    alerts: boolean;
}

export interface CustomConfig {
    debugMode: boolean;
    development: boolean;
    environment: string;
}

export interface Config {
    server: ServerConfig;
    security: SecurityConfig;
    messageQueue: MessageQueueConfig;
    performance: PerformanceConfig;
    logging: LoggingConfig;
    monitoring: MonitoringConfig;
    features: FeatureFlags;
    custom: CustomConfig;
}

export class ConfigManager {
    private static instance: ConfigManager;
    private config: Config;
    private configPath: string;

    private constructor() {
        this.configPath = path.resolve(__dirname, '../../../config/communication.yaml');
        this.config = this.loadConfig();
    }

    static getInstance(): ConfigManager {
        if (!ConfigManager.instance) {
            ConfigManager.instance = new ConfigManager();
        }
        return ConfigManager.instance;
    }

    private loadConfig(): Config {
        try {
            const fileContents = fs.readFileSync(this.configPath, 'utf8');
            return yaml.load(fileContents) as Config;
        } catch (error) {
            throw ErrorHandler.createError(
                `Failed to load configuration: ${error}`,
                ErrorSeverity.CRITICAL,
                'CONFIG_MANAGER'
            );
        }
    }

    get<T = any>(path: string): T {
        try {
            return this.getValueByPath(this.config, path);
        } catch (error) {
            throw ErrorHandler.createError(
                `Failed to get configuration value for path ${path}: ${error}`,
                ErrorSeverity.ERROR,
                'CONFIG_MANAGER'
            );
        }
    }

    set<T = any>(path: string, value: T): void {
        try {
            this.setValueByPath(this.config, path, value);
        } catch (error) {
            throw ErrorHandler.createError(
                `Failed to set configuration value for path ${path}: ${error}`,
                ErrorSeverity.ERROR,
                'CONFIG_MANAGER'
            );
        }
    }

    save(): void {
        try {
            const yamlStr = yaml.dump(this.config);
            fs.writeFileSync(this.configPath, yamlStr, 'utf8');
        } catch (error) {
            throw ErrorHandler.createError(
                `Failed to save configuration: ${error}`,
                ErrorSeverity.ERROR,
                'CONFIG_MANAGER'
            );
        }
    }

    reload(): void {
        try {
            this.config = this.loadConfig();
        } catch (error) {
            throw ErrorHandler.createError(
                `Failed to reload configuration: ${error}`,
                ErrorSeverity.ERROR,
                'CONFIG_MANAGER'
            );
        }
    }

    private getValueByPath(obj: any, path: string): any {
        return path.split('.').reduce((acc, part) => {
            if (acc === undefined) {
                throw new Error(`Invalid path: ${path}`);
            }
            return acc[part];
        }, obj);
    }

    private setValueByPath(obj: any, path: string, value: any): void {
        const parts = path.split('.');
        const lastPart = parts.pop()!;
        const target = parts.reduce((acc, part) => {
            if (!(part in acc)) {
                acc[part] = {};
            }
            return acc[part];
        }, obj);
        target[lastPart] = value;
    }

    getFullConfig(): Config {
        return { ...this.config };
    }
} 