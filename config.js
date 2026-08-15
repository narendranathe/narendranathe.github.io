// ============================================
// PORTFOLIO CONFIGURATION - NARENDRANATH EDARA
// ============================================

const CONFIG = {

    name: 'Narendranath Edara',

    // ── Availability Badge ─────────────────────────────────────────
    status: {
        available: true,
        tagline: 'Data Engineer · AI-Enabled Data Platforms · Open to Hybrid/Relocation',
        details: [
            { label: 'Response', value: '< 24 hours' },
            { label: 'Visa',     value: 'H1B Transfer' },
            { label: 'Focus',    value: 'Senior DE · ML Engineer · AI/ML Platform' },
            { label: 'Location', value: 'Dallas TX · Hybrid / Relocation OK' }
        ]
    },

    // ── Hero Terminal Animation ────────────────────────────────────
    terminal: [
        { type: 'cmd',    text: 'az pipelines run --name db-copydown --parameters env=staging' },
        { type: 'output', text: '[OK] restore · security · CDC instance · AAG listener validated' },
        { type: 'cmd',    text: 'python cdc_merge.py --mode incremental' },
        { type: 'output', text: '[OK] merge-upsert complete · 30min full reload replaced · -67% compute' },
        { type: 'cmd',    text: 'pytest backend/tests -q' },
        { type: 'warn',   text: '✓  355 passed  ·  0 failed  ·  AutoApply backend' },
    ],

    // ── Konami Code Easter Egg ─────────────────────────────────────
    metrics: {
        experience_years:      '6 professional, 3 in data engineering',
        current_role:          'Data Engineer @ ExponentHR - data platform + CI/CD ownership',
        gpa:                   4.0,
        sdlc_speedup:          '3 months to 14 days',
        etl_runtime:           '~30 min to under 8 min (67% faster)',
        compute_cost_cut:      '67%',
        ats_adapters:          11,
        llm_providers:         6,
        anomaly_accuracy:      '95%+',
        azure_savings:         '$3,200/month',
        node_consolidation:    '20 nodes to 4-8 nodes',
        udaan_roi:             '+7% ROI on inventory allocation',
        fulfillment_rate:      '99.3%',
        zomato_market_share:   '+9%',
        fraud_tps:             '100+ TPS at 1.12ms P99 (synthetic dataset)',
        jobscout_companies:    109,
        jobscout_resumes:      '95+',
        publication:           'Taylor and Francis 2025, DOI: 10.1080/10495142.2025.2525123',
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

// Bridge for app.js which expects window.PORTFOLIO_CONFIG
window.PORTFOLIO_CONFIG = {
    navigation: [
        { label: 'What shipped', href: '#proof' },
        { label: 'Systems',      href: '#systems' },
        { label: 'Track record', href: '#experience' },
        { label: 'Writing',      href: '#notes' },
        { label: 'Connect',      href: '#connect' }
    ],
    links: {
        home:     'index.html',
        resume:   'https://github.com/narendranathe/resume2/releases/download/resume/Narendranath.pdf',
        linkedin: 'https://www.linkedin.com/in/narendranathe/',
        github:   'https://github.com/narendranathe',
        substack: 'https://narendranathe.substack.com',
        email:    'mailto:edara.narendranath@gmail.com'
    },
    identity: {
        name:             CONFIG.name,
        role:             'Data Engineer, AI Platforms',
        footerStatement:  'Senior AI platform engineering across retrieval, workflow automation, reusable engines, and production delivery.'
    },
    contactLinks: [
        { label: 'Email',    href: 'mailto:edara.narendranath@gmail.com' },
        { label: 'LinkedIn', href: 'https://www.linkedin.com/in/narendranathe/' },
        { label: 'GitHub',   href: 'https://github.com/narendranathe' },
        { label: 'Substack', href: 'https://narendranathe.substack.com' },
        { label: 'Resume',   href: 'https://github.com/narendranathe/resume2/releases/download/resume/Narendranath.pdf' }
    ]
};
