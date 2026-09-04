/* Shared helpers for every simulation on the site. Real AES via Web Crypto. */

const hex = b => [...new Uint8Array(b)].map(x => x.toString(16).padStart(2,'0')).join('');
const bytes = s => new TextEncoder().encode(s);
const text  = b => new TextDecoder().decode(b);

async function aesKey(raw){
  return crypto.subtle.importKey('raw', raw, {name:'AES-CBC'}, false, ['encrypt','decrypt']);
}
/* Deterministic demo key so results are reproducible and never secret. */
async function demoKeyBytes(seed='evil-encryption-academy'){
  return new Uint8Array(await crypto.subtle.digest('SHA-256', bytes(seed)));
}
async function aesCBC(data, keyRaw, ivRaw){
  const k = await aesKey(keyRaw);
  const iv = ivRaw || new Uint8Array(16);
  return new Uint8Array(await crypto.subtle.encrypt({name:'AES-CBC', iv}, k, data));
}
/* Web Crypto deliberately omits ECB. Encrypting each 16-byte block with a
   zero IV is mathematically identical to ECB, so we can demonstrate the real
   failure mode rather than a mock-up. */
async function aesECB(data, keyRaw){
  const k = await aesKey(keyRaw), zero = new Uint8Array(16);
  const out = new Uint8Array(data.length);
  for(let i=0;i<data.length;i+=16){
    const blk = data.slice(i, i+16);
    const enc = new Uint8Array(await crypto.subtle.encrypt({name:'AES-CBC', iv:zero}, k, blk));
    out.set(enc.slice(0,16), i);
  }
  return out;
}
function shannon(u8){
  if(!u8.length) return 0;
  const c = new Array(256).fill(0);
  for(const b of u8) c[b]++;
  let h = 0;
  for(const n of c){ if(n){ const p = n/u8.length; h -= p*Math.log2(p); } }
  return h;
}
function distinctBlocks(u8, size=16){
  const s = new Set();
  for(let i=0;i+size<=u8.length;i+=size) s.add(hex(u8.slice(i,i+size)));
  return s.size;
}
function hexdump(u8, limit=64){
  let o='';
  for(let i=0;i<Math.min(u8.length,limit);i+=16){
    const c=[...u8.slice(i,i+16)];
    o+=c.map(b=>b.toString(16).padStart(2,'0')).join(' ').padEnd(47)+'  |'+
       c.map(b=>b>=32&&b<127?String.fromCharCode(b):'.').join('')+'|\n';
  }
  return o.trimEnd();
}
/* Byte-frequency histogram. Flat = random-looking. Spiky = structured. */
function histogram(u8, buckets=32, height=5){
  const c=new Array(buckets).fill(0), span=256/buckets;
  for(const b of u8) c[Math.floor(b/span)]++;
  const peak=Math.max(...c)||1; let rows=[];
  for(let l=height;l>0;l--)
    rows.push('|'+c.map(v=>(v/peak*height>=l?'█':' ')).join('')+'|');
  rows.push('+'+'-'.repeat(buckets)+'+');
  return rows.join('\n');
}
/* Mobile nav */
document.addEventListener('DOMContentLoaded',()=>{
  const b=document.querySelector('.menu-btn'), s=document.querySelector('.side');
  if(b&&s) b.addEventListener('click',()=>s.classList.toggle('open'));
});
