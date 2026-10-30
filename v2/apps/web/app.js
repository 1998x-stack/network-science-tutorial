(function(){
'use strict';
const list=globalThis.NETSCI_CURRICULUM?.chapters||[], P=globalThis.NetsciProgress;
const storage=(()=>{try{return localStorage;}catch{return {getItem(){return null},setItem(){}};}})();
const search=document.getElementById('search'), count=document.getElementById('progress-count'), cards=[...document.querySelectorAll('.lesson')];
let group='全部';
function refresh(){let n=0;for(const card of cards){const q=(search?.value||'').trim().toLocaleLowerCase(),match=(group==='全部'||card.dataset.group===group)&&card.textContent.toLocaleLowerCase().includes(q);card.hidden=!match;if(match)n++;}
 if(count)count.textContent=`已完成 ${P.count(storage,list)} / ${list.length} 章 · 当前显示 ${n} 章`;
 const empty=document.getElementById('no-results');if(empty)empty.hidden=n!==0;
}
for(const card of cards){const num=card.dataset.number,check=card.querySelector('input[type=checkbox]');check.checked=P.completed(storage,num);check.addEventListener('change',()=>{P.mark(storage,num,check.checked);refresh();});card.querySelector('.open-lesson').addEventListener('click',()=>P.setLast(storage,num));}
for(const button of document.querySelectorAll('[data-filter]'))button.addEventListener('click',()=>{group=button.dataset.filter;for(const b of document.querySelectorAll('[data-filter]'))b.setAttribute('aria-pressed',String(b===button));refresh();});
search?.addEventListener('input',refresh);
const previous=P.resume(storage),resume=document.getElementById('resume');if(previous&&resume){resume.href=`lessons/${previous}.html`;resume.hidden=false;}
refresh();
})();
