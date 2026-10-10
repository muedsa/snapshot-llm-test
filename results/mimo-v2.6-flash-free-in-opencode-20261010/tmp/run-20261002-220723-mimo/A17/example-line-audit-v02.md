# example line audit (-v02)  limit: 94 chars / 1040px at mono fs22

## example-01  lines = 18  (example-01-v02.snapshot)
  1 ( 231px) <Snapshot type="png">
  2 ( 594px)   <Container width="400" height="240" color="#0F172A">
  3 ( 132px)     <Column>
  4 ( 825px)       <Container width="400" height="56" color="#1D4ED8" padding="(14,24)">
  5 ( 715px)         <Text fontSize="26" color="#FFFFFF">POST /snapshot</Text>
  6 ( 198px)       </Container>
  7 ( 660px)       <Container width="400" height="184" padding="(12,24)">
  8 ( 473px)         <Column crossAxisAlignment="START">
  9 ( 869px)           <Text fontSize="20" color="#4ADE80">HTTP/1.1 200 OK  image/png</Text>
 10 ( 858px)           <Text fontSize="20" color="#94A3B8">请求体 = UTF-8 纯文本 DSL</Text>
 11 ( 814px)           <Text fontSize="20" color="#94A3B8">X-Request-Id 两边都有</Text>
 12 ( 847px)           <Text fontSize="20" color="#94A3B8">429 / 503 看 Retry-After</Text>
 13 ( 957px)           <Text fontSize="20" color="#FDE68A">error = {code, message, requestId}</Text>
 14 ( 187px)         </Column>
 15 ( 198px)       </Container>
 16 ( 143px)     </Column>
 17 ( 154px)   </Container>
 18 ( 121px) </Snapshot>

## example-02  lines = 18  (example-02-v02.snapshot)
  1 ( 231px) <Snapshot type="png">
  2 ( 737px)   <Container width="400" height="240" color="#0F172A" padding="24">
  3 ( 132px)     <Column>
  4 ( 506px)       <Container width="352" height="56"><Row>
  5 ( 759px)         <Expanded><Container height="56" color="#245CE4"/></Expanded>
  6 ( 649px)         <Container width="88" height="56" color="#E88E35"/>
  7 ( 264px)       </Row></Container>
  8 ( 638px)       <Container width="352" height="120" color="#E2E8F0">
  9 ( 165px)         <Stack>
 10 ( 990px)           <Positioned left="16" top="16" width="120" height="56"><Container color="lime"/>
 11 ( 253px)           </Positioned>
 12 ( 946px)           <Positioned right="16" bottom="14"><Text fontSize="20">right + bottom</Text>
 13 ( 253px)           </Positioned>
 14 ( 176px)         </Stack>
 15 ( 198px)       </Container>
 16 ( 143px)     </Column>
 17 ( 154px)   </Container>
 18 ( 121px) </Snapshot>

## example-03  lines = 18  (example-03-v02.snapshot)
  1 ( 231px) <Snapshot type="png">
  2 ( 737px)   <Container width="400" height="240" color="#0F172A" padding="12">
  3 ( 132px)     <Column>
  4 ( 803px)       <Text fontSize="20" color="#FFFFFF">tail alpha · Raw · CDATA</Text>
  5 ( 506px)       <Container width="376" height="48"><Row>
  6 ( 682px)         <Container width="125" height="48" color="#3B82F6FF"/>
  7 ( 682px)         <Container width="125" height="48" color="#3B82F680"/>
  8 ( 682px)         <Container width="126" height="48" color="#3B82F626"/>
  9 ( 264px)       </Row></Container>
 10 ( 792px)       <Text fontSize="20" color="#94A3B8">#RRGGBBAA not #AARRGGBB</Text>
 11 ( 858px)       <Text fontSize="20" color="#94A3B8">old #80FF0000 = new #FF000080</Text>
 12 ( 924px)       <Text fontSize="20" color="#CBD5E1"><![CDATA[CDATA keeps <tag> and &]]></Text>
 13 ( 880px)       <Text fontSize="20" color="#CBD5E1">Text<Raw>    keeps spaces</Raw></Text>
 14 ( 792px)       <Text fontSize="16" color="#94A3B8">FF = opaque, 26 = faint</Text>
 15 ( 781px)       <Text fontSize="16" color="#94A3B8">Kotlin DSL: 0xAARRGGBB</Text>
 16 ( 143px)     </Column>
 17 ( 154px)   </Container>
 18 ( 121px) </Snapshot>

## example-04  lines = 18  (example-04-v02.snapshot)
  1 ( 231px) <Snapshot type="png">
  2 ( 594px)   <Container width="400" height="240" color="#0F172A">
  3 ( 209px)     <Stack><Column>
  4 ( 638px)       <Container width="400" height="48" color="#245CE4"/>
  5 ( 638px)       <Container width="400" height="48" color="#E88E35"/>
  6 ( 638px)       <Container width="400" height="48" color="#22C55E"/>
  7 ( 638px)       <Container width="400" height="48" color="#E83D6B"/>
  8 ( 957px)       <ImageFiltered sigmaX="5" sigmaY="5"><Text fontSize="30" color="#FFF">BLUR</Text>
  9 ( 242px)       </ImageFiltered>
 10 ( 143px)     </Column>
 11 ( 638px)     <Positioned left="0" top="0" width="150" height="240">
 12 ( 594px)       <ClipRect><BackdropFilter sigmaX="8" sigmaY="8">
 13 ( 693px)         <Container width="150" height="240" color="#FFFFFF44"/>
 14 ( 374px)       </BackdropFilter></ClipRect>
 15 ( 187px)     </Positioned>
 16 ( 110px)   </Stack>
 17 ( 154px)   </Container>
 18 ( 121px) </Snapshot>

PROBLEMS = 0
