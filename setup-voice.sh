#!/bin/bash

echo "🎤 Setting up Babelfish Voice System..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

echo "✅ Python found: $(python3 --version)"

# Install backend dependencies
echo "📦 Installing backend dependencies..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "🔧 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install requirements
echo "📥 Installing Python packages..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    cat > .env << EOF
# Rime Voice AI (get from https://rime.ai)
RIME_API_KEY=your_rime_api_key_here

# AWS Services (for transcription)
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=us-east-1

# MongoDB (optional)
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=babelfish

# Tavily Search (optional)
TAVILY_API_KEY=your_tavily_api_key

# ClickHouse (optional)
CLICKHOUSE_HOST=localhost
CLICKHOUSE_USER=default
CLICKHOUSE_PASSWORD=
EOF
    echo "⚠️  Please edit backend/.env and add your API keys"
else
    echo "✅ .env file already exists"
fi

cd ..

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
npm install

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit backend/.env and add your API keys"
echo "2. Start the backend: cd backend && python main.py"
echo "3. Start the frontend: npm run dev"
echo "4. Test voice: Open browser console and run testVoice()"
echo ""
echo "For troubleshooting, see AUDIO_TROUBLESHOOTING.md" 