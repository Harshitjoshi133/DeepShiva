# Deep-Shiva Database Setup Guide

This guide will help you set up and connect the Deep-Shiva backend to your Neon PostgreSQL database.

## Prerequisites

- Python 3.8+
- Neon PostgreSQL database (DATABASE_URL in .env file)
- Required Python packages (see requirements.txt)

## Quick Setup

### Option 1: Automated Setup (Windows)
```bash
# Run the setup script
setup_database.bat
```

### Option 2: Manual Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Initialize Database**
   ```bash
   python init_db.py
   ```

3. **Start the Server**
   ```bash
   python run.py
   ```

## Database Schema

The database includes the following main tables:

### Core Tables
- **users** - User profiles and preferences
- **chats** - Chat sessions
- **chat_messages** - Individual messages and AI responses

### Content Tables
- **cultural_sites** - Cultural heritage sites and temples
- **artisans** - Local artisan profiles
- **artisan_products** - Products created by artisans
- **tourism_places** - Tourist destinations and attractions
- **yoga_poses** - Yoga pose database with instructions
- **emergency_contacts** - Emergency services by district

### Analytics
- **dashboard_metrics** - System metrics and analytics data

## API Endpoints

Once the database is set up, you can access these endpoints:

### Database Stats
- `GET /api/v1/database/stats/overview` - Complete database statistics
- `GET /api/v1/database/stats/recent-activity` - Recent chat activity
- `GET /api/v1/database/health` - Database health check

### Data Access
- `GET /api/v1/database/users` - List users
- `GET /api/v1/database/cultural-sites` - List cultural sites
- `GET /api/v1/database/artisans` - List artisans
- `GET /api/v1/database/artisan-products` - List artisan products
- `GET /api/v1/database/tourism-places` - List tourism places

## Sample Data

The setup includes comprehensive sample data:

- **5 sample users** with different preferences
- **5 cultural sites** including Kedarnath, Badrinath, Haridwar
- **5 artisans** with different specializations
- **7 artisan products** showcasing local crafts
- **5 tourism places** including Valley of Flowers, Nainital
- **5 yoga poses** with detailed instructions
- **12 emergency contacts** across different districts
- **Sample chat conversations** for testing

## Database Utilities

### Check Database Status
```bash
python db_utils.py
```

### Manual Database Operations
```python
from db_utils import DatabaseUtils

with DatabaseUtils() as db:
    # Get statistics
    user_stats = db.get_user_stats()
    chat_stats = db.get_chat_stats()
    
    # Update metrics
    db.update_dashboard_metrics()
```

## Environment Configuration

Ensure your `.env` file contains:
```
DATABASE_URL='postgresql://username:password@host:port/database?sslmode=require'
```

## Troubleshooting

### Connection Issues
1. Verify DATABASE_URL is correct
2. Check Neon database is active
3. Ensure SSL mode is properly configured

### Permission Issues
1. Verify database user has CREATE/INSERT permissions
2. Check if tables already exist

### Import Errors
1. Install all requirements: `pip install -r requirements.txt`
2. Ensure you're in the server directory
3. Check Python path includes the app module

## Testing the Setup

1. **Start the server:**
   ```bash
   python run.py
   ```

2. **Check API documentation:**
   Visit `http://localhost:8000/docs`

3. **Test database endpoint:**
   Visit `http://localhost:8000/api/v1/database/health`

4. **View dashboard stats:**
   Visit `http://localhost:8000/api/v1/database/stats/overview`

## Next Steps

After successful database setup:

1. **Frontend Integration** - Update frontend to use database endpoints
2. **Authentication** - Add user authentication system
3. **Real-time Features** - Implement WebSocket for live chat
4. **File Upload** - Add image upload for artisan products
5. **Search & Filtering** - Implement advanced search capabilities

## Support

If you encounter issues:
1. Check the console output for detailed error messages
2. Verify your Neon database connection
3. Ensure all dependencies are installed
4. Check the FastAPI logs for API-related issues