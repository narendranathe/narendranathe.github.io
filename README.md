<br/>

<p align="center">
  

  <h4 align="center">Portfolio Template for Data & ML Engineers</h4>

  <p align="center">
    <a href="https://github.com/narendranathe/narendranathe.github.io/issues"><img src="https://img.shields.io/github/issues/narendranathe/narendranathe.github.io"/></a>
    <a href="https://github.com/narendranathe/narendranathe.github.io/stargazers"><img src="https://img.shields.io/github/stars/narendranathe/narendranathe.github.io"/></a>
    <a href="https://github.com/narendranathe/narendranathe.github.io/network/members"><img src="https://img.shields.io/github/forks/narendranathe/narendranathe.github.io"/></a>
    <a href="https://github.com/narendranathe/narendranathe.github.io/commits/main"><img src="https://img.shields.io/github/last-commit/narendranathe/narendranathe.github.io/main"/></a>
    <a href="https://github.com/narendranathe/narendranathe.github.io/blob/main/LICENSE"><img src="https://img.shields.io/github/license/narendranathe/narendranathe.github.io"/></a>
  </p>

  <p align="center">
    <a href="https://narendranathe.github.io">View Demo</a>
    ·
    <a href="https://github.com/narendranathe/narendranathe.github.io/issues">Report Bug</a>
    ·
    <a href="https://github.com/narendranathe/narendranathe.github.io/discussions">Request Feature</a>
  </p>
</p>

<p align="center">
  <a href="https://narendranathe.github.io">
    <img src="images/preview.png" alt="Preview" width="60%"/>
  </a>
</p>

**DevFolio** is a clean, minimal portfolio template designed for **Data Engineers**, **ML Engineers**, and **Software Developers**. Built with pure HTML, CSS, and JavaScript—no frameworks, no build tools, no dependencies. Just fork, customize, and deploy to GitHub Pages in minutes.

##  Features

| Core Features | Dynamic Content | Security |
|---------------|-----------------|----------|
| ✅ Zero Dependencies | ✅ Auto-updating RSS Articles | ✅ Config-based Architecture |
| ✅ One-Click Fork & Deploy | ✅ Recommendations Carousel | ✅ Personal Data Gitignored |
| ✅ Elegant White Theme | ✅ Research Publications | ✅ Template for Forkers |
| ✅ Mobile Responsive | ✅ Resume Download Button | ✅ No API Keys Required |
| ✅ SEO Optimized | ✅ Platform Switching Tabs | |

###  What's Included

- **Hero Section** — Eye-catching intro with floating cards and stats
- **About Section** — Bio with skills grid and social links
- **Education** — Academic credentials with GPA badges
- **Experience Timeline** — Career journey with company logos
- **Projects Showcase** — Featured work with metrics and GitHub links
- **Certifications** — Professional credentials with badge styling
- **Research Publications** — Academic work with DOI links
- **Featured Articles** — Auto-updating from Medium/Dev.to/Substack via RSS
- **Recommendations Carousel** — Testimonials with auto-rotation
- **Achievements** — Key metrics and impact numbers
- **Contact Section** — Multiple contact methods with resume download

---

##  Quick Start

### Option 1: Fork This Repo (Recommended)

1. **Fork the repo** — Click the Fork button at the top right
2. **Rename your repo:**
   - For `https://<USERNAME>.github.io` → Rename to `<USERNAME>.github.io`
   - For `https://<USERNAME>.github.io/portfolio` → Rename to `portfolio`
3. **Create your config file:**
   ```bash
   cp config.template.js config.js
   ```
4. **Edit `config.js`** with your information (see [Configuration](#-configuration))
5. **Enable GitHub Pages:**
   - Go to Settings → Pages
   - Set Source to "Deploy from a branch"
   - Select Branch: `main` and folder `/ (root)`
   - Click Save
6. **Wait 2-3 minutes** — Your site will be live!

### Option 2: Download & Upload

1. Click **Code → Download ZIP**
2. Extract and edit files locally
3. Create `config.js` from `config.template.js`
4. Create a new repo named `<USERNAME>.github.io`
5. Upload all files to the new repo
6. Enable GitHub Pages in Settings

---

##  Configuration

### File Structure

```
your-portfolio/
├── index.html              # Main portfolio page
├── config.js               # Your personal config (gitignored)
├── config.template.js      # Template for forkers (committed)
├── README.md               # This file
├── LICENSE                 # MIT License
└── .gitignore              # Ignores config.js
```

### Setting Up `config.js`

Copy `config.template.js` to `config.js` and customize:

```javascript
const CONFIG = {
    name: 'Your Name',
    
    // RSS Feed Sources (public feeds - no API keys needed)
    rss: {
        medium: {
            enabled: true,  // Set to true to enable
            username: 'your-medium-username',
            feedUrl: 'https://medium.com/feed/@your-medium-username',
            profileUrl: 'https://medium.com/@your-medium-username'
        },
        devto: {
            enabled: false,
            username: 'your-devto-username',
            feedUrl: 'https://dev.to/feed/your-devto-username',
            profileUrl: 'https://dev.to/your-devto-username'
        },
        substack: {
            enabled: false,
            username: 'your-substack-name',
            feedUrl: 'https://your-substack-name.substack.com/feed',
            profileUrl: 'https://your-substack-name.substack.com'
        }
    },
    
    // Testimonials/Recommendations
    recommendations: [
        {
            text: "Your recommendation text here...",
            name: "Recommender Name",
            role: "Their Role at Company",
            initials: "RN",
            avatar: "",  // Optional: URL to their photo
            linkedin: "https://linkedin.com/in/their-profile"
        }
    ],
    
    // Social Links
    social: {
        linkedin: 'https://linkedin.com/in/your-profile',
        github: 'https://github.com/your-username',
        email: 'your.email@example.com'
    }
};
```

### Why This Architecture?

| Concern | Solution |
|---------|----------|
| **Personal data exposure** | `config.js` is gitignored |
| **Easy for forkers** | Template file with clear instructions |
| **No API keys needed** | RSS feeds are public by default |
| **Auto-updating content** | Articles sync when you publish |

---

##  Customization

### Personal Information

Edit directly in `index.html`:

```html

Your Name | Your Title



Hi, I'm Your Name
```

### Color Scheme

Find CSS variables in `<style>` section:

```css
:root {
    --accent-primary: #2D5A4A;    /* Forest green */
    --accent-warm: #C4A77D;       /* Gold accent */
    --bg-primary: #FDFCFA;        /* Main background */
}
```

**Popular Alternatives:**

| Theme | Primary | Warm |
|-------|---------|------|
| Ocean Blue | `#1e40af` | `#f59e0b` |
| Royal Purple | `#7c3aed` | `#ec4899` |
| Slate Pro | `#334155` | `#0ea5e9` |

### Resume Download

Host your resume using GitHub Releases:

1. Create a separate repo (e.g., `assets` or use your portfolio repo)
2. Go to Releases → Create new release
3. Tag: `resume`, Title: `Resume`
4. Attach your PDF file
5. Publish release
6. Use URL format: `https://github.com/USERNAME/REPO/releases/download/resume/YourName.pdf`

### Adding Images

**Profile Picture:**
- Recommended size: 400×400px
- Formats: `.jpg`, `.jpeg`, `.png`
- Host on GitHub Issues (drag & drop) or use external CDN

**Company Logos:**
- Recommended size: 100×100px
- Use transparent PNG for best results

>  GitHub Pages is case-sensitive! `Company.PNG` ≠ `company.png`

---

## 📰 Featured Articles (RSS)

Articles auto-update from your blog platforms. No manual updates needed!

### Supported Platforms

| Platform | Feed URL Format |
|----------|-----------------|
| Medium | `https://medium.com/feed/@username` |
| Dev.to | `https://dev.to/feed/username` |
| Substack | `https://name.substack.com/feed` |

### How It Works

1. Uses free [RSS2JSON](https://rss2json.com) API (no key required)
2. Fetches latest 6 articles on page load
3. Displays thumbnail, title, description, read time
4. Platform tabs for multi-platform support

### Enabling Platforms

In `config.js`, set `enabled: true` for your platforms:

```javascript
rss: {
    medium: {
        enabled: true,  // ← Enable this
        username: 'narendranathe',
        // ...
    }
}
```

---

## 💬 Recommendations Carousel

Display testimonials from colleagues with an auto-rotating carousel.

### Features

-  Auto-rotation every 6 seconds
-  Pauses on hover
-  Touch/swipe support for mobile
-  Keyboard navigation (arrow keys)
-  Progress bar indicator

### Adding Recommendations

In `config.js`:

```javascript
recommendations: [
    {
        text: "Naren is an exceptional engineer who consistently delivers...",
        name: "John Doe",
        role: "Engineering Manager at Company",
        initials: "JD",
        avatar: "",  // Leave empty to show initials
        linkedin: "https://linkedin.com/in/johndoe"
    },
    // Add more...
]
```

---

##  Research Publications

Showcase your academic work:

```html

    
         Peer-Reviewed Journal
    
    Your Paper Title
    
        Author 1, Your Name, Author 3
    
    
         Journal Name
         2025
    
    
        View Publication 
    

```

---

##  Responsive Design

The template is fully responsive out of the box:

| Device | Layout |
|--------|--------|
| Desktop | Full layout with dropdown navigation |
| Tablet | Adjusted grids (2 columns) |
| Mobile | Stacked sections with hamburger menu |

No additional configuration needed!

---

##  SEO

Customize meta tags in `<head>`:

```html
Your Name | Your Title







```

---

##  Custom Domain (Optional)

1. Purchase a domain (Namecheap, Google Domains, etc.)
2. Go to Settings → Pages → Custom domain
3. Enter your domain (e.g., `yourname.com`)
4. Add DNS records at your registrar:

| Type | Name | Value |
|------|------|-------|
| A | @ | `185.199.108.153` |
| A | @ | `185.199.109.153` |
| A | @ | `185.199.110.153` |
| A | @ | `185.199.111.153` |
| CNAME | www | `<USERNAME>.github.io` |

---

##  Troubleshooting

### Page shows 404
- Ensure repo is named correctly (`<USERNAME>.github.io` for root domain)
- Check that `index.html` is in the root directory
- Verify GitHub Pages is enabled in Settings

### Images not loading
- Check file names are case-sensitive (`PP.jpg` ≠ `pp.jpg`)
- Verify images are committed to the repo
- Use relative paths (`images/photo.jpg` not `/images/photo.jpg`)

### Articles not loading
- Check `config.js` exists and has correct usernames
- Verify your blog platform RSS feed is public
- Check browser console for errors

### Changes not showing
- Hard refresh: `Ctrl + Shift + R` (Windows) or `Cmd + Shift + R` (Mac)
- Wait 2-3 minutes for GitHub Pages to rebuild
- Check the Actions tab for deployment status

---

##  Support

If this template helped you, please consider:

 **Star this repository**

 **Fork and share with others**

 **Report bugs or suggest features**

---

##  License

**MIT** — Feel free to use this template for personal or commercial projects. Attribution appreciated but not required.

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/narendranathe">Narendranath Edara</a>
</p>
