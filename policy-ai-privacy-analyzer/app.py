import os
import requests
from flask import Flask, request, jsonify, render_template
from io import BytesIO

# ── Optional PDF library detection ────────────────────────────────────────────

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

# ── API Key Setup ──────────────────────────────────────────────────────────────
# Set the GROQ_API_KEY environment variable, or paste your key below.
# Get a free key at https://console.groq.com
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "PASTE_YOUR_GROQ_KEY_HERE")

# Model to use
GROQ_MODEL = "llama-3.3-70b-versatile"


def validate_api_key():
    """Return the Groq API key, or raise a clear error if it is not set."""
    key = GROQ_API_KEY.strip()
    if not key or key == "PASTE_YOUR_GROQ_KEY_HERE":
        raise ValueError(
            "No Groq API key found.\n\n"
            "To fix this:\n"
            "  1. Go to https://console.groq.com and sign up (free)\n"
            "  2. Click API Keys → Create API Key\n"
            "  3. Copy the key (starts with gsk_...)\n"
            "  4. Set it as an environment variable: export GROQ_API_KEY=gsk_...\n"
            "     OR open app.py and paste it where it says PASTE_YOUR_GROQ_KEY_HERE\n"
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


# ─── Groq API helper ───────────────────────────────────────────────────────────
def call_groq(system_prompt, user_prompt):
    """
    Call the Groq API via direct HTTP — no SDK required.
    Free tier: 30 req/min · 14,400 req/day · No credit card needed.
    Model: llama-3.3-70b-versatile
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

    if resp.status_code == 401:
        raise RuntimeError(
            "Invalid Groq API key (401 Unauthorised).\n"
            "Please check your key at https://console.groq.com and update it in app.py."
        )

    if resp.status_code == 403:
        raise RuntimeError(
            "Access denied (403 Forbidden).\n"
            "Your Groq API key may have been revoked. "
            "Create a new one at https://console.groq.com → API Keys."
        )

    if resp.status_code == 429:
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
        try:
            msg = resp.json().get("error", {}).get("message", resp.text[:300])
        except Exception:
            msg = resp.text[:300]
        raise RuntimeError(
            f"Groq API returned HTTP {resp.status_code}: {msg}"
        )

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


# ─── PDF helper ────────────────────────────────────────────────────────────────
def _extract_text_from_pdf_bytes(raw_bytes):
    """Extract all text from PDF bytes using whichever library is available."""
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


# ─── Routes ────────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template(
        "index.html",
        scenarios=PREDEFINED_SCENARIOS,
        default_policy=DEFAULT_POLICY_TEXT
    )


@app.route("/api/extract-pdf", methods=["POST"])
def extract_pdf():
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
[Adapted purpose and scope for this specific audience/scenario]

## 2. CORE DATA PROTECTION GOALS FOR THIS CONTEXT
[4–6 goals specifically relevant to this scenario]

## 3. DATA COLLECTION: ADAPTED PRINCIPLES
[What data may and may not be collected in this context]

## 4. DATA USE & SHARING: ADAPTED PROVISIONS
[How data use and third-party sharing is restricted or modified]

## 5. USER / DATA SUBJECT RIGHTS
[How user rights apply or are enhanced/modified for this specific audience]

## 6. TRACKING, ADVERTISING & COOKIES: ADAPTED RULES
[How tracking technologies and advertising practices are governed]

## 7. KEY OBLIGATIONS & RESPONSIBILITIES
[Who is responsible for what in this adapted context]

## 8. IMPLEMENTATION PATHWAY
[Practical steps for organisations deploying this adapted policy]

## 9. SCENARIO-SPECIFIC RECOMMENDATIONS
[3–5 specific, actionable recommendations unique to this scenario]

---
*This adapted framework reflects the priorities and constraints of the "{scenario_name}" scenario.*"""

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
        print("   Set it via environment variable:  export GROQ_API_KEY=gsk_...")
        print("   Or paste it directly in app.py where it says PASTE_YOUR_GROQ_KEY_HERE\n")
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
