"""
ساخت دیتاست ارقام سودوکو با رندر فونت‌ها + Augmentation
خروجی: data/X_train.npy, y_train.npy, X_test.npy, y_test.npy
"""

import os
import glob
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from tqdm import tqdm
import matplotlib.pyplot as plt

# ============================================================
# بخش ۱: پیدا کردن فونت‌های سیستم
# ============================================================

def find_system_fonts():
    """فونت‌های TTF/OTF موجود روی سیستم رو پیدا می‌کنه"""
    if os.name == "nt":  # ویندوز
        font_dirs = [
            "C:/Windows/Fonts",
            os.path.expanduser("~/AppData/Local/Microsoft/Windows/Fonts"),
        ]
    elif os.name == "posix":  # لینوکس/مک
        font_dirs = [
            "/usr/share/fonts",
            "/usr/local/share/fonts",
            os.path.expanduser("~/.fonts"),
            "/Library/Fonts",
        ]
    else:
        font_dirs = []

    fonts = []
    for d in font_dirs:
        if os.path.exists(d):
            fonts.extend(glob.glob(os.path.join(d, "**", "*.ttf"), recursive=True))
            fonts.extend(glob.glob(os.path.join(d, "**", "*.otf"), recursive=True))
    return fonts

# ============================================================
# بخش ۲: فیلتر فونت‌های نامناسب
# ============================================================

BAD_FONT_KEYWORDS = [
    "wingding", "webding", "symbol", "marlett", "bookshelf",
    "icon", "emoji", "segmdl2", "holomdl2",
    "cambria math", "msmincho", "msgothic",
    "barcode", "qr", "pict",
]


def is_good_font(font_path):
    """بررسی می‌کنه فونت برای ارقام سودوکو مناسبه"""
    name = os.path.basename(font_path).lower()
    for bad in BAD_FONT_KEYWORDS:
        if bad in name:
            return False
    try:
        font = ImageFont.truetype(font_path, size=20)
        bbox = font.getbbox("1")
        if bbox[2] - bbox[0] < 1:
            return False
    except Exception:
        return False
    return True

# ============================================================
# بخش ۳: توابع کمکی رندر
# ============================================================

def crop_to_content(img, bg_color):
    """نواحی خالی اطراف متن رو حذف می‌کنه"""
    arr = np.array(img)
    if bg_color == 255:
        mask = arr < 200
    else:
        mask = arr > 55
    if not mask.any():
        return img
    rows = np.any(mask, axis=1)
    cols = np.any(mask, axis=0)
    y1, y2 = np.where(rows)[0][[0, -1]]
    x1, x2 = np.where(cols)[0][[0, -1]]
    return img.crop((x1, y1, x2 + 1, y2 + 1))


def to_mnist_format(img, bg_color):
    """تبدیل به 28×28 با حاشیه‌ی ۴ پیکسلی (استاندارد MNIST)"""
    w, h = img.size
    size = max(w, h)
    square = Image.new("L", (size, size), color=bg_color)
    square.paste(img, ((size - w) // 2, (size - h) // 2))
    digit = square.resize((20, 20), Image.LANCZOS)
    final = Image.new("L", (28, 28), color=bg_color)
    final.paste(digit, (4, 4))
    return final


def render_digit(digit, font_path, canvas_size=100, font_size=80,
                 color_mode="black_on_white"):
    """یه رقم رو با فونت مشخص رندر می‌کنه → np.array (28, 28)"""
    if color_mode == "black_on_white":
        bg_color, fg_color = 255, 0
    else:
        bg_color, fg_color = 0, 255

    img = Image.new("L", (canvas_size, canvas_size), color=bg_color)
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype(font_path, size=font_size)
    except Exception:
        return None

    text = str(digit)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    x = (canvas_size - text_w) // 2 - bbox[0]
    y = (canvas_size - text_h) // 2 - bbox[1]

    draw.text((x, y), text, fill=fg_color, font=font)

    img = crop_to_content(img, bg_color)
    img = to_mnist_format(img, bg_color)
    return np.array(img, dtype=np.uint8)

# ============================================================
# بخش ۴: Augmentation (۷ نوع تغییر)
# ============================================================

def augment_digit(img_array, bg_color=255):
    """یه نسخه‌ی تصادفی augment‌شده برمی‌گردونه"""
    img = Image.fromarray(img_array)

    # ۱. چرخش کوچیک
    if random.random() < 0.7:
        angle = random.uniform(-10, 10)
        img = img.rotate(angle, resample=Image.BILINEAR,
                         fillcolor=bg_color, expand=False)

    # ۲. جابه‌جایی
    if random.random() < 0.6:
        dx = random.randint(-2, 2)
        dy = random.randint(-2, 2)
        img = img.transform(
            img.size, Image.AFFINE,
            (1, 0, dx, 0, 1, dy),
            fillcolor=bg_color, resample=Image.BILINEAR
        )

    # ۳. تغییر مقیاس
    if random.random() < 0.5:
        scale = random.uniform(0.85, 1.1)
        new_size = int(28 * scale)
        img = img.resize((new_size, new_size), Image.LANCZOS)
        canvas = Image.new("L", (28, 28), color=bg_color)
        offset = (28 - new_size) // 2
        canvas.paste(img, (offset, offset))
        img = canvas

    # ۴. تغییر ضخامت
    if random.random() < 0.4:
        if random.random() < 0.5:
            img = img.filter(ImageFilter.MaxFilter(3))
        else:
            img = img.filter(ImageFilter.MinFilter(3))

    # ۵. Blur
    if random.random() < 0.3:
        radius = random.uniform(0.3, 0.8)
        img = img.filter(ImageFilter.GaussianBlur(radius))

    # ۶. روشنایی/کنتراست
    if random.random() < 0.4:
        arr = np.array(img).astype(np.float32)
        factor = random.uniform(0.85, 1.15)
        arr = np.clip(arr * factor, 0, 255)
        img = Image.fromarray(arr.astype(np.uint8))

    # ۷. نویز نمکی-فلفلی
    if random.random() < 0.2:
        arr = np.array(img)
        for _ in range(random.randint(5, 20)):
            x = random.randint(0, 27)
            y = random.randint(0, 27)
            arr[y, x] = random.choice([0, 255])
        img = Image.fromarray(arr)

    return np.array(img, dtype=np.uint8)

# ============================================================
# بخش ۵: ساخت دیتاست کامل
# ============================================================

def generate_dataset(fonts, num_variations_per_font=20,
                     augment_ratio=2, seed=42):
    random.seed(seed)
    np.random.seed(seed)
    X_all, y_all = [], []

    print(f"🔨 شروع رندر با {len(fonts)} فونت...")

    for font_path in tqdm(fonts, desc="Fonts"):
        for digit in range(1, 10):
            for _ in range(num_variations_per_font):
                font_size = random.randint(60, 90)
                color_mode = random.choice(
                    ["black_on_white", "black_on_white", "white_on_black"]
                )
                bg_color = 255 if color_mode == "black_on_white" else 0

                img = render_digit(digit, font_path,
                                   font_size=font_size,
                                   color_mode=color_mode)
                if img is None:
                    continue

                X_all.append(img)
                y_all.append(digit - 1)

                for _ in range(augment_ratio):
                    aug_img = augment_digit(img.copy(), bg_color)
                    X_all.append(aug_img)
                    y_all.append(digit - 1)

    X_all = np.array(X_all, dtype=np.uint8)
    y_all = np.array(y_all, dtype=np.int32)

    print(f"\n✅ کل نمونه‌ها: {len(X_all)}")
    for d in range(9):
        print(f"   رقم {d+1}: {(y_all == d).sum()}")

    indices = np.random.permutation(len(X_all))
    X_all = X_all[indices]
    y_all = y_all[indices]

    split = int(0.85 * len(X_all))
    return (X_all[:split], y_all[:split]), (X_all[split:], y_all[split:])

# ============================================================
# بخش ۶: ذخیره و نمایش
# ============================================================

def save_dataset(X_train, y_train, X_test, y_test, out_dir="data"):
    os.makedirs(out_dir, exist_ok=True)
    np.save(f"{out_dir}/X_train.npy", X_train)
    np.save(f"{out_dir}/y_train.npy", y_train)
    np.save(f"{out_dir}/X_test.npy", X_test)
    np.save(f"{out_dir}/y_test.npy", y_test)
    print(f"💾 دیتاست توی {out_dir}/ ذخیره شد")


def visualize_samples(X, y, n=20, save_path="samples.png"):
    fig, axes = plt.subplots(4, 5, figsize=(10, 8))
    indices = np.random.choice(len(X), n, replace=False)
    for ax, idx in zip(axes.flat, indices):
        ax.imshow(X[idx], cmap="gray", vmin=0, vmax=255)
        ax.set_title(f"Label: {y[idx] + 1}")
        ax.axis("off")
    plt.tight_layout()
    plt.savefig(save_path, dpi=100)
    plt.show()
    print(f"🖼️ نمونه‌ها توی {save_path} ذخیره شد")

# ============================================================
# بخش ۷: اجرای اصلی
# ============================================================

def main():
    print("🔍 جستجوی فونت‌ها...")
    all_fonts = find_system_fonts()
    print(f"   {len(all_fonts)} فونت پیدا شد")

    good_fonts = [f for f in all_fonts if is_good_font(f)]
    print(f"   {len(good_fonts)} فونت مناسب")

    if len(good_fonts) < 5:
        print("⚠️ کمتر از ۵ فونت مناسب! از فونت‌های پیش‌فرض استفاده می‌کنم")
        good_fonts = [
            "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/times.ttf",
            "C:/Windows/Fonts/calibri.ttf",
            "C:/Windows/Fonts/verdana.ttf",
            "C:/Windows/Fonts/consola.ttf",
        ]

    if len(good_fonts) > 60:
        good_fonts = random.sample(good_fonts, 60)

    (X_train, y_train), (X_test, y_test) = generate_dataset(
        fonts=good_fonts,
        num_variations_per_font=20,
        augment_ratio=2,
        seed=42
    )

    save_dataset(X_train, y_train, X_test, y_test)
    visualize_samples(X_train, y_train, n=20)

    print(f"\n📊 خلاصه:")
    print(f"   X_train: {X_train.shape}")
    print(f"   X_test:  {X_test.shape}")


if __name__ == "__main__":
    main()