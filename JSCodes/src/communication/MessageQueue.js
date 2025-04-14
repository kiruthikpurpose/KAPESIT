const { DateTime } = require('luxon');
const SecureProtocol = require('./SecureProtocol');
const { ErrorHandler, ErrorSeverity } = require('../utils/ErrorHandling');
const ConfigManager = require('../utils/ConfigManager');

class MessageQueue {
    constructor(maxRetries = 3, retryDelay = 5000) {
        this.secureProtocol = new SecureProtocol();
        this.queues = new Map();
        this.retryCounts = new Map();
        this.maxRetries = maxRetries;
        this.retryDelay = retryDelay;
        this.cleanupInterval = null;
        this.config = ConfigManager.getInstance();
    }

    async start() {
        this.cleanupInterval = setInterval(
            () => this.cleanupLoop(),
            3600000 // Run cleanup every hour
        );
    }

    async stop() {
        if (this.cleanupInterval) {
            clearInterval(this.cleanupInterval);
            this.cleanupInterval = null;
        }
    }

    async enqueue(sessionId, message, priority = 0) {
        try {
            if (!this.queues.has(sessionId)) {
                this.queues.set(sessionId, []);
            }

            const messageData = {
                message,
                timestamp: DateTime.utc(),
                priority,
                retryCount: 0
            };

            const queue = this.queues.get(sessionId);
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

    async dequeue(sessionId) {
        try {
            if (!this.queues.has(sessionId) || this.queues.get(sessionId).length === 0) {
                return null;
            }

            const queue = this.queues.get(sessionId);
            const messageData = queue.shift();
            return messageData.message;
        } catch (error) {
            throw ErrorHandler.createError(
                `Message dequeue failed: ${error}`,
                ErrorSeverity.ERROR,
                'MESSAGE_QUEUE'
            );
        }
    }

    async retryMessage(sessionId, message) {
        try {
            if (!this.retryCounts.has(sessionId)) {
                this.retryCounts.set(sessionId, 0);
            }

            const retryCount = this.retryCounts.get(sessionId);
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

    cleanupLoop() {
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

    getQueueSize(sessionId) {
        return this.queues.get(sessionId)?.length || 0;
    }

    getTotalMessages() {
        return Array.from(this.queues.values())
            .reduce((total, queue) => total + queue.length, 0);
    }
}

module.exports = MessageQueue; 