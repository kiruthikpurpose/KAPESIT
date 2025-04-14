const { DateTime } = require('luxon');

const MessageType = {
    // System messages
    HEARTBEAT: 'heartbeat',
    ERROR: 'error',
    STATUS: 'status',
    
    // Command messages
    COMMAND: 'command',
    RESPONSE: 'response',
    
    // Data messages
    DATA: 'data',
    STREAM: 'stream',
    
    // Control messages
    CONTROL: 'control',
    CONFIG: 'config',
    
    // Security messages
    AUTH: 'auth',
    KEY_EXCHANGE: 'key_exchange'
};

class Message {
    constructor(type, payload, priority = 0, metadata = {}) {
        this.type = type;
        this.payload = payload;
        this.timestamp = DateTime.utc();
        this.priority = priority;
        this.metadata = metadata;
    }

    toJSON() {
        return {
            type: this.type,
            payload: this.payload,
            timestamp: this.timestamp.toISO(),
            priority: this.priority,
            metadata: this.metadata
        };
    }

    static fromJSON(data) {
        const message = new Message(
            data.type,
            data.payload,
            data.priority,
            data.metadata
        );
        message.timestamp = DateTime.fromISO(data.timestamp);
        return message;
    }
}

class Protocol {
    static createHeartbeat() {
        return new Message(
            MessageType.HEARTBEAT,
            { status: 'alive' }
        );
    }

    static createError(error, code) {
        return new Message(
            MessageType.ERROR,
            { error, code },
            1
        );
    }

    static createCommand(command, args) {
        return new Message(
            MessageType.COMMAND,
            { command, args }
        );
    }

    static createResponse(command, result) {
        return new Message(
            MessageType.RESPONSE,
            { command, result }
        );
    }

    static createData(data, metadata) {
        return new Message(
            MessageType.DATA,
            data,
            0,
            metadata
        );
    }

    static createStream(data, streamId) {
        return new Message(
            MessageType.STREAM,
            { streamId, data }
        );
    }

    static createControl(action, params) {
        return new Message(
            MessageType.CONTROL,
            { action, params }
        );
    }

    static createConfig(config) {
        return new Message(
            MessageType.CONFIG,
            config
        );
    }

    static createAuth(token) {
        return new Message(
            MessageType.AUTH,
            { token }
        );
    }

    static createKeyExchange(key) {
        return new Message(
            MessageType.KEY_EXCHANGE,
            { key }
        );
    }
}

module.exports = {
    MessageType,
    Message,
    Protocol
}; 