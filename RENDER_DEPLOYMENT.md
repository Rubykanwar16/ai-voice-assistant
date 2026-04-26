# Ruby Voice Assistant - Render.com Deployment Guide

## Prerequisites
1. GitHub account with your repository pushed
2. Render.com account (free tier available)
3. Groq API key from https://console.groq.com/keys
4. OpenWeather API key (optional) from https://openweathermap.org/api

## Deployment Steps

### 1. Push Code to GitHub
```bash
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

### 2. Create Render Account
- Go to https://render.com
- Sign up with GitHub
- Authorize GitHub access

### 3. Create New Web Service
1. Click "New +" → "Web Service"
2. Connect your GitHub repository
3. Select the `ai-voice-assistant` repository
4. Fill in the following:
   - **Name:** ruby-voice-assistant (or your choice)
   - **Environment:** Python 3
   - **Region:** Choose closest to you
   - **Branch:** main
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn -w 2 -b 0.0.0.0:$PORT web_app:app`
   - **Plan:** Free tier

### 4. Add Environment Variables
After creating the service, go to **Settings** → **Environment**

Add these variables:
- **GROQ_API_KEY:** Your Groq API key
- **WEATHER_API_KEY:** Your OpenWeather API key (optional)

### 5. Deploy
- Click "Create Web Service"
- Render will automatically build and deploy
- Wait for "Your service is live" message
- Your app URL will be shown (e.g., `https://ruby-voice-assistant.onrender.com`)

### 6. Test Your Deployment
1. Open the URL in Chrome or Edge browser
2. Allow microphone permissions
3. Click 🎤 microphone button to test

## Important Notes

### Free Tier Limitations
- Service spins down after 15 minutes of inactivity (cold start = ~30 seconds first load)
- Limited to 100 hours/month
- Suitable for testing and low-traffic apps

### Production Recommendations
- Upgrade to **Paid plan** for production use
- Use **PostgreSQL** for conversation history storage (optional)
- Add **error monitoring** (Sentry integration available)
- Set up **automatic deployments** from GitHub

### Troubleshooting

**Service won't start:**
- Check Build Logs for errors
- Verify all dependencies in requirements.txt
- Ensure GROQ_API_KEY is set in Environment Variables

**Microphone not working:**
- Ensure you're using HTTPS (Render provides this)
- Check browser permissions
- Use Chrome or Edge browser
- Allow microphone access when prompted

**Slow response time:**
- Free tier has cold starts (first request after inactivity)
- Consider upgrading to paid plan for production
- Groq API calls add 1-2 seconds delay (normal)

**Audio playback issues:**
- Check browser console for CORS errors
- Verify edge-tts is working (upgraded to 7.2.8)
- Try different voice selections

## Environment Variables Reference

```
GROQ_API_KEY=your_groq_api_key_here
WEATHER_API_KEY=your_weather_api_key_here (optional)
PORT=auto (Render sets this automatically)
```

## File Structure After Deployment

```
ai-voice-assistant/
├── Procfile              # Render startup config
├── render.yaml           # Alternative Render config
├── web_app.py           # Flask app (main entry)
├── requirements.txt     # Python dependencies (with Gunicorn)
├── main.py              # Menu system (not used on Render)
├── cli.py               # CLI mode (not used on Render)
├── tools.py             # AI tools/functions
├── templates/
│   └── index.html       # Web UI
├── .env                 # Local config (don't commit)
├── .env.example         # Template
└── README.md            # Documentation
```

## Post-Deployment

### Enable Auto-Deploys (Recommended)
1. Go to Service Settings
2. Scroll to "Auto-Deploy"
3. Select "Yes" to auto-deploy on push to main

### Monitor Logs
- Click "Logs" tab to see real-time logs
- Check for errors after each request
- Monitor API usage

### Database Setup (Optional)
For production conversation history:
1. Add PostgreSQL database
2. Update web_app.py to use database
3. Set DATABASE_URL environment variable

## Cost Estimation (Free Tier)
- **Monthly cost:** $0 (free tier)
- **Includes:** 100 hours compute, shared CPU, 500MB disk
- **Good for:** Development, testing, low-traffic apps

## Next Steps
1. Deploy using the steps above
2. Share your Render URL with others
3. Monitor performance and logs
4. Consider upgrading for production use
