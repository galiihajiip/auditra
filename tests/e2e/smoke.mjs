// E2E smoke: siklus penugasan audit penuh (auditor ↔ reviewer) di browser sungguhan.
//   npm i --no-save playwright-core && AUDITRA_URL=http://localhost:8000 node tests/e2e/smoke.mjs
// Set CHROME_PATH bila bukan Chromium bawaan Playwright. Aman dijalankan berulang (memilih paket tanpa penugasan aktif).
import { chromium } from 'playwright-core';
import fs from 'fs';
import os from 'os';

const BASE = process.env.AUDITRA_URL ?? 'http://localhost:8000';
const results = [];
const step = (name, ok, extra = '') => { results.push(ok); console.log(ok ? 'PASS' : 'FAIL', name, extra); };
const b = await chromium.launch(process.env.CHROME_PATH ? { executablePath: process.env.CHROME_PATH } : {});
const errs = [];
const watch = (p) => p.on('pageerror', (e) => errs.push('PAGEERROR ' + e.message.slice(0, 160)));
const toast = (p, re) => p.locator('[role=alert],[role=status]').filter({ hasText: re }).first().waitFor({ timeout: 20000 });
const tmp = fs.mkdtempSync(os.tmpdir() + '/auditra-');

async function login(p, label) {
  await p.goto(BASE + '/masuk');
  await p.getByRole('button', { name: new RegExp(label) }).click();
  await p.waitForURL('**/kasus');
}
async function tab(p, name) { await p.getByRole('tab', { name: new RegExp('^\\s*' + name) }).click(); }

// ── AUDITOR ────────────────────────────────────────────────────────────────
const ctxA = await b.newContext({ viewport: { width: 1440, height: 900 } });
const a = await ctxA.newPage(); watch(a);
await a.goto(BASE + '/'); await a.waitForSelector('a[aria-label^="Buka passport"]', { timeout: 90000 });
step('hero + value proposition', await a.getByText('diaudit lebih dulu').count() > 0);
await a.getByRole('radio', { name: /Kritis/ }).click();
await a.waitForFunction(() => location.search.includes('rpi=70'));
step('filter reflected in URL', true);
// pencarian, urutan, dan unduh CSV pada tabel paket
await a.getByLabel('Cari paket').fill('Binsat');
await a.waitForFunction(() => location.search.includes('q=Binsat'));
await a.waitForFunction(() => [...document.querySelectorAll('tbody tr')].length > 0 && [...document.querySelectorAll('tbody tr')].every((r) => /binsat/i.test(r.textContent)), null, { timeout: 20000 });
step('keyword search filters the package table', true);
await a.getByLabel('Urutkan').selectOption('pagu:desc');
await a.waitForFunction(() => location.search.includes('sort=pagu'));
const csvHref = await a.getByRole('link', { name: /Unduh CSV/ }).getAttribute('href');
const csv = await a.evaluate(async (u) => { const r = await fetch(u); return { ok: r.ok, ct: r.headers.get('content-type'), txt: (await r.text()).slice(0, 80) }; }, csvHref);
step('CSV export follows active filter and search', csv.ok && /text\/csv/.test(csv.ct) && /id_sirup,rpi/.test(csv.txt) && /q=Binsat/.test(csvHref), csvHref.slice(-60));
await a.getByLabel('Cari paket').fill('zzzz-tidak-ada-paket');
await a.getByText('Tidak ada paket yang cocok').waitFor({ timeout: 20000 }); step('empty state shown for no match', true);
await a.getByRole('button', { name: /Coba demo sekarang/ }).click();
await toast(a, /Masuk sebagai Auditor demo/); step('one-click demo login', true);

let opened = false;
for (let page = 1; page <= 8 && !opened; page++) {
  for (let i = 0; i < 10 && !opened; i++) {
    await a.goto(BASE + `/?rpi=70&p=${page}`); await a.waitForSelector('tbody tr');
    await a.locator('tbody tr').nth(i).click(); await a.waitForURL('**/paket/*');
    await a.getByText('Mengapa paket ini berprioritas?').waitFor(); await a.waitForTimeout(900);
    opened = await a.getByRole('button', { name: 'Buka penugasan audit' }).count() > 0;
  }
}
step('passport shows 7 signals', await a.locator('[role=progressbar]').count() === 7);
step('found package without active assignment', opened);
await a.getByRole('button', { name: 'Buka penugasan audit' }).last().click();
await a.getByRole('dialog').getByRole('textbox').fill('RPI kritis, pagu besar, metode non-kompetitif: layak diprioritaskan.');
await a.getByRole('dialog').getByRole('button', { name: 'Buka penugasan' }).click();
await a.waitForURL('**/kasus/*'); const caseUrl = a.url(); step('assignment opened (seleksi)', /\/kasus\/\d+/.test(caseUrl), caseUrl);

// gerbang: tombol terkunci sampai syarat terpenuhi — diuji dengan penugasan ke-2 tanpa alasan? (diuji di pytest); di UI: syarat tampil
await a.getByRole('heading', { name: 'Tetapkan alasan seleksi sasaran' }).waitFor();
step('readiness checklist shown', await a.getByLabel('Syarat tahap berikutnya').count() > 0);
await a.getByRole('button', { name: /Mulai perencanaan/ }).click(); await toast(a, /Tahap: Perencanaan/); step('seleksi → perencanaan', true);

// ── Perencanaan ────────────────────────────────────────────────────────────
await a.getByRole('button', { name: /Mulai pelaksanaan/ }).isDisabled().then((d) => step('execution locked until plan complete', d));
await a.getByLabel('Tujuan penugasan').fill('Menguji kesesuaian metode pemilihan dan indikasi pemecahan paket.');
await a.getByLabel('Penilaian risiko (termasuk risiko kecurangan)').fill('Risiko bawaan tinggi; risiko kecurangan: pemecahan paket.');
await a.getByLabel('Pertimbangan materialitas').fill('Kuantitatif: nilai paket besar; kualitatif: perhatian publik.');
await a.getByRole('button', { name: 'Simpan rencana' }).click(); await toast(a, /Rencana disimpan/);
await a.getByRole('button', { name: /Bangkitkan program/ }).click(); await toast(a, /Program audit dibangkitkan/);
const nProc = await a.locator('#program-h').innerText();
step('audit program generated from signals', /Program audit \([1-9]\d* prosedur\)/.test(nProc), nProc);
step('procedures cite regulation criteria', await a.getByText(/Perpres 16\/2018 jo\. 12\/2021 jo\. 46\/2025 Pasal/).count() > 0);
await a.getByRole('button', { name: /Mulai pelaksanaan/ }).click(); await toast(a, /Tahap: Pelaksanaan/); step('perencanaan → pelaksanaan', true);

// ── Pelaksanaan: pengujian per prosedur ────────────────────────────────────
await tab(a, 'Pengujian');
const heads = a.locator('[role=tabpanel] li > button[aria-expanded]');
const n = await heads.count(); step('procedure cards rendered', n >= 2, `n=${n}`);
step('submit to review locked while untested', await a.getByRole('button', { name: /Ajukan ke reviu/ }).first().isDisabled());
let findingProc = '';
for (let i = 0; i < n; i++) {
  const h = heads.nth(i);
  if ((await h.getAttribute('aria-expanded')) !== 'true') await h.click();
  const code = (await h.locator('.chip').first().innerText()).trim();
  if (i < 2) {  // dua prosedur pertama didukung bukti
    await a.getByRole('button', { name: /Tambah bukti/ }).first().click();
    await a.getByLabel('Tautan bukti').fill('https://example.org/dokumen-' + code + '.pdf');
    await a.getByLabel('Judul bukti').fill('Dokumen ' + code);
    for (const l of ['Relevan dengan tujuan/kriteria', 'Valid', 'Andal (sumber dapat dipercaya)']) await a.getByRole('dialog').getByLabel(l).check();
    await a.getByRole('dialog').getByRole('button', { name: 'Simpan bukti' }).click(); await toast(a, /Bukti ditambahkan/);
  }
  const grp = a.getByRole('radiogroup', { name: 'Hasil ' + code });
  if (i === 0) { await grp.getByRole('radio', { name: 'Sesuai', exact: true }).click(); }
  else if (i === 1) { findingProc = code; await grp.getByRole('radio', { name: 'Tidak sesuai' }).click(); await a.getByLabel('Catatan hasil ' + code).fill('Kondisi tidak sesuai kriteria, perlu dituangkan sebagai temuan.'); }
  else { await grp.getByRole('radio', { name: 'Tidak dapat diuji' }).click(); await a.getByLabel('Catatan hasil ' + code).fill('Dokumen pelaksanaan belum diserahkan entitas.'); }
  await a.getByRole('button', { name: 'Simpan hasil' }).click(); await toast(a, /Hasil disimpan/);
  await h.click(); // ciutkan agar kartu berikutnya tidak tertukar
}
step('all procedures have results', true);
await a.getByRole('button', { name: /Ajukan ke reviu/ }).first().isDisabled().then((d) => step('still locked: nonconformity has no finding', d));

// ── Temuan ─────────────────────────────────────────────────────────────────
await tab(a, 'Temuan');
await a.getByRole('button', { name: 'Susun temuan' }).click();
await a.getByLabel('Judul temuan *').fill('Indikasi ketidaksesuaian ' + findingProc);
await a.getByLabel('Prosedur terkait').selectOption({ label: (await a.getByLabel('Prosedur terkait').locator('option').allInnerTexts()).find((t) => t.startsWith(findingProc)) });
await a.getByLabel('Kondisi *').fill('Ditemukan pagu dan metode tidak sejalan dengan batas nilai pada dokumen perencanaan.');
step('criterion auto-filled from procedure', (await a.getByLabel('Sumber kriteria *').inputValue()).length > 3);
await a.getByLabel('Rekomendasi', { exact: true }).fill('Evaluasi pemaketan dan metode pemilihan.');
await a.getByRole('dialog').getByRole('button', { name: 'Simpan temuan' }).click();
await a.getByText(/Rekomendasi harus menyebut pihak/).first().waitFor({ timeout: 10000 }).catch(() => {});
step('recommendation requires responsible party (server rule)', await a.locator('[role=alert]').filter({ hasText: /pihak yang bertanggung jawab/ }).count() > 0);
await a.getByLabel('Rekomendasi ditujukan kepada').fill('Pengguna Anggaran');
await a.getByRole('dialog').getByText('Dokumen ' + findingProc).first().click().catch(() => {});
await a.getByRole('dialog').getByRole('button', { name: 'Simpan temuan' }).click(); await toast(a, /Temuan disimpan/);
step('finding with kondisi/kriteria/sebab/akibat saved', await a.getByText('Kondisi', { exact: true }).count() > 0);
await a.getByRole('button', { name: /Ajukan ke reviu/ }).first().waitFor();
const ready = !(await a.getByRole('button', { name: /Ajukan ke reviu/ }).first().isDisabled());
step('submit to review unlocked once gates satisfied', ready);
await a.getByRole('button', { name: /Ajukan ke reviu/ }).first().click(); await toast(a, /Tahap: Reviu berjenjang/); step('pelaksanaan → reviu', true);
step('auditor cannot review evidence', await a.getByRole('button', { name: 'Terima', exact: true }).count() === 0);
await ctxA.close();

// ── REVIEWER ───────────────────────────────────────────────────────────────
const ctxR = await b.newContext({ viewport: { width: 1440, height: 900 } });
const r = await ctxR.newPage(); watch(r);
await login(r, 'Masuk sebagai Reviewer demo');
await r.goto(caseUrl); await r.getByRole('heading', { name: 'Tinjau kertas kerja & bukti' }).waitFor(); step('reviewer guidance', true);
await r.getByRole('button', { name: /Terima kertas kerja/ }).isDisabled().then((d) => step('communication locked until evidence reviewed', d));
await tab(r, 'Pengujian');
let guard = 0;
while ((await r.getByRole('button', { name: 'Terima', exact: true }).count()) > 0 && guard++ < 10) {
  await r.getByRole('button', { name: 'Terima', exact: true }).first().click();
  await r.getByRole('dialog').getByRole('button', { name: 'Terima bukti' }).click(); await toast(r, /Bukti diterima/);
  await r.waitForTimeout(400);
}
step('reviewer accepted all evidence from the review queue', guard >= 2, `n=${guard}`);
step('reviewer has no evidence form', await r.getByRole('button', { name: /Tambah bukti/ }).count() === 0);
await r.getByRole('button', { name: /Terima kertas kerja/ }).click(); await toast(r, /Tahap: Komunikasi hasil/); step('reviu → komunikasi', true);
await ctxR.close();

// ── AUDITOR: tanggapan ─────────────────────────────────────────────────────
const ctxA2 = await b.newContext({ viewport: { width: 1440, height: 900 } });
const a2 = await ctxA2.newPage(); watch(a2);
await login(a2, 'Masuk sebagai Auditor demo');
await a2.goto(caseUrl); await a2.getByRole('heading', { name: 'Catat tanggapan tertulis entitas' }).waitFor();
await tab(a2, 'Temuan');
await a2.getByRole('button', { name: /Catat tanggapan/ }).click().catch(() => {});
await a2.getByLabel(/Isi tanggapan temuan/).first().fill('Entitas menerima sebagian dan akan mengevaluasi pemaketan tahun depan.');
await a2.getByLabel(/Status tanggapan temuan/).first().selectOption('diterima_sebagian');
await a2.getByRole('button', { name: /Catat tanggapan/ }).first().click(); await toast(a2, /Tanggapan dicatat/); step('entity response recorded', true);
await ctxA2.close();

// ── REVIEWER: kesimpulan, selesai ──────────────────────────────────────────
const ctxR2 = await b.newContext({ viewport: { width: 1440, height: 900 } });
const r2 = await ctxR2.newPage(); watch(r2);
await login(r2, 'Masuk sebagai Reviewer demo');
await r2.goto(caseUrl); await r2.getByRole('heading', { name: 'Menunggu tanggapan entitas' }).waitFor().catch(() => {});
await r2.getByRole('button', { name: /Selesaikan penugasan/ }).isDisabled().then((d) => step('completion locked until conclusion written', d));
await tab(r2, 'Ringkasan');
await r2.getByLabel('Kesimpulan penugasan').fill('Terdapat satu temuan ketidakpatuhan yang ditanggapi sebagian oleh entitas.');
await r2.getByRole('button', { name: 'Simpan kesimpulan' }).click(); await toast(r2, /Kesimpulan disimpan/);
await r2.getByRole('button', { name: /Selesaikan penugasan/ }).click(); await toast(r2, /Tahap: Selesai/); step('komunikasi → selesai (dengan temuan)', true);
await r2.getByText('Dengan temuan').first().waitFor(); step('outcome shown', true);
await ctxR2.close();

// ── AUDITOR: tindak lanjut ─────────────────────────────────────────────────
const ctxA3 = await b.newContext({ viewport: { width: 1440, height: 900 } });
const a3 = await ctxA3.newPage(); watch(a3);
await login(a3, 'Masuk sebagai Auditor demo'); await a3.goto(caseUrl);
await tab(a3, 'Temuan');
await a3.getByLabel(/Status tindak lanjut temuan/).first().selectOption('dalam_proses');
await a3.getByLabel(/Catatan tindak lanjut temuan/).first().fill('PA menerbitkan nota dinas perbaikan pemaketan.');
await a3.getByRole('button', { name: 'Simpan pemantauan' }).first().click(); await toast(a3, /Tindak lanjut dicatat/); step('follow-up monitoring recorded', true);
await tab(a3, 'Riwayat');
const hist = await a3.getByRole('heading', { name: 'Riwayat' }).locator('xpath=ancestor::section').innerText();
step('immutable history covers the whole cycle', ['Sasaran dipilih', 'Program audit', 'Hasil pengujian', 'Bukti ditambahkan', 'Temuan', 'Bukti ditinjau', 'Tanggapan entitas', 'Tindak lanjut'].every((k) => hist.includes(k)));
await a3.goto(BASE + '/kasus'); await a3.getByRole('region', { name: 'Selesai' }).getByRole('link').first().waitFor(); step('assignment on board in "Selesai"', true);
await ctxA3.close();

// ── Metodologi & mobile ────────────────────────────────────────────────────
const ctxM = await b.newContext({ viewport: { width: 390, height: 844 } });
const m = await ctxM.newPage(); watch(m);
await m.goto(BASE + '/metodologi'); await m.getByText('Dari mana alur audit ini berasal').waitFor();
step('methodology page lists unverified sources', await m.getByText('Yang belum terverifikasi').count() > 0);
for (const path of ['/', '/masuk', '/metodologi', new URL(caseUrl).pathname]) {
  if (path.startsWith('/kasus')) await login(m, 'Masuk sebagai Auditor demo');
  await m.goto(BASE + path); await m.waitForTimeout(path === '/' ? 6000 : 2000);
  const [sw, iw] = await m.evaluate(() => [document.documentElement.scrollWidth, innerWidth]);
  step(`mobile no horizontal overflow ${path}`, sw <= iw, `${sw}/${iw}`);
}
await ctxM.close(); await b.close();
const real = errs.filter((e) => !/status of 4\d\d/.test(e));
step('no uncaught page errors', real.length === 0, JSON.stringify(real));
console.log(`\n${results.filter(Boolean).length}/${results.length} passed`);
process.exit(results.every(Boolean) ? 0 : 1);
