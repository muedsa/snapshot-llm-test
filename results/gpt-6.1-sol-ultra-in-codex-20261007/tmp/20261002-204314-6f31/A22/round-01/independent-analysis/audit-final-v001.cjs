'use strict';
// Read-only review of existing first-round files. Writes only immutable reviewer outputs.
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const root = 'D:/workspaces/gpt-6.1-sol-ultra';
const run = '20261002-204314-6f31';
const base = root + '/tmp/' + run + '/A22';
const round = base + '/round-01';
const dir = round + '/independent-analysis';
const p = {
  csv: root + '/tasks/A22-staged-data-correction/inputs/monthly.csv',
  independent: dir + '/baseline-arithmetic-v001.json',
  computed: round + '/production/computed-data-v001.json',
  map: round + '/production/layout-map-v002.json',
  mapBefore: round + '/production/layout-map-v001.json',
  parameters: round + '/production/parameters-v001.json',
  source: base + '/requests/A22-request-000002/input.snapshot',
  before: base + '/requests/A22-request-000001/input.snapshot',
  png: base + '/requests/A22-request-000002/response.png',
  meta: base + '/requests/A22-request-000002/render-result.json',
  beforeMeta: base + '/requests/A22-request-000001/render-result.json',
  review: round + '/root-review-v001.json'
};
const sha = b => crypto.createHash('sha256').update(b).digest('hex');
const bytes = Object.fromEntries(Object.entries(p).map(([k, v]) => [k, fs.readFileSync(v)]));
const json = k => JSON.parse(bytes[k].toString('utf8').replace(/^\uFEFF/, ''));
const baseline = json('independent'), computed = json('computed'), map = json('map');
const beforeMap = json('mapBefore'), params = json('parameters'), meta = json('meta');
const beforeMeta = json('beforeMeta'), review = json('review');
const source = bytes.source.toString('utf8'), before = bytes.before.toString('utf8');
const assertions = [], issues = [];
function check(id, pass, evidence = null) {
  const result = {id, pass: !!pass, evidence};
  assertions.push(result);
  if (!result.pass) issues.push(result);
  return result.pass;
}
const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);
const tolerance = 0.00000051; // Submitted DSL rounds coordinates to 6 decimals.
const near = (a, b) => Number.isFinite(a) && Number.isFinite(b) && Math.abs(a - b) <= tolerance;
const nearArray = (a, b) => a.length === b.length && a.every((v, i) => near(v, b[i]));
const money = n => n.toLocaleString('en-US');
function pct(n, d) {
  const nn = BigInt(n), dd = BigInt(d), negative = nn < 0n;
  const abs = negative ? -nn : nn;
  // Exact half-up final-only rounding to two decimal percent places.
  const v = (abs * 10000n * 2n + dd) / (2n * dd);
  return (negative ? '-' : '') + String(v / 100n) + '.' + String(v % 100n).padStart(2, '0') + '%';
}
const csvLines = bytes.csv.toString('utf8').replace(/^\uFEFF/, '').trimEnd().split(/\r?\n/);
const keys = csvLines.shift().split(',');
const rows = csvLines.map(l => {
  const values = l.split(',');
  const r = Object.fromEntries(keys.map((k, i) => [k, k === 'month' ? values[i] : Number(values[i])]));
  r.net_revenue = r.gross_revenue - r.refund_amount;
  r.operating_profit = r.net_revenue - r.operating_cost;
  r.refund_display = pct(r.refund_amount, r.gross_revenue);
  r.conversion_display = pct(r.orders, r.sessions);
  return r;
});
const months = rows.map(r => r.month), totals = {};
const numericKeys = keys.filter(k => k !== 'month').concat(['net_revenue', 'operating_profit']);
for (const k of numericKeys) totals[k] = rows.reduce((s, r) => s + r[k], 0);
check('six_source_rows_safe_integer_numerators_denominators', rows.length === 6 && rows.every(r => numericKeys.every(k => Number.isSafeInteger(r[k])) && r.gross_revenue > 0 && r.sessions > 0), months);
check('original_months_and_order', same(months, ['2026-04','2026-05','2026-06','2026-07','2026-08','2026-09']), months);
check('independent_baseline_reconciles_source', rows.every((r, i) => numericKeys.every(k => r[k] === baseline.monthly[i][k]) && r.refund_display === baseline.monthly[i].refund_rate.display2 && r.conversion_display === baseline.monthly[i].conversion_rate.display2) && numericKeys.every(k => totals[k] === baseline.totals[k]), totals);
check('producer_input_hash_and_original_strings', computed.input.sha256 === sha(bytes.csv) && same(computed.input.original_month_strings, months));
check('producer_computed_rows_exact', computed.rows.length === 6 && rows.every((r, i) => {
  const a = computed.rows[i];
  return a.month === r.month && numericKeys.every(k => a[k] === r[k]) &&
    a.refund_rate.numerator === r.refund_amount && a.refund_rate.denominator === r.gross_revenue && a.refund_rate.display === r.refund_display &&
    a.conversion_rate.numerator === r.orders && a.conversion_rate.denominator === r.sessions && a.conversion_rate.display === r.conversion_display;
}));
check('producer_computed_totals_exact', numericKeys.every(k => computed.totals[k] === totals[k]), totals);
check('overall_rates_use_ratio_of_sums', computed.totals.overall_conversion_rate.numerator === totals.orders && computed.totals.overall_conversion_rate.denominator === totals.sessions && computed.totals.overall_conversion_rate.display === pct(totals.orders, totals.sessions) && computed.totals.overall_refund_rate.numerator === totals.refund_amount && computed.totals.overall_refund_rate.denominator === totals.gross_revenue && computed.totals.overall_refund_rate.display === pct(totals.refund_amount, totals.gross_revenue), {conversion:{numerator:totals.orders,denominator:totals.sessions,display:pct(totals.orders,totals.sessions)},refund:{numerator:totals.refund_amount,denominator:totals.gross_revenue,display:pct(totals.refund_amount,totals.gross_revenue)}});
check('formulas_and_source_currency', computed.formulas.net_revenue === 'gross_revenue - refund_amount' && computed.formulas.operating_profit === 'net_revenue - operating_cost' && computed.formulas.refund_rate === 'refund_amount / gross_revenue' && computed.formulas.conversion_rate === 'orders / sessions' && computed.formulas.overall_conversion_rate === 'sum(orders) / sum(sessions)' && computed.input.source_currency === null);

function attrs(s) { return Object.fromEntries([...s.matchAll(/([A-Za-z][\w-]*)="([^"]*)"/g)].map(m => [m[1], m[2]])); }
const box = a => ['left','top','width','height'].map(k => Number(a[k]));
const allNodes = [...source.matchAll(/<Positioned\b([^>]*)>([\s\S]*?)<\/Positioned>/g)].map((m, i) => {
  const a = attrs(m[1]), inner = m[2], t = inner.match(/^<Text\b([^>]*)><Raw><!\[CDATA\[([\s\S]*?)\]\]><\/Raw><\/Text>$/);
  if (t) return {index:i,type:'text',box:box(a),text:t[2],attrs:attrs(t[1]),raw:m[0]};
  const tr = inner.match(/^<Transform\b([^>]*)><Container\b([^>]*)\/><\/Transform>$/);
  if (tr) return {index:i,type:'line',box:box(a),attrs:attrs(tr[2]),transform:attrs(tr[1]),raw:m[0]};
  const c = inner.match(/^<Container\b([^>]*)\/>$/);
  if (c) return {index:i,type:'rect',box:box(a),attrs:attrs(c[1]),raw:m[0]};
  throw Error('Unrecognized submitted Positioned node '+i);
});
const sourceTexts = allNodes.filter(n => n.type === 'text'), sourceShapes = allNodes.filter(n => n.type !== 'text');
const allowed = new Set(['Snapshot','Container','Stack','Positioned','Text','Raw','Transform']);
const stack = [], tagCounts = {}, xmlProblems = [];
const bare = source.replace(/<!\[CDATA\[[\s\S]*?\]\]>/g, '');
for (const m of bare.matchAll(/<(\/?)([A-Za-z][\w-]*)([^>]*)>/g)) {
  const [, close, name, rest] = m;
  tagCounts[name] = (tagCounts[name] || 0) + 1;
  if (!allowed.has(name)) xmlProblems.push('Unexpected '+name);
  if (close) { if (stack.pop() !== name) xmlProblems.push('Unbalanced '+name); }
  else if (!/\/\s*$/.test(rest)) stack.push(name);
}
if (stack.length) xmlProblems.push('Unclosed '+stack.join(','));
const residual = source.replace(/<Positioned\b[^>]*>[\s\S]*?<\/Positioned>/g,'').replace(/<\/?(?:Snapshot|Container|Stack)\b[^>]*>/g,'').trim();
check('complete_flat_pure_dsl_structure', !xmlProblems.length && residual === '' && source.startsWith('<Snapshot ') && source.endsWith('</Stack></Container></Snapshot>'), {xmlProblems,unaccounted_residual:residual,tagCounts});
const rootSnapshot = attrs(source.match(/^<Snapshot\b([^>]*)>/)[1]);
const rootContainer = attrs(source.match(/^<Snapshot\b[^>]*><Container\b([^>]*)>/)[1]);
check('source_canvas_background_and_no_assets', rootSnapshot.type === 'png' && rootSnapshot.background === map.main_styles.background && Number(rootContainer.width) === 1600 && Number(rootContainer.height) === 1000 && !/<(?:Image|Svg|WebView|Canvas|Network|Asset)\b|https?:\/\//i.test(source) && map.constraints.whole_image_or_external_assets === false);
check('all_submitted_texts_and_shapes_accounted', sourceTexts.length === map.texts.length && sourceShapes.length === map.shapes.length && allNodes.length === map.texts.length + map.shapes.length && new Set(map.texts.map(t=>t.id)).size === map.texts.length && new Set(map.shapes.map(t=>t.id)).size === map.shapes.length, {source_texts:sourceTexts.length,map_texts:map.texts.length,source_shapes:sourceShapes.length,map_shapes:map.shapes.length});
const textEvidence = [];
for (let i = 0; i < map.texts.length; i++) {
  const a = sourceTexts[i], b = map.texts[i];
  const pass = !!a && nearArray(a.box,b.box) && a.text === b.text && Number(a.attrs.fontSize) === b.font_size && a.attrs.color === b.color && a.attrs.fontFamily === b.font && (a.attrs.fontStyle === 'BOLD') === b.bold && (a.attrs.textAlign || 'START') === b.align;
  textEvidence.push({id:b.id,source_index:a?.index,pass,box:a?.box,text:a?.text,font_size:Number(a?.attrs.fontSize)});
}
check('all_source_text_geometry_content_style_match_final_map', textEvidence.every(e=>e.pass), {count:textEvidence.length,failures:textEvidence.filter(e=>!e.pass),coordinate_tolerance_px:tolerance});
const shapeEvidence = [];
for (let i = 0; i < map.shapes.length; i++) {
  const a = sourceShapes[i], b = map.shapes[i];
  let pass = !!a && a.type === b.type && a.attrs.color === b.color;
  if (b.type === 'rect') pass &&= nearArray(a.box,b.box) && near(Number(a.attrs.width),b.box[2]) && near(Number(a.attrs.height),b.box[3]) && Number(a.attrs.borderRadius || 0) === Number(b.options?.radius || 0);
  if (b.type === 'line') {
    const [one,two] = b.points, expectedBox = [one[0],one[1],two[0]-one[0],b.width];
    const matrix = (a?.transform.matrix || '').replace(/[()]/g,'').split(',').map(Number);
    pass &&= one[1] === two[1] && nearArray(a.box,expectedBox) && near(Number(a.attrs.width),expectedBox[2]) && near(Number(a.attrs.height),b.width) && a.transform.origin === '(0,0)' && nearArray(matrix,[1,0,0,0,0,1,0,0,0,0,1,0,0,-b.width/2,0,1]);
  }
  shapeEvidence.push({id:b.id,source_index:a?.index,pass,box:a?.box,type:a?.type});
}
check('all_source_shape_geometry_styles_match_final_map', shapeEvidence.every(e=>e.pass), {count:shapeEvidence.length,failures:shapeEvidence.filter(e=>!e.pass)});
const textById = Object.fromEntries(map.texts.map((t,i) => [t.id,{...t,source:sourceTexts[i]}]));
const shapeById = Object.fromEntries(map.shapes.map((t,i) => [t.id,{...t,source:sourceShapes[i]}]));
const contain = (outer, inner) => inner[0] >= outer[0]-tolerance && inner[1] >= outer[1]-tolerance && inner[0]+inner[2] <= outer[0]+outer[2]+tolerance && inner[1]+inner[3] <= outer[1]+outer[3]+tolerance;
const regionBox = id => map.regions[id] || map.kpi_regions.find(k=>k.id===id)?.box;
check('required_regions_bounds_and_main_styles', ['title','kpis','chart','table'].every(k=>Array.isArray(map.regions[k]) && map.regions[k].length===4 && contain([0,0,1600,1000],map.regions[k])) && same(map.canvas,[1600,1000]) && same(map.chart.region,map.regions.chart) && same(map.table.region,map.regions.table) && map.main_styles.body_min>=22 && map.constraints.body_font_min>=22 && map.main_styles.font === 'Inter,Noto Sans CJK SC', map.regions);
check('all_texts_and_shapes_inside_declared_regions_and_canvas', map.texts.every(t=>contain([0,0,1600,1000],t.box)&&regionBox(t.region)&&contain(regionBox(t.region),t.box)) && map.shapes.every(s=>regionBox(s.region)&&contain(regionBox(s.region),s.type==='rect'?s.box:[s.points[0][0],s.points[0][1],s.points[1][0]-s.points[0][0],0])), {note:'Line center geometry checked against containing region; text rectangle containment does not by itself verify raster glyph spacing.'});
check('all_actual_body_text_font_sizes_at_least_22', sourceTexts.every(t=>Number(t.attrs.fontSize)>=22), {minimum:Math.min(...sourceTexts.map(t=>Number(t.attrs.fontSize))),all_text_count:sourceTexts.length});
const expectedKpi = [['kpi-net','总净收入',money(totals.net_revenue)],['kpi-profit','总经营利润',money(totals.operating_profit)],['kpi-orders','总订单',money(totals.orders)],['kpi-conversion','总体转化率',pct(totals.orders,totals.sessions)]];
const kpiEvidence = expectedKpi.map(([id,label,value])=>({id,label,value,actual_label:textById[id+'-label']?.source.text,actual_value:textById[id+'-value']?.source.text,box:map.kpi_regions.find(k=>k.id===id)?.box}));
check('exactly_four_required_kpis_actual_source', map.kpi_regions.length===4 && map.texts.filter(t=>/^kpi-.*-value$/.test(t.id)).length===4 && kpiEvidence.every(k=>k.label===k.actual_label&&k.value===k.actual_value) && textById['kpi-conversion-formula'].source.text==='3,045 / 27,300 sessions', kpiEvidence);
check('kpi_card_map_source_bounds_and_parameter_grid', expectedKpi.every(([id],i)=>same(map.kpi_regions[i].box,[params.kpi.x+i*(params.kpi.width+params.kpi.gap),params.kpi.y,params.kpi.width,params.kpi.height]) && nearArray(shapeById[id+'-card'].source.box,map.kpi_regions[i].box) && map.kpi_regions[i].value_text_id===id+'-value'));
const tableEvidence = [];
const cellSuffix = ['month','net','profit','refund-rate','conversion-rate'];
const expectedHeaders = ['月份','净收入','经营利润','退款率','转化率'];
for (let i=0;i<rows.length;i++) {
  const r=rows[i], tr=map.table.rows[i];
  const expected=[r.month,money(r.net_revenue),money(r.operating_profit),r.refund_display,r.conversion_display];
  for (let j=0;j<5;j++) {
    const id='table-'+r.month+'-'+cellSuffix[j], t=textById[id], cell=tr?.cells[j];
    tableEvidence.push({id,row:i,column:j,expected:expected[j],map_value:cell?.text,actual_source_value:t?.source.text,pass:tr?.month===r.month && cell?.column===expectedHeaders[j] && cell?.text===expected[j] && t?.source.text===expected[j] && nearArray(t.source.box,cell.box) && contain(tr.row_box,t.source.box)});
  }
}
check('table_has_six_rows_five_headers_exact_thirty_actual_cells', map.table.rows.length===6 && same(map.table.headers,expectedHeaders) && expectedHeaders.every((h,i)=>textById['table-header-'+i].source.text===h) && map.texts.filter(t=>/^table-2026-\d\d-/.test(t.id)).length===30 && tableEvidence.length===30 && tableEvidence.every(c=>c.pass), {count:tableEvidence.length,failures:tableEvidence.filter(c=>!c.pass)});
check('table_original_month_strings_not_reformatted', rows.every(r=>textById['table-'+r.month+'-month'].source.text===r.month && textById['chart-month-'+r.month].source.text===r.month) && map.constraints.original_months_preserved, months);
check('table_parameters_and_cells_inside_table', same(map.table.inner_box,params.table.inner) && same(map.table.column_widths,params.table.column_widths) && map.table.rows.every((r,i)=>same(r.row_box,[params.table.inner[0],params.table.inner[1]+params.table.header_height+i*params.table.row_height,params.table.inner[2],params.table.row_height]) && contain(map.regions.table,r.row_box)) && params.table.column_widths.reduce((a,b)=>a+b,0)===params.table.inner[2]);
const [px,py,pw,ph]=map.chart.plot_box, zero=map.chart.shared_zero_y, maximum=map.chart.y_max;
check('shared_axis_zero_maximum_ticks_parameter_consistency', zero===724 && maximum===250000 && py+ph===zero && same(map.chart.plot_box,[156,452,670,272]) && same(map.chart.y_ticks,[0,50000,100000,150000,200000,250000]) && same(map.chart.plot_box,params.chart.plot) && zero===params.chart.zero_y && maximum===params.chart.y_max && same(map.chart.y_ticks,params.chart.ticks), {plot:map.chart.plot_box,zero_y:zero,maximum,scale_px_per_unit:ph/maximum,ticks:map.chart.y_ticks});
const axisEvidence=map.chart.y_ticks.map(value=>{
  const y=zero-value*ph/maximum, grid=shapeById['chart-grid-'+value], tick=textById['chart-tick-'+value];
  return {value,expected_y:y,actual_y:grid?.source.box[1],label:tick?.source.text,pass:near(grid?.source.box[1],y)&&near(grid?.source.box[0],px)&&near(grid?.source.box[2],pw)&&tick?.source.text===money(value)&&near(tick.source.box[1]+16,y)};
});
check('all_six_actual_axis_lines_and_tick_labels', axisEvidence.every(a=>a.pass),axisEvidence);
const barEvidence=[];
for (let i=0;i<rows.length;i++) for (const [series,color,offset] of [['net_revenue',map.main_styles.net,-21],['operating_profit',map.main_styles.profit,21]]) {
  const r=rows[i], id='bar-'+r.month+'-'+series, bar=map.chart.bars.find(b=>b.id===id), s=shapeById[id], label=textById['bar-label-'+r.month+'-'+series];
  const value=r[series], height=value*ph/maximum, y=zero-height, center=px+pw/6*(i+.5), x=center+offset-15.5;
  const actual=s?.source.box;
  const pass=!!bar&&bar.month===r.month&&bar.series===series&&bar.value===value&&bar.zero_y===zero&&bar.shared_y_max===maximum&&nearArray(bar.box,[x,y,31,height])&&nearArray(actual,[x,y,31,height])&&near(actual[1]+actual[3],zero)&&s.color===color&&s.source.attrs.color===color&&label.source.text===money(value)&&contain(map.chart.plot_box,actual);
  barEvidence.push({id,month:r.month,series,value,expected_height_px:height,actual_height_px:actual?.[3],actual_top_y:actual?.[1],actual_bottom_y:actual?actual[1]+actual[3]:null,height_absolute_error_px:actual?Math.abs(actual[3]-height):null,pass});
}
check('twelve_actual_bars_values_heights_same_zero_scale_labels', map.chart.bars.length===12 && map.shapes.filter(s=>/^bar-2026-/.test(s.id)).length===12 && barEvidence.length===12 && barEvidence.every(b=>b.pass), {count:barEvidence.length,maximum_height_error_px:Math.max(...barEvidence.map(b=>b.height_absolute_error_px)),failures:barEvidence.filter(b=>!b.pass)});
check('two_chart_series_style_and_legend_consistency', same(map.chart.series,[{id:'net_revenue',color:map.main_styles.net},{id:'operating_profit',color:map.main_styles.profit}])&&shapeById['legend-net-swatch'].source.attrs.color===map.main_styles.net&&shapeById['legend-profit-swatch'].source.attrs.color===map.main_styles.profit&&textById['legend-net'].source.text==='净收入'&&textById['legend-profit'].source.text==='经营利润');
const sep=rows[5],june=rows[2],may=rows[1],aug=rows[4];
const facts={september_net_is_strict_max:rows.slice(0,5).every(r=>sep.net_revenue>r.net_revenue),september_profit_is_strict_max:rows.slice(0,5).every(r=>sep.operating_profit>r.operating_profit),june_profit_down:june.operating_profit<may.operating_profit,june_drop_value:may.operating_profit-june.operating_profit,june_drop_pct:pct(may.operating_profit-june.operating_profit,may.operating_profit),june_aug_refund_equal:BigInt(june.refund_amount)*BigInt(aug.gross_revenue)===BigInt(aug.refund_amount)*BigInt(june.gross_revenue)};
const expectedMain='9月净收入与利润均为期内最高，6月利润回落。';
const expectedDetail='2026-06 利润 27,914，较5月下降 33.49%；6月与8月退款率同为 8.00%。';
check('actual_main_and_numeric_detail_conclusions_are_supported', textById['conclusion-main'].source.text===expectedMain && textById['conclusion-detail'].source.text===expectedDetail && facts.september_net_is_strict_max&&facts.september_profit_is_strict_max&&facts.june_profit_down&&facts.june_drop_value===14056&&facts.june_drop_pct==='33.49%'&&facts.june_aug_refund_equal&&june.refund_display==='8.00%', {main:expectedMain,detail:expectedDetail,facts,september:{net:sep.net_revenue,profit:sep.operating_profit}});
check('producer_conclusion_fact_records_reconcile', computed.conclusion_facts.length===4 && computed.conclusion_facts.every(f=>f.predicate===true)&&computed.conclusion_facts[0].value===sep.net_revenue&&computed.conclusion_facts[1].value===sep.operating_profit&&computed.conclusion_facts[2].actual===june.operating_profit&&computed.conclusion_facts[2].previous===may.operating_profit&&computed.conclusion_facts[2].change.numerator===-14056&&computed.conclusion_facts[2].change.denominator===may.operating_profit&&computed.conclusion_facts[2].change.display==='-33.49%'&&computed.conclusion_facts[3].display===june.refund_display);
const oldPosition='<Positioned left="64" top="414" width="744" height="30">';
const newPosition='<Positioned left="156" top="414" width="670" height="30">';
const caption='金额单位同源数据，两组柱共用零起点';
const beforeCaption=[...before.matchAll(/<Positioned\b[^>]*><Text\b[^>]*><Raw><!\[CDATA\[金额单位同源数据，两组柱共用零起点\]\]><\/Raw><\/Text><\/Positioned>/g)].map(m=>m[0]);
const afterCaption=[...source.matchAll(/<Positioned\b[^>]*><Text\b[^>]*><Raw><!\[CDATA\[金额单位同源数据，两组柱共用零起点\]\]><\/Raw><\/Text><\/Positioned>/g)].map(m=>m[0]);
const beforeReplacement=beforeCaption[0]?.replace(oldPosition,newPosition);
check('actual_source_diff_only_chart_unit_position_and_width', beforeCaption.length===1&&afterCaption.length===1&&beforeReplacement===afterCaption[0]&&before.replace(beforeCaption[0],beforeReplacement)===source, {element_id:'chart-unit',text:caption,before_box:[64,414,744,30],after_box:[156,414,670,30],all_other_source_bytes_unchanged:before.replace(beforeCaption[0],beforeReplacement)===source,before_sha256:sha(bytes.before),after_sha256:sha(bytes.source)});
const diffs=[];
function diff(a,b,location='') {
  if (same(a,b)) return;
  if (a && b && typeof a==='object' && typeof b==='object') {
    for (const k of new Set(Object.keys(a).concat(Object.keys(b)))) diff(a[k],b[k],location?location+'.'+k:k);
  } else diffs.push({path:location,before:a,after:b});
}
diff(beforeMap,map);
const unitIndex=map.texts.findIndex(t=>t.id==='chart-unit');
const allowedPaths=new Set(['created_at','version_id','texts.'+unitIndex+'.box.0','texts.'+unitIndex+'.box.2']);
check('final_layout_map_diff_only_version_metadata_and_caption_box', diffs.length===4&&diffs.every(d=>allowedPaths.has(d.path))&&same(beforeMap.texts[unitIndex].box,[64,414,744,30])&&same(map.texts[unitIndex].box,[156,414,670,30]),diffs);
const captionBox=textById['chart-unit'].source.box,tickBox=textById['chart-tick-250000'].source.box;
check('caption_and_top_axis_tick_rectangles_are_separated', captionBox[0]-(tickBox[0]+tickBox[2])>=16, {horizontal_gap_px:captionBox[0]-(tickBox[0]+tickBox[2]),caption_box:captionBox,top_tick_box:tickBox,note:'Box separation independently checked; actual raster view belongs to root.'});
const png=bytes.png, dimensions=[png.readUInt32BE(16),png.readUInt32BE(20)];
check('real_png_signature_dimensions_and_response_hash', png.subarray(0,8).equals(Buffer.from([137,80,78,71,13,10,26,10]))&&png.subarray(12,16).toString('ascii')==='IHDR'&&same(dimensions,[1600,1000])&&png.length===meta.response_bytes&&sha(png)===meta.response_sha256, {dimensions,bytes:png.length,sha256:sha(png)});
check('submitted_source_hash_real_200_metadata_and_version', meta.id==='A22-request-000002'&&meta.http_status===200&&meta.ok===true&&meta.content_type==='image/png'&&meta.body_sha256===sha(bytes.source)&&meta.version_id==='A22-round-01-dashboard-v002'&&map.version_id===meta.version_id&&meta.parent_version==='A22-round-01-dashboard-v001'&&meta.round_id==='round-01'&&same([meta.png_dimensions.width,meta.png_dimensions.height],dimensions),{request_id:meta.id,version:meta.version_id,http_status:meta.http_status,body_sha256:meta.body_sha256});
check('before_source_is_actual_v001_response_provenance', beforeMeta.http_status===200&&beforeMeta.ok===true&&beforeMeta.body_sha256===sha(bytes.before)&&beforeMeta.version_id==='A22-round-01-dashboard-v001');
const view=review.images.find(i=>i.version_id===meta.version_id);
check('root_actual_final_view_evidence_references_same_response', review.reviewer==='root'&&review.actual_tool==='view_image'&&!!view&&view.existing_view_id==='A22-view-000003'&&path.resolve(view.image_path)===path.resolve(p.png)&&review.validation.unresolved_visual_defects.length===0, {review_path:p.review,reviewer:review.reviewer,actual_tool:review.actual_tool,view_id:view?.existing_view_id,image_path:view?.image_path,independent_new_views:0,note:'Evidence read only; this reviewer did not independently view any image.'});
const result={
  schema_version:1,task_id:'A22',round_id:'round-01',run_id:run,reviewer:'/root/a19_audit_resume',reviewed_at:new Date().toISOString(),
  scope:'Independent exact CSV arithmetic, source/text/style/geometry/map audit of the actual request-000002 v002 first-round submission; byte hash/IHDR audit of its original response PNG; before/after caption source regression. No future requirements read, HTTP, render, or new image view. Parent owns visual approval, archival, and suite state.',
  final_version_id:meta.version_id,pass:issues.length===0,all_writes_finished:true,
  source_files:Object.entries(p).map(([name,file])=>({name,path:file,sha256:sha(bytes[name]),bytes:bytes[name].length})),
  arithmetic:{rows,totals,overall_conversion:pct(totals.orders,totals.sessions),overall_refund:pct(totals.refund_amount,totals.gross_revenue)},
  counts:{assertion_groups:assertions.length,source_positioned:allNodes.length,texts:sourceTexts.length,shapes:sourceShapes.length,kpis:kpiEvidence.length,table_cells:tableEvidence.length,bars:barEvidence.length,axis_ticks:axisEvidence.length},
  assertions,kpi_evidence:kpiEvidence,table_cell_evidence:tableEvidence,bar_evidence:barEvidence,axis_evidence:axisEvidence,text_evidence:textEvidence,shape_evidence:shapeEvidence,
  regression:{before_version:beforeMeta.version_id,after_version:meta.version_id,caption_id:'chart-unit',before_box:[64,414,744,30],after_box:[156,414,670,30],map_differences:diffs},
  root_visual_evidence:{path:p.review,view_id:view?.existing_view_id,personally_viewed_by_this_reviewer:false},
  provenance:{new_http_requests:0,new_render_requests:0,new_actual_views:0,future_requirement_files_read:[],no_suite_state_or_producer_changes:true,coordinate_comparison_tolerance_px:tolerance,baseline_parameters_version:params.version_id,baseline_parameters_note:'Parameters preserve the v001 common geometry and styles, which are unchanged in v002. Caption is fully specified by final layout-map and actual source.'},
  unresolved:issues,unknown_costs:{tokens:null,image_cost:null,reason:'No authoritative resource billing supplied for these local audit operations.'}
};
const md=[
  '# A22 round-01 independent final-source audit',
  '',
  'Result: '+(result.pass?'PASS':'FAIL')+' for `A22-round-01-dashboard-v002` (`A22-request-000002`).',
  '',
  'Audited the actual submitted source and original PNG bytes, final layout map, baseline parameters, producer computed data, and the independently recomputed six-row CSV. This review does not itself perform an image view or certify later rounds. Parent image evidence: `A22-view-000003` in `root-review-v001.json`.',
  '',
  '- Four KPIs: net revenue **918,624**; operating profit **262,124**; orders **3,045**; overall conversion **11.15%** = 3,045 / 27,300.',
  '- Six original month strings in chart and table; all **30 table cells** agree with exact independent arithmetic. Percentages use final-only exact half-up rounding.',
  '- All **12 bars** use common zero y=724, scale 272/250000 pixels per unit, maximum 250,000, and correct labels; six axis ticks are 0 through 250,000 at 50,000 intervals.',
  '- All '+sourceTexts.length+' submitted text elements and '+sourceShapes.length+' shapes match final-map content, bounds and styles. Minimum text font size is 22. Region and table/card geometry reconcile with parameters.',
  '- The numeric conclusion is supported: September has maximum net revenue/profit; June profit is 27,914, down 14,056 (33.49%) from May; June/August refund rates both 8.00%. No unsupported currency is asserted.',
  '- The only source change from actual v001 is chart-unit left 64→156 and width 744→670. Other source bytes are unchanged. Caption/top tick boxes now have 16px horizontal separation; parent owns the actual raster confirmation.',
  '- PNG signature/IHDR and response digest confirm '+dimensions[0]+'×'+dimensions[1]+'; '+png.length+' original bytes; sha256 `'+sha(png)+'`. Actual source digest matches successful 200 response metadata.',
  '',
  'Audit JSON includes hashes, '+assertions.length+' assertion groups, per-text/shape/cell/bar/axis evidence, and exact map/source regression. `all_writes_finished=true`. New HTTP/render/view counts are all 0. Future requirement files read: none.',
  '',
  'Unresolved source/data issues: '+(issues.length?issues.map(i=>i.id).join(', '):'none')+'.',
  '',
  'Script: `audit-final-v001.cjs`; machine evidence: `final-audit-v001.json`.',
  ''
].join('\n');
for (const [name,data] of [['final-audit-v001.json',JSON.stringify(result,null,2)+'\n'],['final-audit-v001.md',md]]) fs.writeFileSync(path.join(dir,name),data,{flag:'wx'});
console.log(JSON.stringify({pass:result.pass,all_writes_finished:true,counts:result.counts,unresolved:issues.map(i=>i.id),json_path:path.join(dir,'final-audit-v001.json'),md_path:path.join(dir,'final-audit-v001.md')}));
if (!result.pass) process.exitCode=1;
