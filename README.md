# Keycloak Skeleton Project

## About

This is a simple starter application demonstrating React, FastAPI, and Keycloak integration for authentication and authorization. The project provides a foundation with comprehensive error handling, security best practices, and containerized deployment options. While suitable for proof-of-concept work, additional hardening would be needed for production environments.

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
- Nginx (for frontend production builds)

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
│   ├── Dockerfile
│   └── nginx.conf
├── .gitignore
└── README.md
```

## Getting Started

### 1. Clone the Repository

```bash
git clone <repository-url>
cd keycloak-skeleton
```

### 2. Environment Configuration

**Important**: Never commit `.env` files to version control. Use the provided `.env.example` files as templates.

Create a `.env` file in the backend directory based on `backend/.env.example`:

```bash
# Keycloak Admin Configuration
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=your-secure-password-here

# Keycloak Client Configuration
KEYCLOAK_SERVER_URL=http://keycloak:8080
KEYCLOAK_REALM=testrealm
KEYCLOAK_CLIENT_ID=test-client-id
KEYCLOAK_CLIENT_SECRET=your-client-secret-here

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

**Security Note**: Replace default passwords and secrets with secure values before deployment.

### 3. Build Docker Images

Build the backend image:
```bash
cd backend
docker build -t keycloak-skeleton-backend .
```

The frontend image will be built automatically by Docker Compose.

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

### 5. Install Frontend Dependencies (Development Only)

For local development:
```bash
cd frontend/app
npm install
```

## Running

### Option 1: Full Docker Compose (Recommended)

Start all services using Docker Compose:

```bash
cd backend
docker-compose up -d
```

This will start:
- Keycloak on http://localhost:8080
- FastAPI backend on http://localhost:8000
- React frontend on http://localhost:5173 (containerized)

All services will be fully containerized and production-ready.

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
cd frontend/app
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
- `POST /admin/refresh-keys` - Manually refresh Keycloak public keys (admin only)

**Health Check:**
- `GET /health` - Comprehensive health check with service status and Keycloak connectivity

### Stopping Services

To stop all Docker services:

```bash
cd backend
docker-compose down
```

## Features

### Security
- JWT token validation with public key verification
- Role-based access control (RBAC)
- Secure token refresh handling
- Environment-based configuration management
- Comprehensive `.gitignore` to prevent secret leakage

### Error Handling
- Structured error responses with appropriate HTTP status codes
- Graceful degradation for service failures
- User-friendly error messages in frontend
- Retry mechanisms for failed operations
- Comprehensive logging with appropriate levels

### Production Features
- Multi-stage Docker builds for optimized images
- Nginx reverse proxy with security headers
- Health check endpoints for monitoring
- Gzip compression and static asset caching
- TypeScript for type safety

### Development Experience
- Hot reloading for both frontend and backend
- Comprehensive error handling and debugging
- Clear separation of concerns
- Professional code structure and organization

## Security Considerations

- **Environment Variables**: Never commit `.env` files. Use strong, unique passwords and secrets.
- **Default Credentials**: Change all default passwords before deployment.
- **Token Security**: Tokens are automatically refreshed and properly validated.
- **CORS**: Configured for development; adjust for production domains.
- **Logging**: Sensitive information is logged at debug level only.

## Troubleshooting

### Common Issues

1. **Keycloak Connection Failed**: Ensure Keycloak is running and accessible at the configured URL.
2. **Token Validation Errors**: Check that the realm and client configuration match between Keycloak and the application.
3. **CORS Errors**: Verify that the frontend URL is properly configured in both Keycloak and the backend CORS settings.
4. **Port Conflicts**: Ensure ports 8080, 8000, and 5173 are available.

### Health Checks

Monitor service health using:
```bash
curl http://localhost:8000/health
```

This endpoint provides detailed status information for all services.