# Bike Comparison Website - README

## Project Overview
This project is a bike comparison website that scrapes bike prices from various sources, stores the data in MongoDB, and displays it using a Next.js frontend with an Express API.

## Folder Structure
```
bike-comparison-website/
│── backend/                  # Express API
│   ├── models/               # Mongoose models
│   │   ├── Bike.js
│   ├── routes/               # API routes
│   │   ├── bikes.js
│   ├── server.js             # Express server
│── scraper/                  # Python web scraping scripts
│   ├── scrapers/             # Individual scrapers for different sites
│   │   ├── site1_scraper.py
│   │   ├── site2_scraper.py
│   ├── main.py               # Runs all scrapers
│   ├── requirements.txt      # Python dependencies
│   ├── config.py             # Stores constants (e.g., MongoDB URI)
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
source venv/bin/activate  # (Linux/macOS)
venv\Scripts\Activate     # (Windows PowerShell)
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
```

For JavaScript-heavy sites:
```
playwright
```

## Next Steps
- Set up Express API to serve scraped data
- Connect MongoDB to store bike data
- Develop the Next.js frontend to display bike comparisons

## Contributors
- Lucas Pierru

## License
MIT License

