## Sigmoidal - AI based trading dashboard

End-to-end trading dashboard monorepo combining a FastAPI backend with ML-driven stock predictions and a Next.js frontend. Sigmoidal provides live quotes and history via Twelve Data, user auth and portfolio/trade management backed by Prisma (SQLite), and TensorFlow models for per-symbol price prediction.

### Apps and Packages
- `apps/api` (FastAPI + Prisma + TensorFlow): REST API, websockets, ML train/predict
- `apps/fe` (Next.js 15 + React 19): UI for market data, predictions, portfolio, trades
- `apps/docs` (Next.js): documentation site scaffold
- `packages/ui`, `packages/eslint-config`, `packages/typescript-config`: shared tooling and UI

### High-level Features
- Live market quotes and history via Twelve Data
- User signup/login with JWT
- Portfolio, positions, and trades with transactional updates
- Per-symbol ML models (TensorFlow/Keras) for next price prediction
- WebSocket hooks prepared for streaming updates

---

## Architecture

- Backend: FastAPI (`apps/api/src/main.py`) mounts routers:
  - `market` quotes/history: `/api/v1/market/...`
  - `predictions` train/predict/status: `/api/v1/predictions/...`
  - `portfolio` portfolio/positions/trades: `/api/v1/portfolio/...`
  - `users` signup/login/users: `/api/v1/users/...`
- Database: Prisma (SQLite file at `apps/api/accounts.db`) with migrations under `apps/api/prisma/migrations`.
- ML: Models and scalers live under `apps/api/src/models` and `apps/api/src/scalers` (mirrors also exist under top-level `apps/models` and `apps/scalers`).
- Frontend: Next.js app under `apps/fe` with pages for dashboard, positions, trades, predict, auth.

---

## API Overview

Base URL: `http://localhost:8080`

- Market (`/api/v1/market`)
  - `GET /quote/{symbol}` → current price
  - `GET /quote?symbols=AAPL,MSFT` → multi-price
  - `GET /history/{symbol}?period=1mo&interval=1d` → OHLCV history
- Predictions (`/api/v1/predictions`)
  - `GET /train/{symbol}` → train model for symbol
  - `GET /predict/{symbol}` → predict next value (requires trained model)
  - `GET /model/status/{symbol}` → check if model exists
- Users (`/api/v1/users`)
  - `POST /createUser` → register (email, password, username)
  - `POST /login` → returns JWT
  - `GET /allUsers`, `GET /{user_id}`
- Portfolio (`/api/v1/portfolio`) [requires `Authorization: <JWT>`]
  - `GET /myportfolio`, `GET /myportfolio/positions`, `GET /myportfolio/trades`
  - `POST /myportfolio/trade` → BUY/SELL at live market price, updates positions and portfolio, records trade

---

## Prerequisites

- Node.js 18+ and pnpm
- Python 3.12 (virtualenv used at `apps/api/venv`)
- Twelve Data API key

---

## Environment Variables

Create `.env` in `apps/api` with:

```
JWT_SECRET=replace_with_strong_secret
TWELVE_DATA_API_KEY=your_twelve_data_key
DATABASE_URL=file:./accounts.db
```

Frontend may need `NEXT_PUBLIC_API_URL` when deploying; for local dev it defaults to `http://localhost:8080` in most places.

---

## Install and Develop

From repo root:

```bash
pnpm install
```

### Backend (API)

```bash
# 1) Create/activate venv (already present in repo)
cd apps/api
source venv/bin/activate

# 2) Install Python deps
pip install -r requirements.txt

# 3) Generate Prisma client and apply migrations
venv/bin/prisma generate
venv/bin/prisma migrate deploy

# 4) Run API
pnpm --filter api run start  # or: uvicorn src.main:app --host 0.0.0.0 --port 8080
```

API will be available at `http://localhost:8080`.

### Frontend (FE)

```bash
cd apps/fe
pnpm dev
# open http://localhost:3000
```

---

## Quick Test (cURL)

```bash
# health
curl http://localhost:8080/

# price
curl "http://localhost:8080/api/v1/market/quote/AAPL"

# register and login
curl -X POST http://localhost:8080/api/v1/users/createUser \
  -H 'Content-Type: application/json' \
  -d '{"email":"a@b.com","password":"Passw0rd!","username":"alice"}'

TOKEN=$(curl -s -X POST http://localhost:8080/api/v1/users/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"a@b.com","password":"Passw0rd!"}' | jq -r .token)

# portfolio
curl -H "Authorization: $TOKEN" http://localhost:8080/api/v1/portfolio/myportfolio
```

---

## ML Models

- Pretrained models live in `apps/api/src/models`. Training and prediction are in `src/ml/model_train.py` and `src/ml/model_predict.py`.
- Train on demand via `GET /api/v1/predictions/train/{symbol}`; prediction via `GET /api/v1/predictions/predict/{symbol}`.
- Ensure data provider key is configured; training fetches market data internally.

---

## Monorepo Commands

Common pnpm scripts from root:

```bash
pnpm -w turbo run build
pnpm -w turbo run dev
```

Or run per app:

```bash
pnpm --filter fe dev
pnpm --filter api run start
```

---

## Notes

- CORS is open in development.
- SQLite is the default; switch `DATABASE_URL` to another provider if desired and update Prisma schema accordingly.
- WebSocket endpoints are registered in `src/websocket/ws.py` and mounted via `register_websocket(app)`.
