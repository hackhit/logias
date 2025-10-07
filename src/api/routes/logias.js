/**
 * Rutas API para Logias
 */

const express = require('express');
const database = require('../../config/database');

const router = express.Router();

/**
 * @route GET /api/logias
 * @desc Obtiene todas las logias o las filtra por parámetros
 */
router.get('/', async (req, res) => {
  try {
    const { estado, oriente, nombre, numero, limit, offset } = req.query;

    let logias = await database.searchLogias({
      estado,
      oriente,
      nombre_logia: nombre,
      numero,
    });

    // Paginación
    const total = logias.length;
    const limitNum = parseInt(limit) || total;
    const offsetNum = parseInt(offset) || 0;

    logias = logias.slice(offsetNum, offsetNum + limitNum);

    res.json({
      success: true,
      data: logias,
      meta: {
        total,
        limit: limitNum,
        offset: offsetNum,
        count: logias.length,
      },
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Error interno del servidor',
      error: error.message,
    });
  }
});

/**
 * @route GET /api/logias/:numero
 * @desc Obtiene una logia específica por número
 */
router.get('/:numero', async (req, res) => {
  try {
    const numero = parseInt(req.params.numero);
    const logias = await database.getLogias();
    const logia = logias.find((l) => l.numero === numero);

    if (!logia) {
      return res.status(404).json({
        success: false,
        message: `Logia número ${numero} no encontrada`,
      });
    }

    res.json({
      success: true,
      data: logia,
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Error interno del servidor',
      error: error.message,
    });
  }
});

/**
 * @route GET /api/logias/estado/:estado
 * @desc Obtiene logias por estado
 */
router.get('/estado/:estado', async (req, res) => {
  try {
    const estado = decodeURIComponent(req.params.estado);
    const logias = await database.searchLogias({ estado });

    res.json({
      success: true,
      data: logias,
      meta: {
        estado,
        count: logias.length,
      },
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Error interno del servidor',
      error: error.message,
    });
  }
});

/**
 * @route GET /api/logias/oriente/:oriente
 * @desc Obtiene logias por oriente
 */
router.get('/oriente/:oriente', async (req, res) => {
  try {
    const oriente = decodeURIComponent(req.params.oriente);
    const logias = await database.searchLogias({ oriente });

    res.json({
      success: true,
      data: logias,
      meta: {
        oriente,
        count: logias.length,
      },
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Error interno del servidor',
      error: error.message,
    });
  }
});

module.exports = router;
