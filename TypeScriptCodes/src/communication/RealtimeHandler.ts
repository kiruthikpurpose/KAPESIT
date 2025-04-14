import WebSocket from 'ws';
import { SecureProtocol } from './SecureProtocol';
import { Message } from './Protocol';
import { ErrorHandler, ErrorSeverity } from '../utils/ErrorHandling';
import { ConfigManager } from '../utils/ConfigManager';

type MessageHandler = (sessionId: string, message: Message) => Promise<void>;

export class RealtimeHandler {
    private secureProtocol: SecureProtocol;
    private connections: Map<string, WebSocket>;
    private messageHandlers: Map<string, Set<MessageHandler>>;
    private heartbeatInterval: NodeJS.Timeout | null;
    private config: ConfigManager;

    constructor() {
        this.secureProtocol = new SecureProtocol();
        this.connections = new Map();
        this.messageHandlers = new Map();
        this.heartbeatInterval = null;
        this.config = ConfigManager.getInstance();
    }

    async startServer(host: string = 'localhost', port: number = 8765): Promise<WebSocket.Server> {
        try {
            const server = new WebSocket.Server({ host, port });
            this.startHeartbeat();

            server.on('connection', this.handleConnection.bind(this));
            return server;
        } catch (error) {
            throw ErrorHandler.createError(
                `Failed to start realtime server: ${error}`,
                ErrorSeverity.ERROR,
                'REALTIME_HANDLER'
            );
        }
    }

    private async handleConnection(websocket: WebSocket): Promise<void> {
        try {
            const sessionId = await this.secureProtocol.establishSecureChannel(websocket);
            this.connections.set(sessionId, websocket);

            websocket.on('message', async (message: WebSocket.Data) => {
                await this.processMessage(sessionId, message as Buffer);
            });

            websocket.on('close', () => {
                this.handleDisconnection(sessionId);
            });
        } catch (error) {
            throw ErrorHandler.createError(
                `Connection handling failed: ${error}`,
                ErrorSeverity.ERROR,
                'REALTIME_HANDLER'
            );
        }
    }

    private async processMessage(sessionId: string, message: Buffer): Promise<void> {
        try {
            const decrypted = await this.secureProtocol.decryptMessage(sessionId, message);
            const messageType = decrypted.type;

            if (this.messageHandlers.has(messageType)) {
                const handlers = this.messageHandlers.get(messageType)!;
                for (const handler of handlers) {
                    await handler(sessionId, decrypted);
                }
            }
        } catch (error) {
            throw ErrorHandler.createError(
                `Message processing failed: ${error}`,
                ErrorSeverity.ERROR,
                'REALTIME_HANDLER'
            );
        }
    }

    private handleDisconnection(sessionId: string): void {
        if (this.connections.has(sessionId)) {
            this.connections.delete(sessionId);
        }
        this.secureProtocol.closeSession(sessionId);
    }

    private startHeartbeat(): void {
        this.heartbeatInterval = setInterval(async () => {
            try {
                for (const [sessionId, websocket] of this.connections) {
                    try {
                        if (websocket.readyState === WebSocket.OPEN) {
                            await this.sendPing(websocket);
                        } else {
                            this.handleDisconnection(sessionId);
                        }
                    } catch {
                        this.handleDisconnection(sessionId);
                    }
                }
            } catch (error) {
                throw ErrorHandler.createError(
                    `Heartbeat failed: ${error}`,
                    ErrorSeverity.ERROR,
                    'REALTIME_HANDLER'
                );
            }
        }, 30000); // 30 seconds interval
    }

    private async sendPing(websocket: WebSocket): Promise<void> {
        return new Promise((resolve, reject) => {
            websocket.ping((error) => {
                if (error) reject(error);
                else resolve();
            });
        });
    }

    registerHandler(messageType: string, handler: MessageHandler): void {
        if (!this.messageHandlers.has(messageType)) {
            this.messageHandlers.set(messageType, new Set());
        }
        this.messageHandlers.get(messageType)!.add(handler);
    }

    async broadcast(message: Message): Promise<void> {
        try {
            const promises = Array.from(this.connections.entries()).map(
                async ([sessionId, websocket]) => {
                    if (websocket.readyState === WebSocket.OPEN) {
                        const encrypted = await this.secureProtocol.encryptMessage(sessionId, message);
                        websocket.send(encrypted);
                    }
                }
            );
            await Promise.all(promises);
        } catch (error) {
            throw ErrorHandler.createError(
                `Broadcast failed: ${error}`,
                ErrorSeverity.ERROR,
                'REALTIME_HANDLER'
            );
        }
    }

    stop(): void {
        if (this.heartbeatInterval) {
            clearInterval(this.heartbeatInterval);
            this.heartbeatInterval = null;
        }

        for (const [sessionId, websocket] of this.connections) {
            websocket.close();
            this.handleDisconnection(sessionId);
        }
    }
} 