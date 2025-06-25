# LuluLLM

An intelligent AI assistant with specialized agents for stress management, decision making, lifestyle coaching, and general conversation.

## 🤖 Available Agents

- **🧘 Initial Stress Agent** - Immediate support for stress management and calming techniques
- **⚖️ Decision Making Agent** - Structured approach to making important life decisions  
- **🔍 Indecision Analyst** - Break through analysis paralysis and find clarity
- **🌟 Lifestyle Coach Agent** - Guidance for improving habits, wellness, and personal growth
- **💬 General Chat Agent** - Open conversations on any topic you'd like to discuss

## 🚧 Current Status

**Note: The deployment is currently being finalized. The live demo will be available soon!**

For now, you can run the application locally using the setup instructions below.

## 🛠️ Local Development Setup

### Prerequisites

- Python 3.10+
- Node.js 16+
- MongoDB (local installation or MongoDB Atlas account)
- OpenAI API key (get one at [OpenAI Platform](https://platform.openai.com/api-keys))
- Git

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/lulullm.git
   cd lulullm
   ```

2. **Navigate to backend directory**
   ```bash
   cd app/backend
   ```

3. **Install Python dependencies**
   ```bash
   # If using uv (recommended)
   uv sync
   
   # Or using pip
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the backend directory:
   ```env
   MONGO_URI=mongodb://localhost:27017/lulullm
   # Or use MongoDB Atlas connection string:
   # MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/lulullm
   
   OPENAI_API_KEY=your_openai_api_key_here
   ```

   **Getting an OpenAI API Key:**
   1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
   2. Sign up or log in to your account
   3. Click "Create new secret key"
   4. Copy the key and paste it in your `.env` file
   5. **Important:** Keep this key secure and never commit it to version control

5. **Run the backend server**
   ```bash
   # If using uv
   uv run python main.py
   
   # Or using python directly
   python main.py
   ```

   The backend will be available at `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd ../frontend  # From the backend directory
   # Or from project root: cd app/frontend
   ```

2. **Install Node.js dependencies**
   ```bash
   npm install
   ```

3. **Start the development server**
   ```bash
   npm start
   ```

   The frontend will be available at `http://localhost:3000`

## 📁 Project Structure

```
lulullm/
├── app/
│   ├── backend/                 # FastAPI backend
│   │   ├── api/
│   │   │   └── routes.py       # API endpoints
│   │   ├── agents/             # AI agent implementations
│   │   ├── storage/            # Database models and management
│   │   ├── main.py            # Application entry point
│   │   └── requirements.txt   # Python dependencies
│   └── frontend/              # React frontend
│       ├── src/
│       │   ├── App.js         # Main React component
│       │   └── App.css        # Styling
│       ├── public/
│       └── package.json       # Node.js dependencies
├── pyproject.toml             # Python project configuration
├── uv.lock                    # Dependency lock file
└── README.md
```

## 🚀 Usage

1. **Start both backend and frontend servers** (see setup instructions above)
2. **Open your browser** to `http://localhost:3000`
3. **Sign up for a new account** or sign in if you already have one
4. **Start chatting** with LuluLLM's specialized agents!

## 🔧 Configuration

### Backend Configuration

The backend can be configured through environment variables:

- `MONGO_URI` - MongoDB connection string
- `OPENAI_API_KEY` - Your OpenAI API key for AI agent functionality
- `PORT` - Server port (default: 8000)

### Frontend Configuration

Update the API URL in `app/frontend/src/App.js` if running backend on a different port:

```javascript
const API_BASE_URL = 'http://localhost:8000';  // Update if needed
```

## 🧪 Testing

### Backend Testing
```bash
cd app/backend
# Test the API endpoints
curl http://localhost:8000/
# Should return: {"message": "Welcome to the API!"}
```

### Frontend Testing
```bash
cd app/frontend
npm test
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Troubleshooting

### Common Issues

**Backend not starting:**
- Check if MongoDB is running
- Verify environment variables in `.env` file (especially `OPENAI_API_KEY`)
- Ensure all Python dependencies are installed
- Verify OpenAI API key is valid and has sufficient credits

**Frontend not connecting to backend:**
- Verify backend is running on `http://localhost:8000`
- Check API_BASE_URL in `App.js`
- Look for CORS errors in browser console

**AI agents not responding:**
- Verify `OPENAI_API_KEY` is set correctly in your `.env` file
- Check your OpenAI account has sufficient API credits
- Ensure the API key has the necessary permissions

**Database connection issues:**
- Verify MongoDB connection string
- Check if MongoDB service is running
- For MongoDB Atlas, ensure IP whitelist includes your IP

---

## 🌐 Live Demo

*Coming soon! The application is currently being deployed and will be available at a public URL shortly.*

For now, please use the local development setup above to try out LuluLLM.

---

**Need help?** Open an issue on GitHub or reach out to the development team.
