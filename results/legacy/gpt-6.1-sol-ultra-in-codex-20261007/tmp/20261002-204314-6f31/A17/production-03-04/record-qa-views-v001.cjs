const fs=require('node:fs'),path=require('node:path'),s=require('../../_suite/suite.cjs');
const observations={
 '03-thumbnail':'实际打开600×800临时缩略：整体章节、16行代码、图示、下方卡和页脚视觉层级清楚，无整页内容越界。',
 '03-code':'实际打开650×593临时代码局部：16个完整真源行均可读，CDATA中的双空格、<A>、&，闭合符和BOLD属性完整；局部crop尾部只包含说明的一部分，完整说明已在原图检查。',
 '03-figure':'实际打开400×240临时图示局部：字面<A> & B完整，blue局部样式，FF/80红块与alpha标签完整，同独立例一致。',
 '04-thumbnail':'实际打开600×800 v002缩略：修短后源行号省略说明完整，16真源行、过滤输入对照和底部两卡清楚，左SHARP仍可辨，右明显柔化。',
 '04-code':'实际打开650×593 v002临时代码局部：16真源行不裁，BackdropFilter/ImageFiltered sigma3属性和SHARP原文完整。说明因QA本身crop宽度只展示部分，完整说明已在原图检查。',
 '04-figure':'实际打开400×240 v002图示局部：左前景字/深条锐利，右同字/深条模糊，外部BACKGROUND/SUBTREE清晰，剪裁外白底。'
};
const records=Object.entries(observations).map(([key,observation])=>{const [page,kind]=key.split('-'),image=path.join(__dirname,`handbook-${page}-${kind}-qa-v001.png`);return s.view('A17',image,{tool:'view_image',viewer:'a17_producer_03_04',case_id:'handbook-'+page,version_id:page==='03'?'A17-v001-handbook-03':'A17-v002-handbook-04',view_kind:'temporary_'+kind,observation});});
fs.writeFileSync(path.join(__dirname,'qa-view-records-v001.json'),JSON.stringify(records,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify(records.map(r=>r.id)));
