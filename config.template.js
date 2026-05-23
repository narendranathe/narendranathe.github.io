// ============================================
// PORTFOLIO CONFIGURATION TEMPLATE
// ============================================
//
// SETUP (takes ~5 minutes):
// 1. Copy this file → rename to config.js
// 2. Fill in your information below
// 3. Edit index.html for your experience, projects, skills, etc.
// 4. Push to GitHub — GitHub Pages deploys automatically
//
// config.js is gitignored so your personal data stays private.
// ============================================

const CONFIG = {

    // ── Identity ──────────────────────────────────────────────────
    name: 'Your Name',

    // ── Identity (single source of truth for name, role, meta tags) ─
    // Every field below drives a specific surface in index.html:
    //   name            -> hero name, JSON-LD <Person>, footer copyright
    //   shortName       -> nav logo / short references
    //   role            -> hero subtitle, JSON-LD jobTitle
    //   location        -> JSON-LD addressLocality, contact section
    //   title           -> <title> tag
    //   description     -> <meta name="description">
    //   ogTitle         -> <meta property="og:title">
    //   ogDescription   -> <meta property="og:description">
    //   ogImage         -> <meta property="og:image"> (path relative to mediaRepoUrl or absolute)
    //   canonicalUrl    -> <link rel="canonical"> + <meta property="og:url">
    //   headshot        -> hero portrait <img src>
    //   footerStatement -> footer tagline under name
    //   sameAs          -> JSON-LD sameAs array (external profile URLs)
    //   twitterHandle   -> <meta name="twitter:creator"> (@handle)
    //   mediaRepoUrl    -> base URL for a second GitHub Pages site hosting
    //                      large media (headshots, OG previews). resume.pdf
    //                      stays canonical at /static/resume.pdf in this repo.
    identity: {
        name:            'Your Name',
        shortName:       'You',
        firstName:       'Your First',
        lastName:        'Your Last',
        role:            'Your Role',
        location:        'Your City, ST',
        title:           'Your Name | Your Role',
        description:     'Your Name - Your Role building (one-line description of what you do).',
        ogTitle:         'Your Name | Your Role',
        ogDescription:   'Short, punchy social card description.',
        ogImage:         '/static/og-image.jpg',
        canonicalUrl:    'https://yourusername.github.io',
        headshot:        '/static/originals/headshot.jpg',
        footerStatement: 'One-line footer tagline that sums up your work.',
        sameAs:          ['https://linkedin.com/in/yourusername', 'https://github.com/yourusername'],
        twitterHandle:   '@yourusername',
        mediaRepoUrl:    'https://yourusername.github.io/media'
    },

    // ── Availability Badge (hero section) ─────────────────────────
    // Shows a pulsing green dot with hover tooltip in the hero
    status: {
        available: true,                           // false = hides the badge
        tagline: 'Available · Your Role · City or Remote',
        details: [
            { label: 'Status',   value: 'Actively interviewing' },
            { label: 'Response', value: '< 24 hours' },
            { label: 'Visa',     value: 'Your visa status (or remove this line)' },
            { label: 'Target',   value: 'Role A · Role B · Role C' }
        ]
    },

    // ── Hero Terminal Animation ────────────────────────────────────
    // Lines that type out one-by-one in the hero section terminal widget.
    // type: 'cmd' (blue $), 'output' (green), 'warn' (yellow)
    terminal: [
        { type: 'cmd',    text: 'python your_pipeline.py --env prod' },
        { type: 'output', text: '[✓] Pipeline step 1 complete' },
        { type: 'output', text: '[✓] Pipeline step 2 complete · 0 errors' },
        { type: 'cmd',    text: 'pytest tests/ -v' },
        { type: 'output', text: '[✓] 42 passed · 0 failed' },
        { type: 'cmd',    text: 'git push origin main' },
        { type: 'warn',   text: '✓  CI passed  ·  deployed' },
    ],

    // ── Konami Code Easter Egg (↑↑↓↓←→←→BA) ──────────────────────
    // Shows a debug JSON overlay with your metrics when the Konami
    // code is typed. Add any key/value pairs you want to show off.
    metrics: {
        experience_years: 4,
        current_role:     'Your Title @ Company',
        highlight_1:      'Your biggest impact metric',
        highlight_2:      'Another key achievement',
        highlight_3:      'Something that makes recruiters stop scrolling',
        // Add as many as you like
    },

    // ── RSS Feed Sources ───────────────────────────────────────────
    // Articles auto-update when you publish. No API keys needed.
    rss: {
        medium: {
            enabled: false,
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

    // ── Recommendations Carousel ───────────────────────────────────
    recommendations: [
        {
            text: "Paste your recommendation text here...",
            name: "Recommender Name",
            role: "Their Title at Company",
            initials: "RN",
            avatar: "",    // Optional: URL to their photo
            linkedin: "https://linkedin.com/in/their-profile"
        }
        // Add more objects for more testimonials
    ],

    // ── Social Links ───────────────────────────────────────────────
    social: {
        linkedin: 'https://linkedin.com/in/your-profile',
        github:   'https://github.com/your-username',
        email:    'your.email@example.com'
    }
};
