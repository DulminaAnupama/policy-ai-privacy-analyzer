import os
import requests
from flask import Flask, request, jsonify, render_template_string
from io import BytesIO

# ── Optional PDF library detection 

_PDF_BACKEND = None   

try:
    import pdfplumber as _pdfplumber_mod
    _PDF_BACKEND = "pdfplumber"
except ImportError:
    _pdfplumber_mod = None

if _PDF_BACKEND is None:
    try:
        import pypdf as _pypdf_mod
        _PDF_BACKEND = "pypdf"
    except ImportError:
        _pypdf_mod = None

if _PDF_BACKEND is None:
    try:
        import PyPDF2 as _PyPDF2_mod
        _PDF_BACKEND = "PyPDF2"
    except ImportError:
        _PyPDF2_mod = None

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# ── API Key Setup 
# Option 2 — Paste directly below:
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "") or "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"

# Model to use 
GROQ_MODEL = "llama-3.3-70b-versatile"


def validate_api_key():
    """Return the Groq API key, or raise a clear error if it is not set."""
    key = GROQ_API_KEY.strip()
    if not key or key == "PASTE_YOUR_GROQ_KEY_HERE":
        raise ValueError(
            "No Groq API key found.\n\n"
            "To fix this:\n"
            "  1. Go to https://console.groq.com and sign up ()\n"
            "  2. Click API Keys → Create API Key\n"
            "  3. Copy the key (starts with gsk_...)\n"
            "  4. Open policy_app.py and paste it where it says PASTE_YOUR_GROQ_KEY_HERE\n"
            "  5. Restart the app"
        )
    if not key.startswith("gsk_"):
        raise ValueError(
            "This doesn't look like a valid Groq API key.\n"
            "Groq keys start with 'gsk_'. Please check your key at https://console.groq.com"
        )
    return key

# ─── Pre-loaded Policy Text: Netflix Privacy Statement (April 17, 2025) ───────
DEFAULT_POLICY_TEXT = """
NETFLIX PRIVACY STATEMENT
Last Updated: April 17, 2025
Source: https://help.netflix.com/legal/privacy

INTRODUCTION:
This Privacy Statement explains how Netflix collects, uses, and discloses personal information
when users access the Netflix service. It also explains what privacy rights users have and how
to exercise them. Certain Netflix service features may provide additional contextual privacy
information beyond what is described here.

Contact: privacy@netflix.com | Data Protection Officer/Privacy Office

─────────────────────────────────────────────────────────────
SECTION A: COLLECTION, USE, AND DISCLOSURE OF PERSONAL INFORMATION
─────────────────────────────────────────────────────────────

CATEGORIES OF PERSONAL INFORMATION COLLECTED:

Personal details:
Email address, authentication credentials (e.g. password), first and last name, phone number,
postal address, gender, date of birth, and other identifiers provided during account setup.

Payment details:
Payment history, billing address, gift card and promotional offer redemptions, and information
required to process payments.

Purchase information:
Records of purchases made, shopping cart contents, purchase history, and overall purchase habits.

Netflix account and profile information:
Profile name and icon, Netflix game handle, content ratings and feedback, My List (watchlist),
continue watching data, account and profile settings, and feature preferences.

Usage information:
Playback events (play, pause, rewind, etc.), choices in interactive titles, Netflix game activity
(gameplay, progress, saved game data), viewing and gaming history, search queries, app clicks,
text input, page views, session duration, and camera/photo access for QR-code functionality.

Advertising information:
Data about ads viewed or interacted with on Netflix, resettable device identifiers, IP addresses,
and interest data collected or inferred by Advertising Companies from third-party websites and apps.
Used to support behavioural and non-behavioural advertising.

Device and network information:
Device IDs and unique identifiers (including network devices such as routers), IP addresses
(used to infer general location such as city, state, postal code), device and software characteristics,
referrer URLs, browser and app log data, connection type (wifi or cellular), crash reports,
timestamps, debug logs, cookies, resettable device identifiers, and advertising identifiers.

Communications:
Content of customer support interactions (chat, voice), survey responses, feedback provided
during service interactions (e.g. cancellation flows), and metadata about communications Netflix
sends to users (emails, push notifications, texts) including interaction data.

─────────────────────────────────────────────────────────────
SOURCES OF PERSONAL INFORMATION:
─────────────────────────────────────────────────────────────

Directly from users: Registration, account updates, purchases, correspondence, surveys.

Automatically during service use: Account/profile data, usage data, advertising data,
device/network data, and communications collected automatically.

From Partners: TV manufacturers, internet service providers, streaming device providers,
mobile carriers, and payment-assisting partners may share personal details, device/network
information, payment details, and search queries/commands applicable to Netflix.

From Service Providers: Vendors and contractors providing geolocation, fraud prevention,
payment processing, and game services on Netflix's behalf.

From Netflix Marketing Providers: Data from marketing campaigns promoting the Netflix
service or content on third-party platforms.

From Advertising Companies: Advertisers, Ad Service Providers, Ad Measurement Companies,
and online/offline data providers supplying demographic, interest, and location data.

From public sources: Publicly available social media posts, public databases, in compliance
with applicable laws.

─────────────────────────────────────────────────────────────
HOW NETFLIX USES PERSONAL INFORMATION:
─────────────────────────────────────────────────────────────

To provide the service:
Personalised content recommendations (netflix.com/recommendations), service optimisation
and feature personalisation, and localisation of content per licensing agreements. Uses:
personal details, account/profile info, purchase info, usage info, device/network info, communications.

To administer and operate the business:
Payment processing, gift card redemption, transactional communications, ISP identification for
troubleshooting, responding to user inquiries, password resets. Uses: personal details,
payment details, purchase info, account/profile info, usage info, device/network info, communications.

To research, analyse, and improve services:
Audience analytics, content selection optimisation, service delivery improvement, survey
processing. Uses: all categories listed above.

To enable Partner integrations and promotions:
Allowing Partners to promote Netflix and present it through their interfaces. Uses: personal
details, payment details, account/profile info, usage info, device/network info, communications.

To send marketing and informational messages:
News, promotional communications, new feature alerts, special offers — personalised where
applicable — delivered via email, push notification, text, or Netflix itself, and on third-party
platforms. Uses: personal details, account/profile info, purchase info, usage info,
device/network info, communications.

To support Advertisements:
Providing, analysing, administering, optimising, selecting, delivering, and measuring Advertisements,
including behavioural advertising based on third-party activity. Uses: personal details,
account/profile info, usage info, advertising info, device/network info.

For safety, security, and fraud prevention:
Securing systems, investigating and detecting prohibited or illegal activities and technical issues.
Uses: all categories listed above.

To comply with law and enforce Terms of Use:
Satisfying legal obligations, governmental requests, and protecting Netflix and user rights.
Includes verifying eligibility for signup offers and device-level compliance checks.
Uses: all categories listed above.

─────────────────────────────────────────────────────────────
WHO RECEIVES PERSONAL INFORMATION:
─────────────────────────────────────────────────────────────

Netflix family of companies — for all operational purposes listed above.
Service Providers — for communications, security, infrastructure, IT, games, payment processing,
and service personalisation. May monitor/record message content (e.g. chat) for safety.
Partners — for content suggestions, feature integration, and promotional purposes.
Netflix Marketing Providers — for campaign measurement and optimisation; contractual measures
prevent access to specific viewing title selections.
Advertising Companies — for ad selection, delivery, interaction facilitation, and measurement.
Promotional collaborators — for executing joint promotions.
Corporate transaction parties — in mergers, acquisitions, or asset transfers.
Law enforcement and government — when legally required or permitted.

─────────────────────────────────────────────────────────────
SECTION B: USER RIGHTS AND CONTROLS
─────────────────────────────────────────────────────────────

Access, correct, update, or delete personal information:
Users can access, correct, update, or request deletion of their personal information.
Data download available at: netflix.com/account/getmyinfo

Portability: Users can request a copy of their personal data.

Objection and consent withdrawal: Users may object to or request restriction of data processing.
Consent may be withdrawn at any time without affecting prior lawful processing.

Right to complain: Users may complain to a data protection authority.

Right against automated decision-making: Users may have the right not to be subject to
decisions made solely through automated means with significant legal or similar effects.

Communication preferences:
- Email and text: Manage via "Notification settings" in Account section, or unsubscribe links.
- Push notifications: Managed via device settings or Netflix Notification settings.
- Matched Identifier Communications: Opt out via "Privacy and data settings" in Account.
- Behavioural advertising: Opt out via "Behavioral Advertising" in Privacy and data settings.
  (Kids profiles: behavioural advertising is not used and no opt-out option is needed.)

Digital Advertising Alliance programs supported:
- EU: European Interactive Digital Advertising Alliance (EDAA)
- Canada: Digital Advertising Alliance of Canada (DAAC)
- US: Digital Advertising Alliance (DAA)

─────────────────────────────────────────────────────────────
SECTION C: ACCOUNT AND PROFILE ACCESS
─────────────────────────────────────────────────────────────

Account sharing: Account holders control all profiles and may share accounts with household
members. Shared users can see viewing history, account information, and game-related data
including chat and saved game information. Profile Lock PINs can restrict profile access.

Profiles: Profiles give personalised experiences with separate watch histories. Any account
user can navigate to, edit, or delete profiles. Profile transfer feature allows moving profiles
to separate accounts.

Parental controls: Available to manage minor users' access (see help.netflix.com/node/264).

Device access: Users can sign out of all devices via the Account section. Public or shared
device users should log out after each session.

─────────────────────────────────────────────────────────────
SECTION D: COOKIES AND TRACKING TECHNOLOGIES
─────────────────────────────────────────────────────────────

Technologies used: Cookies, pixel tags, browser storage (HTML5, IndexedDB, WebSQL), hashed
identifiers, and resettable device identifiers (e.g. Apple IDFA, Google Advertising ID).

Purposes: Service delivery (remembering users), business operations, analytics, marketing
personalisation, advertising support, safety and fraud prevention, and legal compliance.

Netflix Marketing Providers may collect data (pages visited, device/network info) via these
technologies and track activity across websites and sessions.

Hashed identifiers: Used for cross-platform marketing, advertising delivery, and analytics.
Resettable device identifiers: Used for marketing and advertising on mobile and streaming devices.

User choices:
- Cookies: Managed via Netflix cookie settings or browser preferences.
- Hashed identifiers: Opt out via "Matched Identifier Communications" in Privacy and data settings.
- Resettable device identifiers: Opt out via device "Privacy" or "Ads" settings.
- Other technologies: Managed via browser settings (clear storage, disable auto-image loading).
Netflix does not currently respond to browser "Do Not Track" signals.

─────────────────────────────────────────────────────────────
SECTION E: OTHER IMPORTANT DISCLOSURES
─────────────────────────────────────────────────────────────

Sharing functionality: Users can share personal information via in-service sharing tools
(email, text, social sharing apps) and social plugins operated by third-party social networks.

Security: Netflix employs administrative, logical, physical, and managerial safeguards
appropriate to the risks of processing personal information.

Data retention: Personal information is retained as long as necessary for service delivery,
operations, marketing, advertising, safety, and legal compliance. Securely destroyed or
de-identified when no longer needed.

Third-party platforms and links: Netflix may operate via or link to third-party platforms
(smart TVs, gaming systems, streaming devices). Those platforms have their own privacy policies.

Minors: Subscribers must be 18+ (or the age of majority in their country). Minors may access
the service only under parent or guardian supervision. Parental controls are available.

Policy updates: Netflix updates this Privacy Statement periodically. Continued use of the
service after updates constitutes acceptance. Users may cancel if they do not accept changes.

─────────────────────────────────────────────────────────────
SECTION F: NETFLIX GAMES SUPPLEMENTAL DISCLOSURES
─────────────────────────────────────────────────────────────

Additional data collected for Netflix Games:
- Account/profile info: Friend/team lists and team names (local and online multiplayer).
- Usage info: Leaderboard status and scores, game achievements, online/availability status,
  player searches and connections, multiplayer interactions, chat content, community guideline
  violation reports, and user-generated content (drawings, photos, videos, sound recordings).
- Device/network info: App, device, and account data when using Netflix game controller
  (e.g. connecting a mobile device to a Netflix Game on TV by scanning a QR code).

Data use in games: Game handle and leaderboard data displayed to all players; location used
for multiplayer matchmaking; chat content transmitted between players and monitored for safety;
user-generated content displayed per sharing settings.

Public visibility: Game handle, gameplay, chat, UGC, and online status are publicly visible
to other players in games with leaderboards, multiplayer, chat, or UGC features.

Legal compliance in games: Chat and game communications may be accessed, preserved, and
disclosed in response to legal requests from government agencies or civil litigants.

Games on TV/Netflix.com: Some games allow non-logged-in users to join; data collected
(usage, device/network, communications, saved game activity) may be linked to the host account.
""".strip()

# ─── Predefined Scenarios ─────────────────────────────────────────────────────
PREDEFINED_SCENARIOS = [
    {
        "id": "scenario_1",
        "name": "Children's Streaming Platform (Under-13)",
        "emoji": "👶",
        "description": (
            "Adapt the Netflix Privacy Statement for a streaming service primarily targeting children "
            "under 13. The platform must comply with COPPA (Children's Online Privacy Protection Act) "
            "and equivalent international child-safety laws. Parental consent is mandatory before any "
            "personal data can be collected. Behavioural advertising is completely prohibited. Data "
            "collection must be strictly minimal — only what is necessary to deliver the service. "
            "Parents must have full, real-time visibility and control over their child's data, viewing "
            "history, and communications. The policy tone must be accessible, reassuring, and clear "
            "for parents reading on behalf of their children."
        ),
        "audience": "Parents, child-safety regulators, COPPA compliance officers, child psychologists"
    },
    {
        "id": "scenario_2",
        "name": "Enterprise / Corporate Deployment",
        "emoji": "🏢",
        "description": (
            "Adapt the Netflix Privacy Statement for a corporate environment where a company is "
            "deploying the streaming service as an employee benefit or internal entertainment tool. "
            "The subscribing company (not individual employees) is the data controller. IT administrators "
            "require oversight of usage patterns for licence management and network compliance. Employee "
            "viewing activity may be subject to the company's acceptable use and monitoring policies. "
            "Data handling must align with corporate data governance frameworks, employment law, and "
            "HR regulations. The policy must clearly delineate what Netflix collects versus what the "
            "employer can access."
        ),
        "audience": "HR directors, IT security teams, legal counsel, corporate compliance officers"
    },
    {
        "id": "scenario_3",
        "name": "EU / GDPR Strict Compliance Mode",
        "emoji": "🇪🇺",
        "description": (
            "Adapt the Netflix Privacy Statement for users in the European Union under strict GDPR "
            "requirements. Every category of data processing must have a clearly stated, valid legal "
            "basis (consent, legitimate interest, contract, legal obligation, or vital interests). "
            "Consent must be freely given, specific, informed, and unambiguous — pre-ticked boxes and "
            "bundled consent are not permitted. Behavioural advertising requires explicit opt-in consent, "
            "not merely an opt-out mechanism. Data minimisation and purpose limitation are foundational "
            "principles. Users must have easily exercisable rights: erasure, portability, rectification, "
            "restriction, and objection to automated profiling. International data transfers must cite "
            "specific GDPR transfer mechanisms (SCCs, adequacy decisions)."
        ),
        "audience": "EU data protection officers, GDPR compliance teams, EU regulators, legal advisors"
    },
    {
        "id": "scenario_4",
        "name": "Health & Wellness Streaming Platform",
        "emoji": "🏥",
        "description": (
            "Adapt the Netflix Privacy Statement for a health-focused streaming service delivering "
            "medical education, mental health support content, therapy guidance, addiction recovery "
            "programmes, and general wellness videos. Viewing history on this platform may reveal "
            "highly sensitive health conditions — for example, watching content about cancer, HIV, "
            "mental illness, substance abuse, or reproductive health. This data must be treated as "
            "sensitive health information, equivalent to medical records in some jurisdictions. "
            "Sharing with advertisers must be heavily restricted or prohibited. Users must have "
            "explicit granular control over whether their viewing behaviour can be inferred, stored, "
            "or shared. The policy must address healthcare privacy laws such as HIPAA (US) or "
            "equivalent national health data regulations."
        ),
        "audience": "Healthcare providers, mental health advocates, patients, medical data regulators"
    }
]

# ─── HTML Template ─────────────────────────────────────────────────────────────
HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>PolicyAI — Privacy Policy Analyser</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Source+Serif+4:ital,wght@0,300;0,400;0,600;1,300&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
  <style>
    *,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
    :root{
      --navy:#1a1208;--deep:#211608;--panel:#27190a;--card:#301f0c;--border:#4a3010;
      --gold:#c9a84c;--gold-light:#e8c97a;--gold-dim:rgba(201,168,76,0.15);
      --green:#f59e0b;--green-dim:rgba(245,158,11,0.12);--green-light:#fbbf24;
      --teal:#fb923c;--teal-dim:rgba(251,146,60,0.12);
      --text:#fef3e2;--text-muted:#c4956a;--text-dim:#7a5c38;
      --success:#f59e0b;--error:#ef4444;
    }
    html,body{height:100%;background:var(--navy);color:var(--text);font-family:'Source Serif 4',Georgia,serif;font-size:15px;line-height:1.6;overflow:hidden}

    /* ── Welcome Overlay ── */
    #welcomeOverlay{position:fixed;inset:0;z-index:999;background:linear-gradient(135deg,#1a1208 0%,#2d1a06 50%,#1a1208 100%);display:flex;align-items:center;justify-content:center;animation:none}
    #welcomeOverlay.hidden{display:none}
    .welcome-box{text-align:center;max-width:560px;padding:3rem 2.5rem;background:rgba(48,31,12,0.85);border:1px solid var(--border);border-radius:20px;box-shadow:0 24px 80px rgba(0,0,0,0.7),0 0 0 1px rgba(245,158,11,0.1);backdrop-filter:blur(8px)}
    .welcome-logo{width:72px;height:72px;background:linear-gradient(135deg,var(--green),var(--teal));border-radius:18px;display:flex;align-items:center;justify-content:center;font-size:38px;margin:0 auto 1.5rem;box-shadow:0 8px 32px rgba(245,158,11,0.35)}
    .welcome-box h1{font-family:'Playfair Display',serif;font-size:2.1rem;color:var(--green-light);margin-bottom:0.4rem;letter-spacing:-0.5px}
    .welcome-box .subtitle{font-family:'JetBrains Mono',monospace;font-size:0.72rem;color:var(--text-muted);text-transform:uppercase;letter-spacing:2px;margin-bottom:1.75rem}
    .welcome-features{display:grid;grid-template-columns:1fr 1fr;gap:0.9rem;margin-bottom:2rem;text-align:left}
    .wf-item{background:rgba(245,158,11,0.07);border:1px solid rgba(245,158,11,0.2);border-radius:10px;padding:0.85rem;display:flex;gap:0.65rem;align-items:flex-start}
    .wf-icon{font-size:1.3rem;flex-shrink:0;margin-top:1px}
    .wf-title{font-size:0.8rem;font-weight:600;color:var(--green-light);margin-bottom:2px}
    .wf-desc{font-size:0.71rem;color:var(--text-muted);line-height:1.4}
    .btn-start{background:linear-gradient(135deg,var(--green),#d97706);color:#1a1208;font-weight:700;font-family:'JetBrains Mono',monospace;font-size:0.95rem;padding:0.85rem 2.5rem;border:none;border-radius:10px;cursor:pointer;transition:all 0.2s;letter-spacing:0.5px;box-shadow:0 4px 20px rgba(245,158,11,0.4)}
    .btn-start:hover{transform:translateY(-2px);box-shadow:0 8px 28px rgba(245,158,11,0.5)}
    .welcome-footer{margin-top:1.25rem;font-size:0.68rem;color:var(--text-dim);font-family:'JetBrains Mono',monospace}
    @keyframes fadeOutUp{to{opacity:0;transform:translateY(-20px)}}
    .welcome-box{animation:fadeInUp 0.5s ease}
    @keyframes fadeInUp{from{opacity:0;transform:translateY(24px)}to{opacity:1;transform:translateY(0)}}

    /* ── Header ── */
    header{background:var(--deep);border-bottom:2px solid var(--green);padding:0 2rem;height:64px;display:flex;align-items:center;justify-content:space-between;position:sticky;top:0;z-index:100;box-shadow:0 4px 24px rgba(0,0,0,0.6)}
    .brand{display:flex;align-items:center;gap:12px}
    .brand-icon{width:38px;height:38px;background:linear-gradient(135deg,var(--green),var(--green-light));border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:20px}
    .brand h1{font-family:'Playfair Display',serif;font-size:1.3rem;color:var(--green-light)}
    .brand p{font-size:0.68rem;color:var(--text-muted);font-family:'JetBrains Mono',monospace;letter-spacing:1px;text-transform:uppercase}
    .badge{background:rgba(76,175,130,0.15);border:1px solid var(--green);color:var(--green-light);padding:4px 12px;border-radius:20px;font-size:0.72rem;font-family:'JetBrains Mono',monospace}

    /* ── Layout ── */
    .workspace{display:grid;grid-template-columns:1fr 1fr;height:calc(100vh - 64px)}
    .panel{height:100%;overflow-y:auto;padding:1.5rem;background:var(--panel);scrollbar-width:thin;scrollbar-color:var(--border) transparent}
    .panel:first-child{border-right:2px solid var(--border)}
    .panel::-webkit-scrollbar{width:4px}
    .panel::-webkit-scrollbar-thumb{background:var(--border);border-radius:2px}

    /* ── Panel headers ── */
    .panel-header{display:flex;align-items:center;gap:10px;margin-bottom:1.25rem;padding-bottom:1rem;border-bottom:1px solid var(--border)}
    .panel-icon{width:36px;height:36px;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:18px;flex-shrink:0}
    .panel-icon.green{background:var(--green-dim)}
    .panel-icon.teal{background:var(--teal-dim)}
    .panel-header h2{font-family:'Playfair Display',serif;font-size:1.1rem}
    .panel-header p{font-size:0.75rem;color:var(--text-muted);margin-top:1px}

    /* ── Cards ── */
    .card{background:var(--card);border:1px solid var(--border);border-radius:10px;padding:1.1rem;margin-bottom:1rem}
    .card-title{font-family:'JetBrains Mono',monospace;font-size:0.68rem;text-transform:uppercase;letter-spacing:1.5px;color:var(--text-muted);margin-bottom:0.75rem;display:flex;align-items:center;justify-content:space-between}

    /* ── Form elements ── */
    label{display:block;font-size:0.78rem;color:var(--text-muted);margin-bottom:4px;font-family:'JetBrains Mono',monospace}
    textarea,select,input[type=text]{width:100%;background:var(--navy);border:1px solid var(--border);border-radius:8px;color:var(--text);font-family:'Source Serif 4',serif;font-size:0.83rem;padding:0.65rem 0.75rem;transition:border-color 0.2s;resize:vertical}
    textarea:focus,select:focus,input[type=text]:focus{outline:none;border-color:var(--green)}
    input[type=text]{resize:none}

    /* ── Tabs ── */
    .tab-row{display:flex;gap:4px;margin-bottom:0.75rem;background:var(--navy);padding:4px;border-radius:8px}
    .tab-btn{flex:1;padding:0.4rem;border:none;border-radius:6px;background:transparent;color:var(--text-muted);font-size:0.73rem;font-family:'JetBrains Mono',monospace;cursor:pointer;transition:all 0.2s;letter-spacing:0.5px}
    .tab-btn.active{background:var(--card);color:var(--green-light)}
    .tab-content{display:none}
    .tab-content.active{display:block}

    /* ── Upload zone ── */
    .upload-zone{border:2px dashed var(--border);border-radius:8px;padding:1.2rem;text-align:center;cursor:pointer;transition:all 0.2s;background:var(--navy);margin-bottom:0.75rem}
    .upload-zone:hover,.upload-zone.drag-over{border-color:var(--green);background:var(--green-dim)}
    .upload-zone span{font-size:1.5rem;display:block;margin-bottom:4px}
    .upload-zone p{font-size:0.79rem;color:var(--text-muted)}
    #fileInput{display:none}

    /* ── Buttons ── */
    .btn{display:inline-flex;align-items:center;gap:7px;padding:0.55rem 1rem;border:none;border-radius:7px;font-size:0.8rem;font-family:'JetBrains Mono',monospace;cursor:pointer;transition:all 0.2s;letter-spacing:0.3px}
    .btn-green{background:linear-gradient(135deg,var(--green),#3a9a6a);color:#fff;font-weight:600}
    .btn-green:hover{transform:translateY(-1px);box-shadow:0 4px 12px rgba(76,175,130,0.35)}
    .btn-teal{background:linear-gradient(135deg,var(--teal),#3ab5ac);color:var(--navy);font-weight:600}
    .btn-teal:hover{transform:translateY(-1px);box-shadow:0 4px 12px rgba(78,205,196,0.3)}
    .btn-ghost{background:transparent;border:1px solid var(--border);color:var(--text-muted)}
    .btn-ghost:hover{border-color:var(--text-muted);color:var(--text)}
    .btn:disabled{opacity:0.45;cursor:not-allowed;transform:none!important}
    .btn-row{display:flex;gap:8px;flex-wrap:wrap;margin-top:0.75rem}
    .btn-full{width:100%;justify-content:center;padding:0.7rem}

    /* ── Scenario chips ── */
    .scenario-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:0.75rem}
    .chip{background:var(--navy);border:1.5px solid var(--border);border-radius:8px;padding:0.7rem;cursor:pointer;transition:all 0.2s}
    .chip:hover{border-color:var(--teal);background:var(--teal-dim)}
    .chip.selected{border-color:var(--teal);background:var(--teal-dim)}
    .chip-title{font-weight:600;color:var(--text);font-size:0.82rem;margin-bottom:2px}
    .chip-sub{color:var(--text-muted);font-size:0.7rem;line-height:1.3}

    /* ── Status bars ── */
    .status{display:flex;align-items:flex-start;gap:8px;padding:0.5rem 0.8rem;border-radius:6px;font-size:0.77rem;font-family:'JetBrains Mono',monospace;margin-bottom:0.75rem;animation:fadeIn 0.3s ease;white-space:pre-wrap;word-break:break-word;line-height:1.5}
    .status.loading{background:rgba(76,175,130,0.1);border:1px solid rgba(76,175,130,0.3);color:var(--green-light)}
    .status.success{background:rgba(76,175,130,0.1);border:1px solid rgba(76,175,130,0.3);color:var(--success)}
    .status.error{background:rgba(224,90,106,0.1);border:1px solid rgba(224,90,106,0.3);color:var(--error)}
    .spinner{width:13px;height:13px;border:2px solid transparent;border-top-color:var(--green);border-radius:50%;animation:spin 0.8s linear infinite;flex-shrink:0}
    @keyframes spin{to{transform:rotate(360deg)}}
    @keyframes fadeIn{from{opacity:0;transform:translateY(-4px)}to{opacity:1;transform:translateY(0)}}

    /* ── Output box ── */
    .output-box{background:var(--navy);border:1px solid var(--border);border-radius:8px;padding:1rem;min-height:150px;font-size:0.82rem;line-height:1.75;color:var(--text)}
    .output-box h2{font-family:'Playfair Display',serif;color:var(--green-light);font-size:0.95rem;margin:0.8rem 0 0.3rem;border-bottom:1px solid var(--border);padding-bottom:3px}
    .output-box h3{color:var(--teal);font-size:0.82rem;margin:0.5rem 0 0.2rem;font-family:'JetBrains Mono',monospace}
    .output-box strong{color:var(--green-light)}
    .output-box ul{padding-left:1.2rem;margin:0.3rem 0}
    .output-box li{margin-bottom:0.2rem}

    /* ── Draft cards ── */
    .draft-card{background:var(--navy);border:1px solid var(--border);border-radius:10px;overflow:hidden;margin-bottom:1rem}
    .draft-header{background:var(--card);padding:0.65rem 1rem;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid var(--border)}
    .draft-title{font-family:'JetBrains Mono',monospace;font-size:0.78rem;color:var(--teal)}
    .draft-body{padding:1rem;font-size:0.82rem;line-height:1.75;color:var(--text);max-height:520px;overflow-y:auto}

    /* ── Copy button ── */
    .copy-btn{background:transparent;border:1px solid var(--border);border-radius:5px;color:var(--text-muted);font-size:0.7rem;font-family:'JetBrains Mono',monospace;padding:3px 8px;cursor:pointer;transition:all 0.2s}
    .copy-btn:hover{border-color:var(--teal);color:var(--teal)}

    /* ── Divider ── */
    .divider{display:flex;align-items:center;gap:8px;margin:0.75rem 0;color:var(--text-dim);font-size:0.7rem;font-family:'JetBrains Mono',monospace}
    .divider::before,.divider::after{content:'';flex:1;height:1px;background:var(--border)}

    /* ── Char count ── */
    .char-count{text-align:right;font-size:0.67rem;font-family:'JetBrains Mono',monospace;color:var(--text-dim);margin-top:3px}

    /* ── Empty state ── */
    .empty-state{text-align:center;padding:2.5rem 1rem;color:var(--text-dim);font-style:italic;font-size:0.85rem}
    .empty-state .icon{font-size:2.2rem;display:block;margin-bottom:0.5rem}

    /* ── Helper ── */
    .mb{margin-bottom:0.6rem}

    /* ── Responsive ── */
    @media(max-width:860px){
      .workspace{grid-template-columns:1fr;height:auto;overflow-y:auto}
      .panel{height:auto;overflow-y:visible}
      html,body{overflow:auto}
      .scenario-grid{grid-template-columns:1fr}
    }
  </style>
</head>
<body>

<!-- ══════ WELCOME OVERLAY ══════ -->
<div id="welcomeOverlay">
  <div class="welcome-box">
    <div class="welcome-logo">🔒</div>
    <h1>PolicyAI</h1>
    <p class="subtitle">Privacy Policy Analyser &amp; Generator</p>
    <div class="welcome-features">
      <div class="wf-item">
        <span class="wf-icon">📄</span>
        <div>
          <div class="wf-title">Smart Summarisation</div>
          <div class="wf-desc">Upload, paste, or use pre-loaded policies — get a structured AI summary in seconds</div>
        </div>
      </div>
      <div class="wf-item">
        <span class="wf-icon">🎭</span>
        <div>
          <div class="wf-title">Scenario Generation</div>
          <div class="wf-desc">Adapt any policy for children, enterprise, GDPR, healthcare &amp; custom contexts</div>
        </div>
      </div>
      <div class="wf-item">
        <span class="wf-icon">⚡</span>
        <div>
          <div class="wf-title">Groq-Powered AI</div>
          <div class="wf-desc">Lightning-fast LLaMA 3.3 70B model — completely free to use</div>
        </div>
      </div>
      <div class="wf-item">
        <span class="wf-icon">📎</span>
        <div>
          <div class="wf-title">PDF Support</div>
          <div class="wf-desc">Extract text directly from PDF files or paste policy text manually</div>
        </div>
      </div>
    </div>
    <button class="btn-start" onclick="startApp()">🚀 Get Started</button>
    <p class="welcome-footer">⚡ Powered by Groq AI · Free tier ·</p>
  </div>
</div>

<header>
  <div class="brand">
    <div class="brand-icon">🔒</div>
    <div>
      <h1>PolicyAI — Privacy Analyser</h1>
      <p>Privacy Policy Summarisation &amp; Scenario Generation</p>
    </div>
  </div>
  <div class="badge">⚡ Powered by Groq AI (Free)</div>
</header>

<div class="workspace">

  <!-- ══════ LEFT PANEL — POLICY SUMMARISATION ══════ -->
  <div class="panel">
    <div class="panel-header">
      <div class="panel-icon green">📄</div>
      <div>
        <h2>Policy Summarisation</h2>
        <p>Upload, paste, or use the pre-loaded Netflix policy — then generate an AI summary covering goals, strategies &amp; direction</p>
      </div>
    </div>

    <!-- Input source tabs -->
    <div class="card">
      <div class="card-title">📥 POLICY INPUT SOURCE</div>
      <div class="tab-row">
        <button class="tab-btn active" onclick="switchTab('upload', event)">📎 Upload PDF</button>
        <button class="tab-btn" onclick="switchTab('paste', event)">📝 Paste Text</button>
        <button class="tab-btn" onclick="switchTab('preload', event)">🏛️ Pre-loaded</button>
      </div>

      <!-- Upload tab -->
      <div id="tab-upload" class="tab-content active">
        <div class="upload-zone" id="uploadZone" onclick="document.getElementById('fileInput').click()">
          <span>📂</span>
          <p><strong>Click to upload</strong> or drag &amp; drop a PDF</p>
          <p style="font-size:0.7rem;margin-top:4px;color:var(--text-dim)">PDF files up to 16MB</p>
        </div>
        <input type="file" id="fileInput" accept=".pdf" onchange="handleFile(event)">
        <div id="uploadStatus"></div>
      </div>

      <!-- Paste tab -->
      <div id="tab-paste" class="tab-content">
        <label>Paste policy text below:</label>
        <textarea id="pasteText" rows="7" placeholder="Paste your privacy policy or any policy document text here..."
          oninput="document.getElementById('pasteChars').textContent=this.value.length.toLocaleString()"></textarea>
        <div class="char-count"><span id="pasteChars">0</span> characters</div>
        <div class="btn-row">
          <button class="btn btn-ghost" onclick="usePasteText()">✓ Use This Text</button>
          <button class="btn btn-ghost" onclick="document.getElementById('pasteText').value='';document.getElementById('pasteChars').textContent='0'">✕ Clear</button>
        </div>
      </div>

      <!-- Pre-loaded tab -->
      <div id="tab-preload" class="tab-content">
        <div style="background:var(--navy);border-radius:8px;padding:0.85rem;margin-bottom:0.75rem">
          <p style="font-size:0.82rem;color:var(--green-light);font-weight:600;margin-bottom:4px">🔒 Pre-loaded privacy policy ready</p>
          <p style="font-size:0.75rem;color:var(--text-muted)">Netflix Privacy Statement — April 17, 2025</p>
          <p style="font-size:0.7rem;color:var(--text-dim);margin-top:3px;font-family:'JetBrains Mono',monospace">Data Collection · User Rights · Advertising · Cookies · Games</p>
        </div>
        <button class="btn btn-green" onclick="loadDefault()">🔒 Load Netflix Privacy Policy</button>
      </div>
    </div>

    <!-- Active policy preview -->
    <div class="card" id="previewCard" style="display:none">
      <div class="card-title">
        <span>📋 ACTIVE POLICY TEXT (editable)</span>
        <button class="copy-btn" onclick="copyEl('activeText')">Copy</button>
      </div>
      <textarea id="activeText" rows="5"
        oninput="activePolicyText=this.value;document.getElementById('activeChars').textContent=this.value.length.toLocaleString()"></textarea>
      <div class="char-count"><span id="activeChars">0</span> characters loaded</div>
    </div>

    <!-- Generate summary button -->
    <div id="sumStatus"></div>
    <button class="btn btn-green btn-full" id="sumBtn" onclick="generateSummary()" disabled>
      🔍 Generate Policy Summary
    </button>

    <!-- Summary output -->
    <div class="card" id="summaryCard" style="margin-top:1rem;display:none">
      <div class="card-title">
        <span>📊 AI-GENERATED SUMMARY</span>
        <div style="display:flex;gap:6px">
          <button class="copy-btn" onclick="copyEl('summaryOut')">Copy</button>
          <button class="copy-btn" style="color:var(--teal);border-color:var(--teal)"
            onclick="document.getElementById('rightPanel').scrollIntoView({behavior:'smooth'})">→ Scenarios</button>
        </div>
      </div>
      <div class="output-box" id="summaryOut"></div>
    </div>
  </div>

  <!-- ══════ RIGHT PANEL — SCENARIO GENERATION ══════ -->
  <div class="panel" id="rightPanel">
    <div class="panel-header">
      <div class="panel-icon teal">🎭</div>
      <div>
        <h2>Scenario-Based Policy Generation</h2>
        <p>Select one or more scenarios and generate adapted policy drafts from the summary</p>
      </div>
    </div>

    <!-- Scenario selector -->
    <div class="card">
      <div class="card-title">🎯 SELECT PREDEFINED SCENARIOS</div>
      <p style="font-size:0.78rem;color:var(--text-muted);margin-bottom:0.75rem">
        Each scenario changes the target audience, priorities, or constraints of the privacy policy. Select one or more, then click Generate.
      </p>
      <div class="scenario-grid" id="scenarioGrid">
        {% for s in scenarios %}
        <div class="chip" id="chip-{{ s.id }}" onclick="toggleChip('{{ s.id }}')">
          <div class="chip-title">{{ s.emoji }} {{ s.name }}</div>
          <div class="chip-sub">{{ s.audience }}</div>
        </div>
        {% endfor %}
      </div>

      <div class="divider">OR DEFINE A CUSTOM SCENARIO</div>

      <label class="mb">Custom Scenario Name:</label>
      <input type="text" id="customName" placeholder="e.g., Public Sector / Government Agency" class="mb" style="margin-bottom:0.6rem">

      <label class="mb">Custom Scenario Description:</label>
      <textarea id="customDesc" rows="3"
        placeholder="Describe the context, target audience, and key priorities for this scenario..." class="mb"></textarea>

      <label style="margin-top:0.4rem">Additional Requirements (optional):</label>
      <textarea id="customReqs" rows="2" placeholder="Any specific constraints, regulations, or emphasis areas..."></textarea>
    </div>

    <!-- Summary readiness indicator -->
    <div class="card">
      <div class="card-title">📋 SUMMARY STATUS</div>
      <div id="summaryStatus" style="font-size:0.8rem;color:var(--text-muted);font-style:italic">
        ⚠️ No summary yet — generate a summary in the left panel first.
      </div>
    </div>

    <!-- Generate & clear buttons -->
    <div id="genStatus"></div>
    <div style="display:flex;gap:8px;margin-bottom:1rem">
      <button class="btn btn-teal btn-full" id="genBtn" onclick="generateScenarios()" disabled style="flex:1">
        ⚡ Generate Selected Scenarios
      </button>
      <button class="btn btn-ghost" onclick="clearDrafts()" title="Clear all drafts" style="padding:0.7rem 0.9rem">✕</button>
    </div>

    <!-- Draft outputs -->
    <div id="draftsContainer">
      <div class="empty-state">
        <span class="icon">📜</span>
        <p>Adapted policy drafts will appear here.</p>
        <p style="font-size:0.75rem;margin-top:0.3rem">Select scenarios above and click <strong>Generate</strong>.</p>
        <p style="font-size:0.72rem;margin-top:0.5rem;color:var(--text-dim)">You can change scenarios and regenerate at any time.</p>
      </div>
    </div>
  </div>

</div><!-- /workspace -->

<script>
  // ── Welcome overlay ────────────────────────────────────────────────────────
  function startApp() {
    const overlay = document.getElementById('welcomeOverlay');
    overlay.style.animation = 'fadeOutUp 0.4s ease forwards';
    setTimeout(() => overlay.classList.add('hidden'), 400);
  }

  // ── State ──────────────────────────────────────────────────────────────────
  let activePolicyText = '';
  let activeSummary = '';
  let selectedScenarios = {};

  const SCENARIO_DATA = {
    {% for s in scenarios %}
    '{{ s.id }}': {
      name: '{{ s.emoji }} {{ s.name }}',
      description: `{{ s.description }}`
    },
    {% endfor %}
  };

  // ── Tabs ───────────────────────────────────────────────────────────────────
  function switchTab(name, evt) {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    evt.currentTarget.classList.add('active');
    document.getElementById('tab-' + name).classList.add('active');
  }

  // ── File upload ────────────────────────────────────────────────────────────
  const zone = document.getElementById('uploadZone');
  zone.addEventListener('dragover', e => { e.preventDefault(); zone.classList.add('drag-over'); });
  zone.addEventListener('dragleave', () => zone.classList.remove('drag-over'));
  zone.addEventListener('drop', e => {
    e.preventDefault(); zone.classList.remove('drag-over');
    if (e.dataTransfer.files[0]) processFile(e.dataTransfer.files[0]);
  });

  function handleFile(e) { if (e.target.files[0]) processFile(e.target.files[0]); }

  async function processFile(file) {
    showStatus('uploadStatus', 'loading', `⏳ Extracting text from "${file.name}"...`);
    const fd = new FormData();
    fd.append('file', file);
    try {
      const r = await fetch('/api/extract-pdf', { method: 'POST', body: fd });
      const d = await r.json();
      if (d.error) throw new Error(d.error);
      setPolicy(d.text);
      const backend = d.backend ? ` (via ${d.backend})` : '';
      showStatus('uploadStatus', 'success', `✓ Extracted ${d.chars.toLocaleString()} characters from "${file.name}"${backend}`);
    } catch (e) {
      // Show the full error message — it may contain install instructions
      const msg = e.message || 'Unknown error. Is the Flask server running?';
      showStatus('uploadStatus', 'error', `✕ ${msg}`);
    }
  }

  // ── Paste / Default ────────────────────────────────────────────────────────
  function usePasteText() {
    const t = document.getElementById('pasteText').value.trim();
    if (!t) { alert('Please paste some text first.'); return; }
    setPolicy(t);
  }

  function loadDefault() {
    setPolicy({{ default_policy | tojson }});
    showStatus('uploadStatus', 'success', '✓ Netflix Privacy Statement (Apr 2025) loaded successfully');
  }

  function setPolicy(text) {
    activePolicyText = text;
    document.getElementById('activeText').value = text;
    document.getElementById('activeChars').textContent = text.length.toLocaleString();
    document.getElementById('previewCard').style.display = 'block';
    document.getElementById('sumBtn').disabled = false;
  }

  // ── Summarisation ──────────────────────────────────────────────────────────
  async function generateSummary() {
    if (!activePolicyText) { alert('No policy text loaded.'); return; }
    showStatus('sumStatus', 'loading', '🔍 Analysing privacy policy — this may take 20–40 seconds...');
    document.getElementById('sumBtn').disabled = true;
    // Reset summary status on right panel
    updateSummaryStatus(false);
    try {
      const r = await fetch('/api/summarise', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ policy_text: activePolicyText })
      });
      const d = await r.json();
      if (d.error) throw new Error(d.error);
      activeSummary = d.summary;
      renderSummary(d.summary);
      showStatus('sumStatus', 'success', '✓ Summary generated — ready for scenario generation');
      updateSummaryStatus(true);
    } catch (e) {
      showStatus('sumStatus', 'error', `✕ ${e.message}`);
    } finally {
      document.getElementById('sumBtn').disabled = false;
    }
  }

  function renderSummary(text) {
    const card = document.getElementById('summaryCard');
    const out = document.getElementById('summaryOut');
    card.style.display = 'block';
    out.innerHTML = formatText(text);
  }

  function updateSummaryStatus(ready) {
    const el = document.getElementById('summaryStatus');
    const btn = document.getElementById('genBtn');
    if (ready && activeSummary) {
      el.innerHTML = `<span style="color:var(--success)">✓ Summary ready</span> — <span style="color:var(--text-muted);font-size:0.75rem">${activeSummary.length.toLocaleString()} chars · select scenarios below and generate drafts</span>`;
      el.style.fontStyle = 'normal';
      btn.disabled = false;
    } else {
      el.innerHTML = '⚠️ No summary yet — generate a summary in the left panel first.';
      el.style.fontStyle = 'italic';
      btn.disabled = true;
    }
  }

  // ── Scenario chips ─────────────────────────────────────────────────────────
  function toggleChip(id) {
    const chip = document.getElementById('chip-' + id);
    if (selectedScenarios[id]) {
      delete selectedScenarios[id];
      chip.classList.remove('selected');
    } else {
      selectedScenarios[id] = SCENARIO_DATA[id];
      chip.classList.add('selected');
    }
  }

  // ── Generate scenarios ─────────────────────────────────────────────────────
  async function generateScenarios() {
    if (!activeSummary) { alert('Please generate a policy summary first.'); return; }

    const list = [...Object.values(selectedScenarios)];
    const cName = document.getElementById('customName').value.trim();
    const cDesc = document.getElementById('customDesc').value.trim();
    if (cName && cDesc) {
      list.push({
        name: cName,
        description: cDesc,
        custom_requirements: document.getElementById('customReqs').value.trim()
      });
    }

    if (list.length === 0) {
      alert('Please select at least one scenario chip, or fill in a custom scenario name and description.');
      return;
    }

    showStatus('genStatus', 'loading', `⚡ Generating ${list.length} scenario draft(s) — please wait...`);
    document.getElementById('genBtn').disabled = true;
    document.getElementById('draftsContainer').innerHTML = '';

    let successCount = 0;
    for (const s of list) {
      const el = makePlaceholder(s.name);
      document.getElementById('draftsContainer').appendChild(el);
      try {
        const r = await fetch('/api/generate-scenario', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            summary: activeSummary,
            scenario_name: s.name,
            scenario_description: s.description,
            custom_requirements: s.custom_requirements || ''
          })
        });
        const d = await r.json();
        if (d.error) throw new Error(d.error);
        fillDraft(el, s.name, d.draft);
        successCount++;
      } catch (e) {
        fillError(el, s.name, e.message);
      }
    }

    showStatus('genStatus', 'success', `✓ Generated ${successCount}/${list.length} scenario draft(s) — change selections to iterate`);
    document.getElementById('genBtn').disabled = false;
  }

  // ── Draft rendering helpers ────────────────────────────────────────────────
  function makePlaceholder(name) {
    const d = document.createElement('div');
    d.className = 'draft-card';
    d.innerHTML = `
      <div class="draft-header">
        <span class="draft-title">⏳ Generating: ${escHtml(name)}</span>
        <div class="spinner" style="border-top-color:var(--teal)"></div>
      </div>
      <div class="draft-body" style="color:var(--text-dim);font-style:italic">Drafting adapted policy...</div>`;
    return d;
  }

  function fillDraft(el, name, text) {
    el.innerHTML = `
      <div class="draft-header">
        <span class="draft-title">📜 ${escHtml(name)}</span>
        <button class="copy-btn" onclick="copyDraft(this)">Copy Draft</button>
      </div>
      <div class="draft-body">${formatText(text)}</div>`;
  }

  function fillError(el, name, msg) {
    el.innerHTML = `
      <div class="draft-header">
        <span class="draft-title" style="color:var(--error)">✕ Failed: ${escHtml(name)}</span>
      </div>
      <div class="draft-body" style="color:var(--error)">${escHtml(msg)}</div>`;
  }

  function clearDrafts() {
    document.getElementById('draftsContainer').innerHTML = `
      <div class="empty-state">
        <span class="icon">📜</span>
        <p>Adapted policy drafts will appear here.</p>
        <p style="font-size:.75rem;margin-top:.3rem">Select scenarios above and click <strong>Generate</strong>.</p>
        <p style="font-size:.72rem;margin-top:.5rem;color:var(--text-dim)">You can change scenarios and regenerate at any time.</p>
      </div>`;
    document.getElementById('genStatus').innerHTML = '';
  }

  // ── Text formatter ─────────────────────────────────────────────────────────
  function formatText(t) {
    return t
      .replace(/^# (.+)$/gm, '<h2 style="font-size:1rem;color:var(--green-light);font-family:Playfair Display,serif;margin:.6rem 0 .25rem">$1</h2>')
      .replace(/^## (.+)$/gm, '<h2 style="color:var(--green-light);font-family:Playfair Display,serif;margin:.6rem 0 .25rem">$1</h2>')
      .replace(/^### (.+)$/gm, '<h3 style="color:var(--teal);font-family:JetBrains Mono,monospace;font-size:.82rem;margin:.4rem 0 .2rem">$1</h3>')
      .replace(/^---+$/gm, '<hr style="border:none;border-top:1px solid var(--border);margin:.5rem 0">')
      .replace(/\*\*(.+?)\*\*/g, '<strong style="color:var(--green-light)">$1</strong>')
      .replace(/\*(.+?)\*/g, '<em>$1</em>')
      .replace(/^[•\-] (.+)$/gm, '<li style="margin-left:1.2rem;margin-bottom:.2rem">$1</li>')
      .replace(/(<li.*<\/li>)/gs, '<ul style="margin:.3rem 0">$1</ul>')
      .replace(/\n/g, '<br>');
  }

  function escHtml(str) {
    return String(str).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
  }

  // ── Utilities ──────────────────────────────────────────────────────────────
  function showStatus(id, type, msg) {
    const spin = type === 'loading' ? '<div class="spinner"></div>' : '';
    document.getElementById(id).innerHTML = `<div class="status ${type}">${spin}${msg}</div>`;
  }

  function copyEl(id) {
    const el = document.getElementById(id);
    navigator.clipboard.writeText(el.innerText || el.value)
      .then(() => alert('Copied to clipboard!'));
  }

  function copyDraft(btn) {
    const body = btn.closest('.draft-card').querySelector('.draft-body');
    navigator.clipboard.writeText(body.innerText)
      .then(() => { btn.textContent = '✓ Copied!'; setTimeout(() => btn.textContent = 'Copy Draft', 2000); });
  }
</script>
</body>
</html>"""

# ─── Groq API helper (100% FREE) ───────────────────────────────────────────────
def call_groq(system_prompt, user_prompt):
    """
    Call the Groq API via direct HTTP — no SDK required.
    Groq uses the OpenAI-compatible chat completions format.

    Free tier: 30 req/min · 14,400 req/day · No credit card needed.
    Model: llama-3.3-70b-versatile — excellent quality, very fast on Groq hardware.

    Raises RuntimeError with a clear, user-friendly message on any failure.
    """
    key = validate_api_key()

    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt},
        ],
        "max_tokens": 3000,
        "temperature": 0.4,
    }

    try:
        resp = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=120,
        )
    except requests.exceptions.Timeout:
        raise RuntimeError(
            "The request timed out after 120 seconds.\n"
            "The policy text may be very long — try trimming it and retrying."
        )
    except requests.exceptions.ConnectionError:
        raise RuntimeError(
            "Could not connect to the Groq API.\n"
            "Please check your internet connection and try again."
        )

    # ── Handle HTTP errors with clear, actionable messages ──────────────────
    if resp.status_code == 401:
        raise RuntimeError(
            "Invalid Groq API key (401 Unauthorised).\n"
            "Please check your key at https://console.groq.com and update it in policy_app.py."
        )

    if resp.status_code == 403:
        raise RuntimeError(
            "Access denied (403 Forbidden).\n"
            "Your Groq API key may have been revoked. "
            "Create a new one at https://console.groq.com → API Keys."
        )

    if resp.status_code == 429:
        # Groq includes a Retry-After header when rate-limited
        retry_after = resp.headers.get("Retry-After", "a few seconds")
        try:
            err_detail = resp.json().get("error", {}).get("message", "")
        except Exception:
            err_detail = ""
        raise RuntimeError(
            f"Groq rate limit reached (429). Please wait {retry_after} and try again.\n"
            f"Free tier allows 30 requests/minute and 14,400/day.\n"
            + (f"Detail: {err_detail}" if err_detail else "")
        )

    if resp.status_code == 503:
        raise RuntimeError(
            "Groq servers are temporarily unavailable (503).\n"
            "This is rare — please wait 15–30 seconds and try again."
        )

    if not resp.ok:
        # Catch any other unexpected HTTP status
        try:
            msg = resp.json().get("error", {}).get("message", resp.text[:300])
        except Exception:
            msg = resp.text[:300]
        raise RuntimeError(
            f"Groq API returned HTTP {resp.status_code}: {msg}"
        )

    # ── Parse the successful response ───────────────────────────────────────
    try:
        data = resp.json()
    except Exception:
        raise RuntimeError(
            f"Could not parse Groq API response (HTTP {resp.status_code}). Please try again."
        )

    if "error" in data:
        err = data["error"]
        raise RuntimeError(
            f"Groq API error: {err.get('message', str(err))}"
        )

    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError):
        raise RuntimeError(
            f"Unexpected response structure from Groq API: {data}"
        )

# ─── Routes ────────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template_string(
        HTML_TEMPLATE,
        scenarios=PREDEFINED_SCENARIOS,
        default_policy=DEFAULT_POLICY_TEXT
    )

@app.route("/api/extract-pdf", methods=["POST"])
def extract_pdf():
    """
    Extract plain text from an uploaded PDF file.
    Tries pdfplumber → pypdf → PyPDF2 in order.
    Returns a clear error if no PDF library is installed, rather than crashing.
    """
    # Check up front that we have at least one PDF library available
    if _PDF_BACKEND is None:
        return jsonify({
            "error": (
                "No PDF library is installed on this server. "
                "Please run ONE of the following commands in your terminal, then restart the app:\n\n"
                "  pip install pdfplumber       ← recommended\n"
                "  pip install pypdf            ← alternative\n"
                "  pip install PyPDF2           ← older alternative\n\n"
                "Once installed, upload your PDF again."
            )
        }), 500

    if "file" not in request.files:
        return jsonify({"error": "No file was attached to the request."}), 400

    f = request.files["file"]

    if not f.filename:
        return jsonify({"error": "No filename detected — please select a PDF file."}), 400

    if not f.filename.lower().endswith(".pdf"):
        return jsonify({"error": f'"{f.filename}" is not a PDF. Please upload a .pdf file.'}), 400

    raw_bytes = f.read()
    if len(raw_bytes) == 0:
        return jsonify({"error": "The uploaded file is empty. Please try again with a valid PDF."}), 400

    try:
        text = _extract_text_from_pdf_bytes(raw_bytes)

        if not text or not text.strip():
            return jsonify({
                "error": (
                    "The PDF was opened but no readable text was found. "
                    "This usually means it is a scanned image PDF without OCR. "
                    "Try copying the text manually and using the 'Paste Text' tab instead."
                )
            }), 400

        return jsonify({"text": text.strip(), "chars": len(text.strip()), "backend": _PDF_BACKEND})

    except Exception as e:
        return jsonify({
            "error": (
                f"Could not read this PDF ({type(e).__name__}: {e}). "
                "The file may be password-protected or corrupted. "
                "Try the 'Paste Text' tab as an alternative."
            )
        }), 500


def _extract_text_from_pdf_bytes(raw_bytes):
    """
    Extract all text from PDF bytes using whichever library is available.
    Returns a single string with page text joined by newlines.
    """
    if _PDF_BACKEND == "pdfplumber":
        pages = []
        with _pdfplumber_mod.open(BytesIO(raw_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    pages.append(page_text)
        return "\n\n".join(pages)

    elif _PDF_BACKEND == "pypdf":
        pages = []
        reader = _pypdf_mod.PdfReader(BytesIO(raw_bytes))
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                pages.append(page_text)
        return "\n\n".join(pages)

    elif _PDF_BACKEND == "PyPDF2":
        pages = []
        reader = _PyPDF2_mod.PdfReader(BytesIO(raw_bytes))
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                pages.append(page_text)
        return "\n\n".join(pages)

    return ""

@app.route("/api/summarise", methods=["POST"])
def summarise():
    data = request.get_json()
    policy_text = data.get("policy_text", "").strip()
    if not policy_text:
        return jsonify({"error": "No policy text provided"}), 400

    system = (
        "You are a senior privacy law and data governance analyst. You produce clear, structured, "
        "professional summaries of privacy policies and data protection frameworks that are accessible "
        "to both legal specialists and general readers. Focus on practical implications for users, "
        "the organisation's data practices, and the overall regulatory posture of the policy."
    )

    prompt = f"""Analyse the following privacy policy document and produce a comprehensive, structured summary.

Your summary MUST clearly cover all three of these required areas:

1. **Main Goals** — What is this privacy policy trying to achieve? What data protection commitments and user rights are central?
2. **Key Measures & Strategies** — What specific mechanisms, controls, and practices does the policy use to handle personal data?
3. **Overall Policy Direction** — What does this policy signal about the organisation's broader values, data philosophy, and regulatory posture?

Structure your summary exactly as follows:

## 📋 Policy Overview
[2–3 sentences: what this policy is, who it applies to, and its overall purpose]

## 🎯 Main Goals
[5–7 bullet points covering the primary data protection objectives and user rights commitments]

## 🔑 Key Measures & Strategies

### 📥 Data Collection & Sources
[3–5 bullet points on what data is collected and from where]

### ⚙️ Data Use & Processing
[3–5 bullet points on how data is used, shared, and for what purposes]

### 🛡️ User Rights & Controls
[3–5 bullet points on the rights users have and how they can exercise them]

### 🍪 Tracking & Advertising
[3–5 bullet points on cookies, device identifiers, and advertising practices]

## 📈 Notable Policies & Practices
[3–5 notable or distinctive aspects of this privacy policy worth highlighting]

## 🧭 Overall Policy Direction
[2–3 sentences describing the broader strategic posture, values, and regulatory philosophy signalled by this policy]

---
POLICY TEXT:
{policy_text[:10000]}"""

    try:
        result = call_groq(system, prompt)
        return jsonify({"summary": result})
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500
    except ValueError as e:
        return jsonify({"error": str(e)}), 401

@app.route("/api/generate-scenario", methods=["POST"])
def generate_scenario():
    data = request.get_json()
    summary = data.get("summary", "").strip()
    scenario_name = data.get("scenario_name", "Custom Scenario")
    scenario_description = data.get("scenario_description", "").strip()
    custom_requirements = data.get("custom_requirements", "").strip()

    if not summary:
        return jsonify({"error": "No summary provided. Please generate a summary first."}), 400
    if not scenario_description:
        return jsonify({"error": "No scenario description provided"}), 400

    system = (
        "You are a senior privacy policy drafter and data governance consultant. You create adapted "
        "privacy policy frameworks that are professional, context-specific, and actionable. Each "
        "adapted policy must clearly reflect its target audience's needs and constraints, differ "
        "meaningfully from other adaptations in emphasis and approach, cite relevant regulations where "
        "applicable, and maintain a formal, policy-appropriate tone throughout."
    )

    prompt = f"""Using the privacy policy summary below as your foundation, generate a comprehensive ADAPTED PRIVACY POLICY DRAFT for the following scenario.

SCENARIO: {scenario_name}
CONTEXT & PRIORITIES: {scenario_description}
{f'ADDITIONAL REQUIREMENTS: {custom_requirements}' if custom_requirements else ''}

ORIGINAL PRIVACY POLICY SUMMARY:
{summary[:5000]}

INSTRUCTIONS:
- The adapted draft must clearly reflect the scenario's priorities, audience, and regulatory constraints.
- It must differ meaningfully from the original policy in focus, tone, and recommended provisions.
- Cite relevant laws or regulations where applicable to the scenario (e.g. COPPA, GDPR, HIPAA).
- Maintain formal, policy-style language throughout.
- Structure as follows:

---
# ADAPTED PRIVACY POLICY FRAMEWORK
## Scenario: {scenario_name}
### Derived from: Netflix Privacy Statement (April 17, 2025)
---

## 1. PURPOSE & SCOPE
[Adapted purpose and scope for this specific audience/scenario, including which data subjects and processing activities are covered]

## 2. CORE DATA PROTECTION GOALS FOR THIS CONTEXT
[4–6 goals specifically relevant to this scenario — not a copy of the original]

## 3. DATA COLLECTION: ADAPTED PRINCIPLES
[What data may and may not be collected in this context; any minimisation requirements unique to this scenario]

## 4. DATA USE & SHARING: ADAPTED PROVISIONS
[How data use and third-party sharing is restricted, permitted, or modified for this scenario]

## 5. USER / DATA SUBJECT RIGHTS
[How user rights apply or are enhanced/modified for this specific audience]

## 6. TRACKING, ADVERTISING & COOKIES: ADAPTED RULES
[How tracking technologies and advertising practices are governed in this context]

## 7. KEY OBLIGATIONS & RESPONSIBILITIES
[Who is responsible for what in this adapted context — controller, processor, user]

## 8. IMPLEMENTATION PATHWAY
[Practical steps for organisations deploying this adapted policy, with realistic timelines]

## 9. SCENARIO-SPECIFIC RECOMMENDATIONS
[3–5 specific, actionable recommendations unique to this scenario that would not appear in another adaptation]

---
*This adapted framework reflects the priorities and constraints of the "{scenario_name}" scenario and may differ substantially from the original privacy statement in emphasis, scope, and recommended provisions.*"""

    try:
        result = call_groq(system, prompt)
        return jsonify({"draft": result, "scenario": scenario_name})
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500
    except ValueError as e:
        return jsonify({"error": str(e)}), 401

# ─── Startup ───────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 62)
    print("  PolicyAI — Privacy Policy Summariser & Scenario Generator")
    print("  Pre-loaded: Netflix Privacy Statement (April 17, 2025)")
    print(f"  Powered by Groq AI — Model: {GROQ_MODEL}")
    print("  Free tier: 30 req/min · 14,400 req/day · No card needed")
    print("=" * 62)

    key = GROQ_API_KEY.strip()
    if not key or key == "PASTE_YOUR_GROQ_KEY_HERE":
        print("\n⚠️  WARNING: No Groq API key found!")
        print("   1. Go to https://console.groq.com  (free signup)")
        print("   2. Click API Keys → Create API Key")
        print("   3. Paste the key (gsk_...) into policy_app.py")
        print("      where it says PASTE_YOUR_GROQ_KEY_HERE\n")
    else:
        masked = key[:8] + "..." + key[-4:]
        print(f"\n✓ Groq API Key loaded ({masked})")

    if _PDF_BACKEND:
        print(f"✓ PDF backend: {_PDF_BACKEND} (PDF upload is enabled)")
    else:
        print("⚠️  No PDF library — PDF upload will prompt to install one.")
        print("   Run:  pip install pdfplumber")

    print("\n  Open in browser: http://localhost:5000")
    print("=" * 62 + "\n")
    app.run(debug=True, host="0.0.0.0", port=5000)