// ============================================
// PORTFOLIO CONFIGURATION - NARENDRANATH EDARA
// ============================================

const CONFIG = {

    name: 'Narendranath Edara',

    // ── Availability Badge ─────────────────────────────────────────
    status: {
        available: true,
        tagline: 'Available · Senior DE / ML Engineer · Dallas TX or Remote',
        details: [
            { label: 'Status',   value: 'Actively interviewing' },
            { label: 'Response', value: '< 24 hours' },
            { label: 'Visa',     value: 'H1B transfer' },
            { label: 'Target',   value: 'Senior DE · ML Eng · AI Platform' }
        ]
    },

    // ── Hero Terminal Animation ────────────────────────────────────
    terminal: [
        { type: 'cmd',    text: 'python scrape.py --companies 109 --interval 5m' },
        { type: 'output', text: '[✓] Workday · Greenhouse · Lever · iCIMS scraped' },
        { type: 'output', text: '[✓] 173 jobs indexed  · 12 new · 0 errors' },
        { type: 'cmd',    text: 'python score.py --threshold 0.65' },
        { type: 'output', text: '[✓] 3 dream-company matches  →  alerts fired' },
        { type: 'cmd',    text: 'git push origin main' },
        { type: 'warn',   text: '✓  CI passed  ·  deployed to GitHub Pages' },
    ],

    // ── Konami Code Easter Egg ─────────────────────────────────────
    metrics: {
        experience_years:      4,
        current_role:          'Data Engineer @ ExponentHR',
        gpa:                   4.0,
        sdlc_speedup:          '3 months → 14 days (21×)',
        etl_runtime:           '~30 min → <8 min (73% faster)',
        query_latency:         '12s → 4s (67% faster)',
        compute_cost_cut:      '~67%',
        support_tickets:       '-40%',
        anomaly_accuracy:      '95%+',
        false_positives:       '-40%',
        azure_savings:         '$3,200/month',
        node_consolidation:    '20 nodes → 4–8 nodes',
        udaan_savings:         '$4M annual',
        fulfillment_rate:      '99.3%',
        zomato_market_share:   '+9%',
        fraud_tps:             '100+ TPS at <1ms P99',
        portfolio_analytics:   '47.8 TPS, <5s VaR latency',
        jobscout_companies:    109,
        jobscout_resumes:      '95+',
        publication:           'Taylor & Francis 2025 — DOI: 10.1080/10495142.2025.2525123',
        easter_egg:            true
    },

    // ── RSS Feed Sources ───────────────────────────────────────────
    rss: {
        medium: {
            enabled: false,
            username: 'narendranathedara',
            feedUrl: 'https://medium.com/feed/@narendranathedara',
            profileUrl: 'https://medium.com/@narendranathedara'
        },
        devto: {
            enabled: false,
            username: 'narendranathe',
            feedUrl: 'https://dev.to/feed/narendranathe',
            profileUrl: 'https://dev.to/narendranathe'
        },
        substack: {
            enabled: true,
            username: 'narendranathe',
            feedUrl: 'https://narendranathe.substack.com/feed',
            profileUrl: 'https://narendranathe.substack.com'
        }
    },

    // ── Recommendations ────────────────────────────────────────────
    recommendations: [
        {
            text: "Naren is a great talent in the product ownership space. He is a critical thinker and understands how to analyze a problem, and convert that problem into a tangible requirements doc. He also understands how to take a data driven approach to tackle features and initiatives. Most importantly, he is a quick and humble learner that loves researching the areas of the business that are new to him. I highly recommend Naren for any product, business analyst, or data analyst roles.",
            name: "Richard Enright",
            role: "Lead Product Manager at Harness",
            initials: "RE",
            avatar: "",
            linkedin: "https://www.linkedin.com/in/richard-enright-mba/"
        },
        {
            text: "I had the pleasure of working closely with Narendranath for 3+ years and can confidently attest to his outstanding performance and exceptional work ethic. He had keen eye for solving business problems by identifying trends to improve the overall business of the clients and the company as well. Narendranath was always willing to go above and beyond his responsibilities to support the team and the company's overall goals. His positive attitude, professionalism, and strong communication skills made him a pleasure to work with.",
            name: "Snehal Moni",
            role: "Operations and Policy Analyst at Oregon Health Authority",
            initials: "SM",
            avatar: "",
            linkedin: "https://www.linkedin.com/in/snehal-moni/"
        },
        {
            text: "Narendranath has been an efficient source to the team at all times. He expertly trained himself to adapt to the various sectors of the business and was one of the few people who took up every challenge offered to him.",
            name: "Pranav Suresh",
            role: "Business Effectiveness - CIBC",
            initials: "PS",
            avatar: "",
            linkedin: "https://www.linkedin.com/in/pranav-s-47356a58/"
        }
    ],

    // ── Social Links ───────────────────────────────────────────────
    social: {
        linkedin: 'https://linkedin.com/in/narendranathe',
        github:   'https://github.com/narendranathe',
        email:    'edara.narendranath@gmail.com'
    }
};
