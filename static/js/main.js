function switchTab(tabId) {
  document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));

  document.getElementById(tabId).classList.add('active');
  event.target.classList.add('active');
}

async function submitQuery() {
  const query = document.getElementById('queryInput').value;
  const out = document.getElementById('queryResults');
  if (!query) return;

  out.classList.remove('hidden');
  out.innerHTML = "<em>Analyzing Indian statutes and penal provisions...</em>";

  try {
    const res = await fetch('/api/query', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query })
    });
    const result = await res.json();

    if (result.success) {
      let html = `<h3 style="margin-bottom:1rem;color:#f0f6fc;">Statutory Analysis</h3>`;
      result.data.forEach(item => {
        html += `
          <div class="statute-card">
            <div class="statute-title">${item.statute}</div>
            <div class="statute-score">Cosine Relevance: ${item.relevance_score}</div>
            <p style="margin-top:0.4rem;font-size:0.875rem;">${item.explanation}</p>
          </div>
        `;
      });
      out.innerHTML = html;
    }
  } catch (err) {
    out.innerHTML = `<span style="color:#f85149;">Error processing legal query.</span>`;
  }
}

async function submitSummarize() {
  const text = document.getElementById('summarizeInput').value;
  const out = document.getElementById('summarizeResults');
  if (!text) return;

  out.classList.remove('hidden');
  out.innerHTML = "<em>Computing TF-IDF extractive summary...</em>";

  try {
    const res = await fetch('/api/summarize', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text })
    });
    const result = await res.json();
    if (result.success) {
      out.innerHTML = `
        <h3 style="margin-bottom:0.5rem;color:#f0f6fc;">Executive Document Summary</h3>
        <p style="font-size:0.9rem;">${result.summary}</p>
      `;
    }
  } catch (err) {
    out.innerHTML = `<span style="color:#f85149;">Failed to summarize document.</span>`;
  }
}

async function submitDraft() {
  const payload = {
    client_name: document.getElementById('clientName').value,
    opposite_party: document.getElementById('oppositeParty').value,
    issue_type: document.getElementById('issueType').value,
    amount: document.getElementById('amount').value,
    details: document.getElementById('draftDetails').value
  };

  const out = document.getElementById('draftResults');
  out.classList.remove('hidden');
  out.innerHTML = "<em>Drafting formal legal notice...</em>";

  try {
    const res = await fetch('/api/draft', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const result = await res.json();
    if (result.success) {
      out.innerHTML = `
        <h3 style="margin-bottom:0.5rem;color:#f0f6fc;">Generated Legal Notice</h3>
        <pre>${result.draft}</pre>
      `;
    }
  } catch (err) {
    out.innerHTML = `<span style="color:#f85149;">Failed to generate legal draft.</span>`;
  }
}

async function submitAnalyze() {
  const text = document.getElementById('analyzeInput').value;
  const out = document.getElementById('analyzeResults');
  if (!text) return;

  out.classList.remove('hidden');
  out.innerHTML = "<em>Scanning document for one-sided and predatory terms...</em>";

  try {
    const res = await fetch('/api/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text })
    });
    const result = await res.json();

    if (result.success) {
      let risks = result.analysis.risks;
      let html = `<h3 style="margin-bottom:0.5rem;color:#f0f6fc;">Contract Risk Assessment</h3>`;
      
      if (risks.length === 0) {
        html += `<p style="color:#58a6ff;font-size:0.9rem;">No immediate high-risk predatory phrases detected based on the standard risk dictionary.</p>`;
      } else {
        html += `<p style="margin-bottom:1rem;font-size:0.875rem;">Flagged Clauses (${risks.length}):</p>`;
        risks.forEach(r => {
          html += `
            <div style="margin-bottom:0.75rem;">
              <span class="tag-risk ${r.severity}">${r.severity} RISK: ${r.category}</span>
              <div style="font-size:0.85rem;color:#8b949e;">Matched terms: <em>"${r.matches.join('", "')}"</em></div>
            </div>
          `;
        });
      }

      html += `<div style="margin-top:1rem;padding-top:0.75rem;border-top:1px solid #30363d;">
                 <strong>Core Clause Summary:</strong>
                 <p style="font-size:0.85rem;margin-top:0.3rem;">${result.summary}</p>
               </div>`;
      out.innerHTML = html;
    }
  } catch (err) {
    out.innerHTML = `<span style="color:#f85149;">Error scanning document clauses.</span>`;
  }
}