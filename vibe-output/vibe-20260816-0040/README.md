# README.md

## VibeFinance – Personal Finance Tracker  
**Version:** 0.1.0 (Draft)  
**Generated:** 2025‑09‑26  
**Status:** Draft  

> *A lightweight, mobile‑first web app that gives users a real‑time view of income, expenses, and net balance, with actionable insights and timely alerts.*

---

### Table of Contents
1. [Project Overview](#project-overview)  
2. [Features](#features)  
3. [Tech Stack](#tech-stack)  
4. [Setup & Installation](#setup--installation)  
5. [Running the Application](#running-the-application)  
6. [Usage Guide](#usage-guide)  
7. [API Documentation](#api-documentation)  
8. [Contributing](#contributing)  
9. [License](#license)  

---

## Project Overview
Many adults struggle to keep a simple, real‑time view of their personal finances, which leads to overspending, missed payments, and difficulty hitting savings goals. Existing tools are either too complex or lack actionable insights and timely alerts.

**VibeFinance** addresses this gap by providing:
- A clean expense dashboard with summary totals and a transaction log.  
- Real‑time updates for income, expenses, and net balance (today, week, month).  
- Optional dark mode and a mobile‑first responsive UI.  
- Alerts for upcoming bills and unusual spending patterns.  

The app is built as a single‑page web application (SPA) with a RESTful API backend.

---

## Features
| Feature | Description |
|---------|-------------|
| **Expense Dashboard & Transaction Log** | View total income, total expense, and net balance for selected periods (today, week, month). See a list of recent transactions. |
| **Income & Expense Entry** | Add, edit, or delete transactions with category, amount, date, and optional notes. |
| **Bill Reminders** | Set recurring bills; receive in‑app notifications when a payment is due. |
| **Spending Insights** | Simple charts showing category‑wise spend vs. budget; alerts when spending exceeds thresholds. |
| **Dark Mode** | Toggle light/dark theme persisted in localStorage. |
| **Responsive Design** | Optimized for mobile browsers; works on desktop as well. |
| **RESTful API** | Backend endpoints for CRUD operations on users, transactions, categories, and bills. |

---

## Tech Stack
- **Frontend:** React 18, TypeScript, Vite, Tailwind CSS, Recharts (charts)  
- **Backend:** Node.js 20, Express, TypeORM (PostgreSQL)  
- **Database:** PostgreSQL (dev: Docker‑compose)  
- **Authentication:** JWT‑based stateless auth (access token stored in httpOnly cookie)  
- **Testing:** Jest + React Testing Library (frontend), Supertest (backend)  
- **CI/CD:** GitHub Actions (lint, test, build)  

---

## Setup & Installation

### Prerequisites
- Node.js ≥ 20.x  
- npm ≥ 10.x or yarn ≥ 1.22.x  
- Docker & Docker‑Compose (for PostgreSQL)  
- Git  

### Clone the Repository
```bash
git clone https://github.com/your-org/vibefinance.git
cd vibefinance
```

### Environment Variables
Create a `.env` file at the project root (copy from `.env.example`):
```dotenv
# Server
PORT=5000
NODE_ENV=development
JWT_SECRET=your_super_secret_jwt_key
JWT_EXPIRES_IN=7d

# Database (PostgreSQL)
DB_HOST=localhost
DB_PORT=5432
DB_USERNAME=postgres
DB_PASSWORD=postgres
DB_NAME=vibefinance
```

### Install Dependencies
```bash
# Install root (monorepo) dependencies
npm install   # or yarn install

# Optional: install frontend/backend separately
cd client && npm install
cd ../server && npm install
```

### Start PostgreSQL (Docker)
```bash
docker-compose up -d db
```
*This spins up a PostgreSQL container defined in `docker-compose.yml`.*

### Run Database Migrations
```bash
# From the server directory
npm run typeorm migration:run
```

---

## Running the Application

### Development Mode (hot reload)
```bash
# Start both client and server concurrently
npm run dev   # defined in root package.json
```
- Client: http://localhost:5173  
- Server API: http://localhost:5000/api  

### Production Build
```bash
# Build client
npm run build:client   # creates dist/ in client/
# Build server (TS → JS)
npm run build:server   # creates dist/ in server/
# Start server (serves static client files)
npm start
```
The app will be accessible at http://localhost:5000.

### Running Tests
```bash
# Frontend
npm run test:client
# Backend
npm run test:server
# All
npm test
```

---

## Usage Guide

1. **Sign Up / Log In**  
   - Navigate to `/register` to create an account.  
   - After verification, log in via `/login`.  
   - JWT token is stored in an httpOnly cookie; subsequent requests are authenticated automatically.

2. **Dashboard**  
   - On landing (`/`), you see the **Expense Dashboard**: total income, total expense, net balance for the selected period (toggle Today/Week/Month).  
   - Below the summary, a list of the **10 most recent transactions** appears (click to edit/delete).

3. **Adding a Transaction**  
   - Click the **+** button (top‑right).  
   - Fill in: type (Income/Expense), category, amount, date, optional note.  
   - Press **Save** – the dashboard updates in real time.

4. **Managing Categories**  
   - Go to `/categories` to add, edit, or delete custom categories (e.g., “Groceries”, “Freelance”).  

5. **Bill Reminders**  
   - Visit `/bills` to create recurring bills (name, amount, day‑of‑month).  
   - Enable notifications; you’ll receive an in‑app toast 24 h before the due date.

6. **Dark Mode**  
   - Toggle the moon/sun icon in the header; preference persists via `localStorage`.

7. **Logging Out**  
   - Click your avatar → **Log Out** – clears the auth cookie.

---

## API Documentation
See the dedicated **[API.md](./API.md)** file for full endpoint specifications, request/response examples, and error codes.

---

## Contributing
We welcome contributions! Please follow these steps:

1. Fork the repository.  
2. Create a feature branch (`git checkout -b feat/awesome-feature`).  
3. Make your changes, ensuring lint (`npm run lint`) and tests pass.  
4. Submit a Pull Request with a clear description of the changes.  

Please adhere to the [Code of Conduct](./CODE_OF_CONDUCT.md) and respect the project's contribution guidelines.

---

## License
This project is licensed under the **MIT License** – see the [LICENSE](./LICENSE) file for details.

--- 

*Happy tracking!* 🚀