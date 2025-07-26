# VendorNet V2V Collaboration Platform - Backend

A Flask-based backend for the VendorNet V2V collaboration platform with MongoDB integration.

## Features

- **User Management**: Registration, login, JWT authentication
- **Listings**: Create, view, and filter product listings
- **Transactions**: Handle buy/sell, group buys, and lending
- **Chat System**: Real-time messaging between vendors
- **Feedback & Trust**: Rating system and trust score calculation
- **Analytics**: Platform statistics and user insights
- **Notifications**: Email/SMS alerts for matching listings

## Prerequisites

- Python 3.8+
- MongoDB 4.4+
- pip (Python package manager)

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd vendornet-backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up MongoDB**
   - Install MongoDB on your system
   - Start MongoDB service
   - Create database: `vendornet`

5. **Environment Configuration**
   Create a `.env` file in the root directory:
   ```env
   # Flask Configuration
   SECRET_KEY=your-super-secret-key-here
   JWT_SECRET_KEY=your-jwt-secret-key-here

   # MongoDB Configuration
   MONGODB_URI=mongodb://localhost:27017/
   DATABASE_NAME=vendornet

   # Email Configuration (optional)
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USE_TLS=true
   MAIL_USERNAME=your-email@gmail.com
   MAIL_PASSWORD=your-app-password

   # SMS Configuration (optional)
   TWILIO_ACCOUNT_SID=your-twilio-account-sid
   TWILIO_AUTH_TOKEN=your-twilio-auth-token
   TWILIO_PHONE_NUMBER=+1234567890
   ```

6. **Run the application**
   ```bash
   python app.py
   ```

The server will start on `http://localhost:5000`

## API Endpoints

### Authentication
- `POST /api/register` - User registration
- `POST /api/login` - User login

### Listings
- `GET /api/listings` - Get all listings (with filters)
- `POST /api/listings` - Create new listing
- `GET /api/listings/<id>` - Get specific listing

### Transactions
- `POST /api/transactions` - Create transaction
- `PUT /api/transactions/<id>/complete` - Complete transaction

### Chat
- `POST /api/chat` - Send message
- `GET /api/chat/<user_id>` - Get chat history

### Feedback
- `POST /api/feedback` - Submit feedback

### Analytics
- `GET /api/analytics` - Get platform analytics

### Users
- `GET /api/users/<id>` - Get user details

## Database Schema

### Users Collection
```json
{
  "_id": "ObjectId",
  "name": "string",
  "email": "string",
  "password": "string (hashed)",
  "company": "string",
  "location": "string",
  "phone": "string",
  "trust_score": "number",
  "total_transactions": "number",
  "created_at": "datetime"
}
```

### Listings Collection
```json
{
  "_id": "ObjectId",
  "user_id": "ObjectId",
  "type": "string (Offer/Need)",
  "product": "string",
  "quantity": "number",
  "location": "string",
  "city": "string",
  "pincode": "string",
  "collaboration_type": "string",
  "validity_time": "datetime",
  "urgency": "string",
  "description": "string",
  "status": "string",
  "created_at": "datetime"
}
```

### Transactions Collection
```json
{
  "_id": "ObjectId",
  "buyer_id": "ObjectId",
  "seller_id": "ObjectId",
  "listing_id": "ObjectId",
  "type": "string",
  "quantity": "number",
  "amount": "number",
  "status": "string",
  "payment_method": "string",
  "logistics": "object",
  "created_at": "datetime",
  "completed_at": "datetime"
}
```

## Usage Examples

### Register a new user
```bash
curl -X POST http://localhost:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Vendor A",
    "email": "vendor@example.com",
    "password": "password123",
    "company": "ABC Company",
    "location": "Mumbai, India",
    "phone": "+91-1234567890"
  }'
```

### Login
```bash
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "vendor@example.com",
    "password": "password123"
  }'
```

### Create a listing
```bash
curl -X POST http://localhost:5000/api/listings \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-jwt-token>" \
  -d '{
    "type": "Offer",
    "product": "Power Bank",
    "quantity": 20,
    "location": "Nagpur, India",
    "city": "Nagpur",
    "pincode": "440001",
    "collaboration_type": "Sell",
    "validity_time": "2024-01-15T10:00:00Z",
    "urgency": "medium",
    "description": "20 power banks at ₹300/unit – in-stock, pick-up ready."
  }'
```

## Development

### Running in Development Mode
```bash
export FLASK_ENV=development
python app.py
```

### Testing
```bash
# Install test dependencies
pip install pytest pytest-flask

# Run tests
pytest
```

## Deployment

### Using Gunicorn (Production)
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Using Docker
```bash
# Build image
docker build -t vendornet-backend .

# Run container
docker run -p 5000:5000 vendornet-backend
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support, email support@vendornet.com or create an issue in the repository. 