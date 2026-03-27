# 🚀 Smart Solar AI - Quick Setup Guide

## ⚡ 5-Minute Setup

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Run the App
```bash
streamlit run streamlit_app.py
```

### Step 3: Access the App
```
Open browser: http://localhost:8501
```

### Step 4: Login
```
Username: admin
Password: admin123
```

---

## 🌐 Deploy to Streamlit Cloud (FREE)

### Step 1: Create GitHub Repo
```bash
git init
git add .
git commit -m "Smart Solar AI Platform"
git push origin main
```

### Step 2: Go to Streamlit Cloud
- Visit: https://streamlit.io/cloud
- Click "New App"
- Select your GitHub repo
- Main file: `streamlit_app.py`
- Click "Deploy"

### Step 3: Share URL
Your app gets a public URL like:
```
https://your-username-smart-solar-ai.streamlit.app
```

**✅ Done! Share this link with anyone!**

---

## 📊 What to Try First

1. **Login** → Use demo credentials
2. **Upload Data** → Use sample CSV/Excel
3. **Create KPI** → Add a custom metric
4. **Generate Forecast** → Predict future values
5. **AI Chat** → Ask questions about data
6. **Download Report** → Get PDF/Excel

---

## 🔑 Demo Accounts

| User | Password | Role |
|------|----------|------|
| admin | admin123 | Admin |
| demo1 | password123 | User |
| demo2 | password123 | Manager |

---

## 🛠️ Environment Variables (for AI Chat)

### Local Development:
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
streamlit run streamlit_app.py
```

### Streamlit Cloud:
1. Go to App Settings
2. Secrets
3. Add: `ANTHROPIC_API_KEY = "sk-ant-..."`

---

## 📂 File Structure

```
smart-solar-ai/
├── streamlit_app.py          # Main application
├── requirements.txt          # Python dependencies
├── smart_solar_ai.db         # SQLite database
├── README.md                 # Full documentation
└── SETUP.md                  # This file
```

---

## ✨ Key Features Ready to Use

- ✅ Secure login with role-based access
- ✅ Smart data upload with auto-cleaning
- ✅ Custom KPI builder
- ✅ Predictive analytics (forecasting)
- ✅ Anomaly detection (outlier finding)
- ✅ AI chat assistant (Claude)
- ✅ Report generation (PDF/Excel)
- ✅ Multi-industry support
- ✅ User management
- ✅ Activity logging

---

## 🎯 Use Cases

**Solar Industry:**
- Track panel efficiency
- Forecast energy production
- Detect equipment failures
- Monitor temperature variations

**Manufacturing:**
- Predict production output
- Optimize inventory levels
- Detect quality issues
- Track equipment performance

**Logistics:**
- Forecast delivery times
- Optimize routes
- Track shipments
- Analyze performance

**Retail:**
- Predict sales trends
- Manage inventory
- Analyze customer behavior
- Forecast demand

---

## 🆘 Troubleshooting

### App won't start?
```bash
pip install --upgrade -r requirements.txt
streamlit run streamlit_app.py
```

### Database error?
```bash
rm smart_solar_ai.db
streamlit run streamlit_app.py
```

### Login not working?
- Use default credentials: admin / admin123
- Database will be created automatically

---

## 📞 Support

### Common Issues:
- **Port already in use:** `streamlit run streamlit_app.py --logger.level=debug`
- **Memory issues:** Use smaller CSV files
- **Slow forecasting:** Reduce number of periods

### Documentation:
- See `README.md` for full documentation
- Check Streamlit docs: https://docs.streamlit.io

---

## 🎉 Success Checklist

- ✅ Dependencies installed
- ✅ App runs without errors
- ✅ Can login with demo account
- ✅ Can upload CSV/Excel file
- ✅ Dashboard shows data
- ✅ Can create KPI
- ✅ Can generate forecast
- ✅ Can create report

**If all checked: You're ready to deploy! 🚀**

---

## 🚀 Ready to Deploy?

### Fastest Option (Streamlit Cloud - 2 minutes):
1. Push to GitHub
2. Go to https://streamlit.io/cloud
3. Connect your repo
4. Deploy
5. Share URL

### Command Line (Local):
```bash
streamlit run streamlit_app.py
```

### Docker:
```bash
docker build -t smart-solar-ai .
docker run -p 8501:8501 smart-solar-ai
```

---

**Questions? See README.md for detailed documentation!**
