import { resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const REPO = '/repos/NVIDIA/cuda-q-academic';

export async function requestJSON(path) {
  const headers = { Accept: 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28' };
  if (process.env.WIDGETS_GITHUB_TOKEN) headers.Authorization = `Bearer ${process.env.WIDGETS_GITHUB_TOKEN}`;
  const response = await fetch(`https://api.github.com${path}`, { headers, signal: AbortSignal.timeout(15_000) });
  if (!response.ok) throw new Error(`GitHub API returned ${response.status()} for ${path}. Check access/rate limits; WIDGETS_GITHUB_TOKEN may supply read-only access.`);
  return response.json();
}

export async function waitForDeployment({
  sha = process.env.CI_COMMIT_SHA,
  request = requestJSON,
  timeoutMs = 600_000,
  pollMs = 30_000,
  now = Date.now,
  pause = ms => new Promise(resolve => setTimeout(resolve, ms)),
} = {}) {
  if (!sha || !/^[a-f0-9]{40}$/i.test(sha)) throw new Error('CI_COMMIT_SHA must be a full commit SHA.');
  const deadline = now() + timeoutMs;
  while (now() < deadline) {
    const deployments = await request(`${REPO}/deployments?environment=github-pages&per_page=1`);
    if (!Array.isArray(deployments)) throw new Error('Unexpected GitHub deployments response.');
    const deployment = deployments[0];
    if (deployment?.sha === sha) {
      const statuses = await request(`${REPO}/deployments/${deployment.id}/statuses?per_page=1`);
      if (!Array.isArray(statuses)) throw new Error('Unexpected GitHub deployment statuses response.');
      const state = statuses[0]?.state;
      if (state === 'success') {
        const branch = await request(`${REPO}/branches/widgets-as-html`);
        if (branch.commit?.sha !== sha) throw new Error('The tested commit has been superseded on widgets-as-html.');
        return deployment;
      }
      if (['failure', 'error', 'inactive'].includes(state)) throw new Error(`GitHub Pages deployment ${deployment.id} is ${state}.`);
    }
    await pause(Math.min(pollMs, Math.max(0, deadline - now())));
  }
  throw new Error(`Timed out waiting for the latest GitHub Pages deployment to publish ${sha}.`);
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  try {
    const deployment = await waitForDeployment();
    console.log(`GitHub Pages deployment ${deployment.id} successfully published ${deployment.sha}.`);
  } catch (error) {
    console.error(error.message);
    process.exitCode = 1;
  }
}
