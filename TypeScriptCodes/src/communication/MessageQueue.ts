import { DateTime } from 'luxon';
import { Message } from './Protocol';
import { SecureProtocol } from './SecureProtocol';
import { ErrorHandler, ErrorSeverity } from '../utils/ErrorHandling';
import { ConfigManager } from '../utils/ConfigManager';

interface QueuedMessage {
    message: Message;
    timestamp: DateTime;
    priority: number;
    retryCount: number;
}

export class MessageQueue {
    private secureProtocol: SecureProtocol;
    private queues: Map<string, QueuedMessage[]>;
    private retryCounts: Map<string, number>;
    private maxRetries: number;
    private retryDelay: number;
    private cleanupInterval: NodeJS.Timeout | null;
    private config: ConfigManager;

    constructor(maxRetries: number = 3, retryDelay: number = 5000) {
        this.secureProtocol = new SecureProtocol();
        this.queues = new Map();
        this.retryCounts = new Map();
        this.maxRetries = maxRetries;
        this.retryDelay = retryDelay;
        this.cleanupInterval = null;
        this.config = ConfigManager.getInstance();
    }

    async start(): Promise<void> {
        this.cleanupInterval = setInterval(
            () => this.cleanupLoop(),
            3600000 // Run cleanup every hour
        );
    }

    async stop(): Promise<void> {
        if (this.cleanupInterval) {
            clearInterval(this.cleanupInterval);
            this.cleanupInterval = null;
        }
    }

    async enqueue(sessionId: string, message: Message, priority: number = 0): Promise<void> {
        try {
            if (!this.queues.has(sessionId)) {
                this.queues.set(sessionId, []);
            }

            const messageData: QueuedMessage = {
                message,
                timestamp: DateTime.utc(),
                priority,
                retryCount: 0
            };

            const queue = this.queues.get(sessionId)!;
            let insertIndex = 0;

            // Insert based on priority
            for (let i = 0; i < queue.length; i++) {
                if (queue[i].priority < priority) {
                    insertIndex = i;
                    break;
                }
                insertIndex = i + 1;
            }

            queue.splice(insertIndex, 0, messageData);
        } catch (error) {
            throw ErrorHandler.createError(
                `Message enqueue failed: ${error}`,
                ErrorSeverity.ERROR,
                'MESSAGE_QUEUE'
            );
        }
    }

    async dequeue(sessionId: string): Promise<Message | null> {
        try {
            if (!this.queues.has(sessionId) || this.queues.get(sessionId)!.length === 0) {
                return null;
            }

            const queue = this.queues.get(sessionId)!;
            const messageData = queue.shift()!;
            return messageData.message;
        } catch (error) {
            throw ErrorHandler.createError(
                `Message dequeue failed: ${error}`,
                ErrorSeverity.ERROR,
                'MESSAGE_QUEUE'
            );
        }
    }

    async retryMessage(sessionId: string, message: Message): Promise<void> {
        try {
            if (!this.retryCounts.has(sessionId)) {
                this.retryCounts.set(sessionId, 0);
            }

            const retryCount = this.retryCounts.get(sessionId)!;
            if (retryCount < this.maxRetries) {
                this.retryCounts.set(sessionId, retryCount + 1);
                await this.enqueue(sessionId, message, 1); // Higher priority for retries
                await new Promise(resolve => setTimeout(resolve, this.retryDelay));
            } else {
                this.retryCounts.set(sessionId, 0);
            }
        } catch (error) {
            throw ErrorHandler.createError(
                `Message retry failed: ${error}`,
                ErrorSeverity.ERROR,
                'MESSAGE_QUEUE'
            );
        }
    }

    private cleanupLoop(): void {
        try {
            const currentTime = DateTime.utc();
            for (const [sessionId, queue] of this.queues.entries()) {
                // Remove messages older than 24 hours
                const filteredQueue = queue.filter(msg => 
                    currentTime.diff(msg.timestamp, 'hours').hours < 24
                );

                if (filteredQueue.length === 0) {
                    this.queues.delete(sessionId);
                    this.retryCounts.delete(sessionId);
                } else {
                    this.queues.set(sessionId, filteredQueue);
                }
            }
        } catch (error) {
            throw ErrorHandler.createError(
                `Cleanup loop failed: ${error}`,
                ErrorSeverity.ERROR,
                'MESSAGE_QUEUE'
            );
        }
    }

    getQueueSize(sessionId: string): number {
        return this.queues.get(sessionId)?.length || 0;
    }

    getTotalMessages(): number {
        return Array.from(this.queues.values())
            .reduce((total, queue) => total + queue.length, 0);
    }
} 