<br/>

<p align="center">
  <img src="https://img.icons8.com/fluency/96/portfolio.png" width="80">

  <h4 align="center">Clean, Professional Portfolio Template for Data & ML Engineers</h4>

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

**DevFolio** is a clean, minimal portfolio template designed for Data Engineers, ML Engineers, and Software Developers. Built with pure HTML, CSS, and JavaScript — no frameworks, no build tools, no dependencies. Just fork, customize, and deploy to GitHub Pages in minutes.

**Features:**

✓ [Zero Dependencies](#-why-this-template)  
✓ [One-Click Fork & Deploy](#-installation--setup)  
✓ [Elegant White Theme](#-customization)  
✓ [Mobile Responsive](#-customization)  
✓ [SEO Optimized](#seo)  
✓ [Experience Timeline](#experience)  
✓ [Skills Section](#skills)  
✓ [Projects Showcase](#projects)  
✓ [Certifications Display](#certifications)  
✓ [Education Section](#education)  
✓ [Achievements Metrics](#achievements)  
✓ [Contact Section](#contact)

To view a live example, **[click here](https://narendranathe.github.io)**.

---

## ✨ Why This Template?

| Feature | This Template | Other Templates |
|---------|---------------|-----------------|
| Build Tools Required | ❌ None | ✅ npm, webpack, etc. |
| Framework Dependencies | ❌ None | ✅ React, Vue, etc. |
| Setup Time | ⚡ 5 minutes | 🕐 30+ minutes |
| Hosting | 🆓 GitHub Pages | May require paid hosting |
| Customization | 📝 Edit HTML directly | Config files, rebuild |

---

## 🛠 Installation & Setup

### Option 1: Fork This Repo _(Recommended)_

1. **Fork the repo:** Click the **Fork** button at the top right, or [click here](https://github.com/narendranathe/narendranathe.github.io/fork).

2. **Rename your repo:**
   - For `https://<USERNAME>.github.io`: Rename to `<USERNAME>.github.io`
   - For `https://<USERNAME>.github.io/portfolio`: Rename to `portfolio`

3. **Enable GitHub Pages:**
   - Go to **Settings** → **Pages**
   - Set **Source** to `Deploy from a branch`
   - Select **Branch:** `main` and folder `/ (root)`
   - Click **Save**

4. **Wait 2-3 minutes** for deployment. Your site will be live at your GitHub Pages URL!

### Option 2: Download & Upload

1. Click **Code** → **Download ZIP**
2. Extract and edit files locally
3. Create a new repo named `<USERNAME>.github.io`
4. Upload all files to the new repo
5. Enable GitHub Pages in Settings

---

## 🎨 Customization

All customization is done directly in `index.html`. Open it in any text editor and modify:

### Personal Info

```html
<!-- Find and replace these values -->
<title>Your Name | Your Title</title>
<meta name="description" content="Your description here">
<meta name="author" content="Your Name">
```

### Hero Section

```html
<section class="hero" id="home">
    <h1>Your Name</h1>
    <p class="hero-subtitle">Your Title | Your Tagline</p>
</section>
```

### Experience

Add or modify experience cards:

```html
<div class="exp-card">
    <div class="exp-logo">
        <img src="images/company/your-company.png" alt="Company">
    </div>
    <div class="exp-content">
        <h4>Your Job Title</h4>
        <p class="exp-company">Company Name</p>
        <p class="exp-date">Start Date - End Date</p>
        <p class="exp-description">Your achievements and responsibilities...</p>
    </div>
</div>
```

### Skills

Modify the skills grid:

```html
<div class="skill-tag">Python</div>
<div class="skill-tag">SQL</div>
<div class="skill-tag">Apache Spark</div>
<!-- Add more skills -->
```

### Projects

Add project cards:

```html
<div class="project-card">
    <h4>Project Name</h4>
    <p>Project description...</p>
    <div class="project-tech">
        <span>Python</span>
        <span>Docker</span>
    </div>
    <a href="https://github.com/username/project" target="_blank">View Project →</a>
</div>
```

### Certifications

```html
<div class="cert-card">
    <div class="cert-icon">
        <i class="fab fa-microsoft"></i>
    </div>
    <h4 class="cert-title">Certification Name</h4>
    <p class="cert-issuer">Issuing Organization</p>
</div>
```

### Education

```html
<div class="edu-card">
    <img src="images/company/university.png" alt="University">
    <h4>Degree Name</h4>
    <p>University Name</p>
    <p>Year - Year | GPA: X.X</p>
</div>
```

### Achievements

```html
<div class="achievement-card">
    <div class="achievement-value">99%</div>
    <div class="achievement-label">Your Achievement</div>
</div>
```

### Contact & Social Links

```html
<a href="mailto:your@email.com">your@email.com</a>
<a href="https://linkedin.com/in/yourprofile" target="_blank">LinkedIn</a>
<a href="https://github.com/yourusername" target="_blank">GitHub</a>
```

---

## 📁 File Structure

```
your-repo/
├── index.html          # Main portfolio page (edit this!)
├── README.md           # This file
├── LICENSE             # MIT License
└── images/
    ├── hero.jpg        # Hero background (optional)
    ├── PP.jpg          # Profile picture
    ├── preview.png     # README preview image
    ├── company/        # Company & university logos
    │   ├── company1.png
    │   └── university.png
    └── certifications/ # Certification badges
        └── cert1.png
```

---

## 🖼 Adding Images

### Profile Picture
- Replace `PP.jpg` with your photo
- Recommended size: 400x400px
- Supported formats: `.jpg`, `.jpeg`, `.png`

### Company Logos
- Add logos to `images/company/`
- Recommended size: 100x100px
- Use transparent PNG for best results

### Certification Badges
- Add badges to `images/certifications/`
- Download official badges from certification providers

> **Note:** GitHub Pages is case-sensitive! `Company.PNG` ≠ `company.png`

---

## 🎨 Color Customization

The template uses CSS variables for easy theming. Find these in the `<style>` section:

```css
:root {
    --bg-primary: #FDFCFA;        /* Main background */
    --bg-secondary: #F7F5F2;      /* Section backgrounds */
    --text-primary: #1C1C1C;      /* Main text */
    --text-secondary: #4A4A4A;    /* Secondary text */
    --accent-primary: #2D5A4A;    /* Primary accent (forest green) */
    --accent-warm: #C4A77D;       /* Warm accent (gold) */
}
```

### Popular Color Schemes

**Ocean Blue:**
```css
--accent-primary: #1e40af;
--accent-warm: #f59e0b;
```

**Royal Purple:**
```css
--accent-primary: #7c3aed;
--accent-warm: #ec4899;
```

**Slate Professional:**
```css
--accent-primary: #334155;
--accent-warm: #0ea5e9;
```

---

## 📱 Responsive Design

The template is fully responsive out of the box:
- **Desktop:** Full layout with sidebar navigation
- **Tablet:** Adjusted grid layouts
- **Mobile:** Stacked sections with hamburger menu

No additional configuration needed!

---

## 🔍 SEO

The template includes SEO meta tags. Customize them:

```html
<head>
    <title>Your Name | Your Title</title>
    <meta name="description" content="Your professional summary (150-160 chars)">
    <meta name="keywords" content="Your, Keywords, Here">
    <meta name="author" content="Your Name">
    
    <!-- Open Graph for social sharing -->
    <meta property="og:title" content="Your Name | Portfolio">
    <meta property="og:description" content="Your description">
    <meta property="og:image" content="https://yourusername.github.io/images/preview.png">
    <meta property="og:url" content="https://yourusername.github.io">
</head>
```

---

## 🚀 Custom Domain (Optional)

1. Purchase a domain (Namecheap, Google Domains, etc.)
2. Go to **Settings** → **Pages** → **Custom domain**
3. Enter your domain (e.g., `yourname.com`)
4. Add DNS records at your registrar:
   - **A Record:** `185.199.108.153`
   - **A Record:** `185.199.109.153`
   - **A Record:** `185.199.110.153`
   - **A Record:** `185.199.111.153`
   - **CNAME:** `www` → `<USERNAME>.github.io`

---

## 🐛 Troubleshooting

### Page shows 404
- Ensure repo is named correctly (`<USERNAME>.github.io` for root domain)
- Check that `index.html` is in the root directory
- Verify GitHub Pages is enabled in Settings

### Images not loading
- Check file names are case-sensitive (`PP.jpg` ≠ `pp.jpg`)
- Verify images are committed to the repo
- Use relative paths (`images/photo.jpg` not `/images/photo.jpg`)

### Changes not showing
- Hard refresh: `Ctrl + Shift + R` (Windows) or `Cmd + Shift + R` (Mac)
- Wait 2-3 minutes for GitHub Pages to rebuild
- Check the **Actions** tab for deployment status

### Fonts not loading
- Ensure you have internet connectivity
- Google Fonts are loaded via CDN

---

## 💖 Support

If this template helped you, please consider:

<p>
<a href="https://github.com/narendranathe/narendranathe.github.io/stargazers">
  <img src="https://img.shields.io/github/stars/narendranathe/narendranathe.github.io?style=social" alt="Github Star">
</a>
</p>

- ⭐ Star this repository
- 🍴 Fork and share with others
- 🐛 Report bugs or suggest features

---

## 📄 License

[MIT](https://github.com/narendranathe/narendranathe.github.io/blob/main/LICENSE) — Feel free to use this template for personal or commercial projects. Attribution appreciated but not required.

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/narendranathe">Narendranath Edara</a>
</p>
