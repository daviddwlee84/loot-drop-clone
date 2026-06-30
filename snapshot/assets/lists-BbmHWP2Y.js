import"./modulepreload-polyfill-B5Qt9EMX.js";/* empty css              */import{T as i}from"./top10data-bqRFPz5T.js";let p="cause_no_market",o=new Set(["cause-of-death"]);const E=document.getElementById("folder-tree"),y=document.getElementById("cards-container"),b=document.getElementById("analysis-section"),L=document.getElementById("list-title"),g=document.getElementById("list-subtitle"),h=document.getElementById("mobile-title"),v=document.getElementById("hamburger-btn"),w=document.getElementById("sidebar-close"),c=document.getElementById("folder-sidebar"),u=document.getElementById("drawer-overlay"),r=document.getElementById("back-to-top");function $(){m(),f(p),x(),S()}function m(){let e="";i.categories.forEach(t=>{const s=o.has(t.id),n=s?"📂":"📁";e+=`
      <div class="tree-category">
        <button class="category-header ${s?"expanded":""}" data-category-id="${t.id}">
          <span class="folder-emoji">${n}</span>
          <span class="category-name">${t.name}</span>
          <span class="expand-icon">▼</span>
        </button>
        <div class="category-items ${s?"expanded":""}">
          ${t.lists.map(a=>`
            <button class="list-item ${p===a.id?"active":""}" data-list-id="${a.id}">
              <span class="list-icon">${a.icon||"📄"}</span>
              <span class="list-name">${a.name}</span>
            </button>
          `).join("")}
        </div>
      </div>
    `}),E.innerHTML=e,document.querySelectorAll(".category-header").forEach(t=>{t.addEventListener("click",()=>{const s=t.dataset.categoryId;T(s)})}),document.querySelectorAll(".list-item").forEach(t=>{t.addEventListener("click",()=>{const s=t.dataset.listId;k(s)})})}function T(e){o.has(e)?o.delete(e):o.add(e),m()}function k(e){p=e,m(),f(e),l()}function f(e){const t=i.lists[e];if(!t){y.innerHTML="<p>List not found.</p>";return}L.textContent=t.title,g.textContent=t.subtitle,h.textContent=t.title;let s="";s+=`<div class="list-slug-badge">📁 ${t.slug}</div>`,t.items.forEach(n=>{s+=I(n)}),y.innerHTML=s,B(e),document.querySelectorAll(".read-more-btn").forEach(n=>{n.addEventListener("click",a=>{a.preventDefault();const d=n.dataset.startupName;window.location.href=`/?search=${encodeURIComponent(d)}`})})}function I(e){return`
    <article class="tldr-card">
      <!-- Header Row: Rank | Name (with country) | Stat Pills -->
      <div class="card-header-row">
        <div class="card-rank-badge">${e.rank}</div>
        <div class="card-name-group">
          <h2 class="card-startup-name">${e.name}</h2>
          ${e.country?`<span class="card-country">${e.country}</span>`:""}
        </div>
        <div class="card-stat-pills">
          <div class="stat-pill burned">
            <span class="stat-pill-label">BURNED</span>
            <span class="stat-pill-value">${e.lootLost}</span>
          </div>
          <div class="stat-pill lived">
            <span class="stat-pill-label">LIVED</span>
            <span class="stat-pill-value">${e.livedYears}</span>
          </div>
          <div class="stat-pill cause">
            <span class="stat-pill-label">CAUSE</span>
            <span class="stat-pill-value">${e.causeTag}</span>
          </div>
        </div>
      </div>
      
      <!-- Body: Off-white background with sections -->
      <div class="card-body-section">
        <div class="body-section">
          <div class="body-section-label">THE VALUE PROPOSITION</div>
          <p class="body-section-text">${e.valueProp}</p>
        </div>
        
        <hr class="card-divider">
        
        <div class="body-section">
          <div class="body-section-label">CAUSE OF DEATH</div>
          <p class="body-section-text">${e.causeOfDeath}</p>
        </div>
      </div>
      
      <!-- TL;DR Footer: Yellow bar -->
      <div class="card-tldr-footer">
        <span class="tldr-label">tl;dr</span>
        <span class="tldr-text">${e.tldr}</span>
      </div>
    </article>
  `}function B(e){let t=null;for(const a of i.categories)if(a.lists.some(d=>d.id===e)){t=a.id;break}const s=i.analysis[t]||i.analysis.default;if(!s){b.innerHTML="";return}const n=s.takeaways.map(a=>`
        <li class="takeaway-item">
            <span class="takeaway-icon">${a.icon}</span>
            <span class="takeaway-text">${a.text}</span>
        </li>
    `).join("");b.innerHTML=`
        <article class="analysis-card">
            <div class="analysis-header">POST-MORTEM ANALYSIS</div>
            <h2 class="analysis-title">${s.title}</h2>
            
            <div class="analysis-content">
                <p><strong>The Common Denominator:</strong> ${s.denominator}</p>
                <p><strong>What to Learn:</strong> ${s.learnings}</p>
            </div>
            
            <div class="takeaway-box">
                <div class="takeaway-title">KEY OVERALL TAKEAWAYS</div>
                <ul class="takeaway-list">
                    ${n}
                </ul>
            </div>
        </article>
    `}function A(){c.classList.add("open"),u.classList.add("active"),v.classList.add("active"),document.body.style.overflow="hidden"}function l(){c.classList.remove("open"),u.classList.remove("active"),v.classList.remove("active"),document.body.style.overflow=""}function S(){window.addEventListener("scroll",()=>{window.scrollY>500?r.classList.add("visible"):r.classList.remove("visible")}),r.addEventListener("click",()=>{window.scrollTo({top:0,behavior:"smooth"})})}function x(){v.addEventListener("click",()=>{c.classList.contains("open")?l():A()}),w.addEventListener("click",l),u.addEventListener("click",l),document.addEventListener("keydown",e=>{e.key==="Escape"&&c.classList.contains("open")&&l()})}document.addEventListener("DOMContentLoaded",$);
