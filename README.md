# Logias Regulares Afiliadas a la M∴R∴G∴L∴R∴V∴

![Gran Logia de Venezuela](https://www.granlogiadevenezuela.com/master/masonic/assets/img/theme/logob_yellow.png)

Bienvenido al Repositorio de las **Logias Regulares Afiliadas a la M∴R∴G∴L∴R∴V∴**, y **Grandes Maestros de nuestra augusta orden**un proyecto dedicado a documentar y compartir información de las Logias Regulares pertenecientes a la **Gran Logia de la República de Venezuela**. ✨✨✨

[Visita la página oficial de la Gran Logia de Venezuela](https://www.granlogiadevenezuela.com/master/masonic/?utm_source=github&utm_medium=referral&utm_campaign=logias_repo)

---


## Descripción del Proyecto
El proyecto tiene como objetivo recopilar, estructurar y mantener un archivo JSON con información esencial sobre las Logias Regulares de la Gran Logia de la Republica de Venezuela. Rescatar la memoria de esos hombre que lo dieron todo por la Masoneria Regular Venezolana Este archivo está diseñado para ser utilizado en proyectos de diversas índoles, incluyendo sistemas de gestión, aplicaciones educativas, plataformas web y más. 📜📊📁


### Características de los Archivos JSON
- Información actualizada sobre las logias y los Grandes Maestros.
- Campos estandarizados y listos para integración en cualquier proyecto.
- Compatible con sistemas y aplicaciones orientados a bases de datos o visualización interactiva.
- Libre de uso bajo los términos de la licencia. 💡

---

## 🛠 Habilidades
Debes tener habilidades en: Javascript, HTML, CSS y todo lo que quieras hacer con estos datos, y donde los quieras utilizar.

---

## Contenido de `logias.json`
El archivo `logias.json` incluye los siguientes campos clave:

| Campo                | Tipo       | Descripción                                                                 |
|----------------------|------------|------------------------------------------------------------------------------|
| `nombre_logia`       | String     | Nombre Oficial de la Logia                                                  |
| `numero`             | Integer    | Número identificador de la Logia                                            |
| `oriente`            | String     | Ubicación del Oriente al que pertenece la Logia                             |
| `estado`             | String     | Estado de ubicación                                                         |
| `fecha_fundacion`    | Date       | Fecha oficial de fundación de la Logia                                      |
| `fecha_instalacion`  | Date       | Fecha de instalación de la Logia                                            |
| `contador`           | Integer    | Número total de Logias en Venezuela                                                 |

### Ejemplo de un Registro


    
   ```json
 {
        "nombre_logia": "Protectora de las Virtudes",
        "numero": 1,
        "oriente": "Barcelona",
        "estado": "Anzoategui",
        "fecha_fundacion": "1810-06-24",
        "fecha_instalacion": "1812-07-01",
        "contador": 1
    }
```

---

## Uso de `logias.json` en Diferentes Tecnologías

### En Vue.js
```javascript
fetch('/ruta/al/logias.json')
  .then(response => response.json())
  .then(data => {
    console.log(data);
  })
  .catch(error => console.error('Error cargando el JSON:', error));
```
---

### React
```javascript
import { useEffect, useState } from 'react';

function App() {
  const [logias, setLogias] = useState([]);

  useEffect(() => {
    fetch('/ruta/al/logias.json')
      .then(response => response.json())
      .then(data => setLogias(data))
      .catch(error => console.error('Error cargando el JSON:', error));
  }, []);

  return (
    <div>
      <h1>Logias</h1>
      <ul>
        {logias.map((logia, index) => (
          <li key={index}>{logia.nombre_logia} - {logia.oriente}</li>
        ))}
      </ul>
    </div>
  );
}

export default App;

```
---
### HTML
```html
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Logias</title>
</head>
<body>
    <h1>Lista de Logias</h1>
    <ul id="lista-logias"></ul>

    <script>
        fetch('/ruta/al/logias.json')
            .then(response => response.json())
            .then(data => {
                const lista = document.getElementById('lista-logias');
                data.forEach(logia => {
                    const item = document.createElement('li');
                    item.textContent = `${logia.nombre_logia} - ${logia.oriente}`;
                    lista.appendChild(item);
                });
            })
            .catch(error => console.error('Error cargando el JSON:', error));
    </script>
</body>
</html>
```
---
## Uso del código Python (Flask)

1.  **Requisitos:**

    *   Asegúrate de tener Python 3 instalado en tu sistema.
    *   Instala la biblioteca Flask: `pip install Flask`

2.  **Ejecución:**

    *   Guarda el código Python en un archivo llamado `app.py` (o cualquier nombre que desees).
    *   Abre una terminal o línea de comandos y navega hasta el directorio donde guardaste el archivo.
    *   Ejecuta la aplicación Flask: `python app.py`

3.  **Acceso a la API:**

    *   La API estará disponible en la dirección `http://127.0.0.1:5000/logias` (o la dirección que se muestre en la terminal al ejecutar la aplicación).
    *   Puedes acceder a esta dirección desde un navegador web o utilizando herramientas como `curl` o Postman para obtener los datos en formato JSON.

## Ejemplo de solicitud (usando `curl`)

```bash
curl [http://127.0.0.1:5000/logias](http://127.0.0.1:5000/logias)
```

---
### Usos del Proyecto

Este repositorio es de utilidad para:

- **Investigadores** que requieran información centralizada sobre las logias regulares. 🌟  
- **Desarrolladores** interesados en crear plataformas o herramientas para gestionar datos sobre logias. 💻  
- **Historiadores** que deseen mantener un registro formal de las logias regulares. 🌍🖥️📚  

Puedes comenzar descargando o clonando el repositorio desde el enlace oficial:  
[Repositorio Oficial en GitHub](https://github.com/hackhit/logias)

---

### ¿Cómo Contribuir?  
Si estás interesado en colaborar con este proyecto:  

1. **Haz un fork del repositorio.**  
2. **Realiza tus modificaciones** o añade información relevante.  
3. **Abre un pull request** para revisar tus cambios.  

¡Síguenos y mantente al día con las últimas actualizaciones del proyecto! 🔄✨🔔

[Repositorio Oficial en GitHub](https://github.com/hackhit/logias)

## Código de Conducta
Este proyecto sigue el [Código de Conducta](./CODE_OF_CONDUCT.md) para asegurar un ambiente positivo y respetuoso.

---

### Licencia  

Este proyecto está licenciado bajo la [MIT License](LICENSE).  
Siéntete libre de usar, modificar y distribuir el contenido del repositorio respetando los términos de la licencia. ⚖️📝  

---

### Contacto  

Para más información o consultas sobre el proyecto, por favor visita:  
[Gran Logia de Venezuela](https://www.granlogiadevenezuela.com/master/masonic/?utm_source=github&utm_medium=referral&utm_campaign=logias_repo) 🌐📬🙏 

---
## Autores

- [@hackhit](https://www.github.com/hackhit)

- [@jppod](https://github.com/jppod)
---
## Escribeme

Si me quieres contactar no dudes en enviarme un correo a mi direccion 83knmujyb@mozmail.com, si requieres indicaciones para implementarlo tampoco dudes en escribirme, siempre podemos ayudarnos.

---
