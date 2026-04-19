#!/usr/bin/env python3
"""
Convert a Markdown file to a styled PDF via headless Chrome.
Usage: python3 scripts/md_to_pdf.py path/to/file.md
Output: same path with .pdf extension.
"""
import re, html, sys, subprocess, pathlib

CSS = """
<style>
body { font-family: -apple-system, BlinkMacSystemFont, 'Helvetica Neue', sans-serif; max-width: 860px; margin: 40px auto; padding: 0 24px; line-height: 1.55; color: #222; }
h1 { border-bottom: 3px solid #b8942e; padding-bottom: 12px; color: #080808; }
h2 { color: #b8942e; margin-top: 2em; border-bottom: 1px solid #eee; padding-bottom: 6px; page-break-before: auto; }
h3 { color: #444; margin-top: 1.8em; }
blockquote { background: #faf7ee; border-left: 4px solid #b8942e; padding: 14px 18px; margin: 14px 0; border-radius: 4px; }
blockquote p { margin: 4px 0; }
table { border-collapse: collapse; width: 100%; margin: 14px 0; font-size: 13px; }
th, td { border: 1px solid #ddd; padding: 6px 10px; text-align: left; vertical-align: top; }
th { background: #faf7ee; color: #080808; }
code { background: #f4f4f4; padding: 2px 6px; border-radius: 3px; font-size: 0.92em; }
pre { background: #1e1e1e; color: #eee; padding: 12px; border-radius: 6px; overflow-x: auto; }
hr { border: 0; border-top: 2px solid #b8942e; margin: 32px 0; opacity: 0.4; }
a { color: #b8942e; }
strong { color: #080808; }
</style>
"""

def inline(t):
    t = html.escape(t)
    t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t)
    t = re.sub(r'`([^`]+)`', r'<code>\1</code>', t)
    t = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', t)
    return t

def convert(md):
    lines = md.split('\n')
    out, in_code, in_bq, in_list = [], False, False, False
    for line in lines:
        if line.startswith('```'):
            in_code = not in_code
            out.append('<pre>' if in_code else '</pre>'); continue
        if in_code: out.append(html.escape(line)); continue
        if '|' in line and line.strip().startswith('|'):
            cells = [c.strip() for c in line.strip().strip('|').split('|')]
            if all(re.match(r'^[-:\s]+$', c) for c in cells): continue
            if not out or not out[-1].startswith('<table'): out.append('<table>')
            tag = 'th' if '**' in line else 'td'
            out.append('<tr>' + ''.join(f'<{tag}>{inline(c)}</{tag}>' for c in cells) + '</tr>')
            continue
        elif out and out[-1].startswith('<tr') and not line.strip().startswith('|'):
            out.append('</table>')
        m = re.match(r'^(#{1,6})\s+(.+)$', line)
        if m:
            n = len(m.group(1)); out.append(f'<h{n}>{inline(m.group(2))}</h{n}>'); continue
        if line.startswith('> '):
            if not in_bq: out.append('<blockquote>'); in_bq = True
            out.append(f'<p>{inline(line[2:])}</p>'); continue
        elif in_bq and not line.startswith('>'):
            out.append('</blockquote>'); in_bq = False
        if line.strip() == '---': out.append('<hr>'); continue
        m = re.match(r'^\s*[-*]\s+(.+)$', line)
        if m:
            if not in_list: out.append('<ul>'); in_list = True
            out.append(f'<li>{inline(m.group(1))}</li>'); continue
        if in_list and not line.strip().startswith(('-','*')):
            out.append('</ul>'); in_list = False
        if line.strip(): out.append(f'<p>{inline(line)}</p>')
        else: out.append('')
    if in_bq: out.append('</blockquote>')
    if in_list: out.append('</ul>')
    return '\n'.join(out)

def main():
    if len(sys.argv) < 2:
        print('Usage: md_to_pdf.py path/to/file.md'); sys.exit(1)
    md_path = pathlib.Path(sys.argv[1]).resolve()
    pdf_path = md_path.with_suffix('.pdf')
    html_tmp = pathlib.Path('/tmp') / (md_path.stem + '.html')
    md = md_path.read_text(encoding='utf-8')
    title = md_path.stem
    doc = f"<!DOCTYPE html><html><head><meta charset='utf-8'><title>{title}</title>{CSS}</head><body>{convert(md)}</body></html>"
    html_tmp.write_text(doc, encoding='utf-8')
    chrome = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    subprocess.run([chrome, '--headless', '--disable-gpu', '--no-pdf-header-footer',
                    f'--print-to-pdf={pdf_path}', f'file://{html_tmp}'],
                   capture_output=True)
    print(f'PDF: {pdf_path}')
    subprocess.run(['open', str(pdf_path)])

if __name__ == '__main__':
    main()
