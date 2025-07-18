/**
 * Servidor principal de la API de Logias
 */

require('dotenv').config();
const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const compression = require('compression');
const path = require('path');

// Importar rutas
const logiasRoutes = require('./api/routes/logias');
const estadisticasRoutes = require('./api/routes/estadisticas');

const app = express();
const PORT = process.env.PORT || 3000;

// Middlewares de seguridad y optimización
app.use(helmet());
app.use(compression());
app.use(cors());
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));

// Servir archivos estáticos
app.use('/static', express.static(path.join(__dirname, '../public')));
app.use('/data', express.static(path.join(__dirname, '../data')));

// Rutas de la API
app.use('/api/logias', logiasRoutes);
app.use('/api/estadisticas', estadisticasRoutes);

// Ruta raíz con información de la API
app.get('/', (req, res) => {
  res.json({
    nombre: 'API Logias Venezuela',
    version: '2.0.0',
    descripcion: 'API RESTful para consultar información de Logias Regulares de Venezuela',
    endpoints: {
      logias: '/api/logias',
      estadisticas: '/api/estadisticas',
      documentacion: '/docs'
    },
    repository: 'https://github.com/hackhit/logias',
    autor: 'hackhit'
  });
});

// Ruta de documentación
app.get('/docs', (req, res) => {
  res.sendFile(path.join(__dirname, '../public/docs.html'));
});

// Ruta de salud del servidor
app.get('/health', (req, res) => {
  res.json({
    status: 'OK',
    timestamp: new Date().toISOString(),
    uptime: process.uptime()
  });
});

// Manejo de errores 404
app.use('*', (req, res) => {
  res.status(404).json({
    success: false,
    message: 'Endpoint no encontrado',
    path: req.originalUrl
  });
});

// Manejo global de errores
app.use((error, req, res, next) => {
  console.error('Error:', error);
  res.status(500).json({
    success: false,
    message: 'Error interno del servidor',
    error: process.env.NODE_ENV === 'development' ? error.message : undefined
  });
});

// Iniciar servidor
app.listen(PORT, () => {
  console.log(`🚀 Servidor corriendo en puerto ${PORT}`);
  console.log(`📚 Documentación disponible en http://localhost:${PORT}/docs`);
  console.log(`🔍 API base en http://localhost:${PORT}/api`);
});

module.exports = app;