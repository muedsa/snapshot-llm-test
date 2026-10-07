# A03 independent semantic audit

Read task entries/config, original broken.snapshot, input README, and already-fetched service guide, parser guide, parser tag reference and layout guide. Reused shared-doc-000001/000003/000004/000005; no new HTTP request. No render, service response inspection or PNG view was performed by this subagent. All service errors remain null in the independent JSON until producer supplies actual responses.

## Exact original positions and documented meaning

| Source line | Finding | Required repair |
|---:|---|---|
| 1 | Snapshot width/height are unsupported attributes and ignored; layout determines canvas size | Bounded root Container1280×800 |
| 2 | `padding="24 32"` is invalid EdgeInsets syntax | Use valid scalar/parenthesized-comma insets; enforce32safe margin |
| 4 | `font-size` unknown and ignored | `fontSize="44"` |
| 6,9 | Expanded/Spacer cannot distribute infinite main-axis space resulting from unbounded root | Provide finite Row/Column bounds or exact bounded geometry |
| 7 | Positioned is directly under Row, violating supported parent rule | Put LIVE directly under Stack;96×36; top-rightclearofheader |
| 10 | `#33FFFFFF` is RRGGBBAA: opaque RGB51,255,255 | White20% is `#FFFFFF33`; keep text fullyopaque |
| 10 | Unknown `rotate` is ignored; Transform's mandatory matrix absent | Real16-entry,column-majorrotationmatrix;alignCENTER |
| 11 | ImageFiltered blurs its entire child subtree, including text | ClipRRect24 around BackdropFilter; background stripes painted beforecard; text rendered clearly |
| 6,7,10,11 | Missing two metrics, tag dimensions/text24, centralradius and crossingstripes | Restore all requested sections; do not delete faulted blocks |

Documentation explicitly supports unknown-attribute ignore, but this audit does not pretend the original failed render produced a visible image exposing every issue. Distinguish producer's true response errors from documented static issues and later actual visual findings in final repair-log.json.

## Rotation and safe geometry

In canvas coordinates y increases downward. Visualcounterclockwise8° requirestheta−8°. Column-major4×4 matrix:

`(0.9902680687,-0.139173101,0,0,0.139173101,0.9902680687,0,0,0,0,1,0,0,0,0,1)`

The rightward basis vector becomes(0.990268,−0.139173), so rightedge rises. Positive8° would rotate visuallyclockwise. Use `alignment="CENTER"` on the160×56tag. Proposed unrotatedx1080y696 gives center(1160,724). Rotatedpaintbounds arex1076.881708–1243.118292,y685.138646–762.861354; width166.236585,height77.722708. These are safely withinx32–1248,y32–768. Reviewisnotatunalteredyright32/bottom32 becausepaintrotationextendsbeyonditslayoutbox; retainadditionalinset.

## Alpha and filter proof

The20%backgroundalphais51/255exactly. UseContainercolor#FFFFFF33withopaqueText#FFFFFFinside, or a backgroundonlyOpacitylayer with siblingText. Do not wrap theentiretagincludingTextinOpacity0.2. Overbase#0B1220,thebackgroundexpectedfloatRGBis(60,65.4,76.6); realPNGmayround. Rootcaninspectarealinteriorpixelawayfromtexttoruleoutopaque/totallytransparentbackground, butpixelmathcannotreplacevisualinspection.

Centralcardproposedx390y416,500×150,borderRadius24. Stripes extendx150–1130andcrosscardleft390andright890. UseClipRRecttoensureBackdropFilteraffectsonlycardregion. RenderingthetextasachildofBackdropFilterisvalidbecausethefilterreadsthealready-paintedbackgroundanddoesnotblurthechildtext. Keepallstripescrispoutsidecardandblurredinside. Asemi-transparenttintstillallowsblurtobevisible;opaquewhitewouldhideit.

## Actualchecksneededfromproducer/root

Originalunmodifiedserviceattemptmustexist,withrequest/responsepreserved. RepairlogmustciteactualresponseIDsandpositionsratherthancopyinghypotheticalHTTPcodes. InspectfinalPNG1280×800andallregions:title44,LIVE96×36,equal3metricsat28,central500×150radius24withsharp28pxtext,visiblecrossingbackgroundstripes,Review160×56white20%opaque24pxtextandCCW8°,allsafe32margin. Noerrorblockmaybedroppedandsignedoffasrepaired.
