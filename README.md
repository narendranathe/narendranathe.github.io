<p align="center">
  <h2 align="center">DevFolio — Portfolio Template for Data & ML Engineers</h2>
  <p align="center">
    <a href="https://github.com/narendranathe/narendranathe.github.io/issues"><img src="https://img.shields.io/github/issues/narendranathe/narendranathe.github.io"/></a>
    <a href="https://github.com/narendranathe/narendranathe.github.io/stargazers"><img src="https://img.shields.io/github/stars/narendranathe/narendranathe.github.io"/></a>
    <a href="https://github.com/narendranathe/narendranathe.github.io/network/members"><img src="https://img.shields.io/github/forks/narendranathe/narendranathe.github.io"/></a>
    <a href="https://github.com/narendranathe/narendranathe.github.io/blob/main/LICENSE"><img src="https://img.shields.io/github/license/narendranathe/narendranathe.github.io"/></a>
  </p>
  <p align="center">
    <a href="https://narendranathe.github.io"><strong>Live Demo →</strong></a>
    &nbsp;·&nbsp;
    <a href="https://github.com/narendranathe/narendranathe.github.io/issues">Report Bug</a>
    &nbsp;·&nbsp;
    <a href="https://github.com/narendranathe/narendranathe.github.io/discussions">Request Feature</a>
  </p>
</p>

---

A clean, zero-dependency portfolio template built for **Data Engineers**, **ML Engineers**, and **Software Developers**. Pure HTML + CSS + JavaScript — no frameworks, no build step, no Node.js. Fork, fill in `config.js`, customize `index.html`, push to GitHub Pages.

---

## What You Get

### Sections
| Section | What it shows |
|---|---|
| **Hero** | Name, live availability badge, animated terminal, stats, profile photo |
| **About** | Bio, skills grid, social links |
| **Education** | Degrees with GPA, logos, dates |
| **Experience** | Timeline with company logos, bullets, tech tags |
| **Projects** | Cards with metrics, GitHub links, live demo links |
| **Certifications** | Badge images + fallback icons |
| **Research** | DOI-linked publication cards |
| **Featured Articles** | Auto-fetches your latest posts from Medium / Dev.to / Substack via RSS |
| **Recommendations** | Auto-rotating testimonial carousel with swipe support |
| **Achievements** | Key metrics that count up on scroll |
| **Contact** | Email, location, resume download, social icons |

### Interactive Features
| Feature | How to trigger |
|---|---|
| **Live status badge** | Hover the green dot in the hero — shows availability, response time, visa, target roles |
| **Hero terminal** | Loads automatically — shows your pipeline commands typing in line by line |
| **Command palette** | Press `Cmd+K` (Mac) or `Ctrl+K` (Windows) — VS Code-style navigation |
| **Scroll progress bar** | Accent-colored bar at the very top tracks reading progress |
| **Achievement counters** | Numbers animate upward when scrolled into view |
| **Easter egg** | Type the Konami code `↑↑↓↓←→←→BA` — reveals your full metrics as a debug JSON overlay |

### Everything is Config-Driven
Most personal content lives in two places:
- **`config.js`** — status badge, terminal lines, Konami metrics, RSS feeds, recommendations, social links
- **`index.html`** — your name, bio, experience bullets, project descriptions, education, certifications

---

## Quick Start (5 minutes)

### 1. Fork the repo

Click **Fork** at the top right of this page.

Then rename your fork:
- For `https://USERNAME.github.io` → rename to `USERNAME.github.io`
- For `https://USERNAME.github.io/portfolio` → keep any name, set base path in Pages settings

### 2. Create your config file

```bash
cp config.template.js config.js
```

Edit `config.js` with your information (see [Configuration](#configuration) below).

> `config.js` is listed in `.gitignore` so your personal data won't be committed to your public fork. `config.template.js` is the version committed to git.

### 3. Customize your content in `index.html`

Search for these sections and replace with your info:

| Search for | What to update |
|---|---|
| `Hi, I'm` | Your name in the hero title |
| `hero-subtitle` | Your one-liner pitch |
| `hero-stats` | Your top 4 headline numbers |
| `about-content` | Your bio paragraphs |
| `skills-grid` | Your skill categories and tags |
| `education-grid` | Your degrees, schools, dates, GPA |
| `experience-timeline` | Each job: title, company, dates, bullets, tags |
| `projects-grid` | Your project cards with stats and links |
| `cert-grid` | Your certifications |
| `research-card` | Your publications (or delete the section) |
| `achievements-grid` | Your 6 headline metrics |
| `contact-cards` | Your email, phone, location |
| `Resume` links | Your resume PDF URL (see [Hosting Your Resume](#hosting-your-resume)) |

### 4. Add your photos

Upload images as GitHub Issue attachments (free, no CDN needed):

1. Open any issue in your repo
2. Drag and drop your image into the comment box
3. Copy the generated `https://github.com/user-attachments/assets/...` URL
4. Paste into `index.html` where the `<img src="">` tags are

### 5. Enable GitHub Pages

1. Go to your repo → **Settings → Pages**
2. Source: **Deploy from a branch**
3. Branch: `main` · Folder: `/ (root)`
4. Click **Save**

Wait 2–3 minutes. Your site will be live at `https://USERNAME.github.io`.

---

## Configuration

### `config.js` Reference

```javascript
const CONFIG = {
    name: 'Your Name',

    // Pulsing green dot in the hero with hover tooltip
    status: {
        available: true,                    // false hides the badge entirely
        tagline: 'Available · Role · City or Remote',
        details: [
            { label: 'Status',   value: 'Actively interviewing' },
            { label: 'Response', value: '< 24 hours' },
            { label: 'Visa',     value: 'Your visa status' },    // remove if not needed
            { label: 'Target',   value: 'Role A · Role B' }
        ]
    },

    // Commands that type in line-by-line in the hero terminal widget
    // type: 'cmd' (blue $ prompt), 'output' (green), 'warn' (yellow)
    terminal: [
        { type: 'cmd',    text: 'python pipeline.py --env prod' },
        { type: 'output', text: '[✓] Step 1 complete' },
        { type: 'cmd',    text: 'git push origin main' },
        { type: 'warn',   text: '✓  Deployed' },
    ],

    // What appears in the Konami code easter egg (↑↑↓↓←→←→BA)
    // Add your real impact numbers — recruiters who find this will be impressed
    metrics: {
        your_metric_1: 'value',
        your_metric_2: 'value',
        easter_egg: true
    },

    // RSS feeds — articles auto-update when you publish, no API key needed
    rss: {
        medium:    { enabled: false, username: '...', feedUrl: '...', profileUrl: '...' },
        devto:     { enabled: false, username: '...', feedUrl: '...', profileUrl: '...' },
        substack:  { enabled: false, username: '...', feedUrl: '...', profileUrl: '...' }
    },

    // Testimonials carousel
    recommendations: [
        { text: '...', name: '...', role: '...', initials: 'AB', avatar: '', linkedin: '...' }
    ],

    // Footer social icons and contact section
    social: {
        linkedin: 'https://linkedin.com/in/your-profile',
        github:   'https://github.com/your-username',
        email:    'your.email@example.com'
    }
};
```

### Color Scheme

Edit CSS variables in the `<style>` block of `index.html`:

```css
:root {
    --accent-primary: #2D5A4A;   /* Main accent — try #1e40af (blue), #7c3aed (purple) */
    --accent-warm:    #C4A77D;   /* Warm highlight */
    --bg-primary:     #FDFCFA;   /* Page background */
}
```

---

## Hosting Your Resume

Use GitHub Releases for a permanent, version-controlled PDF URL:

1. Create a repo named `assets` (or use your portfolio repo)
2. Go to **Releases → Create a new release**
3. Tag: `resume` · Title: `Resume`
4. Attach your PDF (e.g., `YourName.pdf`)
5. Publish

Your download URL will be:
```
https://github.com/USERNAME/REPO/releases/download/resume/YourName.pdf
```

Replace all `Resume` link `href` attributes in `index.html` with this URL.

---

## File Structure

```
your-portfolio/
├── index.html           # Main page — edit your content here
├── config.js            # Your personal data (gitignored)
├── config.template.js   # Template committed to git — forkers start here
├── README.md            # This file
├── LICENSE              # MIT
└── .gitignore           # Ignores config.js (protects your personal data)
```

---

## Easter Egg Details

The **Konami code** (`↑↑↓↓←→←→BA`) triggers a debug JSON overlay showing everything in `CONFIG.metrics`. This is intentionally designed to impress technical recruiters and hiring managers who explore the page source or find it by accident. Put your real numbers in there — metrics that make someone stop and think "I need to talk to this person."

The **command palette** (`Cmd+K` / `Ctrl+K`) opens a VS Code-style navigation modal. It works with keyboard (`↑↓` to move, `Enter` to select, `Esc` to close) and navigates to any section or opens external links.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| Site shows 404 | Confirm repo is named `USERNAME.github.io` and Pages is enabled |
| Config not loading | Ensure `config.js` exists (copy from `config.template.js`) |
| Images broken | GitHub Pages is case-sensitive — `Photo.JPG` ≠ `photo.jpg` |
| Articles not loading | Confirm `enabled: true` in `config.js` and your RSS feed is public |
| Changes not showing | Hard refresh `Ctrl+Shift+R` or wait 2–3 min for Pages to rebuild |
| Terminal not animating | `config.js` must be loaded before the closing `</body>` tag |

---

## License

**MIT** — Use freely for personal or commercial projects. Attribution appreciated but not required.

---

<p align="center">
  Made with care by <a href="https://github.com/narendranathe">Narendranath Edara</a>
</p>
