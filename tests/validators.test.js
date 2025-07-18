/**
 * Tests para validadores
 */

const { validateLogia, validateLogias } = require('../src/validators/logia');

describe('Logia Validators', () => {
    describe('validateLogia', () => {
        it('should validate correct logia', () => {
            const logia = {
                nombre_logia: "Test Logia",
                numero: 1,
                oriente: "Test City",
                estado: "Test State",
                fecha_fundacion: "2020-01-01",
                fecha_instalacion: "2020-01-15",
                contador: 1
            };
            
            const isValid = validateLogia(logia);
            expect(isValid).toBe(true);
        });

        it('should reject logia without required fields', () => {
            const logia = {
                nombre_logia: "Test Logia"
                // faltan campos requeridos
            };
            
            const isValid = validateLogia(logia);
            expect(isValid).toBe(false);
        });

        it('should reject logia with invalid number', () => {
            const logia = {
                nombre_logia: "Test Logia",
                numero: -1, // número inválido
                oriente: "Test City",
                estado: "Test State",
                contador: 1
            };
            
            const isValid = validateLogia(logia);
            expect(isValid).toBe(false);
        });

        it('should accept logia with null dates', () => {
            const logia = {
                nombre_logia: "Test Logia",
                numero: 1,
                oriente: "Test City",
                estado: "Test State",
                fecha_fundacion: null,
                fecha_instalacion: null,
                contador: 1
            };
            
            const isValid = validateLogia(logia);
            expect(isValid).toBe(true);
        });
    });

    describe('validateLogias', () => {
        it('should validate array of correct logias', () => {
            const logias = [
                {
                    nombre_logia: "Test Logia 1",
                    numero: 1,
                    oriente: "Test City 1",
                    estado: "Test State 1",
                    fecha_fundacion: "2020-01-01",
                    fecha_instalacion: "2020-01-15",
                    contador: 1
                },
                {
                    nombre_logia: "Test Logia 2",
                    numero: 2,
                    oriente: "Test City 2",
                    estado: "Test State 2",
                    fecha_fundacion: "2020-02-01",
                    fecha_instalacion: "2020-02-15",
                    contador: 2
                }
            ];
            
            const result = validateLogias(logias);
            expect(result.valido).toBe(true);
            expect(result.errores).toHaveLength(0);
        });

        it('should detect duplicate numbers', () => {
            const logias = [
                {
                    nombre_logia: "Test Logia 1",
                    numero: 1,
                    oriente: "Test City 1",
                    estado: "Test State 1",
                    contador: 1
                },
                {
                    nombre_logia: "Test Logia 2",
                    numero: 1, // número duplicado
                    oriente: "Test City 2",
                    estado: "Test State 2",
                    contador: 2
                }
            ];
            
            const result = validateLogias(logias);
            expect(result.valido).toBe(false);
            expect(result.errores.length).toBeGreaterThan(0);
        });

        it('should detect date inconsistencies', () => {
            const logias = [
                {
                    nombre_logia: "Test Logia",
                    numero: 1,
                    oriente: "Test City",
                    estado: "Test State",
                    fecha_fundacion: "2020-01-15",
                    fecha_instalacion: "2020-01-01", // anterior a fundación
                    contador: 1
                }
            ];
            
            const result = validateLogias(logias);
            expect(result.advertencias.length).toBeGreaterThan(0);
        });

        it('should provide statistics', () => {
            const logias = [
                {
                    nombre_logia: "Test Logia",
                    numero: 1,
                    oriente: "Test City",
                    estado: "Test State",
                    contador: 1
                }
            ];
            
            const result = validateLogias(logias);
            expect(result.estadisticas).toHaveProperty('total', 1);
            expect(result.estadisticas).toHaveProperty('errores');
            expect(result.estadisticas).toHaveProperty('advertencias');
        });
    });
});