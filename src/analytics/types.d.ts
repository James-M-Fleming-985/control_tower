/**
 * TypeScript declarations for analytics window globals
 */

interface GAFunction {
  (command: 'config', targetId: string, config?: any): void;
  (command: 'event', eventName: string, eventParams?: any): void;
  (command: 'set', fieldsObject: any): void;
  (command: 'get', targetId: string, fieldName: string, callback?: (value: any) => void): void;
  (command: string, ...args: any[]): void;
}

interface MixpanelPeople {
  set(properties: Record<string, any>): void;
  set_once(properties: Record<string, any>): void;
  increment(property: string, by?: number): void;
  track_charge(amount: number, properties?: Record<string, any>): void;
}

interface Mixpanel {
  init(token: string, config?: any): void;
  track(eventName: string, properties?: Record<string, any>): void;
  identify(userId: string): void;
  alias(alias: string): void;
  people: MixpanelPeople;
  register(properties: Record<string, any>): void;
  reset(): void;
}

interface AmplitudeIdentify {
  set(property: string, value: any): this;
  setOnce(property: string, value: any): this;
  add(property: string, value: number): this;
  append(property: string, value: any): this;
}

interface AmplitudeRevenue {
  setPrice(price: number): this;
  setQuantity(quantity: number): this;
  setProductId(productId: string): this;
  setRevenueType(revenueType: string): this;
}

interface Amplitude {
  init(apiKey: string, userId?: string | null, options?: any): void;
  track(eventName: string, eventProperties?: Record<string, any>): void;
  setUserId(userId: string | null): void;
  identify(identify: AmplitudeIdentify): void;
  revenue(revenue: AmplitudeRevenue): void;
  Identify: new () => AmplitudeIdentify;
  Revenue: new () => AmplitudeRevenue;
}

declare global {
  interface Window {
    gtag: GAFunction;
    dataLayer: any[];
    GA4_MEASUREMENT_ID: string;
    mixpanel: Mixpanel;
    amplitude: Amplitude;
  }
}

// Analytics module declarations
declare module './ga4-config' {
  export function initGA4(): void;
  export function trackGA4Event(eventName: string, eventParams?: Record<string, any>): void;
  export function trackGA4PageView(path: string, title?: string): void;
  export function identifyGA4User(userId: string, userProperties?: Record<string, any>): void;
  export function trackGA4Purchase(transactionId: string, value: number, currency?: string, items?: any[]): void;
}

declare module './mixpanel-config' {
  export function initMixpanel(): void;
  export function trackMixpanelEvent(eventName: string, properties?: Record<string, any>): void;
  export function identifyMixpanelUser(userId: string, userProperties?: Record<string, any>): void;
  export function trackMixpanelPurchase(amount: number, properties?: Record<string, any>): void;
}

declare module './amplitude-config' {
  export function initAmplitude(): void;
  export function trackAmplitudeEvent(eventName: string, eventProperties?: Record<string, any>): void;
  export function identifyAmplitudeUser(userId: string, userProperties?: Record<string, any>): void;
  export function trackAmplitudePurchase(revenue: number, properties?: Record<string, any>): void;
}

declare module './index' {
  export function initAnalytics(): void;
  export function trackEvent(eventName: string, properties?: Record<string, any>): void;
  export function trackPageView(path: string, title?: string): void;
  export function identifyUser(userId: string, userProperties?: Record<string, any>): void;
  export function trackPurchase(amount: number, productId?: string, properties?: Record<string, any>): void;
}

export {};
