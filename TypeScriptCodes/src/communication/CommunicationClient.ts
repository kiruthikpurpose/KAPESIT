import WebSocket from 'ws';
import { Message, MessageType, Protocol } from './Protocol';
import { ErrorHandler, ErrorSeverity } from '../utils/ErrorHandling';
import { ConfigManager } from '../utils/ConfigManager';

type MessageHandler = (message: Message) => Promise<void>;

export class CommunicationClient {
    private host: string;
    private port: number;
    private websocket: WebSocket | null;
    private sessionId: string | null;
    private messageHandlers: Map<MessageType, MessageHandler>;
    private connected: boolean;
    private reconnectInterval: NodeJS.Timeout | null;
    private config: ConfigManager;

    constructor(host: string = 'localhost', port: number = 8765) {
        this.host = host;
        this.port = port;
        this.websocket = null;
        this.sessionId = null;
        this.messageHandlers = new Map();
        this.connected = false;
        this.reconnectInterval = null;
        this.config = ConfigManager.getInstance();
    }

    async connect(): Promise<void> {
        try {
            this.websocket = new WebSocket(`ws://${this.host}:${this.port}`);
            this.setupWebSocketHandlers();
            this.startReconnectLoop();
            await this.waitForConnection();
        } catch (error) {
            throw ErrorHandler.createError(
                `Connection failed: ${error}`,
                ErrorSeverity.ERROR,
                'COMMUNICATION_CLIENT'
            );
        }
    }

    async disconnect(): Promise<void> {
        try {
            if (this.reconnectInterval) {
                clearInterval(this.reconnectInterval);
                this.reconnectInterval = null;
            }
            if (this.websocket) {
                this.websocket.close();
            }
            this.connected = false;
        } catch (error) {
            throw ErrorHandler.createError(
                `Disconnection failed: ${error}`,
                ErrorSeverity.ERROR,
                'COMMUNICATION_CLIENT'
            );
        }
    }

    private setupWebSocketHandlers(): void {
        if (!this.websocket) return;

        this.websocket.on('open', () => {
            this.connected = true;
        });

        this.websocket.on('message', async (data: WebSocket.Data) => {
            try {
                await this.handleMessage(data.toString());
            } catch (error) {
                console.error('Message handling error:', error);
            }
        });

        this.websocket.on('close', () => {
            this.connected = false;
        });

        this.websocket.on('error', (error: Error) => {
            console.error('WebSocket error:', error);
            this.connected = false;
        });
    }

    private async handleMessage(message: string): Promise<void> {
        try {
            const data = JSON.parse(message);
            const msg = Message.fromJSON(data);

            if (msg.type === MessageType.KEY_EXCHANGE) {
                this.sessionId = msg.payload.sessionId;
            } else if (this.messageHandlers.has(msg.type)) {
                await this.messageHandlers.get(msg.type)!(msg);
            }
        } catch (error) {
            throw ErrorHandler.createError(
                `Message handling failed: ${error}`,
                ErrorSeverity.ERROR,
                'COMMUNICATION_CLIENT'
            );
        }
    }

    private startReconnectLoop(): void {
        this.reconnectInterval = setInterval(async () => {
            if (!this.connected) {
                try {
                    await this.connect();
                } catch (error) {
                    console.error('Reconnection attempt failed:', error);
                }
            }
        }, 5000);
    }

    private async waitForConnection(): Promise<void> {
        return new Promise((resolve, reject) => {
            if (!this.websocket) {
                reject(new Error('WebSocket not initialized'));
                return;
            }

            const timeout = setTimeout(() => {
                reject(new Error('Connection timeout'));
            }, 10000);

            this.websocket.once('open', () => {
                clearTimeout(timeout);
                resolve();
            });

            this.websocket.once('error', (error: Error) => {
                clearTimeout(timeout);
                reject(error);
            });
        });
    }

    registerHandler(messageType: MessageType, handler: MessageHandler): void {
        this.messageHandlers.set(messageType, handler);
    }

    async sendMessage(message: Message): Promise<void> {
        try {
            if (!this.connected || !this.websocket) {
                throw new Error('Not connected');
            }

            await new Promise<void>((resolve, reject) => {
                this.websocket!.send(JSON.stringify(message.toJSON()), (error: Error | undefined) => {
                    if (error) reject(error);
                    else resolve();
                });
            });
        } catch (error) {
            throw ErrorHandler.createError(
                `Message sending failed: ${error}`,
                ErrorSeverity.ERROR,
                'COMMUNICATION_CLIENT'
            );
        }
    }

    async sendCommand(command: string, args: any): Promise<void> {
        const message = Protocol.createCommand(command, args);
        await this.sendMessage(message);
    }

    async sendData(data: any, metadata?: any): Promise<void> {
        const message = Protocol.createData(data, metadata);
        await this.sendMessage(message);
    }

    async sendStream(data: any, streamId: string): Promise<void> {
        const message = Protocol.createStream(data, streamId);
        await this.sendMessage(message);
    }

    async sendControl(action: string, params: any): Promise<void> {
        const message = Protocol.createControl(action, params);
        await this.sendMessage(message);
    }

    async sendConfig(config: any): Promise<void> {
        const message = Protocol.createConfig(config);
        await this.sendMessage(message);
    }

    async authenticate(token: string): Promise<void> {
        const message = Protocol.createAuth(token);
        await this.sendMessage(message);
    }

    async exchangeKey(key: string): Promise<void> {
        const message = Protocol.createKeyExchange(key);
        await this.sendMessage(message);
    }
} 