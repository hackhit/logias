/**
 * Tests para la API
 */

const http = require('http');
process.env.PORT = process.env.PORT || 3001;
const server = require('../src/server');
const baseURL = `http://localhost:${process.env.PORT}`;

delete process.env.http_proxy;
delete process.env.HTTP_PROXY;

const api = (path) => {
    return new Promise((resolve, reject) => {
        http.get(`${baseURL}${path}`, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => {
                try {
                    const body = JSON.parse(data);
                    resolve({ status: res.statusCode, body });
                } catch (err) {
                    reject(err);
                }
            });
        }).on('error', reject);
    });
};

beforeAll(async () => {
    if (!server.listening) {
        await new Promise(resolve => server.on('listening', resolve));
    }
});

afterAll(() => {
    server.close();
});

describe('API Endpoints', () => {
    describe('GET /', () => {
        it('should return API information', async () => {
            const res = await api('/');
            expect(res.status).toBe(200);
            expect(res.body).toHaveProperty('nombre');
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
        it('should return logias list', async () => {
            const res = await api('/api/logias');
            expect(res.status).toBe(200);
            expect(res.body).toHaveProperty('success', true);
            expect(res.body).toHaveProperty('data');
            expect(Array.isArray(res.body.data)).toBe(true);
            expect(res.body).toHaveProperty('meta');
        });

        it('should filter logias by estado', async () => {
            const res = await api('/api/logias?estado=Caracas');
            expect(res.status).toBe(200);
            expect(res.body.success).toBe(true);
            if (res.body.data.length > 0) {
                res.body.data.forEach(logia => {
                    expect(logia.estado).toBe('Caracas');
                });
            }
        });

        it('should limit results', async () => {
            const res = await api('/api/logias?limit=5');
            expect(res.status).toBe(200);
            expect(res.body.success).toBe(true);
            expect(res.body.data.length).toBeLessThanOrEqual(5);
            expect(res.body.meta.limit).toBe(5);
        });
    });

    describe('GET /api/logias/:numero', () => {
        it('should return specific logia', async () => {
            const list = await api('/api/logias');
            if (list.body.data.length === 0) {
                return;
            }
            const numero = list.body.data[0].numero;
            const res = await api(`/api/logias/${numero}`);
            expect(res.status).toBe(200);
            expect(res.body).toHaveProperty('success', true);
            expect(res.body).toHaveProperty('data');
            expect(res.body.data).toHaveProperty('numero', numero);
        });

        it('should return 404 for non-existent logia', async () => {
            const res = await api('/api/logias/99999');
            expect(res.status).toBe(404);
            expect(res.body).toHaveProperty('success', false);
            expect(res.body).toHaveProperty('message');
        });
    });

    describe('GET /api/estadisticas', () => {
        it('should return statistics', async () => {
            const res = await api('/api/estadisticas');
            expect(res.status).toBe(200);
            expect(res.body).toHaveProperty('success', true);
            expect(res.body).toHaveProperty('data');
            expect(res.body.data).toHaveProperty('total_logias');
            expect(res.body.data).toHaveProperty('total_estados');
            expect(res.body.data).toHaveProperty('total_orientes');
        });
    });

    describe('GET /api/estadisticas/por-estado', () => {
        it('should return statistics by state', async () => {
            const res = await api('/api/estadisticas/por-estado');
            expect(res.status).toBe(200);
            expect(res.body).toHaveProperty('success', true);
            expect(res.body).toHaveProperty('data');
            expect(Array.isArray(res.body.data)).toBe(true);

            if (res.body.data.length > 0) {
                const item = res.body.data[0];
                expect(item).toHaveProperty('estado');
                expect(item).toHaveProperty('cantidad');
                expect(item).toHaveProperty('logias');
            }
        });
    });

    describe('Error Handling', () => {
        it('should return 404 for unknown routes', async () => {
            const res = await api('/api/unknown');
            expect(res.status).toBe(404);
            expect(res.body).toHaveProperty('success', false);
            expect(res.body).toHaveProperty('message');
        });
    });
});