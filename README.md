# Morning Cafe ☕

Build your own coffee and buy it — all fake payments. A Django practice project
with a layered architecture (MVT + Service Layer), a REST API, and Playwright
end-to-end tests using the Page Object Model.

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the full design.

## Setup (Windows)

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-dev.txt
playwright install chromium
copy .env.example .env      # then edit the values
```

### MySQL

Create the database and user (as MySQL root):

```sql
CREATE DATABASE morning_cafe CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
CREATE USER 'cafe'@'localhost' IDENTIFIED BY '<DB_PASSWORD from .env>';
GRANT ALL PRIVILEGES ON morning_cafe.* TO 'cafe'@'localhost';
GRANT ALL PRIVILEGES ON test_morning_cafe.* TO 'cafe'@'localhost';  -- for pytest
```

No MySQL handy? Set `DB_ENGINE=sqlite` in `.env`.

## Run

```powershell
python manage.py migrate
python manage.py seed_menu      # load the coffees, milks and sizes (safe to run again)
python manage.py runserver
```

Open http://127.0.0.1:8000/ → **See our menu** → coffee → type → milk → size →
check the price → **Agree & pay** → fake card → preparing → ready for pickup.

| Test card | Result |
|-----------|--------|
| `4242 4242 4242 4242` | Approved |
| `4000 0000 0000 0002` | Declined (you can retry) |

Use any future expiry (e.g. `12/30`) and any 3-digit CVC. The "preparing" screen
lasts `COFFEE_PREP_SECONDS` (default 10) from `.env`.

Edit the menu in the admin (`python manage.py createsuperuser`, then `/admin/`).

## Test & lint

```powershell
pytest                 # all tests
pytest -m "not e2e"    # skip browser tests
ruff check . ; ruff format .
```
