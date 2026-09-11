# 🎨 Frontend - AI Recruiting Dashboard

Beautiful, modern, and functional dashboard for the AI Recruiting System.

## 📸 Features

### ✅ Dashboard View
- **Real-time Statistics**: Total candidates, jobs, interviews, vector store
- **System Status**: Agent status, MCP tools, database connection
- **Beautiful Cards**: Gradient-styled stat cards with icons

### ✅ Jobs Management
- **Job Listings**: View all job postings with details
- **Job Status**: Active/closed status indicators
- **Skills Display**: Visual skill tags
- **Match Count**: See how many candidates match each job

### ✅ Candidates Management
- **Candidate Cards**: Name, email, skills, experience
- **Match Scores**: AI-calculated matching scores
- **Skills Tags**: Visual representation of candidate skills
- **Status Tracking**: Pending, shortlisted, rejected, hired

### ✅ Interviews
- **Interview Schedule**: All scheduled interviews
- **Status Tracking**: Scheduled, completed, cancelled
- **Meeting Links**: Direct links to video meetings
- **Time Display**: Interview date, time, and duration

### ✅ Upload Resume
- **Drag & Drop**: Easy file upload in header
- **Real-time Processing**: Watch as AI processes the resume
- **Instant Feedback**: Notifications for success/errors
- **Auto-matching**: Jobs automatically matched after upload

## 🚀 Quick Start

### Option 1: Standalone HTML (Easiest)

1. **Open the file directly**:
   ```bash
   # Just open in browser
   open frontend/index.html
   # OR
   start frontend/index.html  # Windows
   ```

2. **Make sure API is running**:
   ```bash
   python main.py
   ```

3. **Access dashboard**: The HTML file will connect to `http://localhost:8000`

### Option 2: Served by FastAPI

1. **Start the backend**:
   ```bash
   python main.py
   ```

2. **Open browser**:
   ```
   http://localhost:8000
   ```

The backend will serve the frontend automatically!

## 🎨 Design Features

### Modern UI/UX
- ✅ Gradient backgrounds and cards
- ✅ Smooth animations and transitions
- ✅ Responsive design (mobile-friendly)
- ✅ Toast notifications
- ✅ Loading states
- ✅ Hover effects

### Color Scheme
- **Primary**: Blue (#3B82F6)
- **Secondary**: Purple (#8B5CF6)
- **Success**: Green (#10B981)
- **Warning**: Orange (#F59E0B)
- **Error**: Red (#EF4444)

### Typography
- **Font**: System fonts (Tailwind default)
- **Headings**: Bold, clear hierarchy
- **Body**: Clean, readable

## 📱 Responsive Design

The dashboard works perfectly on:
- 💻 Desktop (1920px+)
- 💻 Laptop (1024px+)
- 📱 Tablet (768px+)
- 📱 Mobile (320px+)

## 🔧 Customization

### Change API URL

Edit the `API_BASE` constant in `index.html`:

```javascript
const API_BASE = 'http://your-api-url:8000';
```

### Change Colors

Update Tailwind classes in the components. For example:

```javascript
// Change primary color from blue to green
className="bg-blue-600"  // Change to
className="bg-green-600"
```

### Add New Tabs

1. Add to navigation array:
```javascript
{ id: 'settings', label: 'Settings', icon: Settings }
```

2. Create new view component:
```javascript
function SettingsView() {
    return <div>Settings content</div>;
}
```

3. Add to main render:
```javascript
{!loading && activeTab === 'settings' && <SettingsView />}
```

## 🎯 Usage Guide

### 1. Upload Resume

1. Click "Upload Resume" button in header
2. Select PDF or DOCX file
3. Wait for processing (shows spinner)
4. See success notification with candidate info
5. Candidate appears in Candidates tab

### 2. View Jobs

1. Click "Jobs" tab
2. Browse all active job postings
3. See required skills and match count
4. Click on job to see details (future feature)

### 3. Manage Candidates

1. Click "Candidates" tab
2. View all uploaded candidates
3. See their match scores
4. Review skills and experience
5. Use shortlist button to schedule interview

### 4. Track Interviews

1. Click "Interviews" tab
2. See all scheduled interviews
3. View meeting times and links
4. Click "Join Meeting" to start interview

## 🔌 API Integration

The frontend uses these API endpoints:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/stats` | GET | Dashboard statistics |
| `/jobs/` | GET | List all jobs |
| `/candidates/` | GET | List all candidates |
| `/interviews/` | GET | List all interviews |
| `/upload/resume` | POST | Upload resume file |
| `/candidates/{email}/shortlist/{job_id}` | POST | Shortlist candidate |

## 🐛 Troubleshooting

### Frontend not loading
**Problem**: Blank page or errors

**Solutions**:
1. Check browser console for errors (F12)
2. Verify API is running: `curl http://localhost:8000/health`
3. Check CORS settings in backend
4. Try different browser

### Data not showing
**Problem**: Empty lists despite having data

**Solutions**:
1. Check API responses: Open Network tab (F12)
2. Verify MongoDB has data
3. Check API endpoint URLs
4. Look for CORS errors

### Upload not working
**Problem**: File upload fails

**Solutions**:
1. Check file format (PDF, DOCX only)
2. Verify file size < 10MB
3. Check backend logs
4. Ensure Groq API key is configured

### Styling issues
**Problem**: Layout broken or colors wrong

**Solutions**:
1. Check Tailwind CDN is loading
2. Clear browser cache
3. Try different browser
4. Check internet connection

## 🚀 Advanced Features

### Add Real-time Updates

Use WebSockets or polling:

```javascript
useEffect(() => {
    const interval = setInterval(() => {
        loadData();  // Refresh every 30 seconds
    }, 30000);
    
    return () => clearInterval(interval);
}, []);
```

### Add Search/Filter

```javascript
const [searchTerm, setSearchTerm] = useState('');

const filteredCandidates = candidates.filter(c => 
    c.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    c.email.toLowerCase().includes(searchTerm.toLowerCase())
);
```

### Add Sorting

```javascript
const sortedCandidates = [...candidates].sort((a, b) => 
    b.score - a.score  // Sort by score descending
);
```

## 📦 Production Build

For production, consider building with:

### Vite + React

```bash
npm create vite@latest frontend -- --template react
cd frontend
npm install
# Copy components from index.html
npm run build
```

### Next.js

```bash
npx create-next-app@latest frontend
cd frontend
# Copy components
npm run build
```

## 🎨 Customization Ideas

1. **Dark Mode**: Add theme toggle
2. **Charts**: Add Chart.js for analytics
3. **Filters**: Advanced filtering by skills, experience
4. **Export**: Export data to CSV/PDF
5. **Notifications**: Browser push notifications
6. **Multi-language**: i18n support
7. **Accessibility**: ARIA labels, keyboard navigation

## 📄 Tech Stack

- **React 18**: UI library
- **Tailwind CSS**: Styling
- **Lucide Icons**: Icon library
- **Babel**: JSX transformation
- **Native Fetch**: API calls

## 🆘 Support

If you encounter issues:

1. Check browser console (F12)
2. Verify API is running
3. Check backend logs
4. Review README
5. Test with different browser

## 🎉 Success Checklist

- [ ] API running on http://localhost:8000
- [ ] MongoDB connected
- [ ] Frontend loads without errors
- [ ] Can upload resume
- [ ] Data displays correctly
- [ ] Notifications work
- [ ] All tabs functional

---

**Enjoy your beautiful AI Recruiting Dashboard! 🚀**