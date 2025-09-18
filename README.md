# HEMIS - Hospital Equipment Management Information System

HEMIS is a comprehensive hospital equipment management system designed to monitor and manage medical equipment, patient data, and telemetry information in real-time.

## Architecture

The system consists of three main components:

- **Frontend**: React-based web application built with Vite
- **Backend**: Flask-based REST API with WebSocket support
- **Database**: MySQL database with role-based access control

## Features

### Core Functionality
- Real-time telemetry monitoring with IoT device integration
- Patient management system with role-based access
- Equipment tracking and management
- Vital signs simulation with three states (normal, critical, death)
- WebSocket-based real-time updates
- Hospital-style monitoring dashboard

### Security & Performance
- Role-based authentication and authorization
- Rate limiting with Redis fallback
- Cookie-based session management
- CORS protection
- Input validation and sanitization
- Multi-user support with different permission levels

## Technology Stack

### Frontend
- React 19
- TypeScript
- Vite
- Material-UI
- Tailwind CSS
- Socket.IO Client

### Backend
- Flask
- Python 3.12
- Gunicorn (production WSGI server)
- Flask-SocketIO
- Flask-Limiter
- PyMySQL
- Redis (optional, for rate limiting)

### Database
- MySQL 8.0
- Role-based user permissions

## Project Structure

```
hemis/
├── frontend/          # React TypeScript frontend
│   ├── src/
│   │   ├── components/    # Reusable UI components
│   │   ├── features/      # Feature-specific modules
│   │   │   ├── auth/      # Authentication features
│   │   │   ├── dashboard/ # Dashboard components
│   │   │   ├── patients/  # Patient management
│   │   │   └── telemetry/ # IoT monitoring features
│   │   ├── services/      # API service layer
│   │   └── types/         # TypeScript definitions
│   ├── package.json
│   └── vite.config.ts
├── backend/           # Flask backend API
│   ├── app/
│   │   ├── auth/          # Authentication modules
│   │   ├── db/            # Database layer
│   │   ├── models/        # Data models
│   │   ├── routes/        # API endpoints
│   │   └── services/      # Business logic
│   ├── requirements.txt
│   └── wsgi.py
├── database/          # Database setup and migrations
└── compose.yml        # Root docker-compose configuration
```

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Node.js 20+ (for local development)
- Python 3.12+ (for local development)
- MySQL 8.0+

### Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd hemis
   ```

2. **Configure environment variables**
   ```bash
   cp config.template .env
   # Edit .env with your database credentials and settings
   ```

3. **Start the database**
   ```bash
   cd database
   docker-compose up -d
   ```

4. **Run database migrations**
   ```bash
   # Follow database setup instructions in database/README.md
   ```

5. **Start the backend**
   ```bash
   cd backend
   make dev
   ```

6. **Start the frontend**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

### Production Deployment

1. **Build and deploy with Docker Compose**
   ```bash
   # Frontend
   cd frontend
   docker-compose up -d

   # Backend
   cd backend
   docker-compose up -d
   ```

2. **Configure reverse proxy (Nginx)**
   - Set up Nginx to proxy requests to frontend (port 5173) and backend (port 5000)
   - Configure SSL certificates for HTTPS

## Configuration

### Environment Variables

Key environment variables that need to be configured:

- `DB_HOST`, `DB_PORT`, `DB_NAME`: Database connection
- `DB_USER`, `DB_PASSWORD`: Database credentials
- `SECRET_KEY`: Flask secret key for sessions
- `REDIS_HOST`, `REDIS_PORT`: Redis configuration (optional)
- `CORS_ORIGINS`: Allowed origins for CORS

### Database Users

The system supports multiple database users with different permission levels:

- `super_admin`: Full system access
- `admin_medical`: Medical data management
- `admin_hr`: Human resources management
- `admin_finance`: Financial data access
- `admin_system`: System and equipment management
- `doctor`: Patient and medical record access (primary medic role)
- `nurse`: Patient care data
- `reception`: Basic patient information
- `coordinator`: Medical coordination

### Default Test Credentials

For development and testing, the following credentials are available (password: `admin123`):

- `superadmin@clinic.test` - Super Admin
- `medical.admin@clinic.test` - Medical Admin
- `greg.house@clinic.test` - Doctor (Medic Role)
- `nurse1@clinic.test` - Nurse
- `reception1@clinic.test` - Reception

## API Documentation

### Authentication Endpoints
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `GET /api/auth/me` - Get current user info
- `GET /api/auth/validate` - Validate session

### Patient Management
- `GET /api/patients` - List patients
- `POST /api/patients` - Create patient
- `GET /api/patients/{id}` - Get patient details
- `PUT /api/patients/{id}` - Update patient

### Telemetry Endpoints
- `GET /api/telemetry` - Get telemetry data
- `POST /api/telemetry` - Submit telemetry data
- `GET /api/vital-signs` - Get vital signs data

### WebSocket Events
- `telemetry_update` - Real-time telemetry updates
- `vital_signs_update` - Vital signs updates
- `authenticate` - WebSocket authentication
- `join_telemetry_room` - Join patient/device monitoring room
- `leave_telemetry_room` - Leave monitoring room

### IoT Telemetry Focus
- **Real Device Integration**: Heart rate, oxygen saturation, body temperature
- **Simulation Mode**: Three-state simulation (normal, critical, death)
- **Real-time Display**: Hospital-style monitoring dashboard
- **Data Storage**: Historical telemetry data for analysis

## Development Commands

### Backend
```bash
make dev      # Start development server (Flask)
make prod     # Start production server (Gunicorn)
make install  # Install dependencies
make test     # Run tests
make lint     # Code linting
make format   # Code formatting
```

### Frontend
```bash
npm run dev     # Start development server (Vite)
npm run build   # Build for production
npm run preview # Preview production build
npm run lint    # Code linting
```

### Development Workflow
- **Backend**: Flask development server on port 5000
- **Frontend**: Vite dev server on port 5173
- **Database**: MySQL on port 3306
- **API**: RESTful endpoints with cookie authentication
- **Real-time**: WebSocket for live data updates

## Security Features

- Rate limiting with Redis fallback
- CORS protection
- Session management
- Role-based access control
- Non-root Docker containers
- Input validation and sanitization

## Monitoring and Logging

- Application logs written to files in production
- Health check endpoints for monitoring
- Structured logging with configurable levels
- Error tracking and reporting

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions, please create an issue in the repository or contact the development team.
