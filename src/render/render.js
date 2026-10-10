// 그림·릴스 렌더 — node src/render/render.js (playwright 필요)
//  · 앱 공지 무대 그림 → assets/img/notice-hero.webp 원본 PNG
//  · 「가족을 초대해요」 릴스 프레임 300장(10초 × 30fps) → .cache/invite-{ko,en}/ → ffmpeg로 mp4
const path = require('path'), fs = require('fs'), os = require('os');
const { chromium } = require(process.env.PLAYWRIGHT || 'playwright');
const ROOT = path.resolve(__dirname, '../..');
const APP = 'file://' + path.join(os.homedir(), 'project/poopiemate');
function page(name) {
  const src = fs.readFileSync(path.join(__dirname, name), 'utf8').replaceAll('APP/', APP + '/');
  const out = path.join(ROOT, '.cache', name);
  fs.mkdirSync(path.dirname(out), { recursive: true });
  fs.writeFileSync(out, src);
  return 'file://' + out;
}
(async () => {
  const b = await chromium.launch();
  const hero = await (await b.newContext({ viewport: { width: 346, height: 170 }, deviceScaleFactor: 3 })).newPage();
  await hero.goto(page('notice_hero.html'), { waitUntil: 'load' });
  await hero.locator('.card').screenshot({ path: path.join(ROOT, '.cache/notice-hero.png'), omitBackground: true });
  const ctx = await b.newContext({ viewport: { width: 360, height: 640 }, deviceScaleFactor: 3 });
  for (const lang of ['ko', 'en']) {
    const dir = path.join(ROOT, '.cache', 'invite-' + lang);
    fs.mkdirSync(dir, { recursive: true });
    const p = await ctx.newPage();
    await p.goto(page('invite_reel.html') + (lang === 'en' ? '?lang=en' : ''), { waitUntil: 'load' });
    await p.evaluate(() => document.fonts.ready);
    for (let i = 0; i < 300; i++) {
      await p.evaluate(t => render(t), i / 300);
      await p.screenshot({ path: path.join(dir, String(i).padStart(3, '0') + '.png') });
    }
    await p.close();
    console.log('frames', lang);
  }
  await b.close();
})();
