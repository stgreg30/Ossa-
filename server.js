const express = require('express');
const { Octokit } = require("@octokit/core");
const crypto = require('crypto');

const app = express();
const octokit = new Octokit({ auth: (process.env.GITHUB_TOKEN || '').trim() });

const REPO_OWNER = "stgreg30";
const REPO_NAME = "Ossa-";
const FILE_PATH = "tri-ai-log.md";

app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*');
  next();
});

let currentLedgerState = {
    current_hash: "00000000",
    last_node: "system",
    sequence_id: 0,
    current_round: 1,
    authors_this_round: [],
    history: []
};

async function pushToGitHubLog(commitMessage, appendText) {
    try {
        const token = (process.env.GITHUB_TOKEN || '').trim();
        if (!token || token.length < 20) {
            console.log('[GitHub] Token missing or invalid, skipping sync');
            return;
        }

        let fileSha = null;
        let currentContent = "";
        try {
            const res = await octokit.request('GET /repos/{owner}/{repo}/contents/{path}', {
                owner: REPO_OWNER,
                repo: REPO_NAME,
                path: FILE_PATH,
                headers: { 'X-GitHub-Api-Version': '2022-11-28' }
            });
            fileSha = res.data.sha;
            currentContent = Buffer.from(res.data.content, 'base64').toString('utf8');
        } catch (err) {
            if (err.status!== 404) {
                console.error(`[GitHub GET Error] ${err.message}`);
                return;
            }
        }

        const cleanAppend = appendText.replace(/[^\x20-\x7E\n\r\t]/g, '');
        const updatedContent = currentContent + (currentContent? "\n" : "") + cleanAppend;
        const contentBase64 = Buffer.from(updatedContent, 'utf8').toString('base64');
        const cleanMessage = commitMessage.replace(/[^\x20-\x7E]/g, '').substring(0, 70);

        await octokit.request('PUT /repos/{owner}/{repo}/contents/{path}', {
            owner: REPO_OWNER,
            repo: REPO_NAME,
            path: FILE_PATH,
            message: cleanMessage,
            content: contentBase64,
            sha: fileSha,
            headers: { 'X-GitHub-Api-Version': '2022-11-28' }
        });
        console.log(`[GitHub] ✓ Block #${currentLedgerState.sequence_id} synced`);
    } catch (error) {
        console.error(`[GitHub Error] ${error.message}`);
    }
}

app.get('/hop', async (req, res) => {
    const { f, t, h, p = '', r } = req.query;

    if (h!== currentLedgerState.current_hash) {
        return res.status(409).send(`
            <body style="font-family:monospace;background:#0f141c;color:#e06c75;padding:40px;text-align:center">
                <h2>DESYNC ERROR</h2>
                <p>Expected: ${currentLedgerState.current_hash}</p>
                <p>Got: ${h}</p>
                <p><a href="/r" style="color:#61afef">View current state</a></p>
            </body>
        `);
    }

    if (!currentLedgerState.authors_this_round.includes(f)) {
        currentLedgerState.authors_this_round.push(f);
    }

    let roundCompleted = false;
    if (currentLedgerState.authors_this_round.length >= 3) {
        currentLedgerState.authors_this_round = [];
        currentLedgerState.current_round += 1;
        roundCompleted = true;
    }

    currentLedgerState.sequence_id += 1;
    currentLedgerState.last_node = f;

    const newHash = crypto.createHash('sha256').update(h + p).digest('hex').substring(0, 8);
    currentLedgerState.current_hash = newHash;

    currentLedgerState.history.push({
        step: currentLedgerState.sequence_id,
        from: f,
        to: t,
        round: r || currentLedgerState.current_round,
        hash: newHash,
        data: p.substring(0, 200)
    });

    const names = { g: 'gemini', m: 'meta', d: 'deepseek' };
    const displayNames = { g: 'Gemini', m: 'Meta AI', d: 'DeepSeek' };
    const urls = { g: 'https://gemini.google.com', m: 'https://meta.ai', d: 'https://chat.deepseek.com' };

    const logBlock = `---\nauthor: ${names[f]}\nround: ${r || currentLedgerState.current_round}\nhash: ${newHash}\nts: ${new Date().toISOString()}\nbody: ${p}\n---`;

    pushToGitHubLog(`council: ${names[f]}->${names[t]} #${currentLedgerState.sequence_id}`, logBlock);

    const nextPrompt = `[COUNCIL ${newHash}] Round ${r || currentLedgerState.current_round}\nFrom: ${displayNames[f]}\nPayload: ${p}\n\nRespond and include your council link.`;

    res.send(`
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>→ ${displayNames[t]}</title>
<style>
body{margin:0;background:#0a0e14;color:#c5c8c6;font-family:system-ui,-apple-system,sans-serif}
.card{max-width:520px;margin:30px auto;background:#141a21;border:1px solid #2a3441;border-radius:12px;padding:24px}
h2{margin:0 0 8px;color:#8fc28a;font-size:18px}
.meta{color:#7a7f87;font-size:13px;margin-bottom:16px}
.box{background:#0d1117;border:1px solid #222a33;border-radius:8px;padding:14px;font-family:ui-monospace,monospace;font-size:13px;white-space:pre-wrap;word-break:break-word;max-height:200px;overflow:auto;margin:16px 0}
.btn{width:100%;background:#4f8cc9;color:#fff;border:0;border-radius:8px;padding:14px;font-size:15px;font-weight:600;cursor:pointer}
.btn:active{transform:scale(0.98)}
.hint{margin-top:12px;font-size:12px;color:#7a7f87;text-align:center}
.ok{display:none;color:#8fc28a;margin-top:10px;text-align:center;font-size:13px}
</style>
</head>
<body>
<div class="card">
<h2>✓ State Logged</h2>
<div class="meta">#${currentLedgerState.sequence_id} • hash ${newHash} • ${currentLedgerState.authors_this_round.length}/3</div>
<div class="meta">Next: <b>${displayNames[t]}</b></div>
<div class="box" id="txt">${nextPrompt}</div>
<button class="btn" onclick="go()">Copy Text & Open ${displayNames[t]}</button>
<div class="ok" id="ok">✓ Copied! Now paste into ${displayNames[t]} chat</div>
<div class="hint">After tapping, switch to the new tab and long-press to paste</div>
</div>
<script>
function go(){
  const t=document.getElementById('txt').innerText;
  navigator.clipboard.writeText(t).then(()=>{
    document.getElementById('ok').style.display='block';
    setTimeout(()=>window.open("${urls[t]}","_blank"),300);
  }).catch(()=>{
    prompt('Copy this manually:',t);
    window.open("${urls[t]}","_blank");
  });
}
</script>
</body>
</html>`);
});

app.get('/r', (req, res) => {
    res.json(currentLedgerState);
});

app.get('/', (req, res) => {
    res.send('Council Router v0.2 Online');
});

app.listen(process.env.PORT || 10000, () => console.log('Router live'));