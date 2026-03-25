import { useAuthStore } from '@/stores/auth-store';
import api from '@/lib/api';
import type { WSServerMessage, TokenResponse } from '@/types/api';

export type WSMessageHandler = (msg: WSServerMessage) => void;
export type WSBinaryHandler = (data: ArrayBuffer) => void;

interface WSOptions {
  onMessage: WSMessageHandler;
  onBinary?: WSBinaryHandler;
  onClose?: (code: number, reason: string) => void;
  onError?: (event: Event) => void;
}

export class WebSocketManager {
  private ws: WebSocket | null = null;
  private url: string;
  private options: WSOptions;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  private intentionallyClosed = false;
  private sessionEnded = false;

  constructor(url: string, options: WSOptions) {
    this.url = url;
    this.options = options;
  }

  connect(): void {
    this.intentionallyClosed = false;
    this._ensureFreshToken().then((token) => {
      if (!token) return;
      this._openSocket(token);
    });
  }

  private async _ensureFreshToken(): Promise<string | null> {
    const store = useAuthStore.getState();
    let token = store.accessToken;
    if (!token) return null;

    // Check if token expires within 60 seconds
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      const expiresAt = payload.exp * 1000;
      if (Date.now() > expiresAt - 60_000) {
        // Token expired or about to expire — refresh
        if (!store.refreshToken) return null;
        const { data } = await api.post<TokenResponse>(
          '/auth/refresh',
          null,
          { params: { refresh_token: store.refreshToken } },
        );
        store.setTokens(data.access_token, data.refresh_token);
        token = data.access_token;
      }
    } catch {
      // If decode fails, try connecting anyway
    }
    return token;
  }

  private _openSocket(token: string): void {

    const separator = this.url.includes('?') ? '&' : '?';
    const wsUrl = `${this.url}${separator}token=${token}`;

    // Build absolute WS URL
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const fullUrl = wsUrl.startsWith('ws') ? wsUrl : `${protocol}//${window.location.host}${wsUrl}`;

    this.ws = new WebSocket(fullUrl);
    this.ws.binaryType = 'arraybuffer';

    this.ws.onopen = () => {
      this.reconnectAttempts = 0;
    };

    this.ws.onmessage = (event) => {
      if (event.data instanceof ArrayBuffer) {
        this.options.onBinary?.(event.data);
      } else {
        try {
          const msg = JSON.parse(event.data) as WSServerMessage;
          this.options.onMessage(msg);
        } catch {
          // Ignore malformed messages
        }
      }
    };

    this.ws.onclose = (event) => {
      this.options.onClose?.(event.code, event.reason);
      // Don't reconnect if: intentionally closed, session ended, or server sent normal close (1000)
      if (this.intentionallyClosed || this.sessionEnded || event.code === 1000) return;
      if (this.reconnectAttempts < this.maxReconnectAttempts) {
        const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000);
        this.reconnectAttempts++;
        this.reconnectTimer = setTimeout(() => this.connect(), delay);
      }
    };

    this.ws.onerror = (event) => {
      this.options.onError?.(event);
    };
  }

  send(data: string | ArrayBuffer): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(data);
    }
  }

  sendJSON(msg: Record<string, unknown>): void {
    this.send(JSON.stringify(msg));
  }

  /** Mark session as ended — prevents any further reconnect attempts. */
  stopReconnect(): void {
    this.sessionEnded = true;
    this.intentionallyClosed = true;
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer);
  }

  close(): void {
    this.intentionallyClosed = true;
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer);
    this.ws?.close();
    this.ws = null;
  }

  get readyState(): number {
    return this.ws?.readyState ?? WebSocket.CLOSED;
  }
}
