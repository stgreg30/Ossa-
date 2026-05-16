const express = require('express');
const { Octokit } = require("@octokit/core");
const crypto = require('crypto');

const app = express();

// AGGRESSIVE TOKEN CLEANING
const rawToken = process.env.GITHUB_TOKEN || '';
const cleanToken = rawToken.replace(/[^A-Za-z0-9_]/g, '').trim();
console.log(`[Startup] Token length: ${cleanToken.length}, starts with: ${cleanToken.substring(0, 4)}`);

const octokit = new Octokit({ auth: cleanToken });

const REPO_OWNER = "stgreg30";
const REPO_NAME = "Ossa-";
const FILE_PATH = "tri-ai-log.md";

app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*');
  next();
});

let state = {
    hash: "00000000",
    seq: 0,
    round: 1,
    authors: [],
};

async function githubPush(msg, text) {
    try {
        if (cleanToken.length < 30) {
            console.log('[GitHub] Token too short, skipping');
            return;
        }

        let sha = null, content = "";
        try {
            const r = await octokit.request('GET /repos/{o}/{r}/contents/{p}', {
                o: REPO_OWNER, r: REPO_NAME, p: FILE_PATH
            });
            sha = r.data.sha;
            content = Buffer.from(r.data.content, 'base64').toString('utf8');
        } catch (e) {
            if (e.status!== 404) throw e;
        }

        const clean = text.replace(/[^\x20-\x7E\n]/g, '');
        const updated = content + (content? "\n" : "") + clean;
        const b64 = Buffer.from(updated, 'utf8').toString('base64');

        await octokit.request('PUT /repos/{o}/{r}/contents/{p}', {
            o: REPO_OWNER, r: REPO_NAME, p: FILE_PATH,
            message: msg.substring(0, 70),
            content: b64,
            sha: sha
        });
        console.log(`[GitHub] ✓ #${state.seq}`);
    } catch (e) {
        console.error(`[GitHub] ${e.message}`);
    }
}

app.get('/hop', async (req, res) => {
    const { f, t, h, p = '', r } = req.query;

    if (h!== state.hash) {
        return res.status(409).send(`Hash mismatch. Expected ${state.hash}, got ${h}`);
    }

    if (!state.authors.includes(f)) state.authors.push(f);
    if (state.authors.length >= 3) {
        state.authors = [];
        state.round++;
    }

    state.seq++;
    const newHash = crypto.createHash('sha256').update(h + p).digest('hex').slice(0, 8);
    state.hash = newHash;

    const names = { g: 'gemini', m: 'meta', d: 'deepseek' };
    const log = `---\nauthor: ${names[f]}\nround: ${r || state.round}\nhash: ${newHash}\nbody: ${p}\n---`;

    githubPush(`council ${names[f]}`, log);

    const next = `[${newHash}] ${p}`;
    const url = { g: 'https://gemini.google.com', m: 'https://meta.ai', d: 'https://chat.deepseek.com' }[t];

    res.send(`<html><body style="font-family:monospace;background:#000;color:#0f0;padding:20px">
<h2>LOGGED #${state.seq}</h2>
<p>Hash: ${newHash}</p>
<p>Next: ${t.toUpperCase()}</p>
<pre style="background:#111;padding:10px">${next}</pre>
<button onclick="navigator.clipboard.writeText('${next}').then(()=>window.open('${url}'))"
style="padding:10px;background:#0f0;color:#000;border:0;cursor:pointer">
Copy & Open
</button>
</body></html>`);
});

app.get('/test-github', async (req, res) => {
    await githubPush('test', 'test entry ' + Date.now());
    res.send('Check logs and GitHub');
});

app.get('/', (req, res) => res.send('OK'));

app.listen(10000, () => console.log('Live'));