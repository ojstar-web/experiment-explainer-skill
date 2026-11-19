#!/usr/bin/env node
// Render one Markdown source to PDF, then optionally create page previews.
const fs = require('node:fs');
const path = require('node:path');
const os = require('node:os');
const { pathToFileURL } = require('node:url');
const { spawnSync } = require('node:child_process');
const { marked } = require('marked');
const { chromium } = require('playwright');

function usage() {
  console.error('Usage: node render_markdown_pdf.cjs input.md [output.pdf] [--preview-dir DIR] [--mathjax FILE_OR_URL]');
  process.exit(2);
}
const args = process.argv.slice(2);
if (!args.length) usage();
const input = path.resolve(args.shift());
let output = input.replace(/\.md$/i, '.pdf');
if (args[0] && !args[0].startsWith('--')) output = path.resolve(args.shift());
let previewDir, mathjax = 'https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js';
for (let i = 0; i < args.length; i++) {
  if (args[i] === '--preview-dir') previewDir = path.resolve(args[++i] || '');
  else if (args[i] === '--mathjax') mathjax = args[++i];
  else usage();
}
if (!fs.existsSync(input)) throw new Error(`Markdown source missing: ${input}`);
const md = fs.readFileSync(input, 'utf8');
const math = [];
const protectedMd = md.replace(/\$\$([\s\S]+?)\$\$|(?<!\$)\$([^\n$]+?)\$(?!\$)/g, (whole) => {
  const token = `MATHPLACEHOLDER${math.length}END`;
  math.push(whole);
  return token;
});
let html = marked.parse(protectedMd);
math.forEach((value, index) => { html = html.replace(`MATHPLACEHOLDER${index}END`, value); });
const base = pathToFileURL(path.dirname(input) + path.sep).href;
const document = `<!doctype html><html lang="zh"><head><meta charset="utf-8"><base href="${base}"><style>
@page{size:A4;margin:18mm 17mm}body{font:11pt/1.65 "Microsoft YaHei","Noto Sans CJK SC",sans-serif;color:#20242a}h1,h2,h3{break-after:avoid;line-height:1.3}h1{font-size:21pt}h2{font-size:16pt;margin-top:1.2em}h3{font-size:13pt}p{margin:.55em 0}img{max-width:100%;height:auto}figure,img,table,pre,blockquote{break-inside:avoid}table{border-collapse:collapse;width:100%;font-size:9.5pt}th,td{border:1px solid #b7bec8;padding:4px 7px}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#f4f6f8;padding:8px}blockquote{border-left:3px solid #7a9ac2;margin-left:0;padding-left:12px;color:#475467}a{color:#225c9d}svg{max-width:100%}
</style><script>window.MathJax={tex:{inlineMath:[['$','$']],displayMath:[['$$','$$']]},svg:{fontCache:'global'}};</script></head><body>${html}</body></html>`;
async function main() {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'md-pdf-'));
  const tmp = path.join(dir, 'document.html');
  fs.writeFileSync(tmp, document);
  const browser = await chromium.launch({headless:true, executablePath:process.env.BROWSER_EXECUTABLE || undefined, args:['--allow-file-access-from-files']});
  try {
    const page = await browser.newPage();
    await page.goto(pathToFileURL(tmp).href, {waitUntil:'load'});
    await page.addScriptTag(mathjax.startsWith('http') ? {url:mathjax} : {path:path.resolve(mathjax)});
    await page.evaluate(() => MathJax.startup.promise);
    await page.evaluate(() => document.fonts.ready);
    const status = await page.evaluate(() => ({badImages:[...document.images].filter(x=>!x.complete||x.naturalWidth===0).map(x=>x.src),mathErrors:document.querySelectorAll('mjx-merror').length}));
    if (status.badImages.length || status.mathErrors) throw new Error(`Render check failed: ${JSON.stringify(status)}`);
    fs.mkdirSync(path.dirname(output), {recursive:true});
    await page.pdf({path:output,format:'A4',printBackground:true,preferCSSPageSize:true});
    console.log(`PDF: ${output}; images OK; math errors: 0`);
  } finally { await browser.close(); fs.rmSync(dir,{recursive:true,force:true}); }
  if (previewDir) {
    fs.mkdirSync(previewDir,{recursive:true});
    const info = spawnSync('pdfinfo',[output],{encoding:'utf8'});
    if (info.status !== 0) throw new Error(`pdfinfo failed: ${info.stderr || info.error}`);
    const pages = Number(info.stdout.match(/^Pages:\s+(\d+)/m)?.[1]);
    if (!pages) throw new Error('Could not determine PDF page count');
    const samples = [...new Set([1,Math.ceil(pages/2),pages])];
    for (const n of samples) {
      const prefix = path.join(previewDir,`page-${String(n).padStart(3,'0')}`);
      const result = spawnSync('pdftoppm',['-f',String(n),'-l',String(n),'-singlefile','-scale-to','1400','-png',output,prefix],{encoding:'utf8'});
      if (result.status !== 0) throw new Error(`pdftoppm failed: ${result.stderr || result.error}`);
    }
    console.log(`Preview: ${samples.length} of ${pages} pages in ${previewDir}`);
  }
}
main().catch(error=>{ console.error(error.message); process.exitCode=1; });

