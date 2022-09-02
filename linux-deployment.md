## Linux deployment

### Dependencies
- Virtualbox
``` bash
sudo apt install virtualbox
```
- Vagrant
``` bash
sudo apt update
curl -O https://releases.hashicorp.com/vagrant/2.2.6/vagrant_2.2.6_x86_64.deb
sudo apt install ./vagrant_2.2.6_x86_64.deb
```

### Steps:

1. Create vagrant configuration in Vagrantfile:
``` bash
mkdir flask-app
cd flask-app
vagrant init
```
Vagrant init will generate a Vagrantfile. There, insert this configuration:
``` bash
Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/xenial64"
  config.vm.network "private_network", ip: "192.168.33.10"
  config.vm.provider "virtualbox" do |vb|
    vb.memory = "1024"
  end
end
```
2. Launch the virtual machine and access it via ssh:
``` bash
vagrant up
vagrant ssh
```

3. Add some security to the server by updating some configuration files inside the virtual machine and installing ufw basic firewall:
``` bash
PermitRootLogin no    # In file "/etc/ssh/sshd_config"
```

``` bash
PasswordAuthentication no   # In file "/etc/ssh/sshd_config"
```

``` bash
sudo service ssh restart
sudo apt-get install -y ufw
sudo ufw allow ssh
sudo ufw allow http
sudo ufw allow 443/tcp
sudo ufw --force enable
```

4. Install necessary packages:
``` bash
sudo apt-get -y update
sudo apt-get -y install python3 python3-venv python3-dev
sudo apt-get -y install supervisor nginx git
```

5. Clone github repository and install necessary python modules
``` bash
git clone https://github.com/AlexMoreno98/videoanim-flask-project.git
cd videoanim-flask-project
```
After cloning the repository, inside "app" folder you have to uncomment line 36 (remote_ip = request.remote_addr) and comment line 38 (remote_ip = request.headers['X-Forwarded-For']) in visitor.py.

``` bash
python3 -m venv venv
source venv/bin/activate
(venv) pip install -r requirements.txt
```

6. Set up supervisor configuration inside "/etc/supervisor/conf.d/flask-app.conf" file:
``` bash
[program:flask-app]
command=/home/vagrant/videoanim-flask-project/venv/bin/gunicorn -b localhost:8000 -w 4 --chdir app app:app
directory=/home/vagrant/videoanim-flask-project
user=vagrant
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
```
Then, reload supervisor service:
``` bash
sudo supervisorctl reload
```

7. Inside project folder, create server certificates:
``` bash
mkdir certs
openssl req -new -newkey rsa:4096 -days 365 -nodes -x509 -keyout certs/key.pem -out certs/cert.pem
sudo rm /etc/nginx/sites-enabled/default
```

8. Set up server configuration inside "/etc/nginx/sites-enabled/flask-app" file:
``` bash
server {
    # listen on port 80 (http)
    listen 80;
    server_name _;
    location / {
        # redirect any requests to the same URL but on https
        return 301 https://$host$request_uri;
    }
}
server {
    # listen on port 443 (https)
    listen 443 ssl;
    server_name _;

    # location of the self-signed SSL certificate
    ssl_certificate /home/vagrant/videoanim-flask-project/certs/cert.pem;
    ssl_certificate_key /home/vagrant/videoanim-flask-project/certs/key.pem;

    # write access and error logs to /var/log
    access_log /var/log/flask-app_access.log;
    error_log /var/log/flask-app_error.log;

    location / {
        # forward application requests to the gunicorn server
        proxy_pass http://localhost:8000;
        proxy_redirect off;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /static {
        # handle static files directly, without forwarding to the application
        alias /home/vagrant/videoanim-flask-project/app/static;
        expires 30d;
    }
}
```

Finally, reload nginx service:
``` bash
sudo service nginx reload
```

To access the website, enter 192.168.33.10 IP in your browser.

9. To update application:
``` bash
(venv) git pull
(venv) sudo supervisorctl stop flask-app
(venv) sudo supervisorctl start flask-app
```
