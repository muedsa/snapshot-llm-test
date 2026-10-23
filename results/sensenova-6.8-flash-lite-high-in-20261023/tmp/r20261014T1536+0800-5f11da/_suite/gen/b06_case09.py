"""B06 case-09: WiFi 密码安全分享
Problem: Sharing WiFi passwords by SMS is insecure and inconvenient
Solution: QR code based password sharing with visual security indicators
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b06_kit as K
from b06_kit import *

W, H = 800, 600
doc = Doc(W, H, BG_WHITE)

# Header
doc.text(40, 30, "WiFi 安全分享", 28, TEXT_PRIMARY, bold=True)
doc.text(40, 68, "扫码连接，无需口头告知密码", 16, TEXT_SECONDARY)

# QR Code area
doc.rect(40, 100, 260, 260, BG_LIGHT, 12)
doc.text_c(170, 115, "扫描连接", 16, TEXT_PRIMARY, bold=True)
# QR code simulation
qr_size = 180
qr_x, qr_y = 80, 140
# QR border
doc.rect(qr_x, qr_y, qr_size, qr_size, TEXT_PRIMARY, 0)
# QR pattern (simplified)
for i in range(12):
    for j in range(12):
        # Corner markers
        is_corner = (i < 3 and j < 3) or (i > 8 and j < 3) or (i < 3 and j > 8)
        # Random pattern for data area
        is_data = ((i+j) % 3 == 0) or (i == 6 and j == 6)
        if is_corner or is_data:
            doc.rect(qr_x + j*15 + 2, qr_y + i*15 + 2, 12, 11, TEXT_PRIMARY)
# Center logo
doc.circle(qr_x+90, qr_y+90, 25, BG_WHITE)
doc.text_c(qr_x+90, qr_y+82, "🔒", 16, ACCENT_GREEN)

# Network info
doc.rect(40, 380, 260, 80, BG_LIGHT, 10)
doc.text(60, 392, "网络名称", 12, TEXT_SECONDARY)
doc.text(60, 412, "MyHome_WiFi_5G", 16, TEXT_PRIMARY, bold=True)
doc.text(60, 438, "加密方式", 12, TEXT_SECONDARY)
doc.text(200, 438, "WPA3", 14, ACCENT_GREEN, bold=True)

# Security indicators
doc.rect(40, 480, 260, 80, BG_LIGHT, 10)
doc.text(60, 492, "安全等级", 12, TEXT_SECONDARY)
# Signal strength
doc.rect(60, 512, 4, 20, ACCENT_GREEN)
doc.rect(68, 508, 4, 24, ACCENT_GREEN)
doc.rect(76, 504, 4, 28, ACCENT_GREEN)
doc.rect(84, 500, 4, 32, ACCENT_GREEN)
doc.text(100, 510, "强信号", 14, ACCENT_GREEN, bold=True)
doc.text(60, 540, "✓ 密码已加密传输", 12, ACCENT_GREEN)

# Right side: How it works
doc.rect(320, 100, 420, 460, BG_LIGHT, 12)
doc.text(340, 115, "工作原理", 18, TEXT_PRIMARY, bold=True)

# Steps
steps = [
    ("生成二维码", "包含加密的WiFi配置信息", "1", ACCENT_BLUE),
    ("朋友扫码", "手机自动读取配置", "2", ACCENT_GREEN),
    ("自动连接", "无需手动输入密码", "3", ACCENT_ORANGE),
    ("安全完成", "密码不经过第三方", "4", ACCENT_PURPLE),
]
for i, (title, detail, num, color) in enumerate(steps):
    y = 150 + i*90
    doc.circle(350, y+20, 18, color)
    doc.text_c(350, y+14, num, 14, TEXT_LIGHT, bold=True)
    doc.text(380, y+5, title, 16, TEXT_PRIMARY, bold=True)
    doc.text(380, y+28, detail, 13, TEXT_SECONDARY)
    # Connection line
    if i < 3:
        doc.line_h(350, 350, y+40, BORDER, 2)

# Comparison
doc.rect(340, 475, 380, 65, BG_LIGHT, 10)
doc.text(360, 487, "对比传统方式", 14, TEXT_PRIMARY, bold=True)
doc.rect(360, 508, 170, 22, ACCENT_RED + "15", 4)
doc.text(375, 511, "✗ 口头告知密码", 13, ACCENT_RED)
doc.rect(540, 508, 170, 22, ACCENT_GREEN + "15", 4)
doc.text(555, 511, "✓ 扫码自动连接", 13, ACCENT_GREEN)

# Footer
doc.text(40, 580, "Wi-Fi Protected Setup 标准（演示用途）", 12, TEXT_SECONDARY)

gates = K.dry_run(doc, "case-09", 12, [], max_parts=9000)
K.save_gates("case-09", gates, "初始版本")
K.assert_gates(gates, "case-09")

stats = doc.stats()
print(f"Parts: {stats['parts']}, Texts: {stats['texts']}, Shapes: {stats['shapes']}")

result = K.render("case-09", doc, "WiFi 密码安全分享", "final", "")
print(json.dumps(result, ensure_ascii=False, indent=2))
