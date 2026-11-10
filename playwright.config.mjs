import { defineConfig } from '@playwright/test';
import { LOCAL_SITE, PUBLIC_SITE } from './ci/widgets/site.mjs';

const live = process.env.WIDGETS_LIVE === '1';

export default defineConfig({
  testDir: './tests',
  testMatch: 'widgets.spec.mjs',
  timeout: 60_000,
  expect: { timeout: 10_000 },
  workers: 2,
  retries: 0,
  forbidOnly: Boolean(process.env.CI),
  reporter: [
    ['list'],
    ['junit', { outputFile: 'test-results/junit.xml' }],
    ['html', { open: 'never' }],
  ],
  use: {
    browserName: 'chromium',
    baseURL: live ? PUBLIC_SITE : LOCAL_SITE,
    viewport: { width: 1440, height: 1000 },
    screenshot: 'only-on-failure',
    trace: 'retain-on-failure',
    launchOptions: {
      args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'],
    },
  },
  webServer: live ? undefined : {
    command: 'node ci/widgets/serve.mjs',
    url: LOCAL_SITE,
    reuseExistingServer: false,
  },
});
