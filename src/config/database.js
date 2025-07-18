/**
 * Configuración de base de datos
 * Manejo centralizado de datos JSON
 */

const fs = require('fs');
const path = require('path');

class Database {
  constructor() {
    this.dataPath = path.join(__dirname, '../../data/');
    this.cache = new Map();
  }

  /**
   * Carga datos desde archivo JSON
   * @param {string} filename - Nombre del archivo
   * @returns {Object} Datos parseados
   */
  loadData(filename) {
    if (this.cache.has(filename)) {
      return this.cache.get(filename);
    }

    try {
      const filePath = path.join(this.dataPath, filename);
      const rawData = fs.readFileSync(filePath, 'utf8');
      const data = JSON.parse(rawData);
      
      // Cache para mejor performance
      this.cache.set(filename, data);
      
      return data;
    } catch (error) {
      console.error(`Error cargando ${filename}:`, error.message);
      return null;
    }
  }

  /**
   * Obtiene todas las logias
   */
  getLogias() {
    return this.loadData('logias.json') || [];
  }

  /**
   * Obtiene grandes maestros
   */
  getGrandesMaestros() {
    return this.loadData('gran_maestros_datos.json') || [];
  }

  /**
   * Obtiene zonas administrativas
   */
  getZonas() {
    return this.loadData('zonas.json') || [];
  }

  /**
   * Busca logias por criterios
   */
  searchLogias(criteria = {}) {
    const logias = this.getLogias();
    
    return logias.filter(logia => {
      return Object.keys(criteria).every(key => {
        if (!criteria[key]) return true;
        
        const value = logia[key];
        const searchTerm = criteria[key].toLowerCase();
        
        return value && value.toString().toLowerCase().includes(searchTerm);
      });
    });
  }

  /**
   * Obtiene estadísticas generales
   */
  getEstadisticas() {
    const logias = this.getLogias();
    const estados = [...new Set(logias.map(l => l.estado))].sort();
    const orientes = [...new Set(logias.map(l => l.oriente))].sort();
    
    return {
      total_logias: logias.length,
      total_estados: estados.length,
      total_orientes: orientes.length,
      estados,
      orientes,
      por_estado: this.groupBy(logias, 'estado'),
      fundaciones_por_siglo: this.getFoundationsByCentury(logias)
    };
  }

  groupBy(array, key) {
    return array.reduce((result, item) => {
      const group = item[key] || 'Sin especificar';
      result[group] = (result[group] || []).concat(item);
      return result;
    }, {});
  }

  getFoundationsByCentury(logias) {
    const centuries = {};
    
    logias.forEach(logia => {
      if (logia.fecha_fundacion) {
        const year = new Date(logia.fecha_fundacion).getFullYear();
        const century = Math.floor(year / 100) + 1;
        const centuryKey = `Siglo ${century}`;
        
        centuries[centuryKey] = (centuries[centuryKey] || 0) + 1;
      }
    });
    
    return centuries;
  }

  /**
   * Limpia cache
   */
  clearCache() {
    this.cache.clear();
  }
}

module.exports = new Database();