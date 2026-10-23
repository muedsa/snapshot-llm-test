"""B05 shared utilities - UI design system for FlowDay app
Uses b01_kit's Doc class for DSL generation, adds UI component helpers.
"""
import sys, os, json
from pathlib import Path

# Import b01_kit for Doc, dry_run, save_gates, assert_gates
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b01_kit
from b01_kit import Doc, dry_run, save_gates, assert_gates

TASK = "B05"

# Override b01_kit's paths for B05
b01_kit.TASK = "B05"
b01_kit.OUT = b01_kit.ROOT / "outputs" / b01_kit.RUN_ID / "B05"
b01_kit.TMP = b01_kit.ROOT / "tmp" / b01_kit.RUN_ID / "B05"

# Import render_case after updating paths
from b01_kit import render_case

# ============================================================ Design System
# FlowDay - Modern productivity app

BG_WHITE = "#FFFFFF"
BG_LIGHT = "#F8F9FA"
BG_CARD = "#FFFFFF"
BG_MUTED = "#F1F3F5"
BG_DARK = "#1A1D23"

# Primary brand
PRIMARY = "#4F46E5"       # Indigo
PRIMARY_LIGHT = "#818CF8"
PRIMARY_DARK = "#3730A3"

# Accent colors
ACCENT_BLUE = "#3B82F6"
ACCENT_GREEN = "#10B981"
ACCENT_ORANGE = "#F59E0B"
ACCENT_RED = "#EF4444"
ACCENT_PURPLE = "#8B5CF6"
ACCENT_PINK = "#EC4899"
ACCENT_CYAN = "#06B6D4"

# Text
TEXT_PRIMARY = "#111827"
TEXT_SECONDARY = "#6B7280"
TEXT_MUTED = "#9CA3AF"
TEXT_WHITE = "#FFFFFF"

# Borders
BORDER_LIGHT = "#E5E7EB"
BORDER_MED = "#D1D5DB"

# Status colors
SUCCESS = "#10B981"
WARNING = "#F59E0B"
DANGER = "#EF4444"
INFO = "#3B82F6"

# Category colors (for task types)
CAT_WORK = "#3B82F6"
CAT_PERSONAL = "#10B981"
CAT_HEALTH = "#EF4444"
CAT_LEARNING = "#F59E0B"
CAT_SOCIAL = "#8B5CF6"
CAT_BREAK = "#6B7280"

# Spacing
SP_S = 8
SP_M = 16
SP_L = 24
SP_XL = 40

# Border radius
RADIUS_SM = 8
RADIUS_MD = 12
RADIUS_LG = 16
RADIUS_FULL = 9999

# Shadow simulation
SHADOW = "#E5E7EB"


def create_doc(w=400, h=800, bg=BG_WHITE):
    """Create a new Doc for mobile UI (phone screen)"""
    return Doc(w, h, bg)


# ============================================================ Add UI methods to Doc
# Monkey-patch the Doc class to include UI component methods
from b01_kit import Doc as BaseDoc

class UIDoc(BaseDoc):
    """UI-specific Doc with FlowDay design system components"""

    # Override rect to use color parameter name
    def rect(self, x, y, w, h, color=None, radius=0, border=None, opacity=None,
             fill=None, stroke=None, stroke_width=1, owner="rect"):
        """Rectangle - accepts both color/fill and border/stroke"""
        if fill is not None and color is None:
            color = fill
        if stroke is not None and border is None:
            border = stroke
        # Format border as "width SOLID color" for DSL
        if border and isinstance(border, str) and border.startswith("#"):
            border = f"{stroke_width} SOLID {border}"
        return super().rect(x, y, w, h, color=color, radius=radius,
                           border=border, opacity=opacity, owner=owner)

    # Override text to accept content parameter
    def text(self, x, y, s=None, fs=20, color="#0F172A", bold=False, owner="txt",
             anchor="left", right=None, center=None, content=None, size=None):
        """Text - accepts both s/content and fs/size"""
        if content is not None and s is None:
            s = content
        if size is not None and fs == 20:
            fs = size
        return super().text(x, y, s, fs, color, bold, owner, anchor, right, center)

    # Override circle to accept fill parameter
    def circle(self, cx, cy, r, color=None, fill=None, step=1.0, owner="circle",
               segs=96, stroke=None, sw=2):
        """Circle - accepts both color/fill"""
        if fill is not None and color is None:
            color = fill
        if stroke is not None:
            # Draw circle with border
            super().circle(cx, cy, r, color, step=step, owner=owner, segs=segs)
            return
        return super().circle(cx, cy, r, color, step=step, owner=owner, segs=segs)

    # Override line_h to accept width parameter
    def line_h(self, x0, x1, y, color, w=1, width=None):
        """Horizontal line - accepts both w/width"""
        if width is not None and w == 1:
            w = width
        return super().line_h(x0, x1, y, color, w)

    # ============================================================ Status Bar
    def status_bar(self, y=0, bg_color=BG_WHITE, text_color=TEXT_PRIMARY):
        """Status bar - accepts y, bg_color, text_color"""
        if bg_color != BG_WHITE:
            self.rect(0, 0, self.w, 40, color=bg_color)
        self.text(32, y+14, "9:41", 14, text_color, bold=True)
        self.text_r(368, y+14, "📶 🔋", 12, text_color)

    # ============================================================ Navigation
    def nav_bar(self, y, title, show_back=False, right_btn=None):
        self.rect(0, y, self.w, 56, color=BG_WHITE)
        self.line_h(0, self.w, y+56, BORDER_LIGHT)
        self.text_c(self.w//2, y+18, title, 18, TEXT_PRIMARY, bold=True)
        if show_back:
            self.text(20, y+18, "←", 20, PRIMARY)
        if right_btn:
            self.text_r(self.w-32, y+18, right_btn, 14, PRIMARY)

    def bottom_tab_bar(self, y, active_idx=0, items=None):
        if items is None:
            items = ["🏠 首页", "📅 日历", "➕ 快速", "📊 统计", "⚙️ 设置"]
        self.rect(0, y, self.w, 80, color=BG_WHITE)
        self.line_h(0, self.w, y, BORDER_LIGHT)
        n = len(items)
        item_w = self.w / n
        for i, item in enumerate(items):
            x = int(item_w * i + item_w / 2)
            color = PRIMARY if i == active_idx else TEXT_MUTED
            bold = i == active_idx
            self.text_c(x, y+22, item, 12, color, bold=bold)

    # ============================================================ Cards
    def bg_section(self, x, y, w, h, color=BG_LIGHT, radius=0):
        self.rect(x, y, w, h, color=color, radius=radius)

    def rect_shadow(self, x, y, w, h, fill=BG_CARD, radius=RADIUS_MD,
                    shadow_offset=4, shadow_color="#F0F0F0"):
        self.rect(x+shadow_offset, y+shadow_offset, w, h, color=shadow_color,
                 radius=radius, opacity=0.5)
        self.rect(x, y, w, h, color=fill, radius=radius)

    def card(self, x, y, w, h, fill=BG_CARD, radius=RADIUS_MD, shadow=True):
        if shadow:
            self.rect(x+3, y+3, w, h, color="#F0F0F0", radius=radius, opacity=0.5)
        self.rect(x, y, w, h, color=fill, radius=radius)

    def section_bg(self, x, y, w, h, color=BG_LIGHT, radius=0):
        self.rect(x, y, w, h, color=color, radius=radius)

    # ============================================================ Buttons
    def button(self, x, y, w, h, text, fill=PRIMARY, text_color=TEXT_WHITE,
               radius=RADIUS_MD, bold=True):
        self.rect(x, y, w, h, color=fill, radius=radius)
        self.text_c(x+w//2, y+8, text, 14, text_color, bold=bold)

    def pill_button(self, x, y, w, h, text, fill=PRIMARY, text_color=TEXT_WHITE):
        self.rect(x, y, w, h, color=fill, radius=h//2)
        self.text_c(x+w//2, y+4, text, 12, text_color, bold=True)

    def icon_button(self, x, y, size, icon, color=PRIMARY, bg=BG_MUTED):
        self.rect(x, y, size, size, color=bg, radius=size//2)
        self.text_c(x+size//2, y+size//2-6, icon, int(size*0.5), color)

    # ============================================================ Progress
    def progress_bar(self, x, y, w, h, progress, color=PRIMARY, bg=BG_MUTED):
        self.rect(x, y, w, h, color=bg, radius=h//2)
        fill_w = max(2, int(w * progress))
        self.rect(x, y, fill_w, h, color=color, radius=h//2)

    def progress_ring(self, cx, cy, r, progress, color=PRIMARY, bg=BG_MUTED,
                      thickness=6):
        self.circle(cx, cy, r, color=bg)
        self.circle(cx, cy, r-thickness, color=BG_WHITE)
        pct_text = f"{int(progress*100)}%"
        self.text_c(cx, cy-8, pct_text, int(r*0.5), color, bold=True)

    # ============================================================ Badges & Chips
    def pill(self, x, y, w, h, fill=PRIMARY, text_color=TEXT_WHITE):
        """Pill-shaped element"""
        self.rect(x, y, w, h, color=fill, radius=h//2)

    def badge(self, x, y, text, color=PRIMARY, text_color=TEXT_WHITE):
        w = max(32, len(text)*10 + 16)
        h = 24
        self.rect(x, y, w, h, color=color, radius=h//2)
        self.text_c(x+w//2, y+4, text, 12, text_color, bold=True)
        return w

    def chip(self, x, y, text, color=BG_MUTED, text_color=TEXT_PRIMARY,
             selected=False):
        w = len(text)*10 + 24
        h = 32
        bg = color if not selected else PRIMARY
        tc = text_color if not selected else TEXT_WHITE
        self.rect(x, y, w, h, color=bg, radius=h//2)
        self.text_c(x+w//2, y+6, text, 12, tc, bold=selected)
        return w

    # ============================================================ Task Cards
    def task_card(self, x, y, w, h, title, subtitle=None, icon=None,
                  accent_color=PRIMARY, icon_color=None):
        self.card(x, y, w, h)
        self.rect(x, y, 4, h, color=accent_color, radius=2)
        if icon:
            self.circle(x+28, y+28, 16, color=icon_color or accent_color)
            self.text_c(x+28, y+22, icon, 12, TEXT_WHITE)
        tx = x + 54 if icon else x + 16
        self.text(tx, y+16, title, 14, TEXT_PRIMARY, bold=True)
        if subtitle:
            self.text(tx, y+38, subtitle, 12, TEXT_SECONDARY)

    # ============================================================ Time Blocks
    def time_block(self, x, y, w, h, time_str, title, category_color=CAT_WORK):
        self.rect(x, y, w, h, color=category_color + "33", radius=RADIUS_SM)
        self.rect(x, y, 3, h, color=category_color)
        if time_str:
            self.text(x+10, y+6, time_str, 12, TEXT_SECONDARY)
        self.text(x+10, y+22, title, 13, TEXT_PRIMARY, bold=True)

    # ============================================================ Stats
    def stat_tile(self, x, y, w, h, label, value, unit="", color=PRIMARY):
        self.card(x, y, w, h)
        self.text_c(x+w//2, y+20, value, 28, color, bold=True)
        if unit:
            self.text_c(x+w//2, y+55, unit, 12, TEXT_MUTED)
        self.text_c(x+w//2, y+h-28, label, 13, TEXT_SECONDARY)

    # ============================================================ Avatars
    def avatar(self, cx, cy, r, color=PRIMARY, letter=""):
        self.circle(cx, cy, r, color=color)
        if letter:
            self.text_c(cx, cy-2, letter, max(12, int(r*0.8)), TEXT_WHITE, bold=True)

    # ============================================================ Form Elements
    def checkbox(self, x, y, size=20, checked=False, color=PRIMARY):
        if checked:
            self.rect(x, y, size, size, color=color, radius=4)
            self.text_c(x+size//2, y+2, "✓", 12, TEXT_WHITE)
        else:
            self.rect(x, y, size, size, color=BG_WHITE, radius=4, border=BORDER_MED)

    def radio(self, x, y, size=20, selected=False, color=PRIMARY):
        self.circle(x+size//2, y+size//2, size//2, color=BG_WHITE)
        if selected:
            self.circle(x+size//2, y+size//2, size//3, color=color)

    def toggle(self, x, y, w=44, h=24, on=False, color=PRIMARY):
        bg = color if on else BORDER_MED
        self.rect(x, y, w, h, color=bg, radius=h//2)
        circle_x = x + w - h//2 if on else x + h//2
        self.circle(circle_x, y+h//2, h//2-2, color=BG_WHITE)

    # ============================================================ List Items
    def list_item(self, x, y, w, h, title, subtitle=None, icon=None,
                  right_text=None, chevron=True):
        self.rect(x, y, w, h, color=BG_LIGHT, radius=RADIUS_SM)
        if icon:
            self.circle(x+28, y+h//2, 16, color=BG_MUTED)
            self.text_c(x+28, y+h//2-6, icon, 12, TEXT_SECONDARY)
        tx = x + 54 if icon else x + 16
        self.text(tx, y+16, title, 14, TEXT_PRIMARY, bold=True)
        if subtitle:
            self.text(tx, y+38, subtitle, 12, TEXT_SECONDARY)
        if right_text:
            self.text_r(x+w-40, y+18, right_text, 13, TEXT_MUTED)
        if chevron:
            self.text_r(x+w-16, y+16, "›", 18, TEXT_MUTED)

    # ============================================================ Calendar
    def date_pill(self, x, y, w, h, day_name="", day_num=None, selected=False,
                  has_event=False, event_color=None):
        bg = PRIMARY if selected else BG_WHITE
        text_color = TEXT_WHITE if selected else TEXT_PRIMARY
        border = BORDER_LIGHT if not selected else None
        self.rect(x, y, w, h, color=bg, radius=RADIUS_SM, border=border)
        if day_num is not None:
            self.text_c(x+w//2, y+8, str(day_num), 16, text_color, bold=True)
        elif day_name:
            self.text_c(x+w//2, y+8, day_name, 12, text_color, bold=True)
        if has_event and not selected:
            self.circle(x+w-8, y+h-8, 4, color=event_color or ACCENT_BLUE)

    def week_pill(self, x, y, w, h, day_name, day_num, selected=False):
        bg = PRIMARY if selected else BG_MUTED
        text_color = TEXT_WHITE if selected else TEXT_SECONDARY
        self.rect(x, y, w, h, color=bg, radius=RADIUS_MD)
        self.text_c(x+w//2, y+4, day_name, 12,
                     TEXT_WHITE if selected else TEXT_MUTED)
        self.text_c(x+w//2, y+20, str(day_num), 18, text_color, bold=True)

    # ============================================================ Modal
    def modal_sheet(self, x, y, w, h, title=None):
        self.card(x, y, w, h, radius=RADIUS_LG, shadow=True)
        self.rect(x+w//2-24, y+10, 48, 4, color=BORDER_MED, radius=2)
        if title:
            self.text_c(x+w//2, y+28, title, 18, TEXT_PRIMARY, bold=True)
            self.divider(x+24, y+56, w-48)

    # ============================================================ Misc
    def divider(self, x, y, w, color=BORDER_LIGHT):
        self.line_h(x, x+w, y, color, 1)

    def empty_state(self, cx, cy, icon, title, subtitle=None):
        self.circle(cx, cy-40, 40, color=BG_MUTED)
        self.text_c(cx, cy-48, icon, 28, TEXT_MUTED)
        self.text_c(cx, cy+20, title, 16, TEXT_SECONDARY, bold=True)
        if subtitle:
            self.text_c(cx, cy+45, subtitle, 13, TEXT_MUTED)


# Replace Doc with UIDoc
Doc = UIDoc


# ============================================================ UI Component Helpers
class UIDoc:
    """UI-specific wrapper around b01_kit Doc"""

    def __init__(self, doc):
        self.doc = doc
        self.w = doc.w
        self.h = doc.h

    # ============================================================ Status Bar
    def status_bar(self, y=0, text_color=TEXT_PRIMARY):
        """iOS-style status bar"""
        self.doc.text(32, y+14, "9:41", 14, text_color, bold=True)
        self.doc.text_r(368, y+14, "📶 🔋", 12, text_color)

    # ============================================================ Navigation
    def nav_bar(self, y, title, show_back=False, right_btn=None):
        """Navigation bar with title"""
        self.doc.rect(0, y, self.w, 56, BG_WHITE)
        self.doc.line_h(0, self.w, y+56, BORDER_LIGHT)
        self.doc.text_c(self.w//2, y+18, title, 18, TEXT_PRIMARY, bold=True)
        if show_back:
            self.doc.text(20, y+18, "←", 20, PRIMARY)
        if right_btn:
            self.doc.text_r(self.w-32, y+18, right_btn, 14, PRIMARY)

    def bottom_tab_bar(self, y, active_idx=0, items=None):
        """Bottom tab bar"""
        if items is None:
            items = ["🏠 首页", "📅 日历", "➕ 快速", "📊 统计", "⚙️ 设置"]
        self.doc.rect(0, y, self.w, 80, BG_WHITE)
        self.doc.line_h(0, self.w, y, BORDER_LIGHT)
        n = len(items)
        item_w = self.w / n
        for i, item in enumerate(items):
            x = int(item_w * i + item_w / 2)
            color = PRIMARY if i == active_idx else TEXT_MUTED
            bold = i == active_idx
            self.doc.text_c(x, y+22, item, 12, color, bold=bold)

    # ============================================================ Cards & Containers
    def card(self, x, y, w, h, fill=BG_CARD, radius=RADIUS_MD, shadow=True):
        """Card with optional shadow"""
        if shadow:
            self.doc.rect(x+3, y+3, w, h, "#F0F0F0", radius=radius, opacity=0.5)
        self.doc.rect(x, y, w, h, fill, radius=radius)

    def section_bg(self, x, y, w, h, color=BG_LIGHT, radius=0):
        """Section background"""
        self.doc.rect(x, y, w, h, color, radius=radius)

    # ============================================================ Buttons
    def button(self, x, y, w, h, text, fill=PRIMARY, text_color=TEXT_WHITE,
               radius=RADIUS_MD, bold=True):
        """Button with text"""
        self.doc.rect(x, y, w, h, fill, radius=radius)
        self.doc.text_c(x+w//2, y+8, text, 14, text_color, bold=bold)

    def pill_button(self, x, y, w, h, text, fill=PRIMARY, text_color=TEXT_WHITE):
        """Pill-shaped button"""
        self.doc.rect(x, y, w, h, fill, radius=h//2)
        self.doc.text_c(x+w//2, y+4, text, 12, text_color, bold=True)

    def icon_button(self, x, y, size, icon, color=PRIMARY, bg=BG_MUTED):
        """Icon button"""
        self.doc.rect(x, y, size, size, bg, radius=size//2)
        self.doc.text_c(x+size//2, y+size//2-6, icon, int(size*0.5), color)

    # ============================================================ Progress
    def progress_bar(self, x, y, w, h, progress, color=PRIMARY, bg=BG_MUTED):
        """Horizontal progress bar"""
        self.doc.rect(x, y, w, h, bg, radius=h//2)
        fill_w = max(2, int(w * progress))
        self.doc.rect(x, y, fill_w, h, color, radius=h//2)

    def progress_ring(self, cx, cy, r, progress, color=PRIMARY, bg=BG_MUTED,
                      thickness=6):
        """Circular progress indicator"""
        self.doc.circle(cx, cy, r, bg)
        self.doc.circle(cx, cy, r-thickness, BG_WHITE)
        pct_text = f"{int(progress*100)}%"
        self.doc.text_c(cx, cy-8, pct_text, int(r*0.5), color, bold=True)

    # ============================================================ Badges & Chips
    def pill(self, x, y, w, h, fill=PRIMARY, text_color=TEXT_WHITE):
        """Pill-shaped element"""
        self.rect(x, y, w, h, color=fill, radius=h//2)

    def badge(self, x, y, text, color=PRIMARY, text_color=TEXT_WHITE):
        """Small badge/tag"""
        w = max(32, len(text)*10 + 16)
        h = 24
        self.doc.rect(x, y, w, h, color, radius=h//2)
        self.doc.text_c(x+w//2, y+4, text, 12, text_color, bold=True)
        return w

    def chip(self, x, y, text, color=BG_MUTED, text_color=TEXT_PRIMARY,
             selected=False):
        """Filter chip"""
        w = len(text)*10 + 24
        h = 32
        bg = color if not selected else PRIMARY
        tc = text_color if not selected else TEXT_WHITE
        self.doc.rect(x, y, w, h, bg, radius=h//2)
        self.doc.text_c(x+w//2, y+6, text, 12, tc, bold=selected)
        return w

    # ============================================================ Task Cards
    def task_card(self, x, y, w, h, title, subtitle=None, icon=None,
                  accent_color=PRIMARY, icon_color=None):
        """Task card with icon, title, subtitle"""
        self.card(x, y, w, h)
        # Accent bar on left
        self.doc.rect(x, y, 4, h, accent_color, radius=2)
        # Icon
        if icon:
            self.doc.circle(x+28, y+28, 16, icon_color or accent_color)
            self.doc.text_c(x+28, y+22, icon, 12, TEXT_WHITE)
        # Title
        tx = x + 54 if icon else x + 16
        self.doc.text(tx, y+16, title, 14, TEXT_PRIMARY, bold=True)
        # Subtitle
        if subtitle:
            self.doc.text(tx, y+38, subtitle, 12, TEXT_SECONDARY)

    # ============================================================ Time Blocks
    def time_block(self, x, y, w, h, time_str, title, category_color=CAT_WORK):
        """Calendar time block"""
        self.doc.rect(x, y, w, h, category_color + "33", radius=RADIUS_SM)
        self.doc.rect(x, y, 3, h, category_color)
        if time_str:
            self.doc.text(x+10, y+6, time_str, 12, TEXT_SECONDARY)
        self.doc.text(x+10, y+22, title, 13, TEXT_PRIMARY, bold=True)

    # ============================================================ Stats
    def stat_tile(self, x, y, w, h, label, value, unit="", color=PRIMARY):
        """Statistics tile"""
        self.card(x, y, w, h)
        self.doc.text_c(x+w//2, y+20, value, 28, color, bold=True)
        if unit:
            self.doc.text_c(x+w//2, y+55, unit, 12, TEXT_MUTED)
        self.doc.text_c(x+w//2, y+h-28, label, 13, TEXT_SECONDARY)

    # ============================================================ Avatars
    def avatar(self, cx, cy, r, color=PRIMARY, letter=""):
        """User avatar circle"""
        self.doc.circle(cx, cy, r, color)
        if letter:
            self.doc.text_c(cx, cy-2, letter, max(12, int(r*0.8)), TEXT_WHITE, bold=True)

    # ============================================================ Form Elements
    def checkbox(self, x, y, size=20, checked=False, color=PRIMARY):
        """Checkbox"""
        if checked:
            self.doc.rect(x, y, size, size, color, radius=4)
            self.doc.text_c(x+size//2, y+2, "✓", 12, TEXT_WHITE)
        else:
            self.doc.rect(x, y, size, size, BG_WHITE, radius=4, border=BORDER_MED)

    def radio(self, x, y, size=20, selected=False, color=PRIMARY):
        """Radio button"""
        self.doc.circle(x+size//2, y+size//2, size//2, BG_WHITE, border=color if selected else BORDER_MED)
        if selected:
            self.doc.circle(x+size//2, y+size//2, size//3, color)

    def toggle(self, x, y, w=44, h=24, on=False, color=PRIMARY):
        """Toggle switch"""
        bg = color if on else BORDER_MED
        self.doc.rect(x, y, w, h, bg, radius=h//2)
        circle_x = x + w - h//2 if on else x + h//2
        self.doc.circle(circle_x, y+h//2, h//2-2, BG_WHITE)

    # ============================================================ List Items
    def list_item(self, x, y, w, h, title, subtitle=None, icon=None,
                  right_text=None, chevron=True):
        """List item with optional icon, title, subtitle, right text"""
        self.doc.rect(x, y, w, h, BG_LIGHT, radius=RADIUS_SM)
        if icon:
            self.doc.circle(x+28, y+h//2, 16, BG_MUTED)
            self.doc.text_c(x+28, y+h//2-6, icon, 12, TEXT_SECONDARY)
        tx = x + 54 if icon else x + 16
        self.doc.text(tx, y+16, title, 14, TEXT_PRIMARY, bold=True)
        if subtitle:
            self.doc.text(tx, y+38, subtitle, 12, TEXT_SECONDARY)
        if right_text:
            self.doc.text_r(x+w-40, y+18, right_text, 13, TEXT_MUTED)
        if chevron:
            self.doc.text_r(x+w-16, y+16, "›", 18, TEXT_MUTED)

    # ============================================================ Calendar
    def date_pill(self, x, y, w, h, day_num, selected=False,
                  has_event=False, event_color=None):
        """Calendar date pill"""
        bg = PRIMARY if selected else BG_WHITE
        text_color = TEXT_WHITE if selected else TEXT_PRIMARY
        border = BORDER_LIGHT if not selected else None
        self.doc.rect(x, y, w, h, bg, radius=RADIUS_SM, border=border)
        self.doc.text_c(x+w//2, y+8, str(day_num), 16, text_color, bold=True)
        if has_event and not selected:
            self.doc.circle(x+w-8, y+h-8, 4, event_color or ACCENT_BLUE)

    def week_pill(self, x, y, w, h, day_name, day_num, selected=False):
        """Week calendar pill"""
        bg = PRIMARY if selected else BG_MUTED
        text_color = TEXT_WHITE if selected else TEXT_SECONDARY
        self.doc.rect(x, y, w, h, bg, radius=RADIUS_MD)
        self.doc.text_c(x+w//2, y+4, day_name, 10,
                         TEXT_WHITE if selected else TEXT_MUTED)
        self.doc.text_c(x+w//2, y+18, str(day_num), 18, text_color, bold=True)

    # ============================================================ Modal
    def modal_sheet(self, x, y, w, h, title=None):
        """Modal sheet from bottom"""
        self.card(x, y, w, h, radius=RADIUS_LG, shadow=True)
        # Handle
        self.doc.rect(x+w//2-24, y+10, 48, 4, BORDER_MED, radius=2)
        if title:
            self.doc.text_c(x+w//2, y+28, title, 18, TEXT_PRIMARY, bold=True)
            self.doc.divider(x+24, y+56, w-48)

    # ============================================================ Misc
    def divider(self, x, y, w, color=BORDER_LIGHT):
        """Divider line"""
        self.doc.line_h(x, x+w, y, color, 1)

    def empty_state(self, cx, cy, icon, title, subtitle=None):
        """Empty state illustration"""
        self.doc.circle(cx, cy-40, 40, BG_MUTED)
        self.doc.text_c(cx, cy-48, icon, 28, TEXT_MUTED)
        self.doc.text_c(cx, cy+20, title, 16, TEXT_SECONDARY, bold=True)
        if subtitle:
            self.doc.text_c(cx, cy+45, subtitle, 13, TEXT_MUTED)
