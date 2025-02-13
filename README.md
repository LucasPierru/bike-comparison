# Bike Comparison Website - README

## Project Overview

This project is a bike comparison website that scrapes bike prices from various sources, stores the data in MongoDB, and displays it using a Next.js frontend with an Express API.

## Folder Structure

```
bike-comparison/
│── backend/                  # Express API
│   ├── models/               # Mongoose models
│   │   ├── Bike.js
│   ├── routes/               # API routes
│   │   ├── bikes.js
│   ├── server.js             # Express server
│── scraper/                  # Python web scraping scripts
│   ├── models/               # Models matching the mongoDB
│   │   ├── bike.py
│   ├── scripts/              # Individual scrapers for different sites
│   │   ├── trek.py
│   │   ├── specialized.py
│   ├── toolbox/              # Toolbox of utility functions
│   │   ├── toolbox.py
│   ├── main.py               # Runs all scrapers
│   ├── requirements.txt      # Python dependencies
│   ├── config.py             # Stores constants (e.g., MongoDB URI)
│   ├── db.py                 # Stores db setup
│── frontend/                 # Next.js frontend
│   ├── components/
│   ├── pages/
│── cronjobs/                 # Server automation scripts
│   ├── cron.sh               # Shell script to automate scraping
│── .env                      # Environment variables
│── package.json              # Node.js dependencies
│── README.md                 # Project documentation
```

## Setting Up the Web Scraper

### 1. Set Up a Virtual Environment (Recommended)

```bash
cd scraper
python -m venv venv
```

```bash
cd scraper/venv/Scripts
. activate
to activate the venv
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Running the Scraper

```bash
python main.py
```

To deactivate the virtual environment:

```bash
deactivate
```

## Automating the Scraper with Cron Jobs

### 1. Create a Shell Script

Create a `cron.sh` file in the `cronjobs/` directory:

```bash
#!/bin/bash
cd /path/to/bike-comparison-website/scraper
source venv/bin/activate
python main.py
deactivate
```

### 2. Set Up a Cron Job

Open the cron editor:

```bash
crontab -e
```

Add the following line to run the scraper daily at 2 AM:

```bash
0 2 * * * /bin/bash /path/to/bike-comparison-website/cronjobs/cron.sh >> /path/to/logfile.log 2>&1
```

## `requirements.txt` for Python Dependencies

```
requests
beautifulsoup4
pymongo
selenium
webdriver-manager
schedule
pandas
pymongo
```

For JavaScript-heavy sites:

```
playwright
```

### 3. Deploy application on DigitalOcean

##### Open the cron editor:

```
ssh root@digital_ocean_droplet_ip
```

Add the following lines to run update, upgrade and install docker:

```
sudo apt update && sudo apt upgrade -y

```

```
sudo apt install docker.io -y
sudo apt install docker-compose -y
sudo systemctl enable docker
sudo systemctl start docker
```

##### Clone the Github repository (Check the personal access token):

```
git clone your-repo-url.git bike-comparison
cd bike-comparison
```

##### Deploy the backend with docker:

```
cd backend
nano .env //add all the environement variables
docker build -t bike-api .
docker run -d -p 4000:4000 --env-file .env --name bike-api bike-api
```

##### Deploy the backend with docker:

```
cd frontend
nano .env //add all the environement variables
docker build -t bike-frontend .
docker run -d -p 3000:3000 --env-file .env --name bike-frontend bike-frontend
```

##### Deploy the scraper with docker:

```
cd scraper
nano config.py //add all the environement variables
docker build -t bike-scraper .
docker run bike-scraper
```

##### Deploy the app with docker compose:

```
docker-compose up --build -d
```

##### Run a cronjob to scrape data every day:

```
crontab -e
0 3 * * * docker run bike-scraper
```

### 4. Configure nginx

##### Install nginx on the server:

```
sudo apt update && sudo apt install nginx -y
```

##### Enable nginx:

```
sudo systemctl enable nginx
sudo systemctl start nginx
```

##### Make sure nginx is running:

```
systemctl status nginx
```

##### Configure DNS and add the Digital Ocean nameservers to GoDaddy domain:

| Type | Name | Value      |
| ---- | ---- | ---------- |
| A    | @    | IP address |
| A    | www  | IP address |
| A    | api  | IP address |

```
nslookup yourdomain.com to make sure it's running
```

##### Create nginx config:

```
sudo nano /etc/nginx/sites-available/default
```

```
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location / {
        proxy_pass http://localhost:3000; # Next.js frontend running on port 3000
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://localhost4000; # Express API running on port 4000
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

```

##### Test and reload nginx:

```
sudo nginx -t
sudo systemctl reload nginx
```

##### Encrypt and get SSL certificate:

```
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com -d api.yourdomain.com
```

##### Certificate auto-renewal:

```
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

##### Final check

```
sudo systemctl restart nginx
```

## Next Steps

- Update SEO features
- Add github workflow to automate deployment

## Contributors

- Lucas Pierru

## License

MIT License
