"""
Bước 3: Giấu thông điệp vào ảnh

Chức năng:
    - Đọc dữ liệu từ bước 1 và bước 2
    - Giấu thông điệp vào ảnh
    - Lưu ảnh đã giấu tin
"""

import os
import json
import pickle
import cv2
import numpy as np

def putDataInPixel(index, sixBinary, pixels):
    """
    Chèn 6 bit thông tin vào 2-bit LSB của 3 kênh màu R,G,B của 1 pixel
    
    Args:
        index (int): Chỉ số của pixel trong danh sách
        sixBinary (str): Chuỗi 6 bit cần chèn
        pixels (list): Danh sách các pixel
    """
    # Xóa 2 bit thấp nhất của mỗi kênh màu (AND với 1111 1100 = 252 ở hệ thập phân)
    pixels[index][2] &= 252  # R
    pixels[index][3] &= 252  # G
    pixels[index][4] &= 252  # B
    
    # Chèn 2 bit đầu vào kênh R
    pixels[index][2] |= int(sixBinary[0:2], 2)
    
    # Chèn 2 bit tiếp theo vào kênh G
    pixels[index][3] |= int(sixBinary[2:4], 2)
    
    # Chèn 2 bit cuối vào kênh B
    pixels[index][4] |= int(sixBinary[4:6], 2)

def encodeMessageLength(message_length, pixels):
    """
    Mã hóa độ dài thông điệp vào 4 pixel đầu tiên của ảnh
    
    Args:
        message_length (int): Độ dài thông điệp cần mã hóa
        pixels (list): Danh sách các pixel
    """
    # Chuyển độ dài thành chuỗi nhị phân 24 bit
    messageLengthBin = bin(message_length)[2:]
    messageLengthBin = (24 - len(messageLengthBin)) * "0" + messageLengthBin
    
    # Thêm độ dài vào 4 pixel đầu tiên (mỗi pixel chứa 6 bit)
    pixelIndex = 0
    for i in range(0, 24, 6):
        putDataInPixel(pixelIndex, messageLengthBin[i:i+6], pixels)
        pixelIndex += 1

def makePicture(pic):
    """
    Chuyển đổi danh sách pixel thành ảnh
    
    Args:
        pic (list): Danh sách các pixel theo định dạng [row, col, R, G, B]
        
    Returns:
        numpy.ndarray: Ảnh dưới dạng mảng numpy
    """
    img1 = []
    img2 = []
    row = pic[-1][0] + 1
    col = pic[-1][1] + 1
    for i in range(row):
        for j in range(col):
            index = i * col + j
            img1 += [[np.uint8(pic[index][4]), np.uint8(pic[index][3]), np.uint8(pic[index][2])]]
        img2 += [img1]
        img1 = []
    return np.array(img2)

def saveImage(pixels, output_filename):
    """
    Lưu danh sách pixel thành file ảnh
    
    Args:
        pixels (list): Danh sách các pixel
        output_filename (str): Tên file đầu ra
        
    Returns:
        bool: True nếu lưu thành công, False nếu có lỗi
    """
    try:
        # Chuyển đổi danh sách pixel thành định dạng ảnh
        image = makePicture(pixels)
        
        # Lưu ảnh
        cv2.imwrite(output_filename, image)
        return True
    except Exception as e:
        print(f"Lỗi khi lưu ảnh: {e}")
        return False

def embed_message(binary_data_path, output_info=None):
    """
    Giấu thông điệp vào ảnh
    
    Args:
        binary_data_path (str): Đường dẫn đến file dữ liệu từ bước 2
        output_info (str, optional): Đường dẫn để lưu thông tin về ảnh đã giấu tin
        
    Returns:
        bool: True nếu giấu tin thành công, False nếu có lỗi
    """
    # Đọc dữ liệu từ bước 2
    print(f"Đọc dữ liệu từ: {binary_data_path}")
    with open(binary_data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Kiểm tra xem có thể giấu tin không
    if 'binary' not in data or data['binary']['can_embed'] is False:
        print("Lỗi: Không thể giấu tin. Dữ liệu không hợp lệ hoặc ảnh không đủ dung lượng.")
        return False
    
    # Đọc danh sách pixels
    pickle_path = "stego_pixels.bin"
    if not os.path.exists(pickle_path):
        print(f"Lỗi: Không tìm thấy file {pickle_path}")
        return False
    
    print(f"Đọc danh sách pixels từ: {pickle_path}")
    with open(pickle_path, 'rb') as f:
        pixels = pickle.load(f)
    
    # Lấy thông tin
    binary_message = data['binary']['message']
    message_length = data['message_info']['length']
    output_image = "encrypted_" + os.path.splitext(os.path.basename(data['image_info']['path']))[0] + ".png"
    
    print("\nThông tin giấu tin:")
    print(f"- Ảnh gốc: {data['image_info']['path']}")
    print(f"- Thông điệp: {message_length} ký tự")
    print(f"- Chuỗi nhị phân: {len(binary_message)} bit")
    print(f"- Pixel cần thiết: {data['binary']['pixels_needed']}")
    print(f"- Pixel có sẵn: {len(pixels)}")
    
    # Mã hóa độ dài thông điệp vào 4 pixel đầu tiên
    print("\nBắt đầu giấu tin...")
    print("- Mã hóa độ dài thông điệp vào 4 pixel đầu tiên")
    encodeMessageLength(message_length, pixels)
    
    # Giấu thông điệp
    print(f"- Giấu {len(binary_message)} bit dữ liệu vào các pixel")
    
    # Bắt đầu giấu tin từ pixel thứ 5 (sau header)
    pixelIndex = 4
    
    # Giấu tin
    for i in range(0, len(binary_message), 6):
        # Đảm bảo chúng ta không vượt quá độ dài của binary_message
        end = min(i + 6, len(binary_message))
        sixBinary = binary_message[i:end]
        
        # Đảm bảo sixBinary có đủ 6 bit
        if len(sixBinary) < 6:
            sixBinary = sixBinary + '0' * (6 - len(sixBinary))
            
        putDataInPixel(pixelIndex, sixBinary, pixels)
        pixelIndex += 1
    
    # Lưu ảnh đã giấu tin
    print(f"Lưu ảnh đã giấu tin vào: {output_image}")
    if not saveImage(pixels, output_image):
        print("Lỗi: Không thể lưu ảnh đã giấu tin")
        return False
    
    # Lưu thông tin
    if output_info:
        data['stego'] = {
            "output_image": output_image,
            "status": "Thành công",
        }
        
        print(f"Lưu thông tin giấu tin vào: {output_info}")
        with open(output_info, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    return True

def import_datetime():
    """Hàm nhỏ để import module datetime"""
    import datetime
    return datetime

def main():
    """
    Hàm chính
    """
    print("=== BƯỚC 3: GIẤU THÔNG ĐIỆP VÀO ẢNH ===")
    
    # Đường dẫn đến file dữ liệu từ bước 2
    binary_data_path = "stego_binary.json"
    
    if not os.path.exists(binary_data_path):
        print(f"Lỗi: Không tìm thấy file {binary_data_path}")
        print("Vui lòng chạy bước 2 trước: python stego_step2_convert.py")
        return
    
    # Đường dẫn để lưu thông tin về ảnh đã giấu tin
    output_info = "stego_output.json"
    
    # Giấu tin
    success = embed_message(binary_data_path, output_info)
    
    if not success:
        print("\nGiấu tin thất bại. Không thể giấu tin.")

if __name__ == "__main__":
    main() 