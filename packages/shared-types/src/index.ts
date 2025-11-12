/**
 * Shared TypeScript types for Senda platform
 */

// Common types
export interface User {
  id: string;
  email: string;
  name: string;
  createdAt: Date;
}

export interface Conversation {
  id: string;
  userId: string;
  status: ConversationStatus;
  startedAt: Date;
  endedAt?: Date;
  messages: Message[];
}

export enum ConversationStatus {
  ACTIVE = 'active',
  COMPLETED = 'completed',
  FAILED = 'failed',
}

export interface Message {
  id: string;
  conversationId: string;
  content: string;
  sender: MessageSender;
  timestamp: Date;
}

export enum MessageSender {
  USER = 'user',
  AGENT = 'agent',
  SYSTEM = 'system',
}

// API Response types
export interface ApiResponse<T> {
  data: T;
  success: boolean;
  error?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
}
