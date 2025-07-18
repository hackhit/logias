# 🚀 Guía de Despliegue

## Opciones de Despliegue

### 1. Vercel (Recomendado para proyectos pequeños)

```bash
# Instalar Vercel CLI
npm i -g vercel

# Desplegar
vercel

# Configurar variables de entorno
vercel env add PORT production
vercel env add NODE_ENV production
```

**vercel.json**:
```json
{
  "version": 2,
  "builds": [
    {
      "src": "src/server.js",
      "use": "@vercel/node"
    },
    {
      "src": "public/**",
      "use": "@vercel/static"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "src/server.js"
    },
    {
      "src": "/(.*)",
      "dest": "public/$1"
    }
  ]
}
```

### 2. Heroku

```bash
# Instalar Heroku CLI
npm install -g heroku

# Login
heroku login

# Crear app
heroku create logias-venezuela

# Configurar variables
heroku config:set NODE_ENV=production
heroku config:set PORT=3000

# Desplegar
git push heroku main
```

**Procfile**:
```
web: node src/server.js
```

### 3. Docker

**Dockerfile**:
```dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .

EXPOSE 3000

USER node

CMD ["npm", "start"]
```

**docker-compose.yml**:
```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - PORT=3000
    restart: unless-stopped
    volumes:
      - ./data:/app/data:ro
```

```bash
# Construir y ejecutar
docker-compose up -d
```

### 4. AWS EC2

```bash
# Conectar a EC2
ssh -i your-key.pem ubuntu@your-ec2-ip

# Instalar Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Clonar repositorio
git clone https://github.com/hackhit/logias.git
cd logias

# Instalar dependencias
npm install --production

# Instalar PM2
npm install -g pm2

# Configurar PM2
echo '{
  "name": "logias-api",
  "script": "src/server.js",
  "env": {
    "NODE_ENV": "production",
    "PORT": 3000
  }
}' > ecosystem.config.json

# Iniciar aplicación
pm2 start ecosystem.config.json
pm2 startup
pm2 save
```

## Variables de Entorno

```bash
# Producción
NODE_ENV=production
PORT=3000

# Desarrollo
NODE_ENV=development
PORT=3000
```

## Nginx (Proxy Reverso)

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
    
    # Caché para archivos estáticos
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
        proxy_pass http://localhost:3000;
    }
}
```

## SSL con Let's Encrypt

```bash
# Instalar Certbot
sudo apt install certbot python3-certbot-nginx

# Obtener certificado
sudo certbot --nginx -d your-domain.com

# Renovación automática
sudo crontab -e
# Agregar: 0 12 * * * /usr/bin/certbot renew --quiet
```