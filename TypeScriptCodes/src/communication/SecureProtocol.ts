import WebSocket from 'ws';
import { QuantumEncryption } from './QuantumEncryption';
import { ErrorHandler, ErrorSeverity } from '../utils/ErrorHandling';
import { ConfigManager } from '../utils/ConfigManager';
import { Message } from './Protocol';

export class SecureProtocol {
    private quantumEnc: QuantumEncryption;
    private sessionKeys: Map<string, CryptoKey>;
    private encryptionKeys: Map<string, CryptoKey>;
    private config: ConfigManager;

    constructor() {
        this.quantumEnc = new QuantumEncryption();
        this.sessionKeys = new Map();
        this.encryptionKeys = new Map();
        this.config = ConfigManager.getInstance();
    }

    async establishSecureChannel(websocket: WebSocket): Promise<string> {
        try {
            // Generate quantum key
            const quantumKey = await this.quantumEnc.generateQuantumKey();

            // Generate session key
            const sessionKey = await this.generateSessionKey();
            const encryptionKey = await this.deriveEncryptionKey(sessionKey);

            // Encrypt session key with quantum key
            const encryptedKey = await this.quantumEnc.encryptMessage(
                this.arrayBufferToBase64(await crypto.subtle.exportKey('raw', sessionKey)),
                quantumKey
            );

            // Send encrypted session key
            websocket.send(JSON.stringify({
                type: 'key_exchange',
                key: this.arrayBufferToBase64(encryptedKey)
            }));

            // Store session information
            const sessionId = this.generateSessionId();
            this.sessionKeys.set(sessionId, sessionKey);
            this.encryptionKeys.set(sessionId, encryptionKey);

            return sessionId;
        } catch (error) {
            throw ErrorHandler.createError(
                `Secure channel establishment failed: ${error}`,
                ErrorSeverity.ERROR,
                'SECURE_PROTOCOL'
            );
        }
    }

    async encryptMessage(sessionId: string, message: Message): Promise<ArrayBuffer> {
        try {
            const key = this.encryptionKeys.get(sessionId);
            if (!key) {
                throw new Error('Invalid session ID');
            }

            const data = new TextEncoder().encode(JSON.stringify(message.toJSON()));
            const iv = crypto.getRandomValues(new Uint8Array(12));
            const encrypted = await crypto.subtle.encrypt(
                { name: 'AES-GCM', iv },
                key,
                data
            );

            // Combine IV and encrypted data
            const result = new Uint8Array(iv.length + encrypted.byteLength);
            result.set(iv);
            result.set(new Uint8Array(encrypted), iv.length);

            return result.buffer;
        } catch (error) {
            throw ErrorHandler.createError(
                `Message encryption failed: ${error}`,
                ErrorSeverity.ERROR,
                'SECURE_PROTOCOL'
            );
        }
    }

    async decryptMessage(sessionId: string, encrypted: ArrayBuffer): Promise<Message> {
        try {
            const key = this.encryptionKeys.get(sessionId);
            if (!key) {
                throw new Error('Invalid session ID');
            }

            // Extract IV and encrypted data
            const data = new Uint8Array(encrypted);
            const iv = data.slice(0, 12);
            const encryptedData = data.slice(12);

            const decrypted = await crypto.subtle.decrypt(
                { name: 'AES-GCM', iv },
                key,
                encryptedData
            );

            const messageData = JSON.parse(new TextDecoder().decode(decrypted));
            return Message.fromJSON(messageData);
        } catch (error) {
            throw ErrorHandler.createError(
                `Message decryption failed: ${error}`,
                ErrorSeverity.ERROR,
                'SECURE_PROTOCOL'
            );
        }
    }

    closeSession(sessionId: string): void {
        this.sessionKeys.delete(sessionId);
        this.encryptionKeys.delete(sessionId);
    }

    private async generateSessionKey(): Promise<CryptoKey> {
        return await crypto.subtle.generateKey(
            { name: 'AES-GCM', length: 256 },
            true,
            ['encrypt', 'decrypt']
        );
    }

    private async deriveEncryptionKey(sessionKey: CryptoKey): Promise<CryptoKey> {
        const salt = crypto.getRandomValues(new Uint8Array(16));
        return await crypto.subtle.deriveKey(
            {
                name: 'PBKDF2',
                salt,
                iterations: 100000,
                hash: 'SHA-256'
            },
            sessionKey,
            { name: 'AES-GCM', length: 256 },
            true,
            ['encrypt', 'decrypt']
        );
    }

    private generateSessionId(): string {
        return crypto.randomUUID();
    }

    private arrayBufferToBase64(buffer: ArrayBuffer): string {
        return Buffer.from(buffer).toString('base64');
    }

    private base64ToArrayBuffer(base64: string): ArrayBuffer {
        return Buffer.from(base64, 'base64');
    }
} 