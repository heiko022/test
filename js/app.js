const $ = (s, r=document) => r.querySelector(s);
const $$ = (s, r=document) => [...r.querySelectorAll(s)];

let CONCEPTS = [], POSTS = [];

const img = c => `concepts/${c.folder}/image-01.png`;

function renderStats(){
  const imgs = POSTS.reduce((n,p)=>n+1,0);           // 30 posts
  const gifs = CONCEPTS.length;
  const reels = CONCEPTS.length;
  const im = CONCEPTS.length*3;
  $("#st-concepts").textContent = CONCEPTS.length;
  $("#st-posts").textContent = POSTS.length;
  $("#st-reels").textContent = reels;
  $("#st-gifs").textContent = gifs;
  $("#st-images").textContent = im;
}

function cardsHTML(list){
  return list.map(c => `
    <article class="card" data-id="${c.id}" onclick="openDetail(${c.id})">
      <div class="cover" style="background-image:url('${img(c)}')">
        <span class="badge">${String(c.id).padStart(2,'0')}</span>
      </div>
      <div class="body">
        <h3>${c.name}</h3>
        <div class="handle">@${c.handle}</div>
        <p>${c.desc}</p>
        <div class="meta">
          <span>${c.frequenz}</span>
          <span>3 Posts</span>
        </div>
        <div class="arrow">Konzept öffnen →</div>
      </div>
    </article>`).join("");
}

function renderGrid(filter){
  let list = CONCEPTS;
  if(filter && filter!=="all") list = CONCEPTS.filter(c=>c.niche.toLowerCase().includes(filter.toLowerCase()));
  $("#grid").innerHTML = list.length ? cardsHTML(list)
    : `<p style="color:var(--mut);grid-column:1/-1;text-align:center;padding:40px">Kein Konzept zur Nische "${filter}" gefunden.</p>`;
}

function tabsHTML(){
  const niches = [...new Set(CONCEPTS.map(c=>c.niche.split("&")[0].trim().split(" ")[0]))];
  const all = ["all", ...niches];
  $("#tabs").innerHTML = all.map(n=>`<button class="tab ${n==="all"?"active":""}" data-f="${n}">${n==="all"?"Alle":n}</button>`).join("");
  $$("#tabs .tab").forEach(t=>t.onclick=()=>{
    $$("#tabs .tab").forEach(x=>x.classList.remove("active"));
    t.classList.add("active");
    renderGrid(t.dataset.f);
  });
}

/* ---------- detail ---------- */
function openDetail(id){
  const c = CONCEPTS.find(x=>x.id===id);
  const posts = POSTS.filter(p=>p.handle===c.handle);
  window.scrollTo(0,0);
  $("#concepts").style.display="none";
  $("#detail").classList.add("active");
  $("#detail").innerHTML = detailHTML(c, posts);
}

function closeDetail(){
  $("#detail").classList.remove("active");
  $("#concepts").style.display="block";
}

function detailHTML(c, posts){
  const imgc = i => `concepts/${c.folder}/image-0${i}.png`;
  return `
  <div class="back"><button onclick="closeDetail()">← Zurück zur Übersicht</button></div>
  <div class="chead">
    <div class="cavatar">${String(c.id).padStart(2,'0')}</div>
    <div class="cinfo">
      <h2>${c.name}</h2>
      <div class="handle">@${c.handle}</div>
      <div class="niche">${c.niche}</div>
      <p class="desc">${c.desc}</p>
      <div class="pills">
        <span class="pill"><b>Zielgruppe:</b> ${c.zielgruppe}</span>
        <span class="pill"><b>Frequenz:</b> ${c.frequenz}</span>
      </div>
    </div>
  </div>

  <div class="block"><h3><span class="ic">🖼</span> Beispielbilder</h3>
    <div class="gal">
      ${[1,2,3].map(i=>`<div><img src="${imgc(i)}" loading="lazy" onclick="zoom('${imgc(i)}')"><div class="lbl">image-0${i}.png</div></div>`).join("")}
    </div>
  </div>

  <div class="block"><h3><span class="ic">▶</span> GIF & Reel</h3>
    <div class="duo">
      <div class="hub">
        <img src="concepts/${c.folder}/animation-01.gif" alt="animiertes GIF">
        <div class="lbl">animation-01.gif (animiert)</div>
      </div>
      <div class="hub">
        <video src="concepts/${c.folder}/reel-01.mp4" controls preload="metadata"></video>
        <div class="lbl">reel-01.mp4 · 9:16 · ~20s</div>
      </div>
    </div>
  </div>

  <div class="block"><h3><span class="ic">💬</span> Content-Strategie</h3>
    <div class="kmeta">
      <div class="kbox"><div class="t">Content-Pillars</div><ul>${c.strategie.map(s=>`<li>${s}</li>`).join("")}</ul></div>
      <div class="kbox"><div class="t">Monetarisierung</div><div class="v">${c.monetarisierung}</div></div>
      <div class="kbox"><div class="t">Automatisierung</div><div class="v">${c.automatisierung}</div></div>
      <div class="kbox"><div class="t">Risiken</div><div class="v">${c.risiken}</div></div>
      <div class="kbox"><div class="t">Tools</div><div class="v">${c.tools}</div></div>
    </div>
  </div>

  <div class="block"><h3><span class="ic">📝</span> Beispiel-Posts & Captions</h3>
    ${posts.slice(0,3).map(p=>postHTML(p, c)).join("")}
  </div>`;
}

function postHTML(p, c){
  return `<div class="post">
    <div class="pt"><span class="pnum">POST ${String(p.post).padStart(2,'0')}</span><h4>${p.titel}</h4></div>
    <div class="hook">🎯 ${p.hook}</div>
    <div class="cap">${p.caption}</div>
    <div class="tags">${p.hashtags.split(/\s+/).map(h=>`<span>${h}</span>`).join("")}</div>
    <div class="files">📁 ${p.image} · ${p.gif} · ${p.reel}</div>
  </div>`;
}

function zoom(src){
  $("#lightbox").src = src;
  $("#lbwrap").classList.add("show");
}
function closeZoom(){ $("#lbwrap").classList.remove("show"); }

function init(){
  Promise.all([
    fetch("content/concepts.json").then(r=>r.json()),
    fetch("content/posts.json").then(r=>r.json())
  ]).then(([concepts, bundle])=>{
    CONCEPTS = concepts;
    POSTS = bundle.posts || bundle;
    renderStats();
    tabsHTML();
    renderGrid("all");
  }).catch(e=>{ $("#grid").innerHTML = `<p style="color:#ff6b6b;padding:30px;text-align:center">Konnte Daten nicht laden: ${e.message}</p>`; });
}
document.addEventListener("DOMContentLoaded", init);
