# LexMetric UI Mockups

Design mockups for the LexMetric Medicaid Audit Defense Agent.

## Structure

```
mockups/
├── public/              Marketing & public pages
│   ├── landing.html           Main landing page (Premium Design) ✅
│   └── landing_premium.html   Legacy reference
│
├── auth/                Authentication flows
│   ├── login.html             Standard login page ✅
│   └── login_premium.html     Premium login page ✅
│
└── app/                 Authenticated application pages
    ├── dashboard.html              Standard case list
    ├── dashboard_premium.html      Premium case list ✅
    ├── case-workspace.html         Standard transaction analysis
    ├── case-workspace_premium.html Premium transaction analysis ✅
    ├── settings.html               Standard user settings
    └── settings_premium.html       Premium user settings ✅
```

## How to View

Simply open any `.html` file in your browser:

```bash
# From project root
open mockups/public/landing.html
open mockups/auth/login_premium.html
open mockups/app/dashboard_premium.html
```

Or double-click the files in Finder.

## Design System

All **premium** mockups follow the **Bespoke Luxury Legal Tech** design:

| Token | Value | Usage |
|-------|-------|-------|
| `--legal-blue` | `#1a365d` | Headers, buttons, primary text |
| `--accent-gold` | `#C5A059` | Hover states, highlights |
| `--bg-ivory` | `#FDFCFB` | Page background |
| `--border-light` | `rgba(26,54,93,0.08)` | Card borders |

**Typography:**
- **Playfair Display** — Headings (serif)
- **Inter** — Body text (sans-serif)
- **JetBrains Mono** — Financial amounts

**Visual Effects:**
- Cream paper texture overlay
- Gold glow on hover
- Subtle card float animations

## Demo Credentials (Login Page)

```
Email: demo@lexmetric.com
Password: demo
```

Or click "Sign in with Google" for SSO demo.

---

**Version:** 2.0 (Premium Design System)  
**Last Updated:** January 23, 2026
