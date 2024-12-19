# Install NGINX
sudo apt install nginx -y

# Setup Container 
install docker 
copy dockerfile and dockercompose
start dockercompose

# Configure NGINX
sudo rm /etc/nginx/sites-enabled/default
sudo nano /etc/nginx/sites-available/heracless
past nginx conf

# Enable NGINX
sudo ln -s /etc/nginx/sites-available/heracless /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Secure Your Domain with SSL
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d heracless.io