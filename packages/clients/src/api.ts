/**
 * Senda API Client
 * Client for interacting with Senda FastAPI backend
 */

import type { ApiResponse, Conversation, User } from '@senda/shared-types';

export interface SendaApiConfig {
  baseUrl: string;
  apiKey?: string;
}

export class SendaApiClient {
  private config: SendaApiConfig;

  constructor(config: SendaApiConfig) {
    this.config = config;
  }

  private async fetch<T>(
    endpoint: string,
    options?: RequestInit
  ): Promise<ApiResponse<T>> {
    const url = `${this.config.baseUrl}${endpoint}`;
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...(this.config.apiKey && { Authorization: `Bearer ${this.config.apiKey}` }),
      ...options?.headers,
    };

    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (!response.ok) {
      throw new Error(`API request failed: ${response.statusText}`);
    }

    return response.json();
  }

  async getHealth(): Promise<ApiResponse<{ status: string }>> {
    return this.fetch('/health');
  }

  async getUser(userId: string): Promise<ApiResponse<User>> {
    return this.fetch(`/users/${userId}`);
  }

  async getConversations(): Promise<ApiResponse<Conversation[]>> {
    return this.fetch('/conversations');
  }

  async createConversation(data: Partial<Conversation>): Promise<ApiResponse<Conversation>> {
    return this.fetch('/conversations', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }
}
