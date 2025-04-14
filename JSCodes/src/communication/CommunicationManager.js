const Protocol = require('./Protocol');
const SecureProtocol = require('./SecureProtocol');
const RealtimeHandler = require('./RealtimeHandler');
const MessageQueue = require('./MessageQueue');
const { ErrorHandler, ErrorSeverity } = require('../utils/ErrorHandling');
const ConfigManager = require('../utils/ConfigManager');

class CommunicationManager {
    constructor() {
        this.config = ConfigManager.getInstance();
        this.secureProtocol = new SecureProtocol();
        this.messageQueue = new MessageQueue();
        this.realtimeHandler = new RealtimeHandler();
        this.messageHandlers = new Map();
        this.isRunning = false;
    }

    async start() {
        try {
            if (this.isRunning) {
                throw new Error('Communication manager is already running');
            }

            await this.messageQueue.start();
            await this.realtimeHandler.startServer(
                this.config.get('server.host'),
                this.config.get('server.port')
            );

            this.registerDefaultHandlers();
            this.isRunning = true;
        } catch (error) {
            throw ErrorHandler.createError(
                `Failed to start communication manager: ${error}`,
                ErrorSeverity.CRITICAL,
                'COMMUNICATION_MANAGER'
            );
        }
    }

    async stop() {
        try {
            if (!this.isRunning) {
                return;
            }

            await this.messageQueue.stop();
            await this.realtimeHandler.stop();
            this.messageHandlers.clear();
            this.isRunning = false;
        } catch (error) {
            throw ErrorHandler.createError(
                `Failed to stop communication manager: ${error}`,
                ErrorSeverity.ERROR,
                'COMMUNICATION_MANAGER'
            );
        }
    }

    registerHandler(messageType, handler) {
        try {
            if (typeof handler !== 'function') {
                throw new Error('Handler must be a function');
            }
            this.messageHandlers.set(messageType, handler);
            this.realtimeHandler.registerHandler(messageType, async (sessionId, message) => {
                try {
                    await handler(sessionId, message);
                } catch (error) {
                    await this.handleMessageError(sessionId, message, error);
                }
            });
        } catch (error) {
            throw ErrorHandler.createError(
                `Failed to register handler: ${error}`,
                ErrorSeverity.ERROR,
                'COMMUNICATION_MANAGER'
            );
        }
    }

    async sendMessage(sessionId, message, priority = 0) {
        try {
            const encryptedMessage = await this.secureProtocol.encryptMessage(sessionId, message);
            await this.messageQueue.enqueue(sessionId, encryptedMessage, priority);
            await this.processQueue(sessionId);
        } catch (error) {
            throw ErrorHandler.createError(
                `Failed to send message: ${error}`,
                ErrorSeverity.ERROR,
                'COMMUNICATION_MANAGER'
            );
        }
    }

    async broadcast(message, priority = 0) {
        try {
            await this.realtimeHandler.broadcast(message);
        } catch (error) {
            throw ErrorHandler.createError(
                `Failed to broadcast message: ${error}`,
                ErrorSeverity.ERROR,
                'COMMUNICATION_MANAGER'
            );
        }
    }

    async processQueue(sessionId) {
        try {
            while (this.messageQueue.getQueueSize(sessionId) > 0) {
                const message = await this.messageQueue.dequeue(sessionId);
                if (!message) break;

                try {
                    await this.realtimeHandler.sendMessage(sessionId, message);
                } catch (error) {
                    await this.messageQueue.retryMessage(sessionId, message);
                }
            }
        } catch (error) {
            throw ErrorHandler.createError(
                `Failed to process queue: ${error}`,
                ErrorSeverity.ERROR,
                'COMMUNICATION_MANAGER'
            );
        }
    }

    async handleMessageError(sessionId, message, error) {
        try {
            const errorMessage = Protocol.createErrorMessage({
                code: error.code || 'UNKNOWN_ERROR',
                message: error.message,
                severity: error.severity || ErrorSeverity.ERROR
            });
            await this.sendMessage(sessionId, errorMessage, 2); // High priority for error messages
        } catch (error) {
            throw ErrorHandler.createError(
                `Failed to handle message error: ${error}`,
                ErrorSeverity.ERROR,
                'COMMUNICATION_MANAGER'
            );
        }
    }

    registerDefaultHandlers() {
        // Handle heartbeat messages
        this.registerHandler(Protocol.MessageType.HEARTBEAT, async (sessionId, message) => {
            const response = Protocol.createHeartbeatMessage();
            await this.sendMessage(sessionId, response, 3); // Highest priority for heartbeat
        });

        // Handle error messages
        this.registerHandler(Protocol.MessageType.ERROR, async (sessionId, message) => {
            console.error(`Error from ${sessionId}:`, message.payload);
        });

        // Handle authentication messages
        this.registerHandler(Protocol.MessageType.AUTHENTICATION, async (sessionId, message) => {
            try {
                await this.secureProtocol.establishSecureChannel(sessionId);
                const response = Protocol.createAuthenticationMessage({ success: true });
                await this.sendMessage(sessionId, response, 2);
            } catch (error) {
                const response = Protocol.createAuthenticationMessage({ 
                    success: false, 
                    error: error.message 
                });
                await this.sendMessage(sessionId, response, 2);
            }
        });
    }

    getStats() {
        return {
            isRunning: this.isRunning,
            totalMessages: this.messageQueue.getTotalMessages(),
            activeHandlers: this.messageHandlers.size,
            connections: this.realtimeHandler.getConnectionCount()
        };
    }
}

module.exports = CommunicationManager; 