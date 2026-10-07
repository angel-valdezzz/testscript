(()=>{
 const root=document.querySelector('.ts-product');
 if(!root)return;
 const reduce=matchMedia('(prefers-reduced-motion: reduce)').matches;
 if(!reduce){let pending=false;root.addEventListener('pointermove',e=>{if(pending)return;pending=true;requestAnimationFrame(()=>{const r=root.getBoundingClientRect();root.style.setProperty('--mx',`${e.clientX-r.left}px`);root.style.setProperty('--my',`${e.clientY-r.top}px`);pending=false;});});}
 for(const button of root.querySelectorAll('[data-copy]'))button.addEventListener('click',async()=>{try{await navigator.clipboard.writeText(button.dataset.copy);button.textContent='✓';button.setAttribute('aria-label',root.dataset.lang==='es'?'Copiado':'Copied');setTimeout(()=>{button.textContent='⧉';},1600);}catch{button.textContent='!';button.setAttribute('aria-label',root.dataset.lang==='es'?'Selecciona el comando para copiarlo':'Select the command to copy it');}});
 const tabs=[...root.querySelectorAll('[role=tab]')];
 function select(tab){for(const item of tabs){const active=item===tab;item.setAttribute('aria-selected',active);item.tabIndex=active?0:-1;document.getElementById(item.getAttribute('aria-controls')).hidden=!active;}}
 for(const tab of tabs){tab.addEventListener('click',()=>select(tab));tab.addEventListener('keydown',e=>{let index=tabs.indexOf(tab);if(e.key==='ArrowRight')index=(index+1)%tabs.length;else if(e.key==='ArrowLeft')index=(index+tabs.length-1)%tabs.length;else if(e.key==='Home')index=0;else if(e.key==='End')index=tabs.length-1;else return;e.preventDefault();select(tabs[index]);tabs[index].focus();});}
})();
