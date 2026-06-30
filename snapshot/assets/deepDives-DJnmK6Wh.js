import"./modulepreload-polyfill-B5Qt9EMX.js";/* empty css              */async function k(){const s=document.getElementById("dd-grid"),p=document.getElementById("dd-skipped");try{const e=await fetch("/data/product-type-articles.json");if(!e.ok)throw new Error("Failed to load articles data");const c=await e.json(),v=c.articles||{},n=Object.entries(v).sort((a,i)=>(i[1].meta?.count||0)-(a[1].meta?.count||0));if(n.length===0){s.innerHTML='<div class="dd-loading">No deep dives generated yet. Check back soon.</div>';return}s.innerHTML=n.map(([a,i])=>{const d=i.meta||{},o=d.codBreakdown||[],u=o[0]?.cause||"Unknown",m=o.slice(0,3),g=["bar-1","bar-2","bar-3"],b=m.map((r,f)=>{const $=parseFloat(r.percentage)||0;return`<div class="dd-bar-row">
                    <span class="dd-bar-label">${t(r.cause)}</span>
                    <div class="dd-bar-track"><div class="dd-bar-fill ${g[f]}" style="width:${Math.min($,100)}%"></div></div>
                    <span class="dd-bar-pct">${r.percentage}%</span>
                </div>`}).join("");return`
                <a href="/deep-dive/${a}" class="dd-card">
                    <div class="dd-card-header">
                        <span class="dd-card-icon">${d.icon||"📊"}</span>
                        <span class="dd-card-name">${t(d.name||a)}</span>
                    </div>
                    <div class="dd-card-title-section">
                        <div class="dd-card-failures">${d.count||0}</div>
                        <div class="dd-card-failures-label">FAILED STARTUPS</div>
                        <div class="dd-card-burned-badge">
                            <span class="dd-card-fire">🔥</span>
                            ${d.totalBurnedFormatted||"$0"}
                        </div>
                    </div>
                    <div class="dd-card-bars">
                        ${b}
                    </div>
                    <div class="dd-card-stats-row">
                        <div class="dd-card-stat-item">
                            <span class="dd-card-stat-value">${d.avgLifespan||"?"}yr</span>
                            <span class="dd-card-stat-label">AVG LIFE</span>
                        </div>
                        <div class="dd-card-stat-item">
                            <span class="dd-card-stat-value">${d.topSectors?.[0]?.split(" (")[0]||"—"}</span>
                            <span class="dd-card-stat-label">TOP SECTOR</span>
                        </div>
                    </div>
                    <div class="dd-card-footer">
                        <span class="dd-card-footer-killer">${t(u)}</span>
                        <span class="dd-card-footer-cta">READ &rarr;</span>
                    </div>
                </a>`}).join("");const l=c.skippedTypes||[];l.length>0&&(p.innerHTML=`
                <div class="dd-skipped">
                    <div class="dd-skipped-title">Categories with fewer than 3 failures (no deep dive yet)</div>
                    <div class="dd-skipped-list">
                        ${l.map(a=>`<span class="dd-skipped-item">${a.icon} ${t(a.name)} (${a.count})</span>`).join("")}
                    </div>
                </div>`)}catch(e){console.error("Failed to load deep dives:",e),s.innerHTML='<div class="dd-loading">Failed to load deep dives. Please try again later.</div>'}}function t(s){return s?String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;"):""}k();
