import { DateTime } from 'luxon';

export enum MessageType {
    // System messages
    HEARTBEAT = 'heartbeat',
    ERROR = 'error',
    STATUS = 'status',
    
    // Command messages
    COMMAND = 'command',
    RESPONSE = 'response',
    
    // Data messages
    DATA = 'data',
    STREAM = 'stream',
    
    // Control messages
    CONTROL = 'control',
    CONFIG = 'config',
    
    // Security messages
    AUTH = 'auth',
    KEY_EXCHANGE = 'key_exchange'
}

export interface MessageMetadata {
    [key: string]: any;
}

export interface MessagePayload {
    [key: string]: any;
}

export class Message {
    type: MessageType;
    payload: MessagePayload;
    timestamp: DateTime;
    priority: number;
    metadata?: MessageMetadata;

    constructor(
        type: MessageType,
        payload: MessagePayload,
        priority: number = 0,
        metadata?: MessageMetadata
    ) {
        this.type = type;
        this.payload = payload;
        this.timestamp = DateTime.utc();
        this.priority = priority;
        this.metadata = metadata;
    }

    toJSON(): any {
        return {
            type: this.type,
            payload: this.payload,
            timestamp: this.timestamp.toISO(),
            priority: this.priority,
            metadata: this.metadata || {}
        };
    }

    static fromJSON(data: any): Message {
        const message = new Message(
            data.type as MessageType,
            data.payload,
            data.priority,
            data.metadata
        );
        message.timestamp = DateTime.fromISO(data.timestamp);
        return message;
    }
}

export class Protocol {
    static createHeartbeat(): Message {
        return new Message(
            MessageType.HEARTBEAT,
            { status: 'alive' }
        );
    }

    static createError(error: string, code: number): Message {
        return new Message(
            MessageType.ERROR,
            { error, code },
            1
        );
    }

    static createCommand(command: string, args: any): Message {
        return new Message(
            MessageType.COMMAND,
            { command, args }
        );
    }

    static createResponse(command: string, result: any): Message {
        return new Message(
            MessageType.RESPONSE,
            { command, result }
        );
    }

    static createData(data: any, metadata?: MessageMetadata): Message {
        return new Message(
            MessageType.DATA,
            data,
            0,
            metadata
        );
    }

    static createStream(data: any, streamId: string): Message {
        return new Message(
            MessageType.STREAM,
            { streamId, data }
        );
    }

    static createControl(action: string, params: any): Message {
        return new Message(
            MessageType.CONTROL,
            { action, params }
        );
    }

    static createConfig(config: any): Message {
        return new Message(
            MessageType.CONFIG,
            config
        );
    }

    static createAuth(token: string): Message {
        return new Message(
            MessageType.AUTH,
            { token }
        );
    }

    static createKeyExchange(key: string): Message {
        return new Message(
            MessageType.KEY_EXCHANGE,
            { key }
        );
    }
} 