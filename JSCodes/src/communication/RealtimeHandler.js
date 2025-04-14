const WebSocket = require('ws');
const SecureProtocol = require('./SecureProtocol');
const { ErrorHandler, ErrorSeverity } = require('../utils/ErrorHandling');
const ConfigManager = require('../utils/ConfigManager');

class RealtimeHandler {
    constructor() {
        this.secureProtocol = new SecureProtocol();
        this.connections = new Map();
        this.messageHandlers = new Map();
        this.heartbeatInterval = null;
        this.config = ConfigManager.getInstance();
    }

    async startServer(host = 'localhost', port = 8765) {
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

    async handleConnection(websocket) {
        try {
            const sessionId = await this.secureProtocol.establishSecureChannel(websocket);
            this.connections.set(sessionId, websocket);

            websocket.on('message', async (message) => {
                await this.processMessage(sessionId, message);
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

    async processMessage(sessionId, message) {
        try {
            const decrypted = await this.secureProtocol.decryptMessage(sessionId, message);
            const messageType = decrypted.type;

            if (this.messageHandlers.has(messageType)) {
                const handlers = this.messageHandlers.get(messageType);
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

    handleDisconnection(sessionId) {
        if (this.connections.has(sessionId)) {
            this.connections.delete(sessionId);
        }
        this.secureProtocol.closeSession(sessionId);
    }

    startHeartbeat() {
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

    async sendPing(websocket) {
        return new Promise((resolve, reject) => {
            websocket.ping((error) => {
                if (error) reject(error);
                else resolve();
            });
        });
    }

    registerHandler(messageType, handler) {
        if (!this.messageHandlers.has(messageType)) {
            this.messageHandlers.set(messageType, new Set());
        }
        this.messageHandlers.get(messageType).add(handler);
    }

    async broadcast(message) {
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

    stop() {
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

module.exports = RealtimeHandler; 