// ============================================
// PORTFOLIO CONFIGURATION TEMPLATE
// ============================================
// 
// INSTRUCTIONS FOR FORKERS:
// 1. Copy this file and rename to: config.js
// 2. Update the values below with your information
// 3. config.js is gitignored and won't be committed
// ============================================

const CONFIG = {
    // Your information
    name: 'Your Name',
    
    // RSS Feed Sources (all public - no API keys needed)
    rss: {
        medium: {
            enabled: true,
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
    
    // Recommendations (add your own)
    recommendations: [
        {
            text: "Add your recommendation text here...",
            name: "Recommender Name",
            role: "Their Role at Company",
            initials: "RN",
            avatar: "", // Optional: URL to their photo
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
