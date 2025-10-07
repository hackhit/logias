const http = require('http');
const server = require('../src/server');

const PORT = process.env.PORT || 3001;
const baseURL = `http://localhost:${PORT}`;

// Helper para realizar peticiones a la API
const api = (path) => {
  return new Promise((resolve, reject) => {
    http.get(`${baseURL}${path}`, (res) => {
      let data = '';
      res.on('data', (chunk) => (data += chunk));
      res.on('end', () => {
        try {
          const body = JSON.parse(data);
          resolve({ status: res.statusCode, body });
        } catch (err) {
          // Si el JSON es inválido, puede ser una respuesta de error no JSON
          resolve({ status: res.statusCode, body: data });
        }
      });
    }).on('error', reject);
  });
};

beforeAll((done) => {
  if (server.listening) {
    done();
  } else {
    server.on('listening', done);
  }
});

afterAll((done) => {
  server.close(done);
});

describe('API Endpoints', () => {
  describe('GET /', () => {
    it('should return API information', async () => {
      const res = await api('/');
      expect(res.status).toBe(200);
      expect(res.body).toHaveProperty('nombre', 'API Logias Venezuela');
      expect(res.body).toHaveProperty('version');
      expect(res.body).toHaveProperty('endpoints');
    });
  });

  describe('GET /health', () => {
    it('should return health status', async () => {
      const res = await api('/health');
      expect(res.status).toBe(200);
      expect(res.body).toHaveProperty('status', 'OK');
      expect(res.body).toHaveProperty('timestamp');
      expect(res.body).toHaveProperty('uptime');
    });
  });

  describe('GET /api/logias', () => {
    it('should return a list of logias with correct metadata', async () => {
      const res = await api('/api/logias');
      expect(res.status).toBe(200);
      expect(res.body.success).toBe(true);
      expect(Array.isArray(res.body.data)).toBe(true);
      expect(res.body.meta.total).toBeGreaterThan(0);
      expect(res.body.meta.count).toBe(res.body.data.length);
    });

    it('should filter logias by estado', async () => {
      const res = await api('/api/logias?estado=Caracas');
      expect(res.status).toBe(200);
      expect(res.body.success).toBe(true);
      res.body.data.forEach((logia) => {
        expect(logia.estado.toLowerCase()).toBe('caracas');
      });
    });

    it('should filter logias by oriente', async () => {
      const res = await api('/api/logias?oriente=Caracas');
      expect(res.status).toBe(200);
      expect(res.body.success).toBe(true);
      res.body.data.forEach((logia) => {
        expect(logia.oriente.toLowerCase()).toBe('caracas');
      });
    });

    it('should limit results', async () => {
      const res = await api('/api/logias?limit=5');
      expect(res.status).toBe(200);
      expect(res.body.success).toBe(true);
      expect(res.body.data.length).toBeLessThanOrEqual(5);
      expect(res.body.meta.limit).toBe(5);
    });

    it('should handle pagination with offset', async () => {
      const res1 = await api('/api/logias?limit=2&offset=0');
      const res2 = await api('/api/logias?limit=2&offset=2');
      expect(res1.body.data.length).toBe(2);
      expect(res2.body.data.length).toBe(2);
      expect(res1.body.data[0].numero).not.toBe(res2.body.data[0].numero);
    });

    it('should return an empty array for a non-existent filter', async () => {
      const res = await api('/api/logias?estado=Inexistente');
      expect(res.status).toBe(200);
      expect(res.body.success).toBe(true);
      expect(res.body.data).toEqual([]);
      expect(res.body.meta.count).toBe(0);
    });
  });

  describe('GET /api/logias/:numero', () => {
    it('should return a specific logia', async () => {
      const res = await api('/api/logias/1');
      expect(res.status).toBe(200);
      expect(res.body.success).toBe(true);
      expect(res.body.data).toHaveProperty('numero', 1);
    });

    it('should return 404 for a non-existent logia', async () => {
      const res = await api('/api/logias/9999');
      expect(res.status).toBe(404);
      expect(res.body.success).toBe(false);
      expect(res.body.message).toContain('no encontrada');
    });

    it('should handle non-numeric numero gracefully', async () => {
      const res = await api('/api/logias/invalid');
      expect(res.status).toBe(404);
    });
  });

  describe('GET /api/estadisticas', () => {
    it('should return general statistics', async () => {
      const res = await api('/api/estadisticas');
      expect(res.status).toBe(200);
      expect(res.body.success).toBe(true);
      expect(res.body.data).toHaveProperty('total_logias');
      expect(res.body.data).toHaveProperty('total_estados');
      expect(res.body.data).toHaveProperty('total_orientes');
      expect(res.body.data).toHaveProperty('estados');
      expect(res.body.data).toHaveProperty('orientes');
    });
  });

  describe('GET /api/estadisticas/por-estado', () => {
    it('should return statistics by state', async () => {
      const res = await api('/api/estadisticas/por-estado');
      expect(res.status).toBe(200);
      expect(res.body.success).toBe(true);
      expect(Array.isArray(res.body.data)).toBe(true);
      if (res.body.data.length > 0) {
        const firstState = res.body.data[0];
        expect(firstState).toHaveProperty('estado');
        expect(firstState).toHaveProperty('cantidad');
        expect(firstState).toHaveProperty('logias');
        expect(Array.isArray(firstState.logias)).toBe(true);
      }
    });
  });

  describe('Error Handling', () => {
    it('should return 404 for an unknown route', async () => {
      const res = await api('/api/nonexistent-route');
      expect(res.status).toBe(404);
      expect(res.body.success).toBe(false);
      expect(res.body.message).toBe('Endpoint no encontrado');
    });
  });
});