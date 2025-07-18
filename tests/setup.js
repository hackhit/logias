/**
 * Configuración global para los tests
 */

// Configurar timeout para tests
jest.setTimeout(10000);

// Mock de console para tests
global.console = {
  ...console,
  // Silenciar logs durante tests
  log: jest.fn(),
  debug: jest.fn(),
  info: jest.fn(),
  warn: jest.fn(),
  error: jest.fn()
};

// Variables de entorno para tests
process.env.NODE_ENV = 'test';
process.env.PORT = 3001;