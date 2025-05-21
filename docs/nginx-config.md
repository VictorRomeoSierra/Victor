# Nginx Configuration for Victor

To route requests properly to the n8n service, add the following configuration to your Nginx server block:

```nginx
# Victor API Service
location /api/ {
    proxy_pass http://your-mac-mini-ip:8000/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}

# n8n Service
location /n8n/ {
    proxy_pass http://your-mac-mini-ip:5678/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    
    # WebSocket support for n8n
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_read_timeout 86400;
}

# Open-WebUI - Already configured
# location / {
#    proxy_pass http://your-mac-mini-ip:3000;
#    ... existing configuration ...
# }
```

Replace `your-mac-mini-ip` with the actual IP address of your Mac Mini on the network. If the Nginx server is on the same network, use the local IP (e.g., 192.168.1.x).

After updating the configuration, test and reload Nginx:

```bash
sudo nginx -t
sudo systemctl reload nginx
```

This configuration will route:
- `/api/` requests to the Victor API service on port 8000
- `/n8n/` requests to the n8n service on port 5678
- Root `/` requests to the existing Open-WebUI on port 3000