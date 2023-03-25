# Hosting on a Linux server

## Disclaimer
The client-server architecture allows you to host the viewer on public servers. But that doesn't mean that you should do it. Please be polite to other users and don't share any sensitive messages with broader audience (or the whole internet), than it was intended to be shared with before.

Intended use cases:
- old private discord server was hacked and new one was created. You want to share a backup with the same people, who were in the old server.
- or you host your own backup on your own server, so you can access it from anywhere.
- ... use common sense

## Protecting the viewer with password authentication

It is recomended to put the server behind another reverse proxy, such as nginx. The reverse proxy should be configured to require authentication (for example using [basic auth](https://docs.nginx.com/nginx/admin-guide/security-controls/configuring-http-basic-authentication/)).

Create firewall rules to open only TCP ports 22 (SSH) and 80 (HTTP) and enable firewall:
```
ufw allow 22/tcp
ufw allow 80/tcp
ufw enable
```

Bind port 21011 from docker container only to loopback (localhost `127.0.0.1`):
```bash
docker run ... -p 127.0.0.1:21011:21011 -it dcef
```

Create .htpasswd file:
```bash
sudo apt install apache2-utils
htpasswd -c /etc/nginx/.htpasswd <username>
<password>
```

Change nginx site config to require authentication (add lines `auth_basic` and `auth_basic_user_file`):
```
server {
        listen 80;

        location / {
            proxy_pass http://localhost:21011/;
            auth_basic           "Auth only";
            auth_basic_user_file /etc/nginx/.htpasswd;
        }
}
```