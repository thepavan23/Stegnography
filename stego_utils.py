import os
from PIL import Image

def text_to_binary(text):
    return ''.join(format(ord(char), '08b') for char in text)

def binary_to_text(binary):
    chars = [binary[i:i+8] for i in range(0, len(binary), 8)]
    return ''.join(chr(int(b, 2)) for b in chars)

def int_to_32bit_binary(n):
    return format(n, '032b')

def binary_to_int(b):
    return int(b, 2)

def encode_text_in_image(image_path, text, output_path):
    # Open and convert input image to RGB
    img = Image.open(image_path).convert("RGB")
    
    # Resize and convert to PNG internally (regardless of format)
    img = img.resize((128, 128))
    
    # Save to temp PNG to avoid compression artifacts from formats like JPG
    temp_path = "uploads/temp_input.png"
    img.save(temp_path, format="PNG")
    
    img = Image.open(temp_path)
    pixels = img.load()

    binary_text = text_to_binary(text)
    length_bin = int_to_32bit_binary(len(text))
    full_data = length_bin + binary_text

    if len(full_data) > 128 * 128:
        raise ValueError("Text too long to hide in 128x128 image.")

    data_index = 0
    for y in range(128):
        for x in range(128):
            if data_index >= len(full_data):
                break
            r, g, b = pixels[x, y]
            r = (r & ~1) | int(full_data[data_index])
            pixels[x, y] = (r, g, b)
            data_index += 1
        if data_index >= len(full_data):
            break

    img.save(output_path, format="PNG")  # Always save stego image as PNG
    os.remove(temp_path)

def decode_text_from_image(image_path):
    img = Image.open(image_path).convert("RGB")
    img = img.resize((128, 128))
    pixels = img.load()

    bits = ""
    bit_count = 0
    for y in range(128):
        for x in range(128):
            r, g, b = pixels[x, y]
            bits += str(r & 1)
            bit_count += 1
            if bit_count == 32:
                break
        if bit_count == 32:
            break

    text_length = binary_to_int(bits)
    total_bits = text_length * 8

    bits = ""
    read_count = 0
    pixel_index = 0
    for y in range(128):
        for x in range(128):
            if pixel_index < 32:
                pixel_index += 1
                continue
            if read_count >= total_bits:
                break
            r, g, b = pixels[x, y]
            bits += str(r & 1)
            read_count += 1
            pixel_index += 1
        if read_count >= total_bits:
            break

    return binary_to_text(bits)
