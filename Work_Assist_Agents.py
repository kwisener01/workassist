import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io
import json
from datetime import datetime, timedelta
import re
from typing import Dict, List, Any
import base64
import requests

# Configure page
st.set_page_config(
    page_title="🤖 Multi-Agent Workplace Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .agent-card {
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    
    .task-status {
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .status-pending { background-color: #fff3cd; color: #856404; }
    .status-processing { background-color: #d1ecf1; color: #0c5460; }
    .status-completed { background-color: #d4edda; color: #155724; }
</style>
""", unsafe_allow_html=True)

BUDGET_LEVELS = ["No Budget", "Under $250", "Under $1000", "Flexible"]
BUDGET_SCORES = {level: index for index, level in enumerate(BUDGET_LEVELS)}

TASK_STATUS_OPTIONS = ["To Do", "In Progress", "Blocked", "Completed"]
TASK_CATEGORIES = [
    "Opportunity Launch",
    "Operations",
    "Research",
    "Marketing",
    "Learning",
    "Personal",
    "Other"
]

OPPORTUNITY_LIBRARY = [
    {
        "name": "Fractional Launch Operator for Solo Course Creators",
        "type": "Done-for-you Service",
        "description": (
            "Partner with overwhelmed course creators to orchestrate their launches, automate repeatable admin, "
            "and build lightweight systems that keep sales rolling without hiring a full-time ops team."
        ),
        "demand_drivers": [
            "Thousands of solo creators are scaling paid courses and cohorts in 2024",
            "Most launches rely on disorganized spreadsheets and manual reminders",
            "Creators want AI help but lack time to stitch tools together"
        ],
        "supply_gap": (
            "Very few operators package a rev-share friendly, AI-enabled launch service targeting solo creators"
        ),
        "why_now": (
            "The course boom continues, yet operators who blend AI + ops are rare, making it easy to stand out"
        ),
        "skills": ["automation", "ops", "ai", "systems", "project management", "notion"],
        "interests": ["education", "creator economy", "coaching", "product launches"],
        "budget_level": "No Budget",
        "delivery_mode": "Online",
        "audience": ["B2B", "Creators"],
        "time_commitment": 12,
        "ideal_timeline_weeks": 4,
        "best_for": ["Land 3 paying clients", "Recurring retainers", "Validate quickly"],
        "starter_stack": [
            "Notion HQ dashboard",
            "Make.com free tier automations",
            "Airtable or Google Sheets tracking",
            "Loom walkthrough library"
        ],
        "low_cost_moves": [
            "Offer rev-share pilots so creators only pay from launch revenue",
            "Use free communities (Tribe of Notion, ConvertKit, Circle) to source first 10 prospects",
            "Repurpose creators' own testimonials into your pitch deck"
        ],
        "validation_steps": [
            "Interview 5 solo course creators about their launch bottlenecks",
            "Shadow an upcoming launch to document time sinks",
            "Pre-sell a 30-day launch sprint with a money-back guarantee"
        ],
        "launch_steps": [
            "Define a three-tier offer (launch sprint, ongoing ops, ops-in-a-box)",
            "Build a Notion-based control center template and record a Loom walkthrough",
            "Publish a case-style teardown thread weekly showcasing fixable launch gaps",
            "Run DM outreach to top 20 Gumroad/Podia creators offering a free readiness audit"
        ],
        "task_templates": [
            {
                "title": "Interview 5 solo course creators to map launch friction",
                "priority": "High",
                "notes": "Capture quotes, tools, and metrics they track to inform your offer"
            },
            {
                "title": "Design rev-share friendly pricing with three package tiers",
                "priority": "High",
                "notes": "Outline scope, deliverables, and risk-reversal for each tier"
            },
            {
                "title": "Build launch command center template in Notion + Make",
                "priority": "Medium",
                "notes": "Automate status updates and daily checklists using free integrations"
            },
            {
                "title": "Publish creator launch gap teardown thread on LinkedIn/Twitter",
                "priority": "Medium",
                "notes": "Highlight 3 quick wins you can implement in under 48 hours"
            }
        ],
        "monetization": [
            "Done-for-you launch sprint retainers",
            "Recurring maintenance retainers",
            "Template + training upsells",
            "Revenue share on new product launches"
        ],
        "market_signals": [
            "ConvertKit creator reports showing rising course revenue",
            "Creators tweeting about burnout from launch admin",
            "Communities begging for vetted launch ops support"
        ],
        "growth_channels": [
            "Creator community AMAs",
            "Personalized Loom teardown outreach",
            "Guest workshops in cohort-based courses"
        ],
        "starter_offer": "30-day launch sprint with a revenue-linked success fee",
        "first_clients": [
            "Gumroad best-selling mini-course creators",
            "Podia/Circle community owners running live cohorts",
            "Solo coaches turning webinars into evergreen funnels"
        ],
        "toolkit": ["Notion", "Make.com", "Zapier free tier", "Typeform", "Slack"],
        "key_metrics": [
            "Launch readiness score",
            "Cart open to close conversion rate",
            "Time saved on admin per launch"
        ],
        "content_prompts": [
            "Before/after of a messy launch timeline",
            "Thread: 5 automations that rescued a course launch",
            "Mini teardown video of a landing page follow-up flow"
        ],
        "pricing_ideas": [
            "$0 upfront + 12% of launch revenue",
            "$1,200 sprint + $500/month maintenance retainer",
            "$350 DIY ops-in-a-box kit upsell"
        ],
        "stretch_learning": [
            "Learn Kajabi or Skool automations",
            "Study conversion copy for launch emails",
            "Practice fractional COO discovery calls"
        ],
        "partnership_ideas": [
            "Affiliate with launch copywriters",
            "Bundle with webinar tech specialists",
            "Cross-promote with community strategists"
        ],
        "automation_ideas": [
            "Slack alerts when checkout spikes",
            "AI summary of daily metrics",
            "Auto-generate creator launch recap reports"
        ],
        "community_hooks": [
            "Weekly launch ops office hours",
            "Creators-only dashboard template drop",
            "Launch stress detox challenge"
        ],
        "stretch_moves": [
            "Shadow a seven-figure launch to reverse-engineer systems",
            "Join a live cohort to understand student journey",
            "Build a public portfolio showing live dashboards"
        ],
        "de_risk_moves": [
            "Sign mutual NDAs to build trust",
            "Offer a pilot with milestone-based billing",
            "Share daily recap emails to maintain visibility"
        ],
        "low_cost_tools": ["Google Sheets", "Notion AI", "Tally forms", "Calendly free"],
        "mini_offer": "$97 launch readiness audit delivered in 48 hours",
        "value_prop": "Operate launches like a full team using scrappy AI-powered systems",
        "fast_follow_offers": [
            "Monthly cohort retention analytics",
            "Creator CRM setup in Airtable",
            "Done-with-you automation training"
        ],
        "upsell_paths": [
            "Evergreen funnel build",
            "Launch analytics dashboard retainers",
            "Team onboarding systems"
        ],
        "retention_moves": [
            "Weekly scoreboard email",
            "Quarterly pipeline planning call",
            "SOP refreshes every new launch"
        ],
        "scale_paths": [
            "Productize dashboards into templates",
            "Build a vetted contractor bench",
            "Create a group program teaching launch ops"
        ],
        "foundation_assets": [
            "Launch dashboard template",
            "Creator intake questionnaire",
            "ROI calculator spreadsheet"
        ],
        "resourcefulness_moves": [
            "Barter launch support for testimonials",
            "Borrow audience by co-hosting with copywriters",
            "Document every workflow to turn into digital products"
        ],
        "buddy_system": "Pair with a copywriter to offer an all-in-one launch duo",
        "score_commentary": "Excellent fit if you enjoy systems thinking and client collaboration"
    },
    {
        "name": "Authority Shorts Studio for B2B Consultants",
        "type": "Productized Content Service",
        "description": (
            "Repurpose consultants' long-form content into high-signal vertical video that feeds LinkedIn, YouTube, "
            "and newsletters while highlighting lead magnets and offers."
        ),
        "demand_drivers": [
            "Consultants know they need daily video but hate editing",
            "Short-form platforms rewarding expertise-rich clips",
            "AI editing tools cut production time dramatically"
        ],
        "supply_gap": (
            "Lots of generalist editors, very few who understand B2B positioning and CTAs"
        ),
        "why_now": (
            "B2B buyers scroll reels for insight, yet consultants lack a consistent presence"
        ),
        "skills": ["video editing", "copywriting", "storytelling", "ai", "marketing", "repurposing"],
        "interests": ["consulting", "b2b", "content", "storytelling"],
        "budget_level": "Under $250",
        "delivery_mode": "Online",
        "audience": ["B2B"],
        "time_commitment": 8,
        "ideal_timeline_weeks": 3,
        "best_for": ["Build recurring retainers", "Land 3 paying clients", "Validate quickly"],
        "starter_stack": [
            "Descript or CapCut",
            "Canva templates",
            "ChatGPT prompt bank",
            "Airtable content tracker"
        ],
        "low_cost_moves": [
            "Use free CapCut templates to build authority-style motion graphics",
            "Exchange first month of editing for recorded testimonial",
            "Co-work inside consultant communities to stay top-of-mind"
        ],
        "validation_steps": [
            "Clip 3 sample videos from a consultant's webinar and ask for blunt feedback",
            "Run a 5-day content sprint for one beta client",
            "Track inbound leads generated from your clips"
        ],
        "launch_steps": [
            "Collect 10 hours of raw consultant content to build sample reels",
            "Design a 3-layer CTA framework (awareness, authority, offer)",
            "Publish a weekly LinkedIn teardown of consultant messaging",
            "Pitch done-with-you batching sessions to record content in one hour"
        ],
        "task_templates": [
            {
                "title": "Create 3 authority short-form video samples for one consultant niche",
                "priority": "High",
                "notes": "Use existing podcast or webinar recordings to demonstrate positioning"
            },
            {
                "title": "Draft retention-focused monthly retainer packages",
                "priority": "High",
                "notes": "Include deliverables, KPIs, and upsell to newsletter repurposing"
            },
            {
                "title": "Publish LinkedIn carousel explaining the Authority Shorts framework",
                "priority": "Medium",
                "notes": "Highlight before/after metrics and include call-to-action for audit"
            },
            {
                "title": "Set up Airtable pipeline to track leads, assets, and approvals",
                "priority": "Medium",
                "notes": "Automate reminders with Zapier free tier"
            }
        ],
        "monetization": [
            "$650/month editing retainers",
            "$1,200/month multi-channel amplification",
            "Upsell to ghostwritten LinkedIn posts",
            "Workshops teaching teams to ideate authority clips"
        ],
        "market_signals": [
            "LinkedIn algorithm favoring native vertical video",
            "Consultants requesting repurposing help in communities",
            "Demand for niche content editors on Contra/Fiverr Pro"
        ],
        "growth_channels": [
            "LinkedIn DMs with personalized clip makeovers",
            "Guest appearances on consultant podcasts",
            "Twitter threads showcasing transformation reels"
        ],
        "starter_offer": "$297 Authority Clip Sprint: 5 clips + CTA map",
        "first_clients": [
            "RevOps consultants",
            "Fractional CFOs",
            "AI strategy advisors"
        ],
        "toolkit": ["CapCut", "Descript", "Canva", "Notion", "ChatGPT"],
        "key_metrics": [
            "Follower growth on priority platform",
            "Average watch time",
            "Leads credited to call-to-actions"
        ],
        "content_prompts": [
            "Clip: 60-second myth busting video",
            "Carousel: The CTA ladder for consultants",
            "Thread: How one clip repurposed into 5 assets"
        ],
        "pricing_ideas": [
            "$850/month for 12 clips",
            "$1,500 VIP day to batch record and edit",
            "$350 add-on for lead magnet landing page refresh"
        ],
        "stretch_learning": [
            "Study motion graphics for expert positioning",
            "Learn YouTube Shorts SEO techniques",
            "Practice consultative sales calls"
        ],
        "partnership_ideas": [
            "Bundle with podcast producers",
            "Collaborate with LinkedIn ghostwriters",
            "Create referral loop with RevOps agencies"
        ],
        "automation_ideas": [
            "Auto-generate clip transcripts",
            "Use AI to suggest CTAs from transcripts",
            "Schedule cross-posting via free tools"
        ],
        "community_hooks": [
            "Weekly live editing session",
            "Swipe file of high-performing B2B hooks",
            "Consultant spotlight series"
        ],
        "stretch_moves": [
            "Shadow a B2B consultant sales call",
            "Learn advanced audio cleanup techniques",
            "Create a public experiment hitting 30 clips in 30 days"
        ],
        "de_risk_moves": [
            "Offer pay-after-approval guarantee",
            "Use clear script approval process",
            "Share KPI dashboard weekly"
        ],
        "low_cost_tools": ["CapCut mobile", "Canva free", "Otter AI", "Metricool free tier"],
        "mini_offer": "Free 2-clip makeover for consultants with a live webinar replay",
        "value_prop": "Consistent authority video without consultants touching an editing timeline",
        "fast_follow_offers": [
            "LinkedIn ghostwriting bundle",
            "Newsletter repurposing service",
            "YouTube channel analytics reports"
        ],
        "upsell_paths": [
            "Paid ad creative package",
            "Community management for content replies",
            "Done-for-you webinar chop-up"
        ],
        "retention_moves": [
            "Monthly performance review call",
            "Content idea vault shared with clients",
            "Quarterly brand refresh recommendations"
        ],
        "scale_paths": [
            "Template library for editing contractors",
            "Hybrid cohort teaching clients' teams",
            "Niche-specific clip subscription"
        ],
        "foundation_assets": [
            "Clip naming convention",
            "CTA script formulas",
            "Content batching schedule"
        ],
        "resourcefulness_moves": [
            "Barter editing for speaking spots",
            "Use free community job boards to find beta clients",
            "Document editing workflows for rapid onboarding"
        ],
        "buddy_system": "Partner with a strategist who maps consultants' offers",
        "score_commentary": "Strong if you enjoy creative production with measurable business outcomes"
    },
    {
        "name": "Compliance-Ready Notion Template Shop",
        "type": "Digital Product + Service Hybrid",
        "description": (
            "Build premium Notion workspaces and SOP packs tailored to regulated industries (healthcare, finance, "
            "climate) that need modern tooling but must stay audit-ready."
        ),
        "demand_drivers": [
            "Regulated startups adopting Notion but lacking compliance guidance",
            "Auditors requesting better documentation",
            "Teams desperate to leave spreadsheets for collaborative workflows"
        ],
        "supply_gap": (
            "Templates rarely address regulatory language, audit logs, or evidence capture"
        ),
        "why_now": (
            "Funding is flowing into climate/health tech; they need fast internal systems that won't trigger audits"
        ),
        "skills": ["notion", "documentation", "research", "ops", "process design"],
        "interests": ["climate", "healthcare", "fintech", "operations"],
        "budget_level": "Under $250",
        "delivery_mode": "Online",
        "audience": ["B2B", "Startups"],
        "time_commitment": 6,
        "ideal_timeline_weeks": 6,
        "best_for": ["Build digital products", "Earn leveraged income", "Validate quickly"],
        "starter_stack": [
            "Notion",
            "Figma",
            "Airtable",
            "Bubble or Softr for portal"
        ],
        "low_cost_moves": [
            "Offer pay-what-you-can audits to gather requirements",
            "Reverse-engineer public compliance checklists",
            "Use community co-building sessions to create assets live"
        ],
        "validation_steps": [
            "Interview compliance leads at 5 startups",
            "Ship an MVP template bundle to one beta client",
            "Track time saved and audit findings resolved"
        ],
        "launch_steps": [
            "Select one regulatory niche (HIPAA, SOC2-lite, climate reporting)",
            "Design a Notion HQ with audit trail database and role-based views",
            "Record walkthrough videos showing how audits become faster",
            "Publish comparison content vs legacy spreadsheet processes"
        ],
        "task_templates": [
            {
                "title": "Research compliance requirements for one niche startup segment",
                "priority": "High",
                "notes": "Collect must-have artifacts, evidence formats, and renewal cadences"
            },
            {
                "title": "Draft Notion workspace structure with audit-ready databases",
                "priority": "High",
                "notes": "Map user roles, permissions, and evidence attachments"
            },
            {
                "title": "Build marketing page highlighting compliance wins vs spreadsheets",
                "priority": "Medium",
                "notes": "Include ROI calculator and testimonial request form"
            },
            {
                "title": "Host a live co-build workshop to gather user feedback",
                "priority": "Medium",
                "notes": "Invite beta users and record session for repurposing"
            }
        ],
        "monetization": [
            "$297 template bundle",
            "$79/month update membership",
            "Done-for-you workspace setup",
            "Compliance operations advisory retainers"
        ],
        "market_signals": [
            "Job boards requesting Notion + compliance experience",
            "Founders tweeting about SOC2 readiness panic",
            "VC updates spotlighting operations maturity"
        ],
        "growth_channels": [
            "Product Hunt launches",
            "LinkedIn long-form breakdowns",
            "Guest sessions in compliance communities"
        ],
        "starter_offer": "$149 compliance workspace beta with lifetime updates",
        "first_clients": [
            "Seed-stage health tech",
            "Climate reporting platforms",
            "Fintech teams preparing for audits"
        ],
        "toolkit": ["Notion", "Figma", "Zapier", "Airtable", "Typedream"],
        "key_metrics": [
            "Hours saved per audit",
            "Documentation completion rate",
            "Renewal rate of update membership"
        ],
        "content_prompts": [
            "Thread: SOC2 evidence workflow before/after",
            "Video: 5 mistakes startups make with compliance docs",
            "Guide: Turning audit findings into product roadmap"
        ],
        "pricing_ideas": [
            "$497 full workspace + onboarding",
            "$79/month compliance war room community",
            "$1,200 done-for-you migration"
        ],
        "stretch_learning": [
            "Take a short compliance fundamentals course",
            "Study permission models for regulated data",
            "Learn lightweight legal copy editing"
        ],
        "partnership_ideas": [
            "Pair with compliance consultants",
            "Bundle with fractional COOs",
            "Affiliate with security questionnaire tools"
        ],
        "automation_ideas": [
            "Automated evidence reminders",
            "Audit checklist progress dashboards",
            "AI policy summarization"
        ],
        "community_hooks": [
            "Monthly compliance template drop",
            "Audit anxiety support circle",
            "Founder hot seat: show your workspace"
        ],
        "stretch_moves": [
            "Shadow a compliance consultant for a week",
            "Earn a basic certification to boost trust",
            "Publish anonymized audit retro reports"
        ],
        "de_risk_moves": [
            "Offer data-handling transparency statement",
            "Provide contract add-ons for NDAs",
            "Create a rapid rollback plan for template tweaks"
        ],
        "low_cost_tools": ["Notion", "Airtable free", "Bento analytics", "Fathom AI"],
        "mini_offer": "$59 compliance workspace gap report",
        "value_prop": "Compliance-ready documentation without expensive consultants",
        "fast_follow_offers": [
            "Quarterly compliance sprint",
            "Stakeholder briefing templates",
            "Team onboarding micro-course"
        ],
        "upsell_paths": [
            "Retainer for evidence upkeep",
            "Custom integration builds",
            "Policy review services"
        ],
        "retention_moves": [
            "Quarterly regulatory change brief",
            "Office hours for compliance questions",
            "Template refresh alerts"
        ],
        "scale_paths": [
            "Launch marketplace for niche packs",
            "License templates to agencies",
            "Build a compliance metrics dashboard SaaS"
        ],
        "foundation_assets": [
            "Audit-ready database schema",
            "Evidence submission workflow",
            "Stakeholder update template"
        ],
        "resourcefulness_moves": [
            "Crowdsource regulatory updates from community",
            "Offer scholarships to nonprofits for testimonials",
            "Swap templates with other builders to expand library"
        ],
        "buddy_system": "Collaborate with a compliance advisor for credibility",
        "score_commentary": "Ideal if you love organized docs and obsess over details"
    },
    {
        "name": "Buyer Insight Sprints for Newsletter Operators",
        "type": "Insight Research Service",
        "description": (
            "Deliver weekly, scrappy research packets that surface subscriber pains, buying triggers, and partnership "
            "ideas so newsletter writers can ship offers faster."
        ),
        "demand_drivers": [
            "Newsletter operators hungry for monetization paths",
            "Brands asking for data-backed sponsorship proposals",
            "Writers lacking time to run continuous audience research"
        ],
        "supply_gap": (
            "Most research agencies focus on enterprise; indie newsletters need lightweight, fast insight"
        ),
        "why_now": (
            "The newsletter boom created thousands of micro-media businesses now pressured to monetize sustainably"
        ),
        "skills": ["research", "analysis", "copywriting", "survey design", "community"],
        "interests": ["media", "newsletters", "marketing", "partnerships"],
        "budget_level": "No Budget",
        "delivery_mode": "Online",
        "audience": ["Creators", "B2B"],
        "time_commitment": 7,
        "ideal_timeline_weeks": 2,
        "best_for": ["Land 3 paying clients", "Build recurring retainers", "Validate quickly"],
        "starter_stack": [
            "Airtable research hub",
            "Typeform or Tally surveys",
            "Google Alerts",
            "Canva insight briefs"
        ],
        "low_cost_moves": [
            "Barter insight sprint for sponsorship shoutouts",
            "Leverage public comments and community threads for qualitative data",
            "Host free office hours to uncover pain points"
        ],
        "validation_steps": [
            "Run a micro-interview blitz with 10 newsletter subscribers",
            "Test a 'rapid insight memo' with one operator",
            "Measure decisions made because of your research"
        ],
        "launch_steps": [
            "Choose one niche (climate media, fintech newsletters, productivity writers)",
            "Design a 3-part insight packet: audience, offer ideas, partnership leads",
            "Share anonymized sample deliverable on social",
            "Pitch a 2-week sprint with clear ROI math"
        ],
        "task_templates": [
            {
                "title": "Map top communities where target subscribers hang out",
                "priority": "High",
                "notes": "List slack groups, forums, and social channels to mine for insight"
            },
            {
                "title": "Draft insight sprint framework and deliverable outline",
                "priority": "High",
                "notes": "Define weekly cadence, metrics tracked, and handoff format"
            },
            {
                "title": "Run 5 subscriber interviews and synthesize decision triggers",
                "priority": "Medium",
                "notes": "Highlight patterns, quotes, and monetization opportunities"
            },
            {
                "title": "Publish a signal report on emerging newsletter sponsorship angles",
                "priority": "Medium",
                "notes": "Use it as lead magnet and proof of expertise"
            }
        ],
        "monetization": [
            "$450 two-week sprint",
            "$800/month retainer for continuous insight",
            "Upsell to sponsorship outreach",
            "Template shop for research systems"
        ],
        "market_signals": [
            "Newsletter communities begging for monetization help",
            "Brands seeking niche audiences",
            "Operators asking for research analysts in job boards"
        ],
        "growth_channels": [
            "Cross-newsletter collaborations",
            "Twitter/X insight threads",
            "Guest segments on newsletter podcasts"
        ],
        "starter_offer": "$97 audience insight sampler (3 quick wins)",
        "first_clients": [
            "Paid newsletter operators",
            "Niche Substack writers",
            "Media collectives"
        ],
        "toolkit": ["Airtable", "Notion", "Figma", "Tally", "Zapier"],
        "key_metrics": [
            "New monetization experiments launched",
            "Sponsorship close rate",
            "Subscriber engagement shifts"
        ],
        "content_prompts": [
            "Signal spotlight: What sponsors want this quarter",
            "Template tour: Audience heatmap dashboard",
            "Case study: How insights unlocked a new offer"
        ],
        "pricing_ideas": [
            "$550 sprint + revenue share bonus",
            "$997/month insight + partnership desk",
            "$149 playbook upsell"
        ],
        "stretch_learning": [
            "Learn basic data visualization",
            "Practice facilitation for insight workshops",
            "Study sponsorship negotiation basics"
        ],
        "partnership_ideas": [
            "Co-create with ad networks",
            "Bundle with copy chiefs",
            "Offer insights to productized service owners"
        ],
        "automation_ideas": [
            "Auto-tag qualitative data",
            "Set up alert feeds for niche trends",
            "Build Airtable dashboards for quick scans"
        ],
        "community_hooks": [
            "Newsletter lab accountability group",
            "Signal swap meetups",
            "Monthly research teardown"
        ],
        "stretch_moves": [
            "Shadow a sponsorship deal negotiation",
            "Publish a public research vault",
            "Host a micro-summit on newsletter monetization"
        ],
        "de_risk_moves": [
            "Offer satisfaction guarantee on first sprint",
            "Share transparent methodology",
            "Keep subscriber data anonymized"
        ],
        "low_cost_tools": ["Google Sheets", "Notion AI", "Hypefury free", "Fathom"],
        "mini_offer": "$49 signal scan for your last 5 newsletters",
        "value_prop": "Monetization-ready insights delivered without hiring a full analyst",
        "fast_follow_offers": [
            "Sponsor outreach playbook",
            "Audience segmentation dashboard",
            "Community co-creation workshops"
        ],
        "upsell_paths": [
            "Insight retainer",
            "White-glove sponsorship outreach",
            "Offer design sprints"
        ],
        "retention_moves": [
            "Monthly insight retro",
            "Opportunity tracker dashboard",
            "Quarterly trend briefings"
        ],
        "scale_paths": [
            "Hire researcher collective",
            "Build insight SaaS",
            "Launch paid community"
        ],
        "foundation_assets": [
            "Interview script library",
            "Insight memo template",
            "Opportunity scorecard"
        ],
        "resourcefulness_moves": [
            "Trade insight sprints for ad slots",
            "Co-market with data tools",
            "Open-source part of the research for backlinks"
        ],
        "buddy_system": "Work with a monetization strategist to deliver end-to-end results",
        "score_commentary": "Great for curious researchers who love uncovering signal"
    }
]


def normalize_list_input(selected: List[str], additional: str) -> List[str]:
    normalized = {item.strip().lower() for item in selected if item}
    if additional:
        normalized.update(
            token.strip().lower()
            for token in additional.split(",")
            if token.strip()
        )
    return sorted(normalized)


def evaluate_opportunity(opportunity: Dict[str, Any], profile: Dict[str, Any]) -> Dict[str, Any]:
    score = 45
    reasons: List[str] = []
    focus_alerts: List[str] = []

    matched_skills = sorted(set(profile["skills"]) & set(opportunity["skills"]))
    if matched_skills:
        score += len(matched_skills) * 7
        reasons.append(
            f"Leverages your skills in {', '.join(matched_skills)}"
        )
    else:
        focus_alerts.append(
            f"Plan quick reps in {opportunity['skills'][0]} to deliver with confidence"
        )

    interest_overlap = sorted(set(profile["interests"]) & set(opportunity["interests"]))
    if interest_overlap:
        score += len(interest_overlap) * 4
        reasons.append(
            f"Matches interests around {', '.join(interest_overlap)}"
        )
    else:
        focus_alerts.append("Clarify if the niche excites you enough to stay curious")

    profile_budget = profile.get("budget", BUDGET_LEVELS[0])
    if BUDGET_SCORES.get(profile_budget, 0) >= BUDGET_SCORES.get(opportunity["budget_level"], 0):
        score += 6
        reasons.append("Fits your launch budget expectations")
    else:
        focus_alerts.append("Scope the offer so it ships with the tools you already have")

    if profile["time_available"] >= opportunity["time_commitment"]:
        score += 5
        reasons.append("Weekly time commitment is realistic")
    else:
        score -= 4
        focus_alerts.append("Automate or batch work to protect your limited hours")

    if profile["timeline"] >= opportunity["ideal_timeline_weeks"]:
        score += 4
        reasons.append("Timeline to validate matches the blueprint")
    else:
        focus_alerts.append("Use a mini-offer to validate faster than the standard playbook")

    delivery_pref = profile["delivery_preference"]
    if delivery_pref == "Either" or delivery_pref == opportunity["delivery_mode"] or opportunity["delivery_mode"] == "Hybrid":
        score += 4
    else:
        focus_alerts.append("Consider whether you can adapt delivery format to your lifestyle")

    if profile["audience_focus"] == "Either" or profile["audience_focus"] in opportunity["audience"]:
        score += 4
    else:
        focus_alerts.append("You may need a partner to access this audience quickly")

    if profile["primary_goal"] in opportunity["best_for"]:
        score += 5
        reasons.append("Direct path to your current goal")

    score = max(25, min(95, score))

    return {
        "score": round(score),
        "fit_reasons": reasons,
        "focus_alerts": focus_alerts,
        "matched_skills": matched_skills
    }


def get_opportunity_recommendations(profile: Dict[str, Any], top_n: int = 3) -> List[Dict[str, Any]]:
    recommendations = []
    for opportunity in OPPORTUNITY_LIBRARY:
        evaluation = evaluate_opportunity(opportunity, profile)
        enriched = {**opportunity, **evaluation}
        recommendations.append(enriched)

    recommendations.sort(key=lambda item: item["score"], reverse=True)
    return recommendations[:top_n]


def get_unique_options(field: str) -> List[str]:
    options = set()
    for opportunity in OPPORTUNITY_LIBRARY:
        for item in opportunity.get(field, []):
            options.add(item)
    return sorted(options)


def next_task_id(tasks: List[Dict[str, Any]]) -> int:
    if not tasks:
        return 1
    return max(task.get("id", 0) for task in tasks) + 1


def add_tasks_from_templates(templates: List[Dict[str, Any]], timeline_weeks: int) -> List[Dict[str, Any]]:
    created_tasks = []
    now = datetime.now()
    total_tasks = max(len(templates), 1)
    for index, template in enumerate(templates):
        due_offset_days = int(((timeline_weeks or 4) * 7) * ((index + 1) / total_tasks))
        due_date = (now + timedelta(days=due_offset_days)).strftime("%Y-%m-%d")
        created_tasks.append({
            "title": template["title"],
            "priority": template.get("priority", "Medium"),
            "urgency": template.get("urgency", "Medium"),
            "status": template.get("status", "To Do"),
            "category": template.get("category", "Opportunity Launch"),
            "due_date": due_date,
            "notes": template.get("notes", ""),
            "response": template.get("notes", ""),
            "agent": template.get("agent", "Opportunity Scout"),
            "created": now.strftime("%Y-%m-%d %H:%M")
        })
    return created_tasks

class MultiAgentAssistant:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.agents = {
            "📋 Checksheet Specialist": {
                "description": "Creates comprehensive checklists, audit forms, and quality control sheets",
                "prompt_prefix": "You are a Checksheet Specialist expert in creating detailed, professional checklists and audit forms. Focus on completeness, clarity, and actionability.",
                "color": "#FF6B6B"
            },
            "📊 Data Analyst": {
                "description": "Analyzes data, creates visualizations, and provides insights",
                "prompt_prefix": "You are a Data Analyst expert in statistical analysis, data visualization, and business intelligence. Provide clear insights with actionable recommendations.",
                "color": "#4ECDC4"
            },
            "📈 Spreadsheet Expert": {
                "description": "Designs and optimizes spreadsheets with formulas and automation",
                "prompt_prefix": "You are a Spreadsheet Expert specialized in Excel/Google Sheets optimization, complex formulas, and data organization. Create efficient, user-friendly solutions.",
                "color": "#45B7D1"
            },
            "💡 Strategic Advisor": {
                "description": "Provides strategic business advice and decision-making support",
                "prompt_prefix": "You are a Strategic Business Advisor with expertise in business strategy, decision-making frameworks, and organizational development. Provide thoughtful, actionable advice.",
                "color": "#96CEB4"
            },
            "👥 Leadership Coach": {
                "description": "Offers leadership development and team management guidance",
                "prompt_prefix": "You are a Leadership Coach specializing in team development, communication, and leadership effectiveness. Provide practical, empathetic guidance.",
                "color": "#FFEAA7"
            },
            "🎯 Six Sigma Black Belt": {
                "description": "Applies Six Sigma methodology for process improvement",
                "prompt_prefix": "You are a Six Sigma Black Belt expert in DMAIC methodology, statistical process control, and quality improvement. Focus on data-driven solutions.",
                "color": "#DDA0DD"
            },
            "⚡ Lean Manufacturing Expert": {
                "description": "Implements lean principles and waste reduction strategies",
                "prompt_prefix": "You are a Lean Manufacturing Expert specializing in waste elimination, value stream mapping, and continuous improvement. Focus on efficiency and value creation.",
                "color": "#98D8C8"
            },
            "🎯 Productivity Coach": {
                "description": "Helps with task management, prioritization, and productivity optimization",
                "prompt_prefix": "You are a Productivity Coach expert in time management, goal setting, and workflow optimization. Help users stay focused and achieve their objectives.",
                "color": "#F7DC6F"
            },
            "🚀 Opportunity Strategist": {
                "description": "Finds high-demand, low-supply business angles and lean launch paths",
                "prompt_prefix": "You are an Opportunity Strategist obsessed with spotting high-demand, low-supply offers that can launch on a shoestring. Blend market signal scanning, creative offer design, and resourceful go-to-market tactics. Always highlight validation steps, scrappy launch moves, and paths to first revenue without paid ads.",
                "color": "#FF8A65"
            },
            "🤖 General Assistant": {
                "description": "Handles diverse tasks and provides comprehensive support",
                "prompt_prefix": "You are a versatile General Assistant capable of handling various business tasks. Adapt your expertise to the specific needs presented.",
                "color": "#BB8FCE"
            }
        }
        
    def get_agent_response(self, agent_name: str, problem_description: str, additional_context: str = "") -> str:
        agent_info = self.agents[agent_name]
        
        full_prompt = f"""
        {agent_info['prompt_prefix']}
        
        Problem/Task: {problem_description}
        
        Additional Context: {additional_context}
        
        Please provide a comprehensive response that includes:
        1. Analysis of the situation
        2. Specific recommendations or solutions
        3. Step-by-step action items where applicable
        4. Expected outcomes or benefits
        5. Any templates, examples, or tools that would be helpful
        
        Format your response clearly with headers and bullet points where appropriate.
        """
        
        try:
            # Use Claude API via requests since anthropic package might not be available
            headers = {
                "Content-Type": "application/json",
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01"
            }
            
            data = {
                "model": "claude-3-5-sonnet-20241022",
                "max_tokens": 4000,
                "temperature": 0.7,
                "messages": [{"role": "user", "content": full_prompt}]
            }
            
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["content"][0]["text"]
            else:
                return f"Error: {response.status_code} - {response.text}"
                
        except Exception as e:
            return f"Error getting response from {agent_name}: {str(e)}"

def create_sample_data():
    """Create sample data for demonstration"""
    dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
    data = {
        'Date': dates,
        'Production': [100 + i*0.5 + (i%30)*2 for i in range(len(dates))],
        'Quality_Score': [95 + (i%10)*0.5 - (i%50)*0.1 for i in range(len(dates))],
        'Defects': [5 - (i%20)*0.2 + (i%15)*0.3 for i in range(len(dates))],
        'Efficiency': [85 + (i%25)*0.8 + (i%40)*0.3 for i in range(len(dates))]
    }
    return pd.DataFrame(data)

def create_dashboard():
    """Create a sample dashboard"""
    df = create_sample_data()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>📈 Avg Production</h3>
            <h2>245.6</h2>
            <p style="color: green;">↗️ +12.3%</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>⭐ Quality Score</h3>
            <h2>94.8%</h2>
            <p style="color: green;">↗️ +2.1%</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>🎯 Efficiency</h3>
            <h2>87.3%</h2>
            <p style="color: orange;">↔️ -0.5%</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <h3>🚫 Defect Rate</h3>
            <h2>3.2%</h2>
            <p style="color: red;">↗️ +0.8%</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        fig1 = px.line(df.tail(30), x='Date', y='Production', 
                      title='Production Trend (Last 30 Days)')
        fig1.update_layout(height=400)
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        fig2 = px.scatter(df.tail(30), x='Production', y='Quality_Score', 
                         size='Efficiency', color='Defects',
                         title='Production vs Quality')
        fig2.update_layout(height=400)
        st.plotly_chart(fig2, use_container_width=True)

def main():
    # Header
    st.markdown('<h1 class="main-header">🤖 Multi-Agent Workplace Assistant</h1>', unsafe_allow_html=True)
    
    # Initialize session state
    if 'tasks' not in st.session_state:
        st.session_state.tasks = []
    if 'assistant' not in st.session_state:
        st.session_state.assistant = None
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("🔧 Configuration")
        
        # API Key input
        api_key = st.text_input("Claude API Key:", type="password", 
                               help="Enter your Anthropic Claude API key")
        
        if not api_key:
            st.warning("⚠️ Please enter your Claude API key to use the agents")
            # Don't stop the app, just disable agent functionality
            agent_available = False
        else:
            try:
                if st.session_state.assistant is None or st.session_state.assistant.api_key != api_key:
                    st.session_state.assistant = MultiAgentAssistant(api_key)
                st.success("✅ API Key provided")
                agent_available = True
            except Exception as e:
                st.error(f"❌ Error with API key: {str(e)}")
                agent_available = False
        
        st.divider()
        
        # Agent selection
        st.header("🤖 Select Agent")
        if agent_available:
            selected_agent = st.selectbox(
                "Choose an agent:",
                list(st.session_state.assistant.agents.keys()),
                help="Select the most appropriate agent for your task"
            )
            
            # Display agent info
            agent_info = st.session_state.assistant.agents[selected_agent]
            st.markdown(f"""
            <div class="agent-card">
                <h4>{selected_agent}</h4>
                <p>{agent_info['description']}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Enter API key to select agents")
            selected_agent = None
    
    # Main content area
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🎯 Problem Solver",
        "🚀 Opportunity Scout",
        "📊 Dashboard",
        "📋 Task Manager",
        "💡 Knowledge Base"
    ])
    
    with tab1:
        st.header("🎯 Problem Solver")
        
        if not agent_available:
            st.warning("⚠️ Please enter your Claude API key in the sidebar to use the Problem Solver")
            return
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Problem description
            problem_description = st.text_area(
                "Describe your problem or task:",
                height=150,
                placeholder="Example: I need to improve our quality control process. We're seeing a 5% defect rate and want to reduce it to under 2%..."
            )
            
            # Additional context
            additional_context = st.text_area(
                "Additional context (optional):",
                height=100,
                placeholder="Budget constraints, timeline, team size, current tools, etc."
            )
            
            # Priority and urgency
            col_priority, col_urgency = st.columns(2)
            with col_priority:
                priority = st.selectbox("Priority:", ["Low", "Medium", "High", "Critical"])
            with col_urgency:
                urgency = st.selectbox("Urgency:", ["Low", "Medium", "High", "Immediate"])
            
            # Submit button
            if st.button("🚀 Get Agent Assistance", type="primary"):
                if problem_description and selected_agent:
                    with st.spinner(f"🤖 {selected_agent} is analyzing your problem..."):
                        response = st.session_state.assistant.get_agent_response(
                            selected_agent, 
                            problem_description, 
                            f"Priority: {priority}, Urgency: {urgency}. {additional_context}"
                        )
                    
                    st.success("✅ Analysis Complete!")
                    st.markdown("### 📝 Agent Response:")
                    st.markdown(response)
                    
                    # Save to session state for task manager
                    task = {
                        'id': len(st.session_state.tasks) + 1,
                        'title': problem_description[:50] + "..." if len(problem_description) > 50 else problem_description,
                        'agent': selected_agent,
                        'priority': priority,
                        'urgency': urgency,
                        'status': 'Completed',
                        'category': 'Agent Insights',
                        'created': datetime.now().strftime("%Y-%m-%d %H:%M"),
                        'response': response,
                        'notes': response
                    }
                    st.session_state.tasks.append(task)
                    
                elif not problem_description:
                    st.warning("⚠️ Please describe your problem or task")
                elif not selected_agent:
                    st.warning("⚠️ Please select an agent")
        
        with col2:
            st.markdown("### 🎯 Quick Actions")
            
            quick_actions = [
                "Create quality checklist",
                "Analyze production data",
                "Design KPI dashboard",
                "Develop training plan",
                "Process improvement project",
                "Cost reduction analysis",
                "Team performance review",
                "Risk assessment"
            ]
            
            for action in quick_actions:
                if st.button(action, key=f"quick_{action}"):
                    # Auto-fill the problem description with the quick action
                    st.session_state[f"quick_action_{action}"] = action
                    st.rerun()
    
    with tab2:
        st.header("🚀 Opportunity Scout")
        st.markdown("Use this lab to surface high-demand, low-supply ideas you can launch with almost no budget.")

        skills_options = sorted({skill.title() for skill in get_unique_options("skills")})
        interests_options = sorted({interest.title() for interest in get_unique_options("interests")})
        audience_options = sorted({aud for aud in get_unique_options("audience")})

        col_left, col_right = st.columns(2)
        with col_left:
            selected_skills_display = st.multiselect(
                "What skills can you leverage right now?",
                options=skills_options,
                help="Pick the skills you're comfortable offering today"
            )
            additional_skills = st.text_input(
                "Add any other skills (comma-separated)",
                help="Example: funnel strategy, email deliverability"
            )
            budget = st.selectbox("Budget you can invest", BUDGET_LEVELS)
            time_available = st.slider("Hours you can focus each week", min_value=2, max_value=30, value=10)
        with col_right:
            selected_interests_display = st.multiselect(
                "Which markets energize you?",
                options=interests_options,
                help="Choose niches you already consume content about"
            )
            additional_interests = st.text_input(
                "Add other interests (comma-separated)",
                help="Example: creator economy, supply chain, parenting"
            )
            timeline = st.slider("Weeks until you want validation", min_value=1, max_value=12, value=4)
            delivery_preference = st.selectbox(
                "Preferred delivery style",
                options=["Either", "Online", "Hybrid", "Local"]
            )

        audience_focus = st.selectbox(
            "Who do you want to serve first?",
            options=["Either"] + audience_options,
            index=0
        )
        primary_goal = st.selectbox(
            "Primary goal for this quarter",
            options=[
                "Land 3 paying clients",
                "Build recurring retainers",
                "Build digital products",
                "Earn leveraged income",
                "Validate quickly"
            ],
            index=0
        )

        profile = {
            "skills": normalize_list_input(selected_skills_display, additional_skills),
            "interests": normalize_list_input(selected_interests_display, additional_interests),
            "budget": budget,
            "time_available": time_available,
            "timeline": timeline,
            "delivery_preference": delivery_preference,
            "audience_focus": audience_focus,
            "primary_goal": primary_goal
        }

        if st.button("🔍 Find Opportunity Matches", type="primary"):
            recommendations = get_opportunity_recommendations(profile)

            if recommendations:
                for index, opportunity in enumerate(recommendations):
                    fit_label = "High Fit" if opportunity["score"] >= 80 else "Promising" if opportunity["score"] >= 65 else "Stretch"
                    with st.container():
                        st.markdown(f"### {opportunity['name']} — {fit_label}")
                        st.markdown(f"**Fit Score:** {opportunity['score']} / 100")
                        st.markdown(f"_{opportunity['score_commentary']}_")

                        col_summary, col_context = st.columns([2, 1])
                        with col_summary:
                            st.markdown(f"**Value Prop:** {opportunity['value_prop']}")
                            st.markdown(f"**Starter Offer:** {opportunity['starter_offer']}")
                            st.markdown(f"**Mini Offer:** {opportunity['mini_offer']}")
                            st.markdown("**Demand Drivers:**")
                            for driver in opportunity["demand_drivers"]:
                                st.markdown(f"- {driver}")
                            st.markdown("**Why Supply Is Thin:**")
                            st.markdown(f"{opportunity['supply_gap']}")
                        with col_context:
                            st.markdown(f"**Why now:** {opportunity['why_now']}")
                            st.markdown("**Ideal Clients:**")
                            for client in opportunity["first_clients"]:
                                st.markdown(f"- {client}")
                            st.markdown("**Tool Stack:**")
                            for tool in opportunity["starter_stack"]:
                                st.markdown(f"- {tool}")

                        if opportunity["fit_reasons"]:
                            st.markdown("**Why this fits you:**")
                            for reason in opportunity["fit_reasons"]:
                                st.markdown(f"- {reason}")
                        if opportunity["focus_alerts"] or opportunity["stretch_moves"]:
                            st.markdown("**Stretch or skill gaps to plan for:**")
                            for alert in opportunity["focus_alerts"]:
                                st.markdown(f"- {alert}")
                            for move in opportunity["stretch_moves"]:
                                st.markdown(f"- {move}")

                        col_plan, col_growth = st.columns(2)
                        with col_plan:
                            st.markdown("**Low/No-Cost Launch Moves:**")
                            for move in opportunity["low_cost_moves"]:
                                st.markdown(f"- {move}")
                            st.markdown("**Validation Steps:**")
                            for step in opportunity["validation_steps"]:
                                st.markdown(f"- {step}")
                            st.markdown("**Launch Plan:**")
                            for step in opportunity["launch_steps"]:
                                st.markdown(f"- {step}")
                        with col_growth:
                            st.markdown("**Monetization Paths:**")
                            for path in opportunity["monetization"]:
                                st.markdown(f"- {path}")
                            st.markdown("**Growth Channels:**")
                            for channel in opportunity["growth_channels"]:
                                st.markdown(f"- {channel}")
                            st.markdown("**Market Signals to Monitor:**")
                            for signal in opportunity["market_signals"]:
                                st.markdown(f"- {signal}")

                        col_metrics, col_assets = st.columns(2)
                        with col_metrics:
                            st.markdown("**Key Metrics to Track:**")
                            for metric in opportunity["key_metrics"]:
                                st.markdown(f"- {metric}")
                            st.markdown("**Content Prompts:**")
                            for prompt in opportunity["content_prompts"]:
                                st.markdown(f"- {prompt}")
                            st.markdown("**Pricing Experiments:**")
                            for idea in opportunity["pricing_ideas"]:
                                st.markdown(f"- {idea}")
                        with col_assets:
                            st.markdown("**Automation + Tools:**")
                            for tool in opportunity["automation_ideas"]:
                                st.markdown(f"- {tool}")
                            st.markdown("**Community Hooks:**")
                            for hook in opportunity["community_hooks"]:
                                st.markdown(f"- {hook}")
                            st.markdown("**Partnership Ideas:**")
                            for partner in opportunity["partnership_ideas"]:
                                st.markdown(f"- {partner}")

                        st.markdown("**Keep momentum:**")
                        for move in opportunity["retention_moves"]:
                            st.markdown(f"- {move}")
                        st.markdown("**Scale paths:**")
                        for path in opportunity["scale_paths"]:
                            st.markdown(f"- {path}")
                        st.markdown("**Resourcefulness Plays:**")
                        for move in opportunity["resourcefulness_moves"]:
                            st.markdown(f"- {move}")
                        st.info(f"Buddy up idea: {opportunity['buddy_system']}")

                        templates = opportunity.get("task_templates", [])
                        if templates:
                            if st.button("Add launch plan to Task Manager", key=f"add_tasks_{index}"):
                                new_tasks = add_tasks_from_templates(templates, profile["timeline"])
                                for new_task in new_tasks:
                                    new_task["id"] = next_task_id(st.session_state.tasks)
                                    st.session_state.tasks.append(new_task)
                                st.success("Launch plan tasks added to your Task Manager")

                        st.divider()
            else:
                st.info("Adjust your inputs and try again to see tailored matches.")

    with tab3:
        st.header("📊 Performance Dashboard")
        st.markdown("*Sample dashboard showing key metrics and visualizations*")
        create_dashboard()

    with tab4:
        st.header("📋 Task Manager")

        if st.session_state.tasks:
            st.markdown("### 📝 Recent Tasks")

            for task in reversed(st.session_state.tasks[-10:]):  # Show last 10 tasks
                title = task.get('title', 'Untitled Task')
                agent_name = task.get('agent', 'Self')
                with st.expander(f"#{task.get('id', '?')} - {title} ({agent_name})"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.markdown(f"**Priority:** {task.get('priority', 'Medium')}")
                        st.markdown(f"**Urgency:** {task.get('urgency', 'Medium')}")
                        st.markdown(f"**Category:** {task.get('category', 'General')}")
                    with col2:
                        status_key = f"status_{task.get('id', '')}"
                        if status_key not in st.session_state:
                            st.session_state[status_key] = task.get('status', 'To Do')
                        updated_status = st.selectbox(
                            "Status",
                            options=TASK_STATUS_OPTIONS,
                            key=status_key
                        )
                        task['status'] = updated_status
                        due_date = task.get('due_date', 'Not set')
                        st.markdown(f"**Due Date:** {due_date}")
                    with col3:
                        st.markdown(f"**Agent:** {agent_name}")
                        st.markdown(f"**Created:** {task.get('created', 'N/A')}")

                    notes = task.get('notes') or task.get('response') or ""
                    if notes:
                        st.markdown("**Notes / Response:**")
                        display_text = notes[:500] + "..." if len(notes) > 500 else notes
                        st.markdown(display_text)

            if st.button("🗑️ Clear All Tasks"):
                st.session_state.tasks = []
                st.rerun()
        else:
            st.info("📝 No tasks yet. Use the Problem Solver or Opportunity Scout tabs to create your first task!")

        st.markdown("---")
        st.subheader("➕ Add a manual task")
        with st.form("manual_task_form"):
            manual_title = st.text_input("Task title")
            manual_category = st.selectbox("Category", TASK_CATEGORIES)
            manual_priority = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"], index=1)
            manual_urgency = st.selectbox("Urgency", ["Low", "Medium", "High", "Immediate"], index=1)
            manual_due_date = st.date_input("Due date", value=datetime.now().date() + timedelta(days=7))
            manual_status = st.selectbox("Status", TASK_STATUS_OPTIONS, index=0)
            manual_notes = st.text_area("Notes / next steps")
            submitted = st.form_submit_button("Add Task")

            if submitted:
                if manual_title:
                    new_task = {
                        'id': next_task_id(st.session_state.tasks),
                        'title': manual_title,
                        'agent': 'Self-assigned',
                        'priority': manual_priority,
                        'urgency': manual_urgency,
                        'status': manual_status,
                        'category': manual_category,
                        'due_date': manual_due_date.strftime("%Y-%m-%d"),
                        'created': datetime.now().strftime("%Y-%m-%d %H:%M"),
                        'notes': manual_notes
                    }
                    st.session_state.tasks.append(new_task)
                    st.success("Task added to your board")
                    st.rerun()
                else:
                    st.warning("Please provide a task title before adding.")

    with tab5:
        st.header("💡 Knowledge Base")
        
        if agent_available:
            st.markdown("### 🤖 Available Agents")
            
            for agent_name, agent_info in st.session_state.assistant.agents.items():
                with st.expander(agent_name):
                    st.markdown(f"**Description:** {agent_info['description']}")
                    st.markdown(f"**Specialization:** {agent_info['prompt_prefix']}")
        
        st.markdown("### 📚 Best Practices")
        
        best_practices = {
            "Problem Description": [
                "Be specific about the current situation",
                "Include quantifiable metrics when possible",
                "Mention constraints and limitations",
                "Specify desired outcomes"
            ],
            "Agent Selection": [
                "Choose the agent that best matches your problem domain",
                "Consider using multiple agents for complex problems",
                "Start with the General Assistant if unsure",
                "Review agent descriptions before selecting"
            ],
            "Context Provision": [
                "Include budget and timeline constraints",
                "Mention team size and capabilities",
                "Specify current tools and systems",
                "Note any regulatory requirements"
            ]
        }
        
        for category, practices in best_practices.items():
            st.markdown(f"**{category}:**")
            for practice in practices:
                st.markdown(f"• {practice}")
            st.markdown("")

if __name__ == "__main__":
    main()
