const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const base=path.resolve('tmp/20261002-204314-6f31'),out=path.join(base,'A17','independent-analysis');fs.mkdirSync(out,{recursive:true});
const decode=s=>s.replace(/&#x([0-9a-f]+);/gi,(_,n)=>String.fromCodePoint(parseInt(n,16))).replace(/&#([0-9]+);/g,(_,n)=>String.fromCodePoint(+n)).replace(/&quot;/g,'"').replace(/&apos;|&#39;/g,"'").replace(/&lt;/g,'<').replace(/&gt;/g,'>').replace(/&nbsp;/g,' ').replace(/&amp;/g,'&');
const strip=s=>decode((s.match(/<article\b[^>]*>([\s\S]*?)<\/article>/)?.[1]||s).replace(/<script[\s\S]*?<\/script>/gi,'').replace(/<style[\s\S]*?<\/style>/gi,'').replace(/<\/(p|h[1-6]|li|tr|pre|section)>/gi,'\n').replace(/<br\s*\/?\s*>/gi,'\n').replace(/<[^>]+>/g,' ').replace(/[ \t]+/g,' ').replace(/ *\n */g,'\n').trim());
const entries=[
['guide','https://open-snapshot.muedsa.com/ai-guide.md','_suite/shared-doc-000001-response.txt'],
['parser','https://snapshot.muedsa.com/guides/parser/','_suite/shared-doc-000003-response.txt'],
['layout','https://snapshot.muedsa.com/guides/layout/','_suite/shared-doc-000005-response.txt'],
['tags','https://snapshot.muedsa.com/reference/parser-tags/','_suite/shared-doc-000004-response.txt'],
['text','https://snapshot.muedsa.com/widgets/text/text/','A11/requests/A11-request-000001/response.txt'],
['rich-text','https://snapshot.muedsa.com/widgets/text/rich-text/','A11/requests/A11-request-000002/response.txt'],
['backdrop-filter','https://snapshot.muedsa.com/widgets/painting/backdrop-filter/','_suite/requests/shared-request-000001/response.txt'],
['image-filtered','https://snapshot.muedsa.com/widgets/painting/image-filtered/','A10/requests/A10-request-000002/response.txt'],
['fonts','https://open-snapshot.muedsa.com/fonts','_suite/shared-fonts-000001-response.txt']];
let manifest=[];for(const [name,url,rel] of entries){const source=path.join(base,rel),bytes=fs.readFileSync(source),text=bytes.toString('utf8');const readable=path.join(out,`official-${name}-readable-v001.txt`);fs.writeFileSync(readable,text.includes('<!DOCTYPE html')||text.includes('<html')?strip(text):text,{flag:'wx'});manifest.push({name,url,source_cache:source,source_sha256:crypto.createHash('sha256').update(bytes).digest('hex'),readable_path:readable,reused:true,new_http_request:false});}
fs.writeFileSync(path.join(out,'official-cache-manifest-v001.json'),JSON.stringify({prepared_at:new Date().toISOString(),scope:'Actual preserved official responses; no new HTTP request. Reading requires opening extracted text, not inferred by this script.',sources:manifest},null,2),{flag:'wx'});console.log(JSON.stringify(manifest,null,2));
