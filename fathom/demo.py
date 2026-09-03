INTEGRATION_CUSTOMERS = [
    ("Northstar Health", "enterprise"),
    ("Helios Bank", "enterprise"),
    ("Atlas Freight", "enterprise"),
    ("Meridian Insurance", "enterprise"),
    ("Cobalt Analytics", "enterprise"),
    ("Pinnacle Retail", "enterprise"),
    ("Orion Cloud", "enterprise"),
    ("Brightpath", "mid-market"),
    ("Kite Labs", "startup"),
    ("Harbor CMS", "mid-market"),
    ("Folio Design", "startup"),
]

SEARCH_CUSTOMERS = [
    ("Northstar Health", "enterprise"),
    ("Lumen Media", "mid-market"),
    ("Parcelly", "startup"),
    ("Helios Bank", "enterprise"),
    ("Nimbus HR", "mid-market"),
    ("Quorum Legal", "enterprise"),
]

BILLING_CUSTOMERS = [
    ("Brightpath", "mid-market"),
    ("Kite Labs", "startup"),
    ("Vesper Shops", "startup"),
    ("Cobalt Analytics", "enterprise"),
    ("Harbor CMS", "mid-market"),
]

NOTIF_CUSTOMERS = [
    ("Meridian Insurance", "enterprise"),
    ("Atlas Freight", "enterprise"),
    ("Folio Design", "startup"),
    ("Lumen Media", "mid-market"),
    ("Nimbus HR", "mid-market"),
]

IDENTITY_CUSTOMERS = [
    ("Helios Bank", "enterprise"),
    ("Pinnacle Retail", "enterprise"),
    ("Quorum Legal", "enterprise"),
    ("Northstar Health", "enterprise"),
]

RELIABILITY_CUSTOMERS = [
    ("Orion Cloud", "enterprise"),
    ("Cobalt Analytics", "enterprise"),
    ("Parcelly", "startup"),
]

SOURCES = ["interview", "support", "sales", "feature_request", "review", "slack"]


def item(text, customer, source, date):
    return {
        "text": text,
        "customer": customer[0],
        "segment": customer[1],
        "source": source,
        "date": date,
    }


INTEGRATION_QUOTES = [
    "Setting this up took our developer almost two weeks.",
    "Can you add a Terraform integration?",
    "We couldn't figure out which permissions were required.",
    "Your docs say X but the API returned Y.",
    "Onboarding stalled because the configuration examples don't match the current API.",
    "We need a Terraform provider so our platform team can provision this without clicking around.",
    "The permissions list in the docs is incomplete — we kept getting 403s during setup.",
    "Initial integration was painful. Our contractor burned 10 days on IAM scopes.",
    "Please add support for Pulumi or Terraform. Click-ops is a non-starter for us.",
    "Couldn't tell which roles the service account actually needed to finish configuration.",
    "Docs walk through setup with fields that no longer exist on the API.",
    "Getting started took far too long for an enterprise implementation.",
    "We want a guided configuration wizard. Right now setup is tribal knowledge.",
    "Your documentation says the webhook secret is in Settings, but it isn't.",
    "Add an official Terraform module. That's how we ship every other vendor.",
    "Permissions were the blocker. We guessed scopes for days.",
    "The SDK install was fine; configuration and IAM were the time sink.",
    "Two weeks to a first successful call is not acceptable for our security review.",
    "Can you publish a least-privilege permission catalog for initial integration?",
    "We couldn't complete setup until a support engineer pasted an undocumented policy.",
    "Feature request: configuration validation API so we know the integration is correct before go-live.",
    "Docs and API disagreement on required headers during onboarding.",
    "Our developer spent a sprint just wiring permissions and env vars.",
    "Terraform support would help, but honestly we just need setup to be less fragile.",
    "Unclear which permissions were required for the production vs sandbox configuration.",
    "The getting-started guide is outdated and sent us down the wrong integration path.",
    "Blocked on implementation until we reverse-engineered the permission set.",
    "Would love an AI integration assistant that checks our config against the live API.",
    "Enterprise customers cannot ship a vendor that takes two weeks to configure.",
    "Support ticket: API returned Y while docs still say X for the same endpoint.",
    "Need infrastructure-as-code. Manual dashboard configuration will fail audit.",
    "Hard to know if our configuration is valid until traffic fails in production.",
    "The onboarding checklist is missing the IAM piece entirely.",
    "Please add a preflight that tells us which permissions are missing.",
    "Implementation partner quoted extra hours solely for configuration complexity.",
    "We asked for Terraform, but the real issue is we can't reproduce a working setup.",
    "Slack thread: still stuck on which scopes the integration user needs.",
    "App review: setup was confusing, permissions undocumented, gave up after a week.",
    "Sales call: deal risk until we prove time-to-integrate is under a few days.",
    "Could not match the documented configuration example to the current console UI.",
    "Our security team rejected the integration until we listed every permission in writing.",
    "The sandbox configuration does not carry over, so we re-did setup twice.",
    "Add a Terraform example in the docs even if a full provider takes longer.",
    "We reverse-engineered required headers because the documentation was wrong.",
    "CS note: third enterprise this month stuck on IAM during implementation.",
    "If setup took two days instead of two weeks we would have gone live last quarter.",
]

SEARCH_QUOTES = [
    "Search never finds the record I know exists unless I use the exact ID.",
    "Filters reset every time we navigate away. We can't find anything in large accounts.",
    "Can you add saved search? We rebuild the same query all day.",
    "Results ranking feels random. Recent junk buries the customer we need.",
    "Support: user unable to find invoices from last quarter using search.",
    "The search bar is decorative. We export to CSV and grep.",
    "Please add better filters for owner and status together.",
    "Couldn't find the account after a rename. Search still uses the old token.",
    "Sales noted the champion complained they can't find open deals in the app.",
    "Query latency on search makes the page feel broken.",
    "Feature request: natural language search across tickets.",
    "Review: 2 stars because I cannot find my own projects.",
    "Slack: CS repeating the same 'use this undocumented filter' workaround.",
    "We need search that handles typos. Agents miss customers daily.",
    "Hard to find related records. No way to jump from company to its tickets.",
    "Interview: PM at Lumen said findability is their number one daily friction.",
    "Add Elasticsearch or whatever — just make find actually work.",
    "Empty search results for names with accents. That's a problem, not a feature idea.",
    "Agents type a company name and get zero hits. That's a daily tax.",
    "Can you search across comments, not just titles?",
    "Filter chips don't combine. Owner plus date returns everything.",
    "Interview: findability is worse than the spreadsheet they replaced.",
    "Global search should include archived records with a toggle.",
    "We lost a renewal because nobody could find the original quote in-product.",
]

BILLING_QUOTES = [
    "The invoice doesn't explain the overage. Finance blocked payment.",
    "Unexpected bill this month. Usage page and invoice don't match.",
    "Can you add a usage forecast? We got surprised by seat charges.",
    "Pricing page says included API calls but billing counted internal retries.",
    "We can't tell which team burned the quota.",
    "Feature request: breakdown of seats vs usage on the invoice.",
    "Confusing charges after we deactivated users who still appeared as billable seats.",
    "Interview: CFO will churn if invoices stay this opaque.",
    "Slack: CS spent an hour reconciling usage for Harbor.",
    "Please add alerts before we cross a spend threshold.",
    "Review: billing is a black box. Two stars.",
    "Support: credit requested because documentation of usage units is wrong.",
    "Sales: procurement wants predictable billing before renewal.",
    "Overage math is unexplained. We cannot accrue properly.",
    "Deactivated seats still billed for a full cycle. That's a trust problem.",
    "Need a chargeback report by department.",
    "The usage API and the invoice use different unit names.",
]

NOTIF_QUOTES = [
    "Too many emails. We missed the one outage notice in the flood.",
    "Notifications are noisy. Please add a daily digest.",
    "Every comment emails the whole account. People mute us and then miss incidents.",
    "Can you let us mute a thread without disabling all alerts?",
    "Slack: CS says customers turn off notifications and then blame us for silence.",
    "Feature request: severity-based routing to PagerDuty vs email.",
    "Interview: ops lead at Atlas called the email volume unusable.",
    "Review: great product, notification spam is exhausting.",
    "We need alert grouping. 40 emails for one failing job.",
    "Couldn't tell which notifications are actually actionable.",
    "Sales call: security team wants fewer emails, not more dashboards.",
    "Digest by default would fix this. Per-event mail does not scale.",
    "People auto-filter our domain. Critical alerts die in spam.",
    "Can you add quiet hours for non-critical notifications?",
    "Too many emails after we invited a 30-person team.",
]

IDENTITY_QUOTES = [
    "SSO works; SCIM provisioning still isn't there. IT will not manually add 400 people.",
    "Can you add SCIM? Okta is a hard requirement for us.",
    "Group-to-role mapping is missing so SSO lands everyone as a viewer.",
    "Azure AD / Entra provisioning failed our security questionnaire.",
    "Feature request: just-in-time SSO with group claims.",
    "Interview: Helios Bank cannot expand seats without directory sync.",
    "We deprovision in Okta but users remain active here. That's a security problem.",
    "Please add SAML group mapping in the admin UI, not a support ticket.",
    "Sales: identity completeness is the remaining enterprise objection.",
    "Support: user still had access two weeks after being removed from IdP.",
]

RELIABILITY_QUOTES = [
    "API timeouts during our peak hour. Retries aren't idempotent so we double-wrote.",
    "Rate limits are too low for enterprise batch jobs.",
    "500s from the search endpoint with no status page note.",
    "Latency spiked and we had no way to know if it was us or you.",
    "Feature request: idempotency keys on all write endpoints.",
    "Support: intermittent 500s, customer blocked on a go-live.",
]


def demo_corpus():
    rows = []
    for i, text in enumerate(INTEGRATION_QUOTES):
        rows.append(
            item(text, INTEGRATION_CUSTOMERS[i % len(INTEGRATION_CUSTOMERS)], SOURCES[i % len(SOURCES)], f"2026-0{(i % 6) + 1}-12")
        )
    for i, text in enumerate(SEARCH_QUOTES):
        rows.append(
            item(text, SEARCH_CUSTOMERS[i % len(SEARCH_CUSTOMERS)], SOURCES[(i + 1) % len(SOURCES)], f"2026-03-{10 + (i % 18)}")
        )
    for i, text in enumerate(BILLING_QUOTES):
        rows.append(
            item(text, BILLING_CUSTOMERS[i % len(BILLING_CUSTOMERS)], SOURCES[(i + 2) % len(SOURCES)], f"2026-04-{8 + i}")
        )
    for i, text in enumerate(NOTIF_QUOTES):
        rows.append(
            item(text, NOTIF_CUSTOMERS[i % len(NOTIF_CUSTOMERS)], SOURCES[(i + 3) % len(SOURCES)], f"2026-05-{4 + i}")
        )
    for i, text in enumerate(IDENTITY_QUOTES):
        rows.append(
            item(text, IDENTITY_CUSTOMERS[i % len(IDENTITY_CUSTOMERS)], SOURCES[i % len(SOURCES)], f"2026-02-{11 + i}")
        )
    for i, text in enumerate(RELIABILITY_QUOTES):
        rows.append(
            item(text, RELIABILITY_CUSTOMERS[i % len(RELIABILITY_CUSTOMERS)], SOURCES[(i + 4) % len(SOURCES)], f"2026-06-{2 + i}")
        )
    noise = [
        item("Love the new navigation. Finally feels calm.", ("Kite Labs", "startup"), "review", "2026-06-01"),
        item("Can you add dark mode to the mobile app?", ("Vesper Shops", "startup"), "feature_request", "2026-06-02"),
        item("The CSV export truncates long notes.", ("Lumen Media", "mid-market"), "support", "2026-06-03"),
        item("We need audit log download for compliance.", ("Quorum Legal", "enterprise"), "sales", "2026-06-04"),
        item("Please add a warehouse sync to Snowflake.", ("Cobalt Analytics", "enterprise"), "feature_request", "2026-06-05"),
        item("Mobile review: export is missing on iOS.", ("Brightpath", "mid-market"), "review", "2026-06-06"),
        item("Interview aside: their intern liked the empty states.", ("Folio Design", "startup"), "interview", "2026-06-07"),
        item("Slack: can someone send the SOC2 PDF again?", ("Harbor CMS", "mid-market"), "slack", "2026-06-08"),
        item("Dark mode please, my eyes at 1am.", ("Parcelly", "startup"), "review", "2026-06-09"),
        item("Compliance asked for a durable export of audit events.", ("Helios Bank", "enterprise"), "sales", "2026-06-10"),
        item("The in-app changelog is actually useful. Keep it.", ("Nimbus HR", "mid-market"), "slack", "2026-06-11"),
        item("Could we get a weekly CSV of all records?", ("Atlas Freight", "enterprise"), "feature_request", "2026-06-12"),
    ]
    return rows + noise


REQUEST_SAMPLE = [
    "Can you add a Terraform integration?",
    "We need a guided setup wizard.",
    "Please publish a least-privilege permission catalog.",
    "Your docs say X but the API returned Y — fix the docs.",
    "Add a configuration validation API before go-live.",
    "Pulumi support so we don’t click around in the dashboard.",
    "Would love an AI integration assistant that checks our config.",
    "Can you add saved search?",
    "Natural language search across tickets.",
    "Please add better filters for owner and status together.",
    "Can you add dark mode to the mobile app?",
]


def request_sample():
    rows = []
    customers = [
        ("Northstar Health", "enterprise"),
        ("Helios Bank", "enterprise"),
        ("Brightpath", "mid-market"),
        ("Kite Labs", "startup"),
    ]
    for i, text in enumerate(REQUEST_SAMPLE):
        rows.append(item(text, customers[i % len(customers)], "feature_request", "2026-09-01"))
    return rows


def priority_sample():
    return {
        "capacity": 50,
        "items": [
            {
                "id": "BL-01",
                "title": "Configuration validation API",
                "reach": 40,
                "impact": 3,
                "confidence": 80,
                "effort": 15,
                "loadPct": 40,
                "revenue": 120000,
                "roi": 4,
                "deal": "signup",
                "dealValue": 90000,
                "churn": "high",
                "churnArr": 180000,
                "debtAdded": "low",
                "debtReduced": "medium",
                "blocksOthers": True,
                "compliance": False,
                "timeSensitive": True,
                "blockedBy": False,
                "workType": "feature",
            },
            {
                "id": "BL-02",
                "title": "Official Terraform provider",
                "reach": 12,
                "impact": 2,
                "confidence": 60,
                "effort": 40,
                "loadPct": 55,
                "revenue": 80000,
                "roi": 1.5,
                "deal": "expansion",
                "dealValue": 40000,
                "churn": "low",
                "churnArr": 20000,
                "debtAdded": "medium",
                "debtReduced": "none",
                "blocksOthers": False,
                "compliance": False,
                "timeSensitive": False,
                "blockedBy": False,
                "workType": "feature",
            },
            {
                "id": "BL-03",
                "title": "SCIM directory sync",
                "reach": 8,
                "impact": 3,
                "confidence": 75,
                "effort": 25,
                "loadPct": 35,
                "revenue": 200000,
                "roi": 5,
                "deal": "signup",
                "dealValue": 180000,
                "churn": "medium",
                "churnArr": 60000,
                "debtAdded": "low",
                "debtReduced": "low",
                "blocksOthers": False,
                "compliance": True,
                "timeSensitive": True,
                "blockedBy": False,
                "workType": "feature",
            },
            {
                "id": "BL-04",
                "title": "Saved search and combined filters",
                "reach": 200,
                "impact": 1,
                "confidence": 85,
                "effort": 3,
                "loadPct": 10,
                "revenue": 15000,
                "roi": 2,
                "deal": "none",
                "dealValue": 0,
                "churn": "low",
                "churnArr": 10000,
                "debtAdded": "low",
                "debtReduced": "none",
                "blocksOthers": False,
                "compliance": False,
                "timeSensitive": False,
                "blockedBy": False,
                "workType": "feature",
            },
            {
                "id": "BL-05",
                "title": "Usage forecast and invoice breakdown",
                "reach": 60,
                "impact": 2,
                "confidence": 70,
                "effort": 20,
                "loadPct": 30,
                "revenue": 70000,
                "roi": 3,
                "deal": "expansion",
                "dealValue": 25000,
                "churn": "high",
                "churnArr": 90000,
                "debtAdded": "none",
                "debtReduced": "medium",
                "blocksOthers": False,
                "compliance": False,
                "timeSensitive": False,
                "blockedBy": False,
                "workType": "feature",
            },
            {
                "id": "BL-06",
                "title": "Dark mode on mobile",
                "reach": 300,
                "impact": 0.5,
                "confidence": 90,
                "effort": 10,
                "loadPct": 10,
                "revenue": 0,
                "roi": 0.2,
                "deal": "none",
                "dealValue": 0,
                "churn": "none",
                "churnArr": 0,
                "debtAdded": "low",
                "debtReduced": "none",
                "blocksOthers": False,
                "compliance": False,
                "timeSensitive": False,
                "blockedBy": False,
                "workType": "feature",
            },
            {
                "id": "BL-07",
                "title": "Patch critical auth vulnerability",
                "reach": 500,
                "impact": 3,
                "confidence": 90,
                "effort": 4,
                "loadPct": 20,
                "revenue": 0,
                "roi": 0,
                "deal": "none",
                "dealValue": 0,
                "churn": "high",
                "churnArr": 250000,
                "debtAdded": "none",
                "debtReduced": "low",
                "blocksOthers": False,
                "compliance": True,
                "timeSensitive": True,
                "blockedBy": False,
                "workType": "security",
            },
            {
                "id": "BL-08",
                "title": "Keep production on-call and incident response staffed",
                "reach": 500,
                "impact": 2,
                "confidence": 95,
                "effort": 8,
                "loadPct": 25,
                "revenue": 0,
                "roi": 0,
                "deal": "none",
                "dealValue": 0,
                "churn": "medium",
                "churnArr": 40000,
                "debtAdded": "none",
                "debtReduced": "none",
                "blocksOthers": True,
                "compliance": False,
                "timeSensitive": False,
                "blockedBy": False,
                "workType": "ktlo",
            },
        ],
    }

