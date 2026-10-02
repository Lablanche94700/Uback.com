# -*- coding: utf-8 -*-
"""Recherche « Search a startup or investor », commune à tous les en-têtes du site.
Index statique /assets/search-index.json (nom, slug, type, pays, rang) écrit par tools/build_companies.py ;
script sans dépendance /assets/search.js (écrit par write_js()), suggestions dès 2 caractères.
Styles : SEARCH_CSS, recopié dans ma/assets/style.css entre deux marqueurs par sync_css() (comme le pied de page),
et intégré à la CSS en ligne des pages de tools/build_home.py.
Sur grand écran (homepage, pages globales, fiches : classe hdr-s), le champ est visible dans l'en-tête ; ailleurs et en dessous
de 1280 px, une loupe l'ouvre sous l'en-tête."""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
START, END = '/* search:start (généré par tools/search.py, ne pas modifier ici) */', '/* search:end */'
LABEL = {'en': 'Search a startup or investor', 'fr': 'Rechercher une startup ou un investisseur'}

SEARCH_CSS = '''.hdr .wrap,header.hdr-lang .wrap{position:relative}
.srch{position:static;display:flex;align-items:center}
.srch-b{display:inline-flex;align-items:center;justify-content:center;width:44px;height:44px;border:0;background:none;color:#1E3A5F;cursor:pointer;border-radius:10px;padding:0}
.srch-b:hover{background:#f3f5f8}
.srch-p{display:none;position:absolute;left:0;right:0;top:100%;background:#fff;border-bottom:1px solid #e5e9ef;padding:10px 16px 12px;z-index:40;box-shadow:0 8px 20px rgba(30,58,95,.08)}
.srch.open .srch-p{display:block}
.srch-f{display:flex;align-items:center;gap:8px;border:1px solid #d9dee5;border-radius:10px;padding:0 12px;min-height:44px;background:#fff;color:#5b6472}
.srch-f:focus-within{border-color:#1E3A5F}
.srch-f input{border:0;outline:0;font:inherit;font-size:16px;color:#1f2937;width:100%;min-width:0;background:transparent;-webkit-appearance:none;appearance:none}
.srch-r{list-style:none;margin:6px 0 0;padding:0;max-height:min(60vh,420px);overflow:auto}
.srch-r:empty{display:none}
.srch-r a{display:flex;justify-content:space-between;gap:12px;padding:9px 10px;border-radius:8px;color:#1f2937;text-decoration:none;font-size:14px}
.srch-r a:hover,.srch-r a[aria-selected=true]{background:#f3f5f8}
.srch-r b{color:#1E3A5F;font-weight:600}
.srch-r small{color:#5b6472;font-size:12.5px;white-space:nowrap}
.srch-r .none{padding:9px 10px;color:#5b6472;font-size:14px}
@media (min-width:1280px){header.hdr-lang .srch,.hdr-s .srch{position:relative}header.hdr-lang .srch-b,.hdr-s .srch-b{display:none}
  header.hdr-lang .srch-p,.hdr-s .srch-p{display:block;position:static;padding:0;border:0;box-shadow:none;background:none;width:230px}
  header.hdr-lang .srch-f,.hdr-s .srch-f{min-height:40px}header.hdr-lang .srch-f input,.hdr-s .srch-f input{font-size:14px}
  header.hdr-lang .srch-r,.hdr-s .srch-r{position:absolute;right:0;top:calc(100% + 6px);width:340px;background:#fff;border:1px solid #e5e9ef;border-radius:12px;padding:6px;margin:0;box-shadow:0 12px 28px rgba(30,58,95,.12)}}
'''

ICON = ('<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
        'aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/></svg>')

def html(root='/', lang='en'):
    """Composant à placer dans l'en-tête (le conteneur de l'en-tête est mis en position relative par SEARCH_CSS).
    root : préfixe du script (« @ROOT@ » dans le gabarit des pays) ; les fiches sont en anglais, à la racine."""
    lb = LABEL[lang]
    return (f'<div class="srch" role="search"><button type="button" class="srch-b" aria-label="{lb}" aria-expanded="false">{ICON}</button>'
            f'<div class="srch-p"><label class="srch-f">{ICON}<input type="search" placeholder="{lb}" aria-label="{lb}" '
            f'autocomplete="off" spellcheck="false" data-root="/"></label><ul class="srch-r" role="listbox" aria-label="Results"></ul></div></div>'
            f'<script src="{root}assets/search.js" defer></script>')

JS = r'''(function(){
  var box=document.querySelector('.srch');if(!box)return;
  var btn=box.querySelector('.srch-b'),inp=box.querySelector('input'),out=box.querySelector('.srch-r'),root=inp.getAttribute('data-root')||'/',idx=null,sel=-1;
  function fold(s){return (s||'').normalize('NFD').replace(/[̀-ͯ]/g,'').toLowerCase();}
  function load(){if(idx)return Promise.resolve(idx);return fetch(root+'assets/search-index.json').then(function(r){return r.json();}).then(function(j){idx=j.map(function(x){x.f=fold(x.n);return x;});return idx;});}
  function esc(s){return s.replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
  function render(q){
    var f=fold(q.trim());sel=-1;
    if(f.length<2){out.innerHTML='';return;}
    load().then(function(ix){
      var hits=ix.filter(function(x){return x.f.indexOf(f)>=0;}).sort(function(a,b){
        var pa=a.f.indexOf(f)===0?0:1,pb=b.f.indexOf(f)===0?0:1;if(pa!==pb)return pa-pb;
        if(a.t!==b.t)return a.t==='c'?-1:1;return (a.r||999)-(b.r||999)||a.n.localeCompare(b.n);}).slice(0,8);
      out.innerHTML=hits.length?hits.map(function(x){
        var meta=x.t==='i'?'Investor · '+x.k+(x.k>1?' startups':' startup'):(x.r?'#'+x.r+' · ':'')+(x.c||'');
        return '<li><a role="option" href="'+root+(x.t==='i'?'investor/':'company/')+x.s+'/"><b>'+esc(x.n)+'</b><small>'+esc(meta)+'</small></a></li>';
      }).join(''):'<li class="none">No startup or investor found</li>';
    });
  }
  inp.addEventListener('input',function(){render(inp.value);});
  inp.addEventListener('focus',load);
  inp.addEventListener('keydown',function(ev){
    var as=out.querySelectorAll('a');if(!as.length)return;
    if(ev.key==='ArrowDown'||ev.key==='ArrowUp'){ev.preventDefault();sel=(sel+(ev.key==='ArrowDown'?1:-1)+as.length)%as.length;
      as.forEach(function(a,i){a.setAttribute('aria-selected',i===sel?'true':'false');});as[sel].scrollIntoView({block:'nearest'});}
    else if(ev.key==='Enter'){ev.preventDefault();location.href=(as[sel>=0?sel:0]).href;}
    else if(ev.key==='Escape'){out.innerHTML='';box.classList.remove('open');btn.setAttribute('aria-expanded','false');}
  });
  btn.addEventListener('click',function(){var o=box.classList.toggle('open');btn.setAttribute('aria-expanded',o);if(o){inp.focus();}});
  document.addEventListener('click',function(ev){if(!box.contains(ev.target)){out.innerHTML='';if(box.classList.contains('open')){box.classList.remove('open');btn.setAttribute('aria-expanded','false');}}});
})();
'''

def write_js():
    p = os.path.join(ROOT, 'assets', 'search.js')
    old = open(p, encoding='utf-8').read() if os.path.exists(p) else None
    if old != JS:
        open(p, 'w', encoding='utf-8', newline='\n').write(JS)

def sync_css(path):
    """Recopie SEARCH_CSS dans la feuille de style des marchés, entre les marqueurs (ajouté en fin de fichier la première fois)."""
    s = open(path, encoding='utf-8').read()
    block = f'{START}\n{SEARCH_CSS}{END}\n'
    if START in s:
        new = s[:s.index(START)] + block + s[s.index(END) + len(END) + 1:]
    else:
        new = s.rstrip('\n') + '\n' + block
    if new != s:
        open(path, 'w', encoding='utf-8', newline='\n').write(new)
