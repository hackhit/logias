/**
 * Validadores para datos de Logias
 */

const Ajv = require('ajv');

// Configurar Ajv con soporte básico para fechas ISO
const ajv = new Ajv();
ajv.addFormat('date', {
  type: 'string',
  validate: (date) => /^\d{4}-\d{2}-\d{2}$/.test(date),
});

// Schema para validar logias
const logiaSchema = {
  type: 'object',
  properties: {
    nombre_logia: {
      type: 'string',
      minLength: 1,
      maxLength: 100,
    },
    numero: {
      type: 'integer',
      minimum: 1,
    },
    oriente: {
      type: 'string',
      minLength: 1,
      maxLength: 50,
    },
    estado: {
      type: 'string',
      minLength: 1,
      maxLength: 50,
    },
    fecha_fundacion: {
      type: ['string', 'null'],
      format: 'date',
    },
    fecha_instalacion: {
      type: ['string', 'null'],
      format: 'date',
    },
    contador: {
      type: 'integer',
      minimum: 1,
    },
  },
  required: ['nombre_logia', 'numero', 'oriente', 'estado', 'contador'],
  additionalProperties: false,
};

const validateLogia = ajv.compile(logiaSchema);

/**
 * Valida un array de logias
 * @param {Array} logias - Array de logias a validar
 * @returns {Object} Resultado de validación
 */
function validateLogias(logias) {
  const errors = [];
  const warnings = [];
  const numerosSeen = new Set();

  logias.forEach((logia, index) => {
    // Validación de schema
    const isValid = validateLogia(logia);
    if (!isValid) {
      errors.push({
        index,
        logia: logia.nombre_logia || `Índice ${index}`,
        errores: validateLogia.errors,
      });
    }

    // Validación de números duplicados
    if (numerosSeen.has(logia.numero)) {
      errors.push({
        index,
        logia: logia.nombre_logia,
        error: `Número ${logia.numero} duplicado`,
      });
    }
    numerosSeen.add(logia.numero);

    // Validaciones adicionales (warnings)
    if (logia.fecha_fundacion && logia.fecha_instalacion) {
      const fundacion = new Date(logia.fecha_fundacion);
      const instalacion = new Date(logia.fecha_instalacion);

      if (instalacion < fundacion) {
        warnings.push({
          index,
          logia: logia.nombre_logia,
          warning: 'Fecha de instalación anterior a la fundación',
        });
      }
    }

    // Verificar fechas futuras
    const now = new Date();
    if (logia.fecha_fundacion && new Date(logia.fecha_fundacion) > now) {
      warnings.push({
        index,
        logia: logia.nombre_logia,
        warning: 'Fecha de fundación en el futuro',
      });
    }
  });

  return {
    valido: errors.length === 0,
    errores: errors,
    advertencias: warnings,
    estadisticas: {
      total: logias.length,
      errores: errors.length,
      advertencias: warnings.length,
    },
  };
}

module.exports = {
  validateLogia,
  validateLogias,
  logiaSchema,
};
