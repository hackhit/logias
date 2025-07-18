/**
 * Tests para la API
 */

const request = require('supertest');
const app = require('../src/server');

describe('API Endpoints', () => {
    describe('GET /', () => {
        it('should return API information', async () => {
            const res = await request(app)
                .get('/')
                .expect(200);
            
            expect(res.body).toHaveProperty('nombre');
            expect(res.body).toHaveProperty('version');
            expect(res.body).toHaveProperty('endpoints');
        });
    });

    describe('GET /health', () => {
        it('should return health status', async () => {
            const res = await request(app)
                .get('/health')
                .expect(200);
            
            expect(res.body).toHaveProperty('status', 'OK');
            expect(res.body).toHaveProperty('timestamp');
            expect(res.body).toHaveProperty('uptime');
        });
    });

    describe('GET /api/logias', () => {
        it('should return logias list', async () => {
            const res = await request(app)
                .get('/api/logias')
                .expect(200);
            
            expect(res.body).toHaveProperty('success', true);
            expect(res.body).toHaveProperty('data');
            expect(Array.isArray(res.body.data)).toBe(true);
            expect(res.body).toHaveProperty('meta');
        });

        it('should filter logias by estado', async () => {
            const res = await request(app)
                .get('/api/logias?estado=Caracas')
                .expect(200);
            
            expect(res.body.success).toBe(true);
            if (res.body.data.length > 0) {
                res.body.data.forEach(logia => {
                    expect(logia.estado).toBe('Caracas');
                });
            }
        });

        it('should limit results', async () => {
            const res = await request(app)
                .get('/api/logias?limit=5')
                .expect(200);
            
            expect(res.body.success).toBe(true);
            expect(res.body.data.length).toBeLessThanOrEqual(5);
            expect(res.body.meta.limit).toBe(5);
        });
    });

    describe('GET /api/logias/:numero', () => {
        it('should return specific logia', async () => {
            const res = await request(app)
                .get('/api/logias/1')
                .expect(200);
            
            expect(res.body).toHaveProperty('success', true);
            expect(res.body).toHaveProperty('data');
            expect(res.body.data).toHaveProperty('numero', 1);
        });

        it('should return 404 for non-existent logia', async () => {
            const res = await request(app)
                .get('/api/logias/99999')
                .expect(404);
            
            expect(res.body).toHaveProperty('success', false);
            expect(res.body).toHaveProperty('message');
        });
    });

    describe('GET /api/estadisticas', () => {
        it('should return statistics', async () => {
            const res = await request(app)
                .get('/api/estadisticas')
                .expect(200);
            
            expect(res.body).toHaveProperty('success', true);
            expect(res.body).toHaveProperty('data');
            expect(res.body.data).toHaveProperty('total_logias');
            expect(res.body.data).toHaveProperty('total_estados');
            expect(res.body.data).toHaveProperty('total_orientes');
        });
    });

    describe('GET /api/estadisticas/por-estado', () => {
        it('should return statistics by state', async () => {
            const res = await request(app)
                .get('/api/estadisticas/por-estado')
                .expect(200);
            
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
            const res = await request(app)
                .get('/api/unknown')
                .expect(404);
            
            expect(res.body).toHaveProperty('success', false);
            expect(res.body).toHaveProperty('message');
        });
    });
});