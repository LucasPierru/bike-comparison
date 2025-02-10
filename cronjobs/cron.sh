docker start bike-comparison_scraper_1
crontab -e
0 0 * * * /bin/bash /bike-comparison/cronjobs/cron.sh