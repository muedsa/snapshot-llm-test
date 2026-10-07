const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const hash=b=>crypto.createHash('sha256').update(b).digest('hex'),workspace=path.resolve(__dirname,'../../../..'),base=path.resolve(__dirname,'..');fs.mkdirSync(__dirname,{recursive:true});
const rels=['tasks/B03-dsl-creative-frontier/TASK.md','tasks/B03-dsl-creative-frontier/AGENTS.md','tasks/B03-dsl-creative-frontier/task.json','tasks/B03-dsl-creative-frontier/run-config.json','tasks/B03-dsl-creative-frontier/inputs/README.md','tasks/B03-dsl-creative-frontier/templates/portfolio-template.json','tasks/B03-dsl-creative-frontier/templates/task-metrics-template.json','tasks/B03-dsl-creative-frontier/templates/snapshot-usage-template.md','run-config.json','tmp/20261002-204314-6f31/B03/plan-v001.json'];
const docs=[{id:'shared-doc-000001',url:'https://open-snapshot.muedsa.com/ai-guide.md',path:'tmp/20261002-204314-6f31/_suite/shared-doc-000001-response.txt',use:'UTF8纯文本POST/响应PNG原字节与错误Content-Type；本题只复用已取得的shared HTTP'},{id:'shared-doc-000004',url:'https://snapshot.muedsa.com/reference/parser-tags/',path:'tmp/20261002-204314-6f31/_suite/shared-doc-000004-readable.txt',use:'实际完整阅读的注册parser标签/属性参考；布局、渐变、矩阵、裁剪、透明度、滤镜、foreground文字轮廓'},{id:'shared-helper-readme',url:null,path:'tmp/20261002-204314-6f31/_suite/dsl-README.md',use:'仅字符串构造，不渲染；Transform矩形线段、纯DSL几何与文字盒需实图验证'}].map(d=>({...d,sha256:hash(fs.readFileSync(path.join(workspace,d.path))),access:'existing local cache reread; zero new HTTP'}));
const plan=JSON.parse(fs.readFileSync(path.join(base,'plan-v001.json'),'utf8'));
const requirements=[
 {id:'R01',rule:'至少10件独立完整主作品，每件有实际受众、观看环境、具体用户任务及完整内容；不能是标签/滤镜小方块示范板',evidence:'最终十件场景与源DSL、root逐图及整集审查，不仅比较hash'},
 {id:'R02',rule:'每件完整、自包含.snapshot通过实际服务渲染并保存原始响应PNG；最终文字、布局和主要视觉由DSL构造',evidence:'请求body/版本/响应SHA、PNG签名与尺寸、资产/后处理记录'},
 {id:'R03',rule:'技术组合应服务内容，不以标签复杂度为完成标准；文档支持、DSL实际存在与图像可见主张分开核对',evidence:'technique-notes逐件依据、实际tag/attribute、view observation与应用价值'},
 {id:'R04',rule:'每张成功响应需真实打开，发现问题则修改/渲染/再查看比较；不用固定迭代次数替代满足需求',evidence:'requests/views/iterations链、草稿失败保留；baseline、visual、syntax-fix/retry/alternative分开'},
 {id:'R05',rule:'交付technique-notes.md逐件说明独到手法、实际文档依据、试验/看图证据、应用价值与已确认边界',evidence:'每件记录引用实际cache版本、request/version/view和可见效果；未尝试的限制标文档所述而非本题实验'},
 {id:'R06',rule:'完成前实际审查整十件合集，内容可读、应用适配、作品独立且没有未解决明显缺陷',evidence:'root原PNG逐件记录及独立终审；接触表只补充整体比较'},
 {id:'R07',rule:'统一同run输出/临时目录；逐件final.png/final.snapshot/case.md及portfolio/本地gallery/usage/metrics完整',evidence:'发布配对、相对链接、索引、日志与额外文档'},
 {id:'R08',rule:'自拟信息标演示，公式/图表精确且与语义一致，真实费用/token未知填null；共享HTTP不重复记',evidence:'内容标识、数据/几何计算、指标来源、协作/请求墙钟区分'}
];
const constraints=[
 {capability:'Container gradients',documented:'gradientType=LINEAR/RADIAL/SWEEP；至少两色；stops与colors等长、0–1升序；类型专用参数不可混用；alpha在CSS颜色最后两位',audit:'检查实际属性和数值；读实际图的渐变层次而非据标签宣称效果。'},
 {capability:'Opacity',documented:'opacity范围0–1，整个子树透明度',audit:'区分子树Opacity与颜色alpha；内容文字如被包在透明层需实际读图。'},
 {capability:'Transform',documented:'列主序4×4共16有限Float，括号和逗号不得有空格；origin=(x,y)',audit:'检查算法/方向/接点与可见几何；变换绘制界可大于原Positioned盒，不能把未变换盒边界当画面溢出结论。'},
 {capability:'ClipRect/ClipOval/ClipRRect',documented:'独立裁剪支持；ClipRRect边角属性；ClipOval/ClipRRect默认ANTI_ALIAS，ClipRect默认HARD_EDGE',audit:'确认真实裁剪包裹子树与图上边界；不要把圆形容器等同于实际嵌套clip技术主张。'},
 {capability:'Container clipBehavior',documented:'非NONE裁剪需背景装饰作为路径，仅纯color不够',audit:'以独立clip或实际装饰路径成立，非凭设置属性成功假定裁剪。'},
 {capability:'ColorFiltered',documented:'必须color和Skia blendMode；边界可确定时限制作用范围，部分模式着色透明间隙',audit:'检查实际混合模式与子树，若本题没使用不计手法。'},
 {capability:'ImageFiltered',documented:'sigmaX/Y有限非负，可tileMode；Parser只提供高斯模糊；按sigma自动扩充模糊输出边界',audit:'只能声明本题实际高斯模糊，不能因标签叫ImageFiltered宣称其他滤镜；输出边界、裁剪以实图验证。'},
 {capability:'BackdropFilter',documented:'读取已画背景，高斯模糊；sigma有限非负；建议配合ClipRect/ClipOval/ClipRRect限定区域',audit:'检查绘制顺序、受滤背景和局部clip，玻璃主张需有可见背景差异与查看证据。'},
 {capability:'Text foreground outline',documented:'foregroundColor是foreground*前提；foregroundMode=FILL/STROKE/STROKE_AND_FILL及foregroundStrokeWidth等真实支持；textShadow支持多层',audit:'确认foregroundColor/Mode/StrokeWidth或阴影真实写入；实际服务图能看到轮廓/层差且活动信息可读。'},
 {capability:'Parser attribute validation',documented:'标签/属性区分大小写；未知属性被忽略',audit:'HTTP200不能独立证明新属性或视觉效果已实施；逐主张按文档、DSL、图三证核对。'}
];
const caseChecks={
 'case-01':['渐变/实际模糊/局部玻璃背景有文档和子树证据','夜间聆听活动时间/地点/参与方式完整，关键文字不受装饰模糊遮挡'],
 'case-02':['分枝叶脉为参数化DSL计算，ClipOval真实包裹标本窗口','种子标签和交换动作清楚，不以示意叶脉冒称实物/植物鉴定'],
 'case-03':['文字轮廓真实foregroundColor与STROKE属性，阴影或错位层可见','书展日期/地点/参加动作及正文可读，雕塑字不替代必要内容'],
 'case-04':['舷窗实际裁剪树与前后绘制层关系成立','三分区路径有顺序与到达位置，导览信息完整，不把景深效果当真实水族馆测量'],
 'case-05':['3:4映射同一循环12细分；两圈触点数量与角度、重合时刻精确','排练动作/数拍方法完整，静态图不声称发声或播放'],
 'case-06':['程序化等高线/半透明构图实际存在，元素数可承载','三站茶香体验路线顺序/时间/参与行动清楚，不冒称地形实测或气味生成'],
 'case-07':['折线/纸层/透光构造与实际制作步骤语义一致','材料/折叠/收尾/使用步骤完整，工具与光源说明适合课程内容'],
 'case-08':['向量场公式、正负方向与短流线算法一致；标为数学模型','观察问题能用图来回答，不把合成流场当实测气象/流体物理结论'],
 'case-09':['等轴测矩阵/正反面及遮挡顺序实际成立','微型城市展的日期/地点/参观用途完整，纸景不是外部整图素材'],
 'case-10':['波形包络由合成公式产生，三段时间与总长、静默段对应','聆听谱说明可执行且区分合成示意与实测声音；静默无误画信号']
};
const boundaryFile='tmp/20261002-204314-6f31/B01/requests/B01-request-000015/response.json',boundaryBytes=fs.readFileSync(path.join(workspace,boundaryFile)),error=JSON.parse(boundaryBytes);
const out={schema_version:1,task_id:'B03',run_id:plan.run_id,reviewer:'b01_independent_audit',created_at:new Date().toISOString(),scope:'已读任务与计划、官方缓存文档支持及逐件技术/实用性审查框架；不是已完成作品或最终终审',sources:rels.map(relative=>({path:relative,sha256:hash(fs.readFileSync(path.join(workspace,relative))),actual_read:true})),documents:docs,requirements,documented_capabilities:constraints,confirmed_shared_boundary:{element_limit:4096,source_response:boundaryFile,source_sha256:hash(boundaryBytes),http_status:400,error_message:error.message,server_request_id:error.requestId,scope:'B01实际服务确认，作为跨题复用知识；不是新增B03失败或HTTP'},cases:plan.cases.map(c=>({...c,review_checks:caseChecks[c.id]})),review_method:['按最终选择清单串接input/version/source DSL、原始PNG、request与root view hash和尺寸。','只为本题真正技术主张核参数/算法/数据/绘制顺序，不用标签数量评审创造力。','逐件实用性以受众/任务/观看环境及root原图实际读图为据；必要重点额外看图私有记账并导入。','technique-notes区分文档已支持、先前套件已遇边界、本题真实试验及尚未验证推测。','十新作品不复计B01/B02成品；本地画廊和正式输出在发布后核查。'],new_http_requests:0,actual_extra_image_views:0,unknown_platform_usage:{tokens:null,image_billing:null,cost:null,reason:'平台未提供本子任务独立计费数值；不从文字数推估。'}};
fs.writeFileSync(path.join(__dirname,'requirements-v001.json'),JSON.stringify(out,null,2)+'\n',{flag:'wx'});
const md='# B03 独立审查框架\n\n先核每件使用任务，再核技术主张。每个主张需要实际官方文档、当前完整DSL、真实服务原图与查看记录相互支持。HTTP成功只是服务链证据；未知属性会被忽略，不能凭HTTP200证明手法出现。\n\n本题不强制凑齐滤镜或裁剪标签。计划十件分别是聆听会、种子交换、书展、水族馆导览、合奏排练、茶香路线、灯笼课、向量场观察、微型城市展和聆听谱；其技术必须帮助相关任务。几何算法与数据核验只覆盖明确技术主张，不为增加检查数而扩测。\n\n官方parser缓存实际支持渐变、Opacity、列主序矩阵Transform、独立裁剪、ColorFiltered、ImageFiltered、BackdropFilter与foreground文字轮廓。ImageFiltered/BackdropFilter在Parser里是高斯模糊；Container自身clip需有装饰路径，BackdropFilter需按顺序读取先画背景并限定范围，foreground文字画笔需要foregroundColor。所有这些均有本run实际取得的缓存来源，详见requirements-v001.json。\n\n4096元素上限来自B01实际HTTP400原响应，作为已确认共享边界复用，不计B03新失败。每题技术笔记须区分文档注意事项与本题实际试验，保留失败、语法修复、静态探索与完整visual迭代的真实差别。\n\n最终审查将检查十件独立完整内容、当前DSL/PNG原字节与尺寸/view链、技术notes文档依据和可见观察，以及整体策展审查。接触表补充十件比较，不能替代每件完整PNG实际查看。当前尚无B03最终候选或额外看图，本框架不声明完成。\n';
fs.writeFileSync(path.join(__dirname,'review-framework-v001.md'),md,{flag:'wx'});
console.log(JSON.stringify({files:['requirements-v001.json','review-framework-v001.md'],requirements:requirements.length,planned_cases:plan.cases.length,documented_capability_groups:constraints.length,new_http_requests:0,actual_extra_image_views:0}));
