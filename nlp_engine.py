import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

LEGAL_CORPUS = [
    {
        "title": "BNS Section 103 / IPC Section 302 (Murder)",
        "keywords": "murder kill death homicidal intent bodily injury assault",
        "details": "Punishment for murder under Bharatiya Nyaya Sanhita (BNS) Section 103 (formerly IPC Section 302). Prescribes death penalty or imprisonment for life, alongside statutory fine."
    },
    {
        "title": "BNS Section 318 / IPC Section 420 (Cheating and Dishonestly Inducing Delivery of Property)",
        "keywords": "cheating fraud scam financial dishonestly fake agreement promised money",
        "details": "Covers intentional deception to deliver property or alter valuable security. Punishable with imprisonment up to 7 years and fine."
    },
    {
        "title": "Section 138, Negotiable Instruments Act (Cheque Bounce)",
        "keywords": "cheque check bounce dishonour funds insufficient drawer bank notice debt",
        "details": "Dishonour of cheque for insufficiency of funds. Legal demand notice must be served to the drawer within 30 days of receiving the return memo, giving 15 days to pay before criminal complaint."
    },
    {
        "title": "Section 66D, Information Technology Act (Cheating by Personation using Computer)",
        "keywords": "cyber fraud online scam phishing hacking password identity theft digital",
        "details": "Impersonation using computer resource or communication device. Punishable with imprisonment up to 3 years and fine up to Rs. 1 lakh."
    },
    {
        "title": "Consumer Protection Act, 2019 (Deficiency in Service)",
        "keywords": "consumer unfair trade practice refund defective product warranty replacement deficiency",
        "details": "Allows consumers to claim compensation and replacements before District/State/National Consumer Commissions for defective goods or unfair trade practices."
    },
    {
        "title": "BNS Section 351 / IPC Section 503 & 506 (Criminal Intimidation)",
        "keywords": "threat intimidation harm reputation injury blackmailing extortion",
        "details": "Threatening injury to person, reputation, or property to compel actions. Punishable with imprisonment up to 2 years, or 7 years if threat involves death/grievous hurt."
    }
]

RISK_TERMS = {
    "Unilateral Termination": ["sole discretion to terminate", "without cause", "immediate termination without notice"],
    "Unlimited Indemnity": ["indemnify and hold harmless", "unlimited liability", "all damages whatsoever"],
    "One-Sided Jurisdiction": ["exclusive jurisdiction of courts in", "waives all rights to dispute jurisdiction"],
    "Forfeiture / High Penalty": ["forfeit entire deposit", "liquidated damages equal to", "penalty without deduction"],
    "Broad Confidentiality": ["perpetual non-disclosure", "in perpetuity", "irrevocable assignment of rights"]
}

def query_legal_database(query: str):
    docs = [f"{item['title']} {item['keywords']} {item['details']}" for item in LEGAL_CORPUS]
    corpus = docs + [query]
    
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(corpus)
    
    similarities = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1]).flatten()
    ranked_indices = similarities.argsort()[::-1]
    
    matches = []
    for idx in ranked_indices[:2]:
        if similarities[idx] > 0.05:
            matches.append({
                "statute": LEGAL_CORPUS[idx]["title"],
                "explanation": LEGAL_CORPUS[idx]["details"],
                "relevance_score": round(float(similarities[idx]), 3)
            })
    
    if not matches:
        return [{
            "statute": "General Indian Jurisprudence & Civil/Criminal Law",
            "explanation": "No specific statutory keyword match. For tailored advisory, consult an enrolled Advocate under the Advocates Act, 1961.",
            "relevance_score": 0.0
        }]
    return matches

def summarize_legal_document(text: str, num_sentences: int = 3):
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if len(s.strip()) > 15]
    if len(sentences) <= num_sentences:
        return " ".join(sentences)
        
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf = vectorizer.fit_transform(sentences)
    scores = tfidf.sum(axis=1).A1
    
    top_indices = scores.argsort()[-num_sentences:][::-1]
    top_indices.sort()
    return " ".join([sentences[i] for i in top_indices])

def draft_statutory_notice(client_name: str, opposite_party: str, issue_type: str, amount: str, details: str):
    if issue_type == "cheque_bounce":
        subject = "LEGAL NOTICE UNDER SECTION 138 OF THE NEGOTIABLE INSTRUMENTS ACT, 1881"
        demand = f"demand that you pay the dishonoured sum of INR {amount} within 15 (fifteen) days of receipt of this statutory notice."
    elif issue_type == "recovery":
        subject = "LEGAL NOTICE FOR RECOVERY OF OUTSTANDING DUES WITH INTEREST"
        demand = f"demand the remittance of the pending principal amount of INR {amount} along with 18% p.a. interest within 15 days."
    elif issue_type == "tenant_eviction":
        subject = "LEGAL NOTICE FOR TERMINATION OF TENANCY AND VACATION OF PREMISES"
        demand = "demand that you deliver vacant and peaceful possession of the demised premises within 15 days, clearing all pending arrears."
    else:
        subject = "LEGAL NOTICE FOR DEMAND OF REDRESSAL AND LEGAL COMPLIANCE"
        demand = "demand that you rectify the breach of obligation specified herein within 15 days from the receipt of this notice."

    notice_text = f"""REF: LEG/NT/{issue_type.upper()}/2026/01
REGISTERED A.D. / SPEED POST / LEGAL COMMUNICATION

TO:
{opposite_party}

FROM (Under Instructions from):
{client_name}

SUBJECT: {subject}

Sir/Madam,

Under instructions from my client, {client_name}, I hereby serve upon you this formal Legal Notice:

1. That you entered into transactions/engagements with my client wherein liabilities and contractual expectations were explicitly agreed upon.
2. STATEMENT OF FACTS:
   {details}
3. That contrary to statutory and contractual undertakings, you have defaulted on your obligations, causing substantial financial and civil prejudice to my client.
4. DEMAND & NOTICE:
   My client hereby calls upon you to {demand}

Take further notice that should you fail to comply with these statutory requisites within the stipulated fifteen (15) days, my client holds full instructions to initiate appropriate civil, consumer, and/or criminal proceedings against you in the competent Court of Jurisdiction entirely at your risk, cost, and consequence.

DATED: Present
COUNSEL FOR THE CLAIMANT / SENDER
"""
    return notice_text

def analyze_document_risks(text: str):
    found_risks = []
    text_lower = text.lower()
    for category, phrases in RISK_TERMS.items():
        matched_phrases = [p for p in phrases if p in text_lower]
        if matched_phrases:
            found_risks.append({
                "category": category,
                "matches": matched_phrases,
                "severity": "HIGH" if category in ["Unlimited Indemnity", "Unilateral Termination"] else "MEDIUM"
            })
    return {
        "risk_count": len(found_risks),
        "risks": found_risks,
        "is_high_risk": any(r["severity"] == "HIGH" for r in found_risks)
    }