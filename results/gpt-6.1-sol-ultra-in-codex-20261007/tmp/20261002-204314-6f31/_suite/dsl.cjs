'use strict';

// Pure Snapshot parser DSL. Documentation provenance is in dsl-README.md.
// This module creates strings only; it performs no HTTP calls or image/state writes.
const DEFAULT_FONT = 'Inter,Noto Sans CJK SC';
const CONTAINER_ATTRS = new Set(('alignment padding margin border borderLeft borderTop borderRight borderBottom borderRadius borderRadiusTopLeft borderRadiusTopRight borderRadiusBottomLeft borderRadiusBottomRight boxShadow shape backgroundBlendMode gradientType gradientColors gradientStops gradientTileMode gradientRotation gradientBegin gradientEnd gradientCenter gradientRadius gradientFocal gradientFocalRadius gradientStartAngle gradientEndAngle foregroundColor foregroundBorder foregroundBorderLeft foregroundBorderTop foregroundBorderRight foregroundBorderBottom foregroundBorderRadius foregroundBoxShadow foregroundShape foregroundBackgroundBlendMode foregroundGradientType foregroundGradientColors foregroundGradientStops foregroundGradientTileMode foregroundGradientRotation foregroundGradientBegin foregroundGradientEnd foregroundGradientCenter foregroundGradientRadius foregroundGradientFocal foregroundGradientFocalRadius foregroundGradientStartAngle foregroundGradientEndAngle clipBehavior').split(' '));
const TEXT_ATTRS = new Set(('fontStyle height topRatio letterSpacing wordSpacing locale baselineMode fontEdging fontHinting subpixel foregroundColor foregroundMode foregroundStrokeWidth foregroundStrokeMiter foregroundStrokeCap foregroundStrokeJoin foregroundAntiAlias backgroundColor decoration decorationColor decorationLineStyle decorationThickness decorationGaps textShadow fontFeatures strutEnabled strutFontFamily strutFontStyle strutFontSize strutHeight strutLeading strutHeightForced strutHeightOverridden textAlign textDirection softWrap overflow maxLines textWidthBasis textHeightMode').split(' '));

function num(value, label = 'number') {
  const n = Number(value);
  if (!Number.isFinite(n)) throw new TypeError(`${label} must be finite`);
  return Math.abs(n) < 1e-8 ? '0' : String(Math.round(n * 1e6) / 1e6);
}
function nonnegative(value, label) {
  if (Number(value) < 0) throw new RangeError(`${label} must be nonnegative`);
  return num(value, label);
}
function quote(value) {
  const s = String(value);
  // The Snapshot parser does not decode XML entities. Pick a literal delimiter.
  if (!s.includes('"')) return `"${s}"`;
  if (!s.includes("'")) return `'${s}'`;
  throw new Error('Attribute contains both quote delimiters; pass this content through text()/CDATA instead');
}
function attrs(values) {
  return Object.entries(values).filter(([,v]) => v !== undefined && v !== null)
    .map(([k,v]) => ` ${k}=${quote(typeof v === 'number' ? num(v,k) : v)}`).join('');
}
function tag(name, values = {}, child = '') {
  return child === '' ? `<${name}${attrs(values)}/>` : `<${name}${attrs(values)}>${child}</${name}>`;
}
function cdata(value) {
  return '<![CDATA[' + String(value).replace(/\]\]>/g, ']]]]><![CDATA[>') + ']]>';
}
function selected(options, whitelist) {
  const result = {};
  for (const [k,v] of Object.entries(options || {})) if (whitelist.has(k)) result[k] = v;
  return result;
}
function matrix2d(a=1,b=0,c=0,d=1,tx=0,ty=0) {
  return '(' + [a,b,0,0,c,d,0,0,0,0,1,0,tx,ty,0,1].map(v=>num(v)).join(',') + ')';
}
function position(x,y,w,h,child) {
  return tag('Positioned',{left:num(x,'left'),top:num(y,'top'),width:nonnegative(w,'width'),height:nonnegative(h,'height')},child);
}

class Canvas {
  constructor(width, height, options = {}) {
    this.width = Number(nonnegative(width,'canvas width'));
    this.height = Number(nonnegative(height,'canvas height'));
    if (!this.width || !this.height) throw new RangeError('Canvas dimensions must be positive');
    this.background = options.background ?? '#FFFFFF';
    this.font = options.font ?? DEFAULT_FONT;
    this.type = options.type ?? 'png';
    this.clipBehavior = options.clipBehavior ?? 'HARD_EDGE';
    this.debug = options.debug ?? false;
    this.children = [];
  }
  add(widget) { this.children.push(String(widget)); return this; }
  at(x,y,w,h,widget) { return this.add(position(x,y,w,h,widget)); }
  rect(x,y,w,h,color='#FFFFFF',options={}) {
    const decoration = selected(options,CONTAINER_ATTRS);
    if (options.radius !== undefined) decoration.borderRadius = options.radius;
    if (options.shadow !== undefined) decoration.boxShadow = options.shadow;
    const widget = tag('Container',{width:nonnegative(w,'width'),height:nonnegative(h,'height'),color,...decoration},options.child ?? '');
    return this.at(x,y,w,h,options.opacity === undefined ? widget : tag('Opacity',{opacity:options.opacity},widget));
  }
  card(x,y,w,h,color='#FFFFFF',options={}) {
    return this.rect(x,y,w,h,color,{radius:16,...options});
  }
  circle(cx,cy,r,color='#FFFFFF',options={}) {
    nonnegative(r,'radius');
    return this.rect(cx-r,cy-r,2*r,2*r,color,{...options,shape:'CIRCLE'});
  }
  oval(x,y,w,h,color='#FFFFFF',options={}) {
    const widget=tag('ClipOval',{clipBehavior:'ANTI_ALIAS'},tag('Container',{width:w,height:h,color}));
    return this.at(x,y,w,h,options.opacity === undefined ? widget : tag('Opacity',{opacity:options.opacity},widget));
  }
  text(x,y,w,h,value,size=20,color='#172033',options={}) {
    const style=selected(options,TEXT_ATTRS);
    if (options.bold || options.italic) style.fontStyle = options.bold && options.italic ? 'BOLD_ITALIC' : options.bold ? 'BOLD' : 'ITALIC';
    if (options.align !== undefined) style.textAlign = String(options.align).toUpperCase();
    if (options.lineHeight !== undefined) style.height=options.lineHeight;
    const widget = tag('Text',{fontFamily:options.font ?? this.font,fontSize:num(size,'fontSize'),color,...style},tag('Raw',{},cdata(value)));
    return this.at(x,y,w,h,options.opacity === undefined ? widget : tag('Opacity',{opacity:options.opacity},widget));
  }
  line(x1,y1,x2,y2,color='#172033',width=1,options={}) {
    [x1,y1,x2,y2,width].forEach(v=>num(v));
    if (width <= 0) throw new RangeError('Line width must be positive');
    const dx=x2-x1,dy=y2-y1,len=Math.hypot(dx,dy);
    if (len < 1e-8) return options.roundCaps ? this.circle(x1,y1,width/2,color) : this;
    const cos=dx/len,sin=dy/len;
    // Layout has len × width, independent of painted rotation. Translate the
    // top-left-origin rectangle so its centreline hits both requested points.
    const widget=tag('Transform',{matrix:matrix2d(cos,sin,-sin,cos,sin*width/2,-cos*width/2),origin:'(0,0)'},tag('Container',{width:len,height:width,color}));
    this.at(x1,y1,len,width,options.opacity === undefined ? widget : tag('Opacity',{opacity:options.opacity},widget));
    if (options.roundCaps) { this.circle(x1,y1,width/2,color,{opacity:options.opacity}); this.circle(x2,y2,width/2,color,{opacity:options.opacity}); }
    return this;
  }
  polyline(points,color='#172033',width=1,options={}) {
    for (let i=1;i<points.length;i++) this.line(...points[i-1],...points[i],color,width,options);
    if (options.closed && points.length>2) this.line(...points[points.length-1],...points[0],color,width,options);
    return this;
  }
  arrow(x1,y1,x2,y2,color='#172033',width=2,options={}) {
    const len=Math.hypot(x2-x1,y2-y1);
    if (len<1e-8) return this;
    const ux=(x2-x1)/len,uy=(y2-y1)/len,head=options.headLength??Math.max(9,width*4),half=options.headWidth??head*.48;
    this.line(x1,y1,x2,y2,color,width,options);
    this.line(x2,y2,x2-ux*head-uy*half,y2-uy*head+ux*half,color,width,options);
    this.line(x2,y2,x2-ux*head+uy*half,y2-uy*head-ux*half,color,width,options);
    if (options.double) {
      this.line(x1,y1,x1+ux*head-uy*half,y1+uy*head+ux*half,color,width,options);
      this.line(x1,y1,x1+ux*head+uy*half,y1+uy*head-ux*half,color,width,options);
    }
    return this;
  }
  // Table cells are separate actual DSL widgets. Row 0 is styled as a header
  // unless header=false. Heights can be a number or an explicit per-row array.
  table(x,y,columnWidths,rowHeights,rows,options={}) {
    const pad=options.padding??12,size=options.size??18;
    let cy=y;
    rows.forEach((row,ri)=>{
      const rh=Array.isArray(rowHeights)?rowHeights[ri]:rowHeights;
      nonnegative(rh,'row height');
      let cx=x;
      columnWidths.forEach((cw,ci)=>{
        const header=options.header!==false&&ri===0;
        const fill=header?(options.headerFill??'#E9EEF5'):(ri%2?(options.alternateFill??'#F8FAFC'):(options.fill??'#FFFFFF'));
        this.rect(cx,cy,cw,rh,fill,{border:`${options.borderWidth??1} SOLID ${options.borderColor??'#DCE3EB'}`});
        const cell=row[ci]??'';
        const cellOptions={bold:header,align:options.aligns?.[ci]??'START',...options.textOptions};
        this.text(cx+pad,cy+pad,cw-2*pad,rh-2*pad,cell,size,header?(options.headerColor??'#172033'):(options.color??'#334155'),cellOptions);
        cx+=cw;
      });
      cy+=rh;
    });
    return this;
  }
  toString() {
    return tag('Snapshot',{type:this.type,background:this.background,debug:String(Boolean(this.debug))},tag('Container',{width:this.width,height:this.height},tag('Stack',{fit:'EXPAND',clipBehavior:this.clipBehavior},this.children.join('\n'))));
  }
}

module.exports={Canvas,DEFAULT_FONT,attrs,tag,cdata,matrix2d,position};
