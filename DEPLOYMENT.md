# UK Tender Scraper - Deployment Guide

## Quick Start

### Local Development

1. **Clone the repository**
```bash
git clone https://github.com/kaljuvee/uk-tender-data.git
cd uk-tender-data
```

2. **Create virtual environment**
```bash
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.sample .env
# Edit .env and add your OpenAI API key
```

5. **Run the application**
```bash
streamlit run Home.py
```

The application will be available at `http://localhost:8501`

## Environment Variables

Create a `.env` file with the following variables:

```env
OPENAI_API_KEY=your_openai_api_key_here
GITHUB_USERNAME=your_github_username
GITHUB_TOKEN=your_github_token
```

## Database Setup

The SQLite database is automatically created when you first run the application. The schema is defined in `sql/create_tables.sql`.

To manually initialize the database:

```bash
python -c "from utils.database import TenderDatabase; TenderDatabase()"
```

## Testing

Run the test suite to verify functionality:

```bash
# Test database operations
python tests/test_database.py

# Test API scraper
python tests/test_api_scraper.py

# Test data generator
python tests/test_data_generator.py
```

Test results are saved to `test-results/*.json`.

## Cloud Deployment

### Streamlit Cloud

1. **Fork/Clone the repository** to your GitHub account

2. **Go to Streamlit Cloud** (https://streamlit.io/cloud)

3. **Create new app**
   - Repository: `kaljuvee/uk-tender-data`
   - Branch: `main`
   - Main file path: `Home.py`

4. **Add secrets** in Streamlit Cloud settings:
   ```toml
   OPENAI_API_KEY = "your_openai_api_key_here"
   ```

5. **Deploy** - Streamlit will automatically install dependencies and run the app

### Heroku

1. **Create Procfile**
```
web: streamlit run Home.py --server.port=$PORT --server.address=0.0.0.0
```

2. **Create runtime.txt**
```
python-3.11.0
```

3. **Deploy to Heroku**
```bash
heroku create uk-tender-scraper
heroku config:set OPENAI_API_KEY=your_key_here
git push heroku main
```

### Docker

1. **Create Dockerfile**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "Home.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

2. **Build and run**
```bash
docker build -t uk-tender-scraper .
docker run -p 8501:8501 -e OPENAI_API_KEY=your_key uk-tender-scraper
```

### AWS EC2

1. **Launch EC2 instance** (Ubuntu 22.04)

2. **SSH into instance**
```bash
ssh -i your-key.pem ubuntu@your-instance-ip
```

3. **Install dependencies**
```bash
sudo apt update
sudo apt install -y python3.11 python3.11-venv git
```

4. **Clone and setup**
```bash
git clone https://github.com/kaljuvee/uk-tender-data.git
cd uk-tender-data
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

5. **Create systemd service** (`/etc/systemd/system/tender-scraper.service`)
```ini
[Unit]
Description=UK Tender Scraper
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/uk-tender-data
Environment="PATH=/home/ubuntu/uk-tender-data/venv/bin"
Environment="OPENAI_API_KEY=your_key_here"
ExecStart=/home/ubuntu/uk-tender-data/venv/bin/streamlit run Home.py --server.port=8501 --server.address=0.0.0.0

[Install]
WantedBy=multi-user.target
```

6. **Start service**
```bash
sudo systemctl daemon-reload
sudo systemctl enable tender-scraper
sudo systemctl start tender-scraper
```

7. **Configure security group** to allow inbound traffic on port 8501

## Production Considerations

### Security

- **Never commit** `.env` file or credentials to git
- Use **environment variables** for sensitive data
- Consider using **secrets management** (AWS Secrets Manager, HashiCorp Vault)
- Enable **HTTPS** for production deployments
- Implement **rate limiting** for API calls

### Performance

- Consider using **PostgreSQL** instead of SQLite for production
- Implement **caching** for frequently accessed data
- Use **connection pooling** for database connections
- Monitor **API rate limits** for Find a Tender service

### Monitoring

- Set up **logging** to track errors and usage
- Use **application monitoring** (New Relic, Datadog)
- Monitor **database size** and performance
- Track **API usage** and costs

### Backup

- Regularly **backup** the SQLite database
- Store backups in **cloud storage** (S3, Google Cloud Storage)
- Test **restore procedures** periodically

## Troubleshooting

### Port already in use
```bash
# Find process using port 8501
lsof -i :8501
# Kill the process
kill -9 <PID>
```

### Database locked
```bash
# Stop all Streamlit processes
pkill -f streamlit
# Remove database lock
rm sql/tenders.db-journal
```

### Missing dependencies
```bash
# Reinstall all dependencies
pip install --force-reinstall -r requirements.txt
```

### API connection issues
- Check internet connectivity
- Verify Find a Tender API is accessible
- Check for rate limiting

## Support

For issues or questions:
- Open an issue on GitHub: https://github.com/kaljuvee/uk-tender-data/issues
- Check the README.md for documentation
- Review test results in `test-results/` directory

## License

This project is for demonstration and educational purposes.
