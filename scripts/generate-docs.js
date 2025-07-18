/**
 * Generador automático de documentación
 */

const fs = require('fs');
const path = require('path');

class DocsGenerator {
    constructor() {
        this.outputPath = path.join(__dirname, '../docs/');
        this.dataPath = path.join(__dirname, '../data/');
    }

    async generate() {
        console.log('📚 Generando documentación...');
        
        try {
            // Crear directorio docs si no existe
            if (!fs.existsSync(this.outputPath)) {
                fs.mkdirSync(this.outputPath, { recursive: true });
            }
            
            // Generar diferentes tipos de documentación
            await this.generateMarkdownDocs();
            await this.generateDataDictionary();
            await this.generateAPISpec();
            
            console.log('✅ Documentación generada exitosamente');
            
        } catch (error) {
            console.error('❌ Error generando documentación:', error.message);
            process.exit(1);
        }
    }

    async generateMarkdownDocs() {
        console.log('📝 Generando documentación Markdown...');
        
        const readmeContent = `# Logias Regulares de Venezuela

## Documentación Técnica

### Estructura del Proyecto

\`\`\`
logias/
├── data/                    # Datos JSON
│   ├── logias.json         # Información de logias
│   ├── gran_maestros_datos.json
│   └── zonas_administrativas.json
├── src/                    # Código fuente
│   ├── api/               # Rutas de la API
│   ├── config/            # Configuración
│   ├── validators/        # Validadores de datos
│   └── server.js          # Servidor principal
├── public/                # Archivos públicos
│   ├── index.html         # Interfaz web
│   ├── css/
│   └── js/
└── scripts/               # Scripts de utilidad
\`\`\`

### Instalación

1. Clonar el repositorio:
\`\`\`bash
git clone https://github.com/hackhit/logias.git
cd logias
\`\`\`

2. Instalar dependencias:
\`\`\`bash
npm install
\`\`\`

3. Iniciar el servidor:
\`\`\`bash
npm start
\`\`\`

### Scripts Disponibles

- \`npm start\` - Inicia el servidor
- \`npm test\` - Ejecuta las pruebas
- \`npm run validate\` - Valida los datos
- \`npm run generate:docs\` - Genera documentación

### API Endpoints

#### Logias
- \`GET /api/logias\` - Lista todas las logias
- \`GET /api/logias/:numero\` - Obtiene una logia específica
- \`GET /api/logias/estado/:estado\` - Logias por estado
- \`GET /api/logias/oriente/:oriente\` - Logias por oriente

#### Estadísticas
- \`GET /api/estadisticas\` - Estadísticas generales
- \`GET /api/estadisticas/por-estado\` - Por estado
- \`GET /api/estadisticas/timeline\` - Timeline de fundaciones

### Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (\`git checkout -b feature/AmazingFeature\`)
3. Commit tus cambios (\`git commit -m 'Add some AmazingFeature'\`)
4. Push a la rama (\`git push origin feature/AmazingFeature\`)
5. Abre un Pull Request

### Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE.md](LICENSE.md) para detalles.
`;
        
        fs.writeFileSync(path.join(this.outputPath, 'README.md'), readmeContent);
    }

    async generateDataDictionary() {
        console.log('📊 Generando diccionario de datos...');
        
        const dictionary = `# Diccionario de Datos

## Estructura de Logias

| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|----------|
| nombre_logia | string | Nombre oficial de la logia | "Protectora de las Virtudes" |
| numero | integer | Número identificador único | 1 |
| oriente | string | Ciudad o localidad donde se ubica | "Barcelona" |
| estado | string | Estado de Venezuela | "Anzoategui" |
| fecha_fundacion | string (ISO 8601) | Fecha de fundación | "1810-06-24" |
| fecha_instalacion | string (ISO 8601) | Fecha de instalación | "1812-07-01" |
| contador | integer | Número secuencial | 1 |

## Estructura de Grandes Maestros

| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|----------|
| id | integer | Identificador único | 1 |
| nombre | string | Nombre completo | "Francisco de Miranda" |
| periodo_inicio | string (ISO 8601) | Inicio del período | "1797-01-01" |
| periodo_fin | string (ISO 8601) | Fin del período | "1806-12-31" |
| lugar_nacimiento | string | Lugar de nacimiento | "Caracas" |
| fecha_nacimiento | string (ISO 8601) | Fecha de nacimiento | "1750-03-28" |
| fecha_fallecimiento | string (ISO 8601) | Fecha de fallecimiento | "1816-07-14" |
| observaciones | string | Notas adicionales | "Primer Gran Maestro..." |

## Estructura de Zonas Administrativas

| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|----------|
| id | integer | Identificador único | 1 |
| nombre | string | Nombre de la zona | "Zona Capital" |
| estados | array[string] | Estados que comprende | ["Distrito Metropolitano"] |
| coordinador | string | Coordinador actual | "Pendiente por designar" |
| logias_asociadas | array[integer] | Números de logias | [5, 7, 18] |
| descripcion | string | Descripción de la zona | "Zona que comprende..." |

## Validaciones

### Logias
- \`numero\` debe ser único
- \`fecha_instalacion\` debe ser posterior a \`fecha_fundacion\`
- Todos los campos requeridos deben estar presentes

### Grandes Maestros
- \`fecha_fallecimiento\` debe ser posterior a \`fecha_nacimiento\`
- Los períodos no deben solaparse

### Zonas Administrativas
- \`id\` debe ser único
- \`estados\` no debe estar vacío
- \`logias_asociadas\` debe contener números válidos
`;
        
        fs.writeFileSync(path.join(this.outputPath, 'DATA_DICTIONARY.md'), dictionary);
    }

    async generateAPISpec() {
        console.log('🔧 Generando especificación OpenAPI...');
        
        const openApiSpec = {
            openapi: "3.0.0",
            info: {
                title: "API Logias Venezuela",
                version: "2.0.0",
                description: "API RESTful para consultar información de las Logias Regulares Afiliadas a la M∴R∴G∴L∴R∴V∴",
                contact: {
                    name: "Soporte",
                    email: "83knmujyb@mozmail.com",
                    url: "https://github.com/hackhit/logias"
                },
                license: {
                    name: "MIT",
                    url: "https://opensource.org/licenses/MIT"
                }
            },
            servers: [
                {
                    url: "http://localhost:3000/api",
                    description: "Servidor de desarrollo"
                }
            ],
            paths: {
                "/logias": {
                    get: {
                        summary: "Obtener todas las logias",
                        description: "Retorna una lista de todas las logias con opciones de filtrado",
                        parameters: [
                            {
                                name: "estado",
                                in: "query",
                                description: "Filtrar por estado",
                                schema: { type: "string" }
                            },
                            {
                                name: "oriente",
                                in: "query",
                                description: "Filtrar por oriente",
                                schema: { type: "string" }
                            },
                            {
                                name: "nombre",
                                in: "query",
                                description: "Filtrar por nombre",
                                schema: { type: "string" }
                            },
                            {
                                name: "limit",
                                in: "query",
                                description: "Número máximo de resultados",
                                schema: { type: "integer", default: 50 }
                            },
                            {
                                name: "offset",
                                in: "query",
                                description: "Número de resultados a saltar",
                                schema: { type: "integer", default: 0 }
                            }
                        ],
                        responses: {
                            "200": {
                                description: "Lista de logias",
                                content: {
                                    "application/json": {
                                        schema: {
                                            $ref: "#/components/schemas/LogiasResponse"
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "/logias/{numero}": {
                    get: {
                        summary: "Obtener una logia específica",
                        parameters: [
                            {
                                name: "numero",
                                in: "path",
                                required: true,
                                description: "Número de la logia",
                                schema: { type: "integer" }
                            }
                        ],
                        responses: {
                            "200": {
                                description: "Información de la logia",
                                content: {
                                    "application/json": {
                                        schema: {
                                            $ref: "#/components/schemas/LogiaResponse"
                                        }
                                    }
                                }
                            },
                            "404": {
                                description: "Logia no encontrada"
                            }
                        }
                    }
                },
                "/estadisticas": {
                    get: {
                        summary: "Obtener estadísticas generales",
                        responses: {
                            "200": {
                                description: "Estadísticas del sistema",
                                content: {
                                    "application/json": {
                                        schema: {
                                            $ref: "#/components/schemas/EstadisticasResponse"
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            components: {
                schemas: {
                    Logia: {
                        type: "object",
                        properties: {
                            nombre_logia: { type: "string" },
                            numero: { type: "integer" },
                            oriente: { type: "string" },
                            estado: { type: "string" },
                            fecha_fundacion: { type: "string", format: "date" },
                            fecha_instalacion: { type: "string", format: "date" },
                            contador: { type: "integer" }
                        }
                    },
                    LogiasResponse: {
                        type: "object",
                        properties: {
                            success: { type: "boolean" },
                            data: {
                                type: "array",
                                items: { $ref: "#/components/schemas/Logia" }
                            },
                            meta: {
                                type: "object",
                                properties: {
                                    total: { type: "integer" },
                                    limit: { type: "integer" },
                                    offset: { type: "integer" },
                                    count: { type: "integer" }
                                }
                            }
                        }
                    },
                    LogiaResponse: {
                        type: "object",
                        properties: {
                            success: { type: "boolean" },
                            data: { $ref: "#/components/schemas/Logia" }
                        }
                    },
                    EstadisticasResponse: {
                        type: "object",
                        properties: {
                            success: { type: "boolean" },
                            data: {
                                type: "object",
                                properties: {
                                    total_logias: { type: "integer" },
                                    total_estados: { type: "integer" },
                                    total_orientes: { type: "integer" },
                                    estados: {
                                        type: "array",
                                        items: { type: "string" }
                                    },
                                    orientes: {
                                        type: "array",
                                        items: { type: "string" }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        };
        
        fs.writeFileSync(
            path.join(this.outputPath, 'openapi.json'), 
            JSON.stringify(openApiSpec, null, 2)
        );
    }
}

// Ejecutar si se llama directamente
if (require.main === module) {
    const generator = new DocsGenerator();
    generator.generate();
}

module.exports = DocsGenerator;