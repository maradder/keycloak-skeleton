# Keycloak Skeleton Project

## About

This is a simple starter app with React, FastAPI, and Keycloak for authentication. It provides a basic setup to demonstrate how we can integrate keycloak into our application for user authentication and authorization. This is only intended to help solve some of the initial integration challenges and is definitely not a production-ready solution.

## Dependencies

### Backend
- Python 3.12+
- FastAPI
- python-jose (JWT handling)
- requests
- python-dotenv

### Frontend
- Node.js 22+
- React 19
- TypeScript
- Vite
- @react-keycloak/web
- axios
- react-router-dom

### Infrastructure
- Docker and Docker Compose
- Keycloak 21.0.0

## Project Structure

```
keycloak-skeleton
├── backend
│   ├── app
│   │   ├── __init__.py
│   │   ├── dependencies
│   │   │   ├── __init__.py
│   │   │   └── keycloak.py
│   │   ├── main.py
│   │   ├── models
│   │   │   ├── __init__.py
│   │   │   └── user.py
│   │   └── routes
│   │       ├── __init__.py
│   │       ├── admin.py
│   │       ├── auth.py
│   │       └── health.py
│   ├── docker-compose.yml
│   ├── Dockerfile
│   └── requirements.txt
├── frontend
│   ├── app
│   │   ├── eslint.config.js
│   │   ├── index.html
│   │   ├── package-lock.json
│   │   ├── package.json
│   │   ├── public
│   │   │   └── vite.svg
│   │   ├── README.md
│   │   ├── src
│   │   │   ├── App.css
│   │   │   ├── App.tsx
│   │   │   ├── assets
│   │   │   │   └── react.svg
│   │   │   ├── components
│   │   │   │   ├── navbars
│   │   │   │   │   └── NavigationBar.tsx
│   │   │   │   └── protectedRoute
│   │   │   │       └── ProtectedRoute.tsx
│   │   │   ├── index.css
│   │   │   ├── lib
│   │   │   │   ├── context
│   │   │   │   │   └── AuthContext.tsx
│   │   │   │   ├── hooks
│   │   │   │   │   ├── useApi.tsx
│   │   │   │   │   ├── useAuthContext.tsx
│   │   │   │   │   └── useKeycloak.tsx
│   │   │   │   ├── services
│   │   │   │   │   └── api.ts
│   │   │   │   └── utilities
│   │   │   │       └── keycloak.ts
│   │   │   ├── main.tsx
│   │   │   ├── pages
│   │   │   │   ├── dashboard
│   │   │   │   │   └── Dashboard.tsx
│   │   │   │   └── userProfile
│   │   │   │       └── UserProfile.tsx
│   │   │   └── vite-env.d.ts
│   │   ├── tsconfig.app.json
│   │   ├── tsconfig.json
│   │   ├── tsconfig.node.json
│   │   └── vite.config.ts
│   └── Dockerfile -- This isn't implemented yet
└── README.md
```

## Getting Started

### 1. Clone the Repository

```bash
git clone <repository-url>
cd keycloak-skeleton
```

### 2. Environment Configuration

Create a `.env` file in the backend directory:

```bash
# Keycloak Admin Configuration
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=admin123

# Keycloak Client Configuration
KEYCLOAK_SERVER_URL=http://keycloak:8080
KEYCLOAK_REALM=testrealm
KEYCLOAK_CLIENT_ID=test-client-id
KEYCLOAK_CLIENT_SECRET=your-client-secret

# FastAPI Configuration
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8000
FASTAPI_RELOAD=true
```

Create a `.env` file in the frontend directory:

```bash
VITE_API_BASE_URL=http://localhost:8000
VITE_AUTH_SERVER_BASE_URL=http://localhost:8080
```

### 3. Build Backend Docker Image

```bash
docker build -t keycloak-skeleton-backend .
```

### 4. Configure Keycloak

Start Keycloak and configure the realm:

```bash
docker-compose up keycloak -d
```

1. Access Keycloak Admin Console at http://localhost:8080
2. Login with the admin credentials from your `.env` file
3. Create a new realm called `testrealm`
4. Create a client with ID `test-client-id`
5. Configure client settings:
   - Client Protocol: `openid-connect`
   - Access Type: `public`
   - Valid Redirect URIs: `http://localhost:5173/*`
   - Web Origins: `http://localhost:5173`

### 5. Install Frontend Dependencies

```bash
npm install
```

## Running

### Option 1: Docker Compose (Recommended)

Start all services using Docker Compose:

```bash
docker-compose up -d
```

This will start:
- Keycloak on http://localhost:8080
- FastAPI backend on http://localhost:8000

Then start the frontend development server:

```bash
npm run dev
```

The frontend will be available at http://localhost:5173

### Option 2: Local Development

Start Keycloak with Docker:

```bash
docker-compose up keycloak -d
```

Run the backend locally:

```bash
# Install Python dependencies
pip install -r requirements.txt

# Start FastAPI development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Run the frontend locally:

```bash
# Start development server
npm run dev
```

### Available Endpoints

After starting the services, the following endpoints are available:

**Authentication Routes:**
- `GET /auth/protected-endpoint` - Protected endpoint requiring authentication
- `GET /auth/user-info` - Get detailed user information
- `POST /auth/logout` - Logout with token revocation

**Admin Routes:**
- `GET /admin/admin-only` - Admin-only endpoint (requires admin role)

**Health Check:**
- `GET /health` - Health check with Keycloak connectivity test

### Stopping Services

To stop all Docker services:

```bash
docker-compose down
```