import WebSocket from 'ws';
import { RealtimeHandler } from './RealtimeHandler';
import { MessageQueue } from './MessageQueue';
import { SecureProtocol } from './SecureProtocol';
import { Message } from './Protocol';
import { ErrorHandler, ErrorSeverity } from '../utils/ErrorHandling';
import { ConfigManager } from '../utils/ConfigManager';

type MessageHandler = (sessionId: string, message: Message) => Promise<void>;

export class CommunicationManager {
    private realtimeHandler: RealtimeHandler;
    private messageQueue: MessageQueue;
    private secureProtocol: SecureProtocol;
    private messageHandlers: Map<string, MessageHandler>;
    private config: ConfigManager;

    constructor() {
        this.realtimeHandler = new RealtimeHandler();
        this.messageQueue = new MessageQueue();
        this.secureProtocol = new SecureProtocol();
        this.messageHandlers = new Map();
        this.config = ConfigManager.getInstance();
    }

    async start(host: string = 'localhost', port: number = 8765): Promise<WebSocket.Server> {
        try {
            // Start realtime server
            const server = await this.realtimeHandler.startServer(host, port);

            // Start message queue
            await this.messageQueue.start();

            // Register default handlers
            this.registerDefaultHandlers();

            return server;
        } catch (error) {
            throw ErrorHandler.createError(
                `Failed to start communication manager: ${error}`,
                ErrorSeverity.ERROR,
                'COMMUNICATION_MANAGER'
            );
        }
    }

    async stop(): Promise<void> {
        try {
            await this.messageQueue.stop();
            this.realtimeHandler.stop();
        } catch (error) {
            throw ErrorHandler.createError(
                `Failed to stop communication manager: ${error}`,
                ErrorSeverity.ERROR,
                'COMMUNICATION_MANAGER'
            );
        }
    }

    private registerDefaultHandlers(): void {
        this.realtimeHandler.registerHandler('message', this.handleRealtimeMessage.bind(this));
        this.realtimeHandler.registerHandler('queue', this.handleQueueMessage.bind(this));
    }

    private async handleRealtimeMessage(sessionId: string, message: Message): Promise<void> {
        try {
            if (message.type && this.messageHandlers.has(message.type)) {
                await this.messageHandlers.get(message.type)!(sessionId, message);
            }
        } catch (error) {
            throw ErrorHandler.createError(
                `Realtime message handling failed: ${error}`,
                ErrorSeverity.ERROR,
                'COMMUNICATION_MANAGER'
            );
        }
    }

    private async handleQueueMessage(sessionId: string, message: Message): Promise<void> {
        try {
            await this.messageQueue.enqueue(sessionId, message);
        } catch (error) {
            throw ErrorHandler.createError(
                `Queue message handling failed: ${error}`,
                ErrorSeverity.ERROR,
                'COMMUNICATION_MANAGER'
            );
        }
    }

    registerHandler(messageType: string, handler: MessageHandler): void {
        this.messageHandlers.set(messageType, handler);
    }

    async sendMessage(sessionId: string, message: Message, priority: number = 0): Promise<void> {
        try {
            const connections = this.realtimeHandler['connections'] as Map<string, WebSocket>;
            if (connections.has(sessionId)) {
                await this.realtimeHandler.broadcast(message);
            } else {
                await this.messageQueue.enqueue(sessionId, message, priority);
            }
        } catch (error) {
            throw ErrorHandler.createError(
                `Message sending failed: ${error}`,
                ErrorSeverity.ERROR,
                'COMMUNICATION_MANAGER'
            );
        }
    }

    async processQueuedMessages(): Promise<void> {
        try {
            const queues = this.messageQueue['queues'] as Map<string, any[]>;
            for (const sessionId of queues.keys()) {
                let message: Message | null;
                while ((message = await this.messageQueue.dequeue(sessionId)) !== null) {
                    if (message.type && this.messageHandlers.has(message.type)) {
                        await this.messageHandlers.get(message.type)!(sessionId, message);
                    }
                }
            }
        } catch (error) {
            throw ErrorHandler.createError(
                `Queued message processing failed: ${error}`,
                ErrorSeverity.ERROR,
                'COMMUNICATION_MANAGER'
            );
        }
    }

    getConnectionStats(): Record<string, any> {
        return {
            activeConnections: (this.realtimeHandler['connections'] as Map<string, WebSocket>).size,
            queuedMessages: this.messageQueue.getTotalMessages(),
            messageTypes: Array.from(this.messageHandlers.keys())
        };
    }
} 