"""Demo recorder — professional scroll-through video with title card."""
import sys
import os
import time
from PIL import Image, ImageDraw, ImageFont
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.microsoft import EdgeChromiumDriverManager

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

FPS = 25
VIDEO_OUT = "demo_output.mp4"
OUT_W, OUT_H = 1280, 720

os.makedirs("demo_frames", exist_ok=True)

# ═══════════════════════════════════════
# Step 1: Create title card
# ═══════════════════════════════════════
print("Creating title card...")
title = Image.new("RGB", (OUT_W, OUT_H), "#0F172A")  # Dark slate bg
draw = ImageDraw.Draw(title)

# Try to use a system font, fall back to default
try:
    font_large = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 52)
    font_medium = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 28)
    font_small = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 20)
except Exception:
    font_large = ImageFont.load_default()
    font_medium = font_large
    font_small = font_large

# Title text
lines = [
    ("跨境电商智能销售数据看板", font_large, "#38BDF8"),
    ("", font_small, "#FFFFFF"),
    ("Amazon + Shopify 多渠道数据 | AI Agent 自动分析", font_medium, "#94A3B8"),
    ("", font_small, "#FFFFFF"),
    ("Python · Pandas · Streamlit · LLM", font_small, "#64748B"),
    ("", font_small, "#FFFFFF"),
    ("", font_small, "#FFFFFF"),
    ("Demo for Insta360 跨境电商运营岗位", font_small, "#475569"),
]

y = 180
for text, font, color in lines:
    if text:
        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        x = (OUT_W - tw) // 2
        draw.text((x, y), text, fill=color, font=font)
        y += bbox[3] - bbox[1] + 8
    else:
        y += 20

title.save("demo_frames/00_title.png")
print("  [OK] Title card")

# ═══════════════════════════════════════
# Step 2: Capture Streamlit screenshots
# ═══════════════════════════════════════
opts = Options()
opts.add_argument("--window-size=1280,3000")
opts.add_argument("--force-device-scale-factor=1")
driver = webdriver.Edge(
    service=Service(EdgeChromiumDriverManager().install()),
    options=opts,
)

try:
    print("\nOpening Streamlit app...")
    driver.get("http://localhost:8501")
    time.sleep(5)

    # Screenshot 1: Full dashboard (KPIs + charts)
    driver.save_screenshot("demo_frames/01_dashboard.png")

    # Click AI report button
    driver.set_window_size(1280, 1000)
    time.sleep(0.5)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
    time.sleep(0.5)

    try:
        btn = driver.find_element(By.XPATH, "//button[@kind='primary']")
        btn.click()
        print("  AI report requested, waiting for response...")
        time.sleep(10)
    except Exception as e:
        print(f"  Button not found: {e}")

    # Screenshot 2: Report page
    driver.set_window_size(1280, 3000)
    time.sleep(1)
    driver.save_screenshot("demo_frames/02_report.png")

    # Screenshot 3: Middle section (charts detail)
    driver.set_window_size(1280, 1000)
    time.sleep(0.5)
    driver.execute_script("window.scrollTo(0, 350)")
    time.sleep(0.5)
    img = driver.get_screenshot_as_png()
    with open("demo_frames/02_charts.png", "wb") as f:
        f.write(img)

    print("  All screenshots captured.")

finally:
    driver.quit()

# ═══════════════════════════════════════
# Step 3: Build video frames
# ═══════════════════════════════════════
print("\nBuilding video frames...")

title_img = Image.open("demo_frames/00_title.png")
dash_img = Image.open("demo_frames/01_dashboard.png")
charts_img = Image.open("demo_frames/02_charts.png")
report_img = Image.open("demo_frames/02_report.png")

# Normalize all to 1280 width
def norm_width(img, w=1280):
    if img.size[0] != w:
        ratio = w / img.size[0]
        return img.resize((w, int(img.size[1] * ratio)), Image.LANCZOS)
    return img

title_img = norm_width(title_img)
dash_img = norm_width(dash_img)
charts_img = norm_width(charts_img)
report_img = norm_width(report_img)

print(f"  Title: {title_img.size}")
print(f"  Dashboard: {dash_img.size}")
print(f"  Charts: {charts_img.size}")
print(f"  Report: {report_img.size}")

# Create combined scroll image: title → dash → charts → report
# We'll treat each as a "scene" and create transitions

frames_dir = "demo_video_frames"
os.makedirs(frames_dir, exist_ok=True)

def lerp(a, b, t):
    return a + (b - a) * t

def crossfade(img1, img2, t):
    """Blend two images with alpha=t (t=0→img1, t=1→img2)."""
    return Image.blend(img1.resize((OUT_W, OUT_H), Image.LANCZOS),
                       img2.resize((OUT_W, OUT_H), Image.LANCZOS), t)

def crop_to(img, y, out_w=OUT_W, out_h=OUT_H):
    """Crop a viewport from img at vertical position y."""
    ih = img.size[1]
    y = max(0, min(y, ih - out_h))
    crop = img.crop((0, y, out_w, y + out_h))
    if crop.size != (out_w, out_h):
        crop = crop.resize((out_w, out_h), Image.LANCZOS)
    return crop

def save_frame(img, idx):
    img.save(os.path.join(frames_dir, f"frame_{idx:05d}.png"))

frame_idx = 0
total_secs = 0

def hold(img, duration_sec, y=0):
    global frame_idx, total_secs
    n = int(duration_sec * FPS)
    for _ in range(n):
        out = crop_to(img, y)
        save_frame(out, frame_idx)
        frame_idx += 1
    total_secs += duration_sec

def scroll(img, duration_sec, y_start, y_end):
    global frame_idx, total_secs
    n = int(duration_sec * FPS)
    for i in range(n):
        t = i / max(n - 1, 1)
        # Ease in-out
        if t < 0.5:
            et = 2 * t * t
        else:
            et = 1 - pow(-2 * t + 2, 2) / 2
        y = int(lerp(y_start, y_end, et))
        out = crop_to(img, y)
        save_frame(out, frame_idx)
        frame_idx += 1
    total_secs += duration_sec

def crossfade_seq(img1, img2, duration_sec):
    global frame_idx, total_secs
    n = int(duration_sec * FPS)
    for i in range(n):
        t = i / max(n - 1, 1)
        out = crossfade(img1, img2, t)
        save_frame(out, frame_idx)
        frame_idx += 1
    total_secs += duration_sec

# ── Timeline ──
# 0-3s: Title card
hold(title_img, 3.0)

# 3-4s: Crossfade title → dashboard
crossfade_seq(title_img, dash_img, 1.0)

# 4-7s: Dashboard KPI cards (top of dashboard)
dh = dash_img.size[1]
hold(dash_img, 3.0, y=0)

# 7-10s: Scroll down through charts
scroll(dash_img, 3.0, y_start=0, y_end=min(dh - OUT_H, 300))

# 10-12s: Hold on charts section
hold(dash_img, 2.0, y=min(dh - OUT_H, 300))

# 12-14s: Crossfade to report
crossfade_seq(dash_img, report_img, 2.0)

# 14-21s: Show AI report (scroll through it)
rh = report_img.size[1]
hold(report_img, 3.0, y=0)
scroll(report_img, 4.0, y_start=0, y_end=min(rh - OUT_H, max(rh - OUT_H, 100)))

print(f"  {frame_idx} frames, {total_secs:.1f}s total")

# ═══════════════════════════════════════
# Step 4: Encode MP4
# ═══════════════════════════════════════
print("\nEncoding MP4...")
os.system(
    f'ffmpeg -y -framerate {FPS} -i {frames_dir}/frame_%05d.png '
    f'-vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" '
    f'-c:v libx264 -pix_fmt yuv420p -preset fast -crf 23 '
    f'{VIDEO_OUT} 2>&1 | grep -E "frame=|error|Error|Done"'
)

if os.path.exists(VIDEO_OUT):
    size_kb = os.path.getsize(VIDEO_OUT) // 1024
    print(f"\n[DONE] {VIDEO_OUT} — {total_secs:.0f}s, {size_kb}KB")
    print("Ready for Insta360 demo!")
else:
    print("\n[ERROR] Encoding failed")
