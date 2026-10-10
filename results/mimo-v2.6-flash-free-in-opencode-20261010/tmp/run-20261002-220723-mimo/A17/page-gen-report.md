# handbook page generation report

## example-01  printed lines = 17
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
  11 ( 913px) <!--省略 example-01.snapshot 第 11、12 行（两条响应提示文本）；完整文件共 18 行 -->
  12 ( 957px)           <Text fontSize="20" color="#FDE68A">error = {code, message, requestId}</Text>
  13 ( 187px)         </Column>
  14 ( 198px)       </Container>
  15 ( 143px)     </Column>
  16 ( 154px)   </Container>
  17 ( 121px) </Snapshot>
  bullets max width ok, caption=818px, desc=480px
  wrote handbook-01-v03.snapshot  lines=63

## example-02  printed lines = 17
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
  12 ( 913px) <!--省略 example-02.snapshot 第 12、13 行（右下定位的第二块）；完整文件共 18 行 -->
  13 ( 176px)         </Stack>
  14 ( 198px)       </Container>
  15 ( 143px)     </Column>
  16 ( 154px)   </Container>
  17 ( 121px) </Snapshot>
  bullets max width ok, caption=818px, desc=504px
  wrote handbook-02-v03.snapshot  lines=63

## example-03  printed lines = 17
   1 ( 231px) <Snapshot type="png">
   2 ( 737px)   <Container width="400" height="240" color="#0F172A" padding="12">
   3 ( 132px)     <Column>
   4 ( 825px)       <Text fontSize="20" color="#FFFFFF">tail alpha · Raw · CDATA</Text>
   5 ( 506px)       <Container width="376" height="48"><Row>
   6 ( 682px)         <Container width="125" height="48" color="#3B82F6FF"/>
   7 ( 682px)         <Container width="125" height="48" color="#3B82F680"/>
   8 ( 682px)         <Container width="126" height="48" color="#3B82F626"/>
   9 ( 264px)       </Row></Container>
  10 ( 792px)       <Text fontSize="20" color="#94A3B8">#RRGGBBAA not #AARRGGBB</Text>
  11 ( 858px)       <Text fontSize="20" color="#94A3B8">old #80FF0000 = new #FF000080</Text>
  12 ( 924px)       <Text fontSize="20" color="#CBD5E1"><![CDATA[CDATA keeps <tag> and &]]></Text>
  13 ( 880px)       <Text fontSize="20" color="#CBD5E1">Text<Raw>    keeps spaces</Raw></Text>
  14 ( 847px) <!--省略 example-03.snapshot 第 14、15 行（两条图例行）；完整文件共 18 行 -->
  15 ( 143px)     </Column>
  16 ( 154px)   </Container>
  17 ( 121px) </Snapshot>
  bullets max width ok, caption=818px, desc=480px
  wrote handbook-03-v03.snapshot  lines=63

## example-04  printed lines = 17
   1 ( 231px) <Snapshot type="png">
   2 ( 594px)   <Container width="400" height="240" color="#0F172A">
   3 ( 132px)     <Column>
   4 ( 231px)       <Stack><Column>
   5 ( 803px) <!--省略 example-04.snapshot 第 5、6 行（两条色带）；完整文件共 18 行 -->
   6 ( 660px)         <Container width="400" height="48" color="#22C55E"/>
   7 ( 660px)         <Container width="400" height="48" color="#E83D6B"/>
   8 ( 165px)       </Column>
   9 ( 682px)         <Positioned left="0" top="0" width="150" height="192">
  10 ( 638px)           <ClipRect><BackdropFilter sigmaX="8" sigmaY="8">
  11 ( 737px)             <Container width="150" height="192" color="#FFFFFF44"/>
  12 ( 561px)           </BackdropFilter></ClipRect></Positioned>
  13 ( 154px)       </Stack>
  14 ( 957px)       <ImageFiltered sigmaX="5" sigmaY="5"><Text fontSize="30" color="#FFF">BLUR</Text>
  15 ( 242px)       </ImageFiltered>
  16 ( 275px)     </Column></Container>
  17 ( 121px) </Snapshot>
  bullets max width ok, caption=818px, desc=456px
  wrote handbook-04-v03.snapshot  lines=63
