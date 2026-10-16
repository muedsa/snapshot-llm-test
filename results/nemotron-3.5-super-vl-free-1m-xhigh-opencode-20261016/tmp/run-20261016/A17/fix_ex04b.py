with open('tmp/run-20261016/A17/gen_a17.py','r',encoding='utf-8') as f:
    content = f.read()

old = '''        "dsl": '''<Snapshot background="#1E3A8A" type="png">
  <Positioned left="60" top="60" width="280" height="120">
    <Container color="#FFFFFF44" borderRadius="16">
      <Text color="#FFFFFF" fontSize="22" fontStyle="BOLD" textAlign="CENTER">半透明卡片</Text>
    </Container>
  </Positioned>
</Snapshot>''','''

new = '''        "dsl": '''<Snapshot background="#1E3A8A" type="png">
  <SizedBox width="400" height="240">
    <Stack alignment="TOP_LEFT">
      <Positioned left="60" top="60" width="280" height="120">
        <Container color="#FFFFFF44" borderRadius="16">
          <Text color="#FFFFFF" fontSize="22" fontStyle="BOLD" textAlign="CENTER">半透明卡片</Text>
        </Container>
      </Positioned>
    </Stack>
  </SizedBox>
</Snapshot>''','''

content = content.replace(old, new)
with open('tmp/run-20261016/A17/gen_a17.py','w',encoding='utf-8') as f:
    f.write(content)
print('Done')