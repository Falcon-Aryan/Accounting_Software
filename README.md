# Accounting Software

A full-stack accounting software solution with a modern frontend built with Nuxt.js and a robust backend powered by Python. Features Firebase authentication and real-time data synchronization.

## Project Structure

- `frontend/` - Nuxt.js based frontend application
- `backend/` - Python backend application
  - `app/` - Main application code
  - `data/` - Default templates and user data
  - `config/` - Configuration files

## Features

- **User Management**
  - Firebase Authentication
  - User-specific data isolation
  - Role-based access control

- **Company Settings**
  - Company profile management
  - Tax ID validation (SSN/EIN)
  - Auto-formatting for tax IDs
  - Address management

- **Advanced Settings**
  - Fiscal year configuration
  - Accounting method selection
  - Chart of accounts customization
  - Currency and format preferences

- **Chart of Accounts**
  - Hierarchical account structure
  - Account type categorization
  - Balance tracking
  - Default templates

- **Customer Management**
  - Customer profiles
  - Contact information
  - Transaction history

- **Product Management**
  - Product catalog
  - Service offerings
  - Pricing management

## Technology Stack

### Frontend
- Nuxt.js 3
- Vue.js 3 (Composition API)
- TailwindCSS
- TypeScript

### Backend
- Python 3.x
- Flask
- Firebase Admin SDK

### Database
- Firebase Realtime Database
- Local JSON storage

## Getting Started

### Prerequisites
- Node.js 16+
- Python 3.8+
- Firebase account

### Installation

1. Clone the repository
```bash
git clone https://github.com/Falcon-Aryan/Accounting_Software.git
cd Accounting_Software
```

2. Frontend Setup
```bash
cd frontend
npm install
cp .env.example .env  # Configure your environment variables
npm run dev
```

3. Backend Setup
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env  # Configure your environment variables
python run.py
```

4. Firebase Setup
- Create a Firebase project
- Enable Authentication
- Download service account key to `backend/config/serviceAccountKey.json`
- Update environment variables in both frontend and backend

## Development

### Code Organization
- Frontend uses Nuxt.js directory structure
- Backend follows Flask blueprint pattern
- User data is isolated in `backend/data/{uid}/` directories
- Default templates in `backend/data/defaults/`

### Data Flow
1. User authenticates via Firebase
2. Backend validates Firebase token
3. User-specific data stored in isolated directories
4. Real-time updates via Firebase events

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
[MIT](https://choosealicense.com/licenses/mit/)
