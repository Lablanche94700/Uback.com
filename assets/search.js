(function(){
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
