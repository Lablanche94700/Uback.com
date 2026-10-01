# -*- coding: utf-8 -*-
"""Mesure d'audience (Google Analytics 4) soumise au consentement, commune à toutes les pages.
HEAD : un seul <script> à placer dans le <head> de chaque page générée (homepage et pages globales, pages pays, segments,
familles, zones). Règles (CNIL) :
- rien n'est chargé chez Google tant que le visiteur n'a pas cliqué sur « Accepter » (aucun appel, aucun cookie) ;
- « Refuser » est aussi simple qu'« Accepter » ; ignorer le bandeau vaut refus ;
- le choix est gardé 6 mois (localStorage), puis redemandé ; un lien « Cookies » du pied de page (data-cookies) rouvre
  le bandeau ; un refus après un accord efface les cookies _ga.
Textes en anglais ou en français selon <html lang>. Mentions légales : section « Cookies » (tools/pages_global.py)."""
import json

GA_ID = 'G-CDF2KWM08X'          # propriété « uback.com », compte Analytics « Uback » (contact@dealing-room.com)
KEY, MONTHS = 'uback-consent', 6

TXT = {
 'en': dict(t='Uback measures its audience with Google Analytics, only if you agree. No advertising, no data sold.',
            more='Details', yes='Accept', no='Refuse', legal='/legal-notice.html#cookies'),
 'fr': dict(t='Uback mesure son audience avec Google Analytics, seulement si vous l’acceptez. Pas de publicité, aucune donnée vendue.',
            more='En savoir plus', yes='Accepter', no='Refuser', legal='/mentions-legales.html#cookies'),
}

CSS = ('#ck{position:fixed;left:16px;right:16px;bottom:16px;z-index:1000;max-width:720px;margin:0 auto;display:flex;flex-wrap:wrap;'
       'align-items:center;gap:12px 20px;padding:16px 18px;background:#fff;border:1px solid #E4E8EE;border-top:3px solid #C8A052;'
       'border-radius:12px;box-shadow:0 10px 30px rgba(30,58,95,.18);font:14px/1.5 Inter,system-ui,sans-serif;color:#1E3A5F}'
       '#ck p{flex:1 1 300px;margin:0}#ck a{color:#1E3A5F;text-decoration:underline}'
       '#ck .b{display:flex;gap:8px}#ck button{min-height:40px;padding:0 18px;border-radius:10px;font:600 14px Inter,system-ui,sans-serif;'
       'cursor:pointer;border:1.5px solid #1E3A5F;background:#fff;color:#1E3A5F}#ck button.y{background:#1E3A5F;color:#fff}')

JS = '''(function(){
var ID=@ID@, K=@KEY@, MAX=@MAX@*864e5, T=@TXT@;
var L=(document.documentElement.lang||'en').slice(0,2)==='fr'?T.fr:T.en;
function get(){try{var v=JSON.parse(localStorage.getItem(K)||'null');return v&&Date.now()-v.t<MAX?v.c:null;}catch(e){return null;}}
function set(c){try{localStorage.setItem(K,JSON.stringify({c:c,t:Date.now()}));}catch(e){}}
var loaded=false;
function load(){if(loaded)return;loaded=true;
  window.dataLayer=window.dataLayer||[];window.gtag=function(){dataLayer.push(arguments);};
  gtag('js',new Date());gtag('config',ID);
  var s=document.createElement('script');s.async=true;s.src='https://www.googletagmanager.com/gtag/js?id='+ID;document.head.appendChild(s);}
function wipe(){document.cookie.split(';').forEach(function(c){var n=c.split('=')[0].trim();if(n.indexOf('_ga')===0){
  ['','.uback.com','uback.com'].forEach(function(d){document.cookie=n+'=; Max-Age=0; path=/'+(d?'; domain='+d:'');});}});}
function hide(){var b=document.getElementById('ck');if(b)b.remove();}
function show(){if(document.getElementById('ck'))return;
  var b=document.createElement('div');b.id='ck';b.setAttribute('role','dialog');b.setAttribute('aria-label','Cookies');
  var st=document.createElement('style');st.textContent=@CSS@;b.appendChild(st);
  var p=document.createElement('p');p.textContent=L.t+' ';var a=document.createElement('a');a.href=L.legal;a.textContent=L.more;p.appendChild(a);
  var w=document.createElement('div');w.className='b';
  var no=document.createElement('button');no.type='button';no.textContent=L.no;
  var yes=document.createElement('button');yes.type='button';yes.className='y';yes.textContent=L.yes;
  no.onclick=function(){set('denied');wipe();hide();};yes.onclick=function(){set('granted');hide();load();};
  w.appendChild(no);w.appendChild(yes);b.appendChild(p);b.appendChild(w);document.body.appendChild(b);}
var c=get();
if(c==='granted')load();
document.addEventListener('DOMContentLoaded',function(){
  if(!c)show();
  document.querySelectorAll('[data-cookies]').forEach(function(el){el.addEventListener('click',function(ev){ev.preventDefault();show();});});});
})();'''

HEAD = '<script>' + (JS.replace('@ID@', json.dumps(GA_ID)).replace('@KEY@', json.dumps(KEY)).replace('@MAX@', str(MONTHS * 30))
                     .replace('@TXT@', json.dumps(TXT, ensure_ascii=False)).replace('@CSS@', json.dumps(CSS))) + '</script>'
