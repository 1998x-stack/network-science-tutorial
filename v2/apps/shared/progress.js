(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;root.NetsciProgress=api;})(typeof globalThis!=='undefined'?globalThis:this,function(){
 'use strict';
 const PREFIX='network-science-tutorial:v1:'; // Preserve earlier localStorage keys on same origin.
 function chapterFile(number){return String(number).padStart(2,'0')+'.html';}
 function safeGet(storage,key){try{return storage.getItem(PREFIX+key);}catch(_){return null;}}
 function safeSet(storage,key,value){try{storage.setItem(PREFIX+key,value);return true;}catch(_){return false;}}
 function completed(storage,number){return safeGet(storage,'done:'+chapterFile(number))==='1';}
 function mark(storage,number,value){return safeSet(storage,'done:'+chapterFile(number),value?'1':'0');}
 function count(storage,chapters){return chapters.filter(c=>completed(storage,c.num)).length;}
 function resume(storage){const x=safeGet(storage,'last');return /^[0-9]{2}\.html$/.test(x||'')?x.slice(0,2):null;}
 function setLast(storage,number){return safeSet(storage,'last',chapterFile(number));}
 return {chapterFile,completed,mark,count,resume,setLast};
});
