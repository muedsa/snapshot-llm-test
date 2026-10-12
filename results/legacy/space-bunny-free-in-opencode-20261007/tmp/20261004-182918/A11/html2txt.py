import html, re, sys

p = sys.argv[1]
out = sys.argv[2]
s = open(p, encoding="utf-8", errors="replace").read()
s = re.sub(r"<script[\s\S]*?</script>", " ", s)
s = re.sub(r"<style[\s\S]*?</style>", " ", s)
s = re.sub(r"<pre[^>]*>", "\n<<<CODE>>>\n", s)
s = re.sub(r"</pre>", "\n<<<ENDCODE>>>\n", s)
s = re.sub(r"<h([1-6])[^>]*>", lambda m: "\n\n" + "#" * int(m.group(1)) + " ", s)
s = re.sub(r"</h[1-6]>", "\n", s)
s = re.sub(r"<li[^>]*>", "\n- ", s)
s = re.sub(r"<br\s*/?>", "\n", s)
s = re.sub(r"</(p|div|tr|td|th|table|section)>", "\n", s)
s = re.sub(r"<[^>]+>", "", s)
s = html.unescape(s)
s = re.sub(r"\n{3,}", "\n\n", s)
s = re.sub(r"[ \t]{2,}", " ", s)
with open(out, "w", encoding="utf-8", newline="\n") as fh:
    fh.write(s.strip() + "\n")
print("wrote", out, len(s))