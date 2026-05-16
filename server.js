const express = require('express');
const { Octokit } = require("@octokit/core");
const crypto = require('crypto');

const app = express();
const octokit = new Octokit({ auth: process.env.GITHUB_TOKEN });

// Configuration - update these if needed
const REPO_OWNER = "stgreg30";
const REPO_NAME = "Ossa-";
const FILE_PATH = "tri-ai-log.md";

// Enable CORS for future daemon integration
app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept');
  next();
});

// Global In-Memory State Machine
let currentLedgerState = {
    current_hash: "00000000",
    last_node: "system",
    sequence_id: 0,
    current_round: 1,
    authors_this_round: [],
    history: []
};

// Helper: Push to GitHub
async function pushToGitHubLog(commitMessage, appendText) {
    try {
        let fileSha = null;
        let currentContent = "";
        try {
            const res = await octokit.request('GET /repos/{owner}/{repo}/contents/{path}', {
                owner: REPO_OWNER,
                repo: REPO_NAME,
                path: FILE_PATH
            });
            fileSha = res.data.sha;
            currentContent = Buffer.from(res.data.content, 'base64').toString('utf-8');
        } catch (err) {
            if (err.status !== 404) throw err;
        }

        const updatedContent = currentContent + "\n" + appendText;
        const contentBase64 = Buffer.from(updatedContent).toString('base64');

        await octokit.request('PUT /repos/{owner}/{repo}/contents/{path}', {
            owner: REPO_OWNER,
            repo: REPO_NAME,
            path: FILE_PATH,
            message: commitMessage,
            content: contentBase64,
            sha: fileSha || undefined
        });
        console.log(`[GitHub] Committed block #${currentLedgerState.sequence_id}`);
    } catch (error) {
        console.error(`[GitHub Error] ${error.message}`);
    }
}

// Main hop endpoint
app.get('/hop', async (req, res) => {
    const { f, t, h, p, r } = req.query;

    // 1. Desync protection
    if (h !== currentLedgerState.current_hash) {
        return res.status(409).send(`
            <body style="font-family:monospace; background:#0f141c; color:#e06c75; text-align:center; padding:50px;">
                <h2>[DESYNC ERROR]</h2>
                <p>Expected hash: <strong>${currentLedgerState.current_hash}</strong></p>
                <p>Received: <strong>${h}</strong></p>
                <p><a href="/r" style="color:#61afef">View current state</a></p>
            </body>
        `);
    }

    // 2. Track round participation
    if (!currentLedgerState.authors_this_round.includes(f)) {
        currentLedgerState.authors_this_round.push(f);
    }

    let roundCompleted = false;
    if (currentLedgerState.authors_this_round.length >= 3) {
        currentLedgerState.authors_this_round = [];
        currentLedgerState.current_round += 1;
        roundCompleted = true;
    }

    // 3. Update state
    currentLedgerState.sequence_id += 1;
    currentLedgerState.last_node = f;
    
    const newHash = crypto.createHash('sha256')
                          .update(h + p)
                          .digest('hex')
                          .substring(0, 8);
                          
    currentLedgerState.current_hash = newHash;
    currentLedgerState.history.push({ 
        step: currentLedgerState.sequence_id, 
        from: f, 
        to: t,
        round: r || currentLedgerState.current_round,
        data: p 
    });

    // 4. Log to GitHub (async)
    const targetNames = { g: 'gemini', m: 'meta', d: 'deepseek' };
    const rawLogBlock = `---\nauthor: ${targetNames[f]}\nts: ${new Date().toISOString()}\nreply_to: ${targetNames[currentLedgerState.last_node] || 'system'}\nround: ${r || currentLedgerState.current_round}\nhash: ${newHash}\nbody: |\n  ${p}\n---`;
    
    pushToGitHubLog(`Council: ${targetNames[f]} -> ${targetNames[t]} (#${currentLedgerState.sequence_id})`, rawLogBlock);

    // 5. Generate next prompt
    const displayNames = { g: 'Gemini', m: 'Meta AI', d: 'DeepSeek' };
    const targetUrls = { 
        g: 'https://gemini.google.com', 
        m: 'https://meta.ai', 
        d: 'https://chat.deepseek.com' 
    };

    const nextPromptText = `[COUNCIL STATE: ${newHash}]
Round: ${r || currentLedgerState.current_round} | From: ${displayNames[f]} | To: ${displayNames[t]}
Payload: ${p}
Status: ${currentLedgerState.authors_this_round.length}/3 nodes this round${roundCompleted ? ' - ROUND COMPLETE' : ''}

Review and respond. End your reply with the council footer.`;

    res.send(`
        <!DOCTYPE html>
        <html>
        <head>
            <title>→ ${displayNames[t]}</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body { font-family: -apple-system, monospace; background: #0f141c; color: #abb2bf; margin: 0; padding: 20px; }
                .card { background: #1e222b; border: 1px solid #61afef; padding: 25px; max-width: 600px; margin: 20px auto; border-radius: 8px; }
                .payload-box { background: #171a21; border-left: 3px solid #98c379; padding: 12px; margin: 15px 0; font-size: 13px; white-space: pre-wrap; word-break: break-word; }
                .btn { background: #61afef; color: #000; padding: 12px 20px; border: none; border-radius: 6px; cursor: pointer; font-weight: 600; width: 100%; font-size: 16px; }
                .meta { color: #e5c07b; font-size: 12px; margin-bottom: 10px; }
                h2 { color: #98c379; margin-top: 0; font-size: 18px; }
            </style>
        </head>
        <body>
            <div class="card">
                <h2>✓ Logged</h2>
                <div class="meta">Seq #${currentLedgerState.sequence_id} | Hash ${newHash} | Round ${r || currentLedgerState.current_round}</div>
                <div class="meta">Next: <strong>${displayNames[t]}</strong> (${currentLedgerState.authors_this_round.length}/3)</div>
                <div class="payload-box" id="promptText">${nextPromptText}</div>
                <button class="btn" onclick="copyAndRoute()">Copy & Open ${displayNames[t]}</button>
            </div>
            <script>
                function copyAndRoute() {
                    const text = document.getElementById('promptText').innerText;
                    navigator.clipboard.writeText(text).then(() => {
                        window.open("${targetUrls[t]}", "_blank");
                    }).catch(() => {
                        prompt("Copy this text:", text);
                        window.open("${targetUrls[t]}", "_blank");
                    });
                }
            </script>
        </body>
        </html>
    `);
});

// Read endpoint - view current state
app.get('/r', (req, res) => {
    res.json({
        current_hash: currentLedgerState.current_hash,
        current_round: currentLedgerState.current_round,
        sequence_id: currentLedgerState.sequence_id,
        authors_this_round: currentLedgerState.authors_this_round,
        last_node: currentLedgerState.last_node,
        history_length: currentLedgerState.history.length
    });
});

// Health check
app.get('/', (req, res) => {
    res.send('Council Router Online. Use /hop?f=m&t=d&h=00000000&p=test&r=1');
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Council router live on port ${PORT}`));
