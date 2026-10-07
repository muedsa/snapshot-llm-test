const fs=require('node:fs'),path=require('node:path'),s=require('../../_suite/suite.cjs');const base=path.resolve(__dirname,'..'),wx=(p,x)=>fs.writeFileSync(p,JSON.stringify(x,null,2)+'\n',{flag:'wx'});
const observation='实际打开十图接触表后整集审查通过：共同双补丁标志、纸色/墨蓝/陶土色、缝线与统一中英标题使项目可识别；招募、预约、导览、工具、评估、教学、取件、交换、月报、排班各有不同任务与构图。近读密集文案须用原尺寸，接触表仅检查体系与构图。单图内容与数据依已有真实原PNG查看记录，三处视觉问题已修正。';
const v=s.view('B02',path.join(__dirname,'contact-v001.png'),{tool:'view_image',reviewer:'root',purpose:'Whole ten-touchpoint collection review',observation});s.toolUsage('B02',{tool:'Python Pillow + functions.view_image',purpose:'Temporary contact preview and actual suite-coherence judgment; no final image bytes altered',input:path.join(__dirname,'selection-v001.json'),output:path.join(__dirname,'contact-v001.png'),view_id:v.id});
const selection=JSON.parse(fs.readFileSync(path.join(__dirname,'selection-v001.json')));
const judgments={
 'case-01':'标题远读、运营近读；补丁衬衣主张与招募三步完整。',
 'case-02':'预约的时间/费用/先评估条件完整，竖屏终端或平板近读，手机需放大；静态按钮无真实支付。',
 'case-03':'入口→签到→评估→入座连贯，示意图和体验时间吻合。',
 'case-04':'四类工具编号与数量匹配；归位闭合剪刀形态和文字一致。',
 'case-05':'三门判断含正负分支及不确定出口；基础体验和评估条件清楚。',
 'case-06':'四步针法有边缘余量/示例针距/完成检查，非比例练习图清楚。',
 'case-07':'取件编号、原物损伤位置、补丁方案、时间和养护一致。',
 'case-08':'六件独立演示织物均具材质/尺寸/瑕疵，交换规则一致。',
 'case-09':'9月接收48/完成44/待4与四周条形数据相符，91.7%正确；18h明确9月示例。',
 'case-10':'10月24日三岗位双班次有15分钟交接，数据不同于9月报告，文本与时间条清楚。'
};
const review={passed:true,actual_view_id:v.id,statement:observation,case_judgments:judgments,reviewed_at:new Date().toISOString(),unresolved_issues:[]};wx(path.join(__dirname,'collection-review-v001.json'),review);
wx(path.join(__dirname,'publish-manifest-v001.json'),{task_id:'B02',curatorial_statement:'再线 / RETHREAD：让旧织物回到社区日常。十件作品把发现、参与、学习、归还、交换、反馈与协作连成可使用的视觉生态。不同任务采用各自布局，纸色、双补丁标志与缝线保持身份。',cases:selection.cases,final_collection_review:review,independent_audit:path.join(base,'independent-audit','audit-final-v001.json'),report_notes:['额外项目简报、真正应用的设计系统、十触点映射见project-brief.md/design-system.json/touchpoint-map.json。所有运营/价格/人员/织物库存/日期/地址/服务数据均自拟演示。9月月报18h与10月24日班次27人时属于不同月份。','本次恢复核对并重新打开03/10/04三图，先前尚未落盘查看由摘要恢复为单独事件，原查看准确时刻不可得并已注明；重开和恢复事件均累计真实次数，不制造额外视觉修改。','本题无失败HTTP和429。工具脚本一次spawnSync EPERM已留存，改为同进程直接调用簿记函数恢复。完整visual三次：招募标题/说明裁剪修复，排班遮线修复，剪刀图文一致性修复。05/06首次提交前静态精修不计visual。'],resume_notes:'B02 ten independent touchpoints, actual full PNG reviews, actual collection review, additional project/system/map documents and independent audit complete. Continue B03.'});
s.taskCheckpoint('B02',{event_type:'collection-reviewed',visual_review_evidence:[v.id],resume_notes:'Whole collection passed actual contact review; awaiting independent audit and extra-document verification before publish.'});s.writeTaskMetrics('B02');console.log(v.id);
