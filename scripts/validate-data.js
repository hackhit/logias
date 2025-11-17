/**
 * Script para validar los datos de las logias
 */

/* eslint-disable no-console */

const path = require('path');
const { validateLogias } = require('../src/validators/logia');
const database = require('../src/config/database');

async function main() {
  console.log('🔍 Validando datos de logias...');

  const logias = await database.getLogias();

  if (!logias || logias.length === 0) {
    console.error('❌ No se encontraron datos de logias para validar.');
    process.exit(1);
  }

  const result = validateLogias(logias);

  console.log('\n--- Resultados de la Validación ---');
  console.log(`🔹 Total de logias analizadas: ${result.estadisticas.total}`);
  console.log(`🔹 Errores encontrados: ${result.estadisticas.errores}`);
  console.log(`🔹 Advertencias: ${result.estadisticas.advertencias}`);
  console.log('-------------------------------------\n');

  if (result.valido) {
    console.log('✅ ¡Validación completada! No se encontraron errores graves.');
  } else {
    console.error('❌ ¡Validación fallida! Se encontraron errores:');
    result.errores.forEach((err) => {
      console.error(`- Logia: ${err.logia} (Índice: ${err.index})`);
      if (err.error) {
        console.error(`  Error: ${err.error}`);
      }
      if (err.errores) {
        err.errores.forEach((e) => {
          console.error(`  - ${e.instancePath || 'logia'} ${e.message}`);
        });
      }
    });
  }

  if (result.advertencias.length > 0) {
    console.warn('⚠️ Se encontraron advertencias:');
    result.advertencias.forEach((warn) => {
      console.warn(
        `- Logia: ${warn.logia} (Índice: ${warn.index}) - ${warn.warning}`
      );
    });
  }

  if (!result.valido) {
    process.exit(1);
  }
}

main().catch((error) => {
  console.error('\n💥 Error inesperado durante la validación:');
  console.error(error);
  process.exit(1);
});
