/**
 * Rutas API para Estadísticas
 */

const express = require('express');
const database = require('../../config/database');

const router = express.Router();

/**
 * @route GET /api/estadisticas
 * @desc Obtiene estadísticas generales del sistema
 */
router.get('/', (req, res) => {
  try {
    const estadisticas = database.getEstadisticas();
    
    res.json({
      success: true,
      data: estadisticas
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Error interno del servidor',
      error: error.message
    });
  }
});

/**
 * @route GET /api/estadisticas/por-estado
 * @desc Obtiene estadísticas agrupadas por estado
 */
router.get('/por-estado', (req, res) => {
  try {
    const logias = database.getLogias();
    const porEstado = database.groupBy(logias, 'estado');
    
    const estadisticas = Object.keys(porEstado).map(estado => ({
      estado,
      cantidad: porEstado[estado].length,
      logias: porEstado[estado].map(l => ({
        numero: l.numero,
        nombre: l.nombre_logia,
        oriente: l.oriente
      }))
    })).sort((a, b) => b.cantidad - a.cantidad);

    res.json({
      success: true,
      data: estadisticas
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Error interno del servidor',
      error: error.message
    });
  }
});

/**
 * @route GET /api/estadisticas/timeline
 * @desc Obtiene timeline de fundaciones por año
 */
router.get('/timeline', (req, res) => {
  try {
    const logias = database.getLogias();
    const timeline = {};
    
    logias.forEach(logia => {
      if (logia.fecha_fundacion) {
        const year = new Date(logia.fecha_fundacion).getFullYear();
        timeline[year] = (timeline[year] || 0) + 1;
      }
    });
    
    const sortedTimeline = Object.keys(timeline)
      .sort()
      .map(year => ({
        año: parseInt(year),
        fundaciones: timeline[year]
      }));

    res.json({
      success: true,
      data: sortedTimeline
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Error interno del servidor',
      error: error.message
    });
  }
});

module.exports = router;