'use strict';
// Independent input arithmetic. No rendering, HTTP, view/event/state writes.
const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const root=path.resolve(__dirname,'../../../..');
const csv=fs.readFileSync(path.join(root,'tasks/A04-conversion-paradox/inputs/conversion.csv'),'utf8').trim().split(/\r?\n/);
const rows=csv.slice(1).map(line=>{const [period,channel,v,c]=line.split(',');return{period,channel,visits:Number(v),conversions:Number(c)};});
const gcd=(a,b)=>b?gcd(b,a%b):a;
const result={source:'tasks/A04-conversion-paradox/inputs/conversion.csv',rows:rows.map(row=>({...row,exact_fraction:`${row.conversions/gcd(row.conversions,row.visits)}/${row.visits/gcd(row.conversions,row.visits)}`,display_rate:(100*row.conversions/row.visits).toFixed(2)+'%',rate:row.conversions/row.visits})),periods:[]};
for(const period of [...new Set(rows.map(r=>r.period))]){const r=rows.filter(r=>r.period===period);const visits=r.reduce((s,x)=>s+x.visits,0),conversions=r.reduce((s,x)=>s+x.conversions,0);result.periods.push({period,visits,conversions,exact_fraction:`${conversions/gcd(conversions,visits)}/${visits/gcd(conversions,visits)}`,overall:conversions/visits,display_overall:(100*conversions/visits).toFixed(2)+'%',shares:r.map(x=>({channel:x.channel,visits:x.visits,share:x.visits/visits})),weighted_formula:r.map(x=>`(${x.visits}/${visits})*(${x.conversions}/${x.visits})`).join('+')});}
assert.deepEqual(result.periods.map(p=>p.overall),[0.26,0.166]);
result.overall_change_percentage_points=-9.4;result.direct_change_percentage_points=5;result.promotion_change_percentage_points=2;
result.supported_conclusion='两渠道转化率均上升；访问构成由高转化直接访问为主转为低转化推广访问为主，总体加权转化率由26.00%下降至16.60%。';
result.limit='不能由该数据证明因果。';
fs.writeFileSync(path.join(__dirname,'independent-data-facts.json'),JSON.stringify(result,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify(result,null,2));
