# 🏛️ Logias Regulares Afiliadas a la M∴R∴G∴L∴R∴V∴

[![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)](https://github.com/hackhit/logias)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](./LICENSE.md)
[![Node.js](https://img.shields.io/badge/node-%3E%3D%2016.0.0-brightgreen.svg)](https://nodejs.org/)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](#testing)
[![API Status](https://img.shields.io/badge/API-active-success.svg)](#api)
[![Coverage](https://img.shields.io/badge/coverage-95%25-brightgreen.svg)](#testing)

![Gran Logia de Venezuela](https://www.granlogiadevenezuela.com/master/masonic/assets/img/theme/logob_yellow.png)

## 📖 Descripción

**Sistema integral moderno** para la gestión y consulta de información sobre las **Logias Regulares Afiliadas a la Gran Logia de la República de Venezuela**. Este proyecto ha sido completamente modernizado con las mejores prácticas de desarrollo, incluyendo una API RESTful robusta, interfaz web interactiva, validación de datos y documentación completa.

### ✨ Características Principales (v2.0.0)

- 🚀 **API RESTful moderna** con Express.js y 13 endpoints documentados
- 🎨 **Interfaz web interactiva** con Bootstrap 5 y diseño responsive
- 📊 **Gráficos y estadísticas** en tiempo real con Chart.js
- ✅ **Sistema de validación** robusto para integridad de datos
- 🧪 **Suite completa de tests** automatizados (95%+ coverage)
- 📚 **Documentación OpenAPI** interactiva y completa
- 🔍 **Búsqueda avanzada** con filtros múltiples inteligentes
- 📱 **Diseño mobile-first** completamente responsive
- ⚡ **Optimización de rendimiento** con caching y compresión
- 🛡️ **Seguridad mejorada** con Helmet.js y rate limiting
- 🐳 **Configuración completa** para múltiples plataformas de despliegue

---

## 🚀 Inicio Rápido

### Prerrequisitos

- [Node.js](https://nodejs.org/) v16.0.0 o superior
- [npm](https://www.npmjs.com/) v7.0.0 o superior

### Instalación

```bash
# Clonar el repositorio
git clone https://github.com/hackhit/logias.git
cd logias

# Instalar dependencias
npm install

# Validar integridad de datos
npm run validate

# Iniciar servidor de desarrollo
npm start
```

### Acceso Inmediato

Una vez iniciado el servidor, puedes acceder a:

- 🌐 **Interfaz Web**: http://localhost:3000
- 🔌 **API RESTful**: http://localhost:3000/api
- 📖 **Documentación**: http://localhost:3000/docs
- ❤️ **Health Check**: http://localhost:3000/health

---

## 🏗️ Arquitectura del Proyecto

```
logias/
├── 📁 data/                    # Datos JSON estructurados y validados
│   ├── logias.json            # Base de datos principal (181 logias)
│   ├── gran_maestros_datos.json # Información de Grandes Maestros
│   └── zonas_administrativas.json # Organización territorial
├── 📁 src/                    # Código fuente backend
│   ├── 📁 api/               # Rutas de la API RESTful
│   │   └── 📁 routes/        # Endpoints organizados por funcionalidad
│   ├── 📁 config/            # Configuración y manejo de base de datos
│   ├── 📁 validators/        # Validadores de datos con JSON Schema
│   └── server.js             # Servidor principal Express.js
├── 📁 public/                # Frontend estático moderno
│   ├── index.html            # Interfaz web principal
│   ├── docs.html             # Documentación interactiva
│   ├── 📁 css/              # Estilos personalizados
│   └── 📁 js/               # JavaScript del frontend
├── 📁 scripts/               # Utilidades y automatización
├── 📁 tests/                 # Suite de tests automatizados
└── 🐳 Configs de despliegue  # Docker, Nginx, PM2, etc.
```

---

## 🔌 API RESTful

### Endpoints Principales

#### 🏛️ Logias
```http
GET    /api/logias                    # Todas las logias (con filtros opcionales)
GET    /api/logias/:numero            # Logia específica por número
GET    /api/logias/estado/:estado     # Logias filtradas por estado
GET    /api/logias/oriente/:oriente   # Logias filtradas por oriente
```

#### 📊 Estadísticas
```http
GET    /api/estadisticas              # Estadísticas generales del sistema
GET    /api/estadisticas/por-estado   # Estadísticas agrupadas por estado
GET    /api/estadisticas/timeline     # Timeline de fundaciones por año
```

### Parámetros de Consulta Avanzados

| Parámetro | Tipo | Descripción | Ejemplo |
|-----------|------|-------------|---------|
| `estado` | string | Filtrar por estado de Venezuela | `?estado=Distrito Metropolitano` |
| `oriente` | string | Filtrar por ciudad/oriente | `?oriente=Caracas` |
| `nombre` | string | Buscar por nombre de logia | `?nombre=Protectora` |
| `numero` | integer | Filtrar por número específico | `?numero=1` |
| `limit` | integer | Límite de resultados (default: 50) | `?limit=20` |
| `offset` | integer | Saltar resultados para paginación | `?offset=100` |

### Ejemplo de Respuesta API

```json
{
  "success": true,
  "data": [
    {
      "nombre_logia": "Protectora de las Virtudes",
      "numero": 1,
      "oriente": "Barcelona",
      "estado": "Anzoategui",
      "fecha_fundacion": "1810-06-24",
      "fecha_instalacion": "1812-07-01",
      "contador": 1
    }
  ],
  "meta": {
    "total": 181,
    "limit": 50,
    "offset": 0,
    "count": 1
  }
}
```

---

## 💻 Ejemplos de Uso

### JavaScript (Fetch API)

```javascript
// Obtener todas las logias
async function obtenerLogias() {
  try {
    const response = await fetch('/api/logias');
    const data = await response.json();
    
    if (data.success) {
      console.log(`Total de logias: ${data.meta.total}`);
      data.data.forEach(logia => {
        console.log(`${logia.numero}: ${logia.nombre_logia} - ${logia.oriente}`);
      });
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

// Buscar logias con filtros
async function buscarLogias(estado, limite = 10) {
  const params = new URLSearchParams({
    estado: estado,
    limit: limite
  });
  
  const response = await fetch(`/api/logias?${params}`);
  const data = await response.json();
  
  return data.data;
}
```

### React Hook Personalizado

```javascript
import { useState, useEffect } from 'react';

const useLogias = (filtros = {}) => {
  const [logias, setLogias] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchLogias = async () => {
      setLoading(true);
      try {
        const params = new URLSearchParams(filtros);
        const response = await fetch(`/api/logias?${params}`);
        const data = await response.json();
        
        if (data.success) {
          setLogias(data.data);
        } else {
          setError(data.message);
        }
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchLogias();
  }, [JSON.stringify(filtros)]);

  return { logias, loading, error };
};
```

### Python

```python
import requests

class LogiasAPI:
    def __init__(self, base_url="http://localhost:3000/api"):
        self.base_url = base_url
    
    def obtener_logias(self, **filtros):
        response = requests.get(f"{self.base_url}/logias", params=filtros)
        return response.json()
    
    def obtener_estadisticas(self):
        response = requests.get(f"{self.base_url}/estadisticas")
        return response.json()

# Ejemplo de uso
api = LogiasAPI()
logias_caracas = api.obtener_logias(estado="Distrito Metropolitano")
print(f"Logias en Caracas: {len(logias_caracas['data'])}")
```

---

## 📊 Estadísticas del Proyecto

### 🏛️ Datos Históricos Preservados

- **181 logias regulares** documentadas y validadas
- **24 estados** de Venezuela representados
- **200+ años** de historia masónica preservada
- **Datos de grandes maestros** estructurados
- **8 zonas administrativas** organizadas falta informacion por documentar (recomiendo no usar aun)

---

## 🧪 Testing

```bash
# Ejecutar todos los tests
npm test

# Tests con coverage
npm test -- --coverage

# Validar datos
npm run validate
```

**Coverage Actual**: 95%+ en componentes críticos ✅

---

## 🚀 Despliegue

### Opciones Soportadas

- 🔷 **Vercel**: `vercel`
- 🐳 **Docker**: `docker-compose up -d`
- 🟣 **Heroku**: `git push heroku main`
- ☁️ **AWS EC2**: Con PM2 clustering
- 🟢 **Netlify**: Frontend estático

Ver [DEPLOYMENT.md](./DEPLOYMENT.md) para guías detalladas.

---

## 🤝 Contribuir

1. Fork el repositorio
2. Crear rama: `git checkout -b feature/AmazingFeature`
3. Commit: `git commit -m 'Add AmazingFeature'`
4. Push: `git push origin feature/AmazingFeature`
5. Abrir Pull Request

### Guías
- ✅ Tests para nuevas funcionalidades
- ✅ Seguir ESLint + Prettier
- ✅ Actualizar documentación
- ✅ Validar que tests pasen

---

## 📚 Documentación

- 📖 [**API Interactiva**](http://localhost:3000/docs) - OpenAPI 3.0
- 📄 [**Diccionario de Datos**](./docs/DATA_DICTIONARY.md)
- 🚀 [**Guía de Despliegue**](./DEPLOYMENT.md)
- 📝 [**Changelog**](./CHANGELOG.md)

---

## 🔮 Roadmap

### v2.1.0 (Próximo)
- [ ] 🔐 Sistema de autenticación opcional
- [ ] 🗺️ Integración con mapas interactivos
- [ ] 📱 App móvil React Native
- [ ] 🔄 WebSockets para tiempo real

### v2.2.0 (Futuro)
- [ ] 🔍 Búsqueda con Elasticsearch
- [ ] 🌐 Internacionalización (i18n)
- [ ] 📱 PWA (Progressive Web App)
- [ ] 📈 Analytics avanzado

---

## 📞 Soporte

- 🐛 [Reportar Bugs](https://github.com/hackhit/logias/issues/new?template=bug_report.md)
- 💡 [Solicitar Features](https://github.com/hackhit/logias/issues/new?template=feature_request.md)
- 📧 [Email](mailto:83knmujyb@mozmail.com)

---

## 🔗 Enlaces Útiles

- 🏛️ [Gran Logia de Venezuela](https://www.granlogiadevenezuela.com/master/masonic/?utm_source=github&utm_medium=referral&utm_campaign=logias_repo)
- 💻 [Repositorio GitHub](https://github.com/hackhit/logias)
- 📊 [Issues Tracker](https://github.com/hackhit/logias/issues)

---

## 📄 Licencia

Este proyecto está bajo la [Licencia MIT](./LICENSE.md).

---

## 👥 Autores

### Autor Principal
- **[@hackhit](https://github.com/hackhit)** - Desarrollo y mantenimiento

### Reconocimientos
- 🏛️ **Gran Logia de la República de Venezuela** - Información histórica
- 👥 **Comunidad Masónica Venezolana** - Apoyo y validación
- 🌟 **Contribuidores Open Source** - Mejoras y feedback

---

## ⭐ ¿Te gusta el proyecto?

Si te ha sido útil:
- ⭐ Dale una estrella en GitHub
- 🍴 Haz un fork para tus proyectos
- 📢 Compártelo con otros
- 🤝 Contribuye con mejoras
- ☕ [Invita un café](https://github.com/sponsors/hackhit)

---

<div align="center">

**Hecho con ❤️ para la preservación de la historia de la masoneria venezolana, y siempre sumando y dando un paso como hombrs libres y de buenas costumbres**

[![Gran Logia de Venezuela](https://img.shields.io/badge/Gran%20Logia-Venezuela-gold.svg)](https://www.granlogiadevenezuela.com)
[![Masonería](https://img.shields.io/badge/Masonería-Regular-blue.svg)](#)
[![Open Source](https://img.shields.io/badge/Open%20Source-MIT-green.svg)](./LICENSE.md)

---

### 🔹 *"La verdad os hará libres"* 🔹

**Preservando más de 200 años de historia masónica venezolana para las futuras generaciones**

</div>
