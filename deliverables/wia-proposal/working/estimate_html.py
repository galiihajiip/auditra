# Estimasi halaman memakai HTML + Chromium (BUKAN keluaran final, hanya pemeriksaan anggaran halaman)
import importlib.util, re, html
from pathlib import Path
WP=Path("/Users/macbookpro/Projects/auditra-main/deliverables/wia-proposal")
spec=importlib.util.spec_from_file_location("c",WP/"working/content.py"); C=importlib.util.module_from_spec(spec); spec.loader.exec_module(C)
FONTDIR="/private/tmp/claude-501/-Users-macbookpro-Projects-auditra-main/5a966cd3-e4bd-44c8-a285-cc64a3b57f81/scratchpad/wia/tx/word/fonts/"
FIG,TAB={},{}
n=m=0
for sec in (C.BAB1,C.BAB2,C.BAB3,C.BAB4,C.LAMPIRAN):
    for e in sec:
        if e[0] in("fig","figrow"): n+=1; FIG[e[1]]=n
        if e[0]=="tab": m+=1; TAB[e[1]]=m
def inl(t):
    t=re.sub(r"\{fig:(\w+)\}",lambda x:f"Gambar {FIG[x.group(1)]}",t); t=re.sub(r"\{tab:(\w+)\}",lambda x:f"Tabel {TAB[x.group(1)]}",t)
    t=html.escape(t); t=re.sub(r"\*\*(.+?)\*\*",r"<b>\1</b>",t); return re.sub(r"\*(.+?)\*",r"<i>\1</i>",t)
def render(sec):
    o=[]
    for e in sec:
        k=e[0]
        if k=="h2": o.append(f"<h2>{inl(e[1])}</h2>")
        elif k=="h3": o.append(f"<h3>{inl(e[1])}</h3>")
        elif k=="p": o.append(f"<p>{inl(e[1])}</p>")
        elif k=="fig": o.append(f'<div class="f"><img style="width:{e[3]}cm" src="file://{WP}/{e[2]}"><div class="c"><b>Gambar {FIG[e[1]]}.</b> {inl(e[4])}</div><div class="s">Sumber: {inl(e[5])}</div></div>')
        elif k=="figrow": o.append('<div class="f"><div style="display:flex;justify-content:center;gap:.3cm">'+"".join(f'<img style="width:{e[3]}cm" src="file://{WP}/{p}">' for p in e[2])+f'</div><div class="c"><b>Gambar {FIG[e[1]]}.</b> {inl(e[4])}</div><div class="s">Sumber: {inl(e[5])}</div></div>')
        elif k=="tab":
            _,key,cap,h,rows,w,src=e
            t=f'<div class="f"><div class="c"><b>Tabel {TAB[key]}.</b> {inl(cap)}</div><table>'+"<tr>"+"".join(f'<th style="width:{x}cm">{inl(c)}</th>' for c,x in zip(h,w))+"</tr>"
            for r in rows: t+="<tr>"+"".join(f"<td>{inl(c)}</td>" for c in r)+"</tr>"
            o.append(t+f'</table><div class="s">Sumber: {inl(src)}</div></div>')
    return "\n".join(o)
css=f"""@font-face{{font-family:PJS;src:url(file://{FONTDIR}PlusJakartaSans-regular.ttf);font-weight:400}}
@font-face{{font-family:PJS;src:url(file://{FONTDIR}PlusJakartaSans-bold.ttf);font-weight:700}}
@font-face{{font-family:PJS;src:url(file://{FONTDIR}PlusJakartaSans-italic.ttf);font-style:italic}}
@page{{size:21.0cm 29.69cm;margin:2.54cm}}
body{{font-family:PJS;font-size:10pt;line-height:1.5;margin:0}}
p{{text-align:justify;margin:0 0 6pt}} h2{{font-size:11pt;margin:14pt 0 4pt;break-after:avoid}} h3{{font-size:10pt;margin:8pt 0 3pt;break-after:avoid;line-height:1.15}}
h1{{font-size:13pt;text-align:center;break-before:page;margin:0 0 12pt}} .f{{text-align:center;break-inside:avoid;margin:6pt 0 10pt}} .c{{font-size:9pt;line-height:1.0;margin-top:2pt}} .s{{font-size:8pt;font-style:italic;line-height:1.0}}
table{{border-collapse:collapse;table-layout:fixed;margin:3pt auto;font-size:8.5pt;line-height:1.1;text-align:left}} td,th{{border:.5pt solid #9aa5b8;padding:2pt 4pt;vertical-align:top}} th{{background:#dce6f2}} tr{{break-inside:avoid}}
img{{max-width:100%}}"""
doc=f"<html><head><meta charset=utf-8><style>{css}</style></head><body>"
doc+="<h1 id=kp>KATA PENGANTAR</h1>"+"".join(f"<p>{inl(e[1])}</p>" for e in C.KATA_PENGANTAR)+'<p style="text-align:right">Surabaya, 11 November 2026<br>Ketua Tim<br><br><br><b>Galih Aji Pangestu</b></p>'
for tag,num,ttl,sec in (("b1","I","PENDAHULUAN",C.BAB1),("b2","II","RANCANGAN SISTEM",C.BAB2),("b3","III","HASIL DAN PEMBAHASAN",C.BAB3),("b4","IV","PENUTUP",C.BAB4)):
    doc+=f'<h1 id={tag}>BAB {num}<br>{ttl}</h1>'+render(sec)
doc+='<h1 id=lp>LAMPIRAN</h1>'+render(C.LAMPIRAN)+'<h1 id=dp>DAFTAR PUSTAKA</h1>'+"".join(f'<p style="text-align:left;padding-left:1cm;text-indent:-1cm;line-height:1.15">{inl(r)}</p>' for r in C.REFS)+"</body></html>"
Path(WP/"working/_estimate.html").write_text(doc,encoding="utf8"); print("html ok")
