# Golf Database Project Setup Instructions

## Quick Start

1. **Activate Virtual Environment:**
   ```
   venv\Scripts\activate
   ```

2. **Install Dependencies:**
   ```
   pip install -r requirements.txt
   ```

3. **Setup Environment Variables:**
   - Copy `.env.template` to `.env`
   - Fill in your database credentials and API keys

4. **Install PostgreSQL (Optional):**
   - Download from https://postgresql.org/download/windows/
   - Or use SQLite (default fallback)

5. **Run the API:**
   ```
   python src\api\app.py
   ```

## Project Structure

- `src/api/` - Flask web API
- `src/models/` - Database models
- `src/etl/` - Data loading and processing
- `data/` - Data storage (raw, processed, kaggle)
- `tests/` - Unit and integration tests

## Next Steps

1. Set up your database connection
2. Download golf data from Kaggle
3. Load data into your database
4. Build analysis notebooks in Jupyter
5. Develop additional API endpoints

## Useful Commands

```bash
# Install development dependencies
pip install -e .

# Run tests
pytest tests/

# Start Jupyter
jupyter notebook

# Database migrations
alembic init alembic
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```
