module.exports = {
  apps: [{
    name: 'logias-api',
    script: 'src/server.js',
    instances: 'max',
    exec_mode: 'cluster',
    env: {
      NODE_ENV: 'development',
      PORT: 3000
    },
    env_production: {
      NODE_ENV: 'production',
      PORT: 3000
    },
    // Logging
    log_file: './logs/combined.log',
    out_file: './logs/out.log',
    error_file: './logs/error.log',
    log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
    
    // Auto restart
    watch: false,
    max_memory_restart: '1G',
    
    // Advanced settings
    kill_timeout: 5000,
    wait_ready: true,
    listen_timeout: 3000,
    
    // Health monitoring
    min_uptime: '10s',
    max_restarts: 10,
    
    // Source map support
    source_map_support: true,
    
    // Environment specific settings
    node_args: '--max-old-space-size=1024'
  }]
};