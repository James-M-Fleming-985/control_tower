// Type declarations for analytics unified interface
export function initAnalytics(): void;
export function trackEvent(eventName: string, properties?: Record<string, any>): void;
export function trackPageView(path: string, title?: string): void;
export function identifyUser(userId: string, userProperties?: Record<string, any>): void;
export function trackPurchase(amount: number, productId?: string, properties?: Record<string, any>): void;
