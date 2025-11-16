#!/usr/bin/env python3
"""
Create app icons from emoji for OctopusFTP
Generates .icns (macOS) and .ico (Windows) from the octopus emoji
"""

import os
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("ERROR: Pillow is required to generate icons")
    print("Install it with: pip3 install Pillow")
    sys.exit(1)

EMOJI = "🐙"  # Octopus emoji
SIZES_ICNS = [16, 32, 64, 128, 256, 512, 1024]  # macOS icon sizes
SIZES_ICO = [16, 32, 48, 64, 128, 256]  # Windows icon sizes

def create_emoji_image(emoji, size):
    """Create an image with centered emoji"""
    # Create transparent image
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    try:
        # Try to use system font for emoji
        # macOS: Apple Color Emoji
        font_paths = [
            "/System/Library/Fonts/Apple Color Emoji.ttc",  # macOS
            "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf",  # Linux
            "C:\\Windows\\Fonts\\seguiemj.ttf",  # Windows
        ]

        font = None
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    font = ImageFont.truetype(font_path, int(size * 0.8))
                    break
                except:
                    continue

        if not font:
            print(f"Warning: Could not load emoji font, using default")
            font = ImageFont.load_default()

        # Get text bounding box
        bbox = draw.textbbox((0, 0), emoji, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # Center text
        x = (size - text_width) // 2 - bbox[0]
        y = (size - text_height) // 2 - bbox[1]

        # Draw emoji
        draw.text((x, y), emoji, font=font, embedded_color=True)

    except Exception as e:
        print(f"Warning: Could not render emoji, creating colored circle instead: {e}")
        # Fallback: create a blue circle with white "O"
        draw.ellipse([size//8, size//8, size*7//8, size*7//8], fill='#2196F3')
        try:
            fallback_font = ImageFont.load_default()
            draw.text((size//3, size//3), "O", fill='white', font=fallback_font)
        except:
            pass

    return img

def create_icns(output_path):
    """Create macOS .icns file"""
    print(f"Creating macOS icon: {output_path}")

    # Create iconset directory
    iconset_dir = output_path.parent / "OctopusFTP.iconset"
    iconset_dir.mkdir(exist_ok=True)

    # Generate all required sizes
    for size in SIZES_ICNS:
        # Standard resolution
        img = create_emoji_image(EMOJI, size)
        img.save(iconset_dir / f"icon_{size}x{size}.png")

        # Retina resolution (2x)
        if size <= 512:  # Don't create 2048x2048
            img_2x = create_emoji_image(EMOJI, size * 2)
            img_2x.save(iconset_dir / f"icon_{size}x{size}@2x.png")

    # Convert to .icns using macOS iconutil
    try:
        import subprocess
        subprocess.run(
            ["iconutil", "-c", "icns", str(iconset_dir), "-o", str(output_path)],
            check=True
        )
        print(f"✓ Created: {output_path}")

        # Clean up iconset directory
        import shutil
        shutil.rmtree(iconset_dir)

    except subprocess.CalledProcessError:
        print(f"ERROR: Failed to create .icns file")
        print(f"       iconset directory left at: {iconset_dir}")
        sys.exit(1)
    except FileNotFoundError:
        print(f"ERROR: 'iconutil' not found (macOS only)")
        print(f"       iconset directory left at: {iconset_dir}")
        sys.exit(1)

def create_ico(output_path):
    """Create Windows .ico file"""
    print(f"Creating Windows icon: {output_path}")

    images = []
    for size in SIZES_ICO:
        img = create_emoji_image(EMOJI, size)
        images.append(img)

    # Save as .ico with multiple sizes
    images[0].save(
        output_path,
        format='ICO',
        sizes=[(img.width, img.height) for img in images],
        append_images=images[1:]
    )
    print(f"✓ Created: {output_path}")

def main():
    # Get script directory
    script_dir = Path(__file__).parent
    assets_dir = script_dir / "assets"
    assets_dir.mkdir(exist_ok=True)

    print("=" * 50)
    print("OctopusFTP Icon Generator 🐙")
    print("=" * 50)
    print()

    # Detect platform
    if sys.platform == "darwin":
        print("Platform: macOS")
        icns_path = assets_dir / "OctopusFTP.icns"
        create_icns(icns_path)
    elif sys.platform == "win32":
        print("Platform: Windows")
        ico_path = assets_dir / "OctopusFTP.ico"
        create_ico(ico_path)
    else:
        print("Platform: Linux/Other")
        print("Creating both .icns and .ico files...")
        icns_path = assets_dir / "OctopusFTP.icns"
        ico_path = assets_dir / "OctopusFTP.ico"

        try:
            create_icns(icns_path)
        except:
            print("Warning: Could not create .icns (requires macOS iconutil)")

        create_ico(ico_path)

    print()
    print("=" * 50)
    print("Icons created successfully!")
    print(f"Location: {assets_dir}")
    print("=" * 50)

if __name__ == "__main__":
    main()
