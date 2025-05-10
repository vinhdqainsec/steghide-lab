"""
Bước 1: Chuẩn bị dữ liệu cho giấu tin

Chức năng:
    - Đọc ảnh gốc và chuyển thành danh sách pixel
    - Đọc thông điệp từ file
    - Lưu thông tin vào file trung gian
"""

import os
import cv2
import numpy as np
import json

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

def getTextFromFile(filename):
    """
    Đọc nội dung văn bản từ file
    
    Args:
        filename (str): Tên file cần đọc
        
    Returns:
        str: Nội dung của file
    """
    with open(filename, 'r', encoding='utf-8') as file:
        return file.read()

def getPicture(filename):
    """
    Đọc ảnh và chuyển đổi thành danh sách các pixel
    
    Args:
        filename (str): Tên file ảnh cần đọc
        
    Returns:
        list: Danh sách các pixel [row, col, R, G, B]
    """
    img = cv2.imread(filename)
    lis = img.shape
    piclist = []
    row = lis[0]
    col = lis[1]
    for i in range(row):
        for j in range(col):
            pix_b = img[i][j][0]
            pix_g = img[i][j][1]
            pix_r = img[i][j][2]
            piclist.append([i, j, pix_r, pix_g, pix_b])
    return piclist

def prepare_data(image_path, message_path, output_json=None):
    """
    Chuẩn bị dữ liệu cho giấu tin
    
    Args:
        image_path (str): Đường dẫn đến ảnh gốc
        message_path (str): Đường dẫn đến file thông điệp
        output_json (str, optional): Đường dẫn để lưu dữ liệu chuẩn bị
        
    Returns:
        dict: Dữ liệu đã chuẩn bị
    """
    print(f"Đọc ảnh từ: {image_path}")
    pixels = getPicture(image_path)
    
    print(f"Đọc thông điệp từ: {message_path}")
    message = getTextFromFile(message_path)
    
    # Tạo cấu trúc dữ liệu đầu ra
    data = {
        "image_info": {
            "path": image_path,
            "pixel_count": len(pixels),
            "height": pixels[-1][0] + 1,
            "width": pixels[-1][1] + 1
        },
        "message_info": {
            "path": message_path,
            "length": len(message),
            "preview": message[:50] + ("..." if len(message) > 50 else "")
        },
        "message": message,
        "output_image": "encrypted_" + os.path.basename(image_path)
    }
    
    # Chúng ta không thể json.dump danh sách pixels trực tiếp 
    # vì nó quá lớn và numpy arrays không serialize được
    # Thay vào đó, chúng ta lưu thông tin về ảnh
    
    if output_json:
        print(f"Lưu thông tin vào: {output_json}")
        with open(output_json, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    # Chỉ để hiển thị
    print("\nThông tin chuẩn bị:")
    print(f"- Ảnh: {image_path}")
    print(f"  + Số pixel: {len(pixels)}")
    print(f"  + Kích thước: {pixels[-1][0] + 1}x{pixels[-1][1] + 1}")
    print(f"- Thông điệp: {message_path}")
    print(f"  + Độ dài: {len(message)} ký tự")
    
    return pixels, message, data

def main():
    """
    Hàm chính
    """
    print("=== BƯỚC 1: CHUẨN BỊ DỮ LIỆU ===")
    
    # Nhập đường dẫn tới ảnh
    image_path = input("Nhập đường dẫn đến ảnh gốc: ")
    if not os.path.exists(image_path):
        print(f"Lỗi: Không tìm thấy file {image_path}")
        return
    
    # Nhập đường dẫn tới thông điệp
    message_path = input("Nhập đường dẫn đến file thông điệp: ")
    if not os.path.exists(message_path):
        print(f"Lỗi: Không tìm thấy file {message_path}")
        return
    
    # Đường dẫn để lưu thông tin
    output_json = "stego_data.json"
    
    # Chuẩn bị dữ liệu
    pixels, message, data = prepare_data(image_path, message_path, output_json)
    
    # Lưu danh sách pixels riêng (chỉ để cho bước 2)
    pickle_path = "stego_pixels.bin"
    import pickle
    print(f"Lưu danh sách pixels vào: {pickle_path}")
    with open(pickle_path, 'wb') as f:
        pickle.dump(pixels, f)

if __name__ == "__main__":
    main() 