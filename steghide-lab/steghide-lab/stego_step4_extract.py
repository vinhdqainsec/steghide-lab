"""
Bước 4: Trích xuất thông điệp từ ảnh

Chức năng:
    - Đọc ảnh đã giấu tin
    - Trích xuất thông điệp từ ảnh
    - Lưu thông điệp vào file
"""

import os
import json
import cv2
import numpy as np

def exportDataFromPixel(index, pixels):
    """
    Trích xuất 6 bit từ 2-bit LSB của 3 kênh màu R,G,B của 1 pixel
    
    Args:
        index (int): Chỉ số của pixel trong danh sách
        pixels (list): Danh sách các pixel
        
    Returns:
        str: Chuỗi 6 bit được trích xuất
    """
    temp = ""
    
    # Lấy 2 bit thấp nhất từ kênh R
    firstLocal = bin(pixels[index][2] & 3)[2:]
    firstLocal = (2 - len(firstLocal)) * "0" + firstLocal
    temp += firstLocal
    
    # Lấy 2 bit thấp nhất từ kênh G
    secondLocal = bin(pixels[index][3] & 3)[2:]
    secondLocal = (2 - len(secondLocal)) * "0" + secondLocal
    temp += secondLocal
    
    # Lấy 2 bit thấp nhất từ kênh B
    thirdLocal = bin(pixels[index][4] & 3)[2:]
    thirdLocal = (2 - len(thirdLocal)) * "0" + thirdLocal
    temp += thirdLocal
    
    return temp

def binaryToText(binary):
    """
    Chuyển đổi chuỗi nhị phân thành văn bản
    
    Args:
        binary (str): Chuỗi nhị phân cần chuyển đổi
        
    Returns:
        str: Văn bản tương ứng
    """
    text = ""
    # Xử lý từng nhóm 8 bit để chuyển thành ký tự
    for i in range(0, len(binary), 8):
        if i + 8 <= len(binary):
            byte = binary[i:i+8]
            text += chr(int(byte, 2))
    
    return text

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

def decodeMessageLength(pixels):
    """
    Giải mã độ dài thông điệp từ 4 pixel đầu tiên
    
    Args:
        pixels (list): Danh sách các pixel
        
    Returns:
        int: Độ dài thông điệp
    """
    # Đọc 24 bit từ 4 pixel đầu tiên
    msgLengthInBinary = ""
    for ind in range(4):
        msgLengthInBinary += exportDataFromPixel(ind, pixels)
    
    # Chuyển đổi từ nhị phân sang số nguyên
    try:
        msgLen = int(msgLengthInBinary, 2)
        return msgLen
    except ValueError:
        print(f"Lỗi: Không thể giải mã độ dài thông điệp")
        return None

def extract_message(stego_image_path, output_text=None, output_info=None):
    """
    Trích xuất thông điệp từ ảnh
    
    Args:
        stego_image_path (str): Đường dẫn đến ảnh đã giấu tin
        output_text (str, optional): Đường dẫn để lưu thông điệp trích xuất
        output_info (str, optional): Đường dẫn để lưu thông tin về việc trích xuất
        
    Returns:
        str: Thông điệp được trích xuất nếu thành công, None nếu thất bại
    """
    # Đọc ảnh đã giấu tin
    print(f"Đọc ảnh đã giấu tin: {stego_image_path}")
    try:
        pixels = getPicture(stego_image_path)
    except Exception as e:
        print(f"Lỗi khi đọc ảnh: {e}")
        return None
    
    print(f"Đã đọc ảnh có {len(pixels)} pixel")
    
    # Đọc độ dài thông điệp từ 4 pixel đầu tiên
    print("Đọc độ dài thông điệp từ header...")
    message_length = decodeMessageLength(pixels)
    
    if message_length is None or message_length <= 0 or message_length > 100000:  # Giới hạn ở 100k ký tự
        print(f"Lỗi: Độ dài thông điệp không hợp lệ ({message_length})")
        return None
    
    print(f"Độ dài thông điệp: {message_length} ký tự")
    
    # Tính số bit cần đọc
    num_bits_needed = message_length * 8
    print(f"Số bit cần đọc: {num_bits_needed}")
    
    # Đọc thông điệp nhị phân
    print("Trích xuất dữ liệu nhị phân...")
    secret_msg_binary = ""
    
    # Bắt đầu đọc từ pixel thứ 5 (sau header)
    pixel_index = 4
    
    # Đọc đủ số bit cần thiết hoặc đến hết ảnh
    while len(secret_msg_binary) < num_bits_needed and pixel_index < len(pixels):
        secret_msg_binary += exportDataFromPixel(pixel_index, pixels)
        pixel_index += 1
    
    # Cắt đến đúng độ dài cần thiết
    secret_msg_binary = secret_msg_binary[:num_bits_needed]
    
    # Kiểm tra xem đã đọc đủ bit chưa
    if len(secret_msg_binary) < num_bits_needed:
        print(f"Cảnh báo: Chỉ đọc được {len(secret_msg_binary)}/{num_bits_needed} bit")
    
    # Chuyển đổi từ nhị phân sang văn bản
    print("Chuyển đổi dữ liệu nhị phân thành văn bản...")
    extracted_message = binaryToText(secret_msg_binary)
    
    # Kiểm tra độ dài thông điệp
    if len(extracted_message) != message_length:
        print(f"Cảnh báo: Độ dài thông điệp trích xuất ({len(extracted_message)}) không khớp với độ dài đã mã hóa ({message_length})")
    
    # Lưu thông điệp trích xuất
    if output_text and extracted_message:
        print(f"Lưu thông điệp trích xuất vào: {output_text}")
        with open(output_text, 'w', encoding='utf-8') as f:
            f.write(extracted_message)
    
    # Lưu thông tin trích xuất
    if output_info:
        # Tạo thông tin trích xuất
        extract_info = {
            "stego_image": stego_image_path,
            "message_length": message_length,
            "bits_read": len(secret_msg_binary),
            "bits_needed": num_bits_needed,
            "extracted_length": len(extracted_message),
            "output_file": output_text
        }
        
        # Đọc file thông tin cũ nếu có
        if os.path.exists(output_info):
            try:
                with open(output_info, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                # Thêm thông tin trích xuất vào dữ liệu cũ
                data['extract'] = extract_info
            except:
                # Nếu file không đọc được, tạo mới
                data = {"extract": extract_info}
        else:
            data = {"extract": extract_info}
        
        # Lưu thông tin
        print(f"Lưu thông tin trích xuất vào: {output_info}")
        with open(output_info, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    # Hiển thị preview thông điệp
    if extracted_message:
        print("\nXem trước thông điệp trích xuất:")
        preview_length = min(100, len(extracted_message))
        preview = extracted_message[:preview_length]
        if len(extracted_message) > preview_length:
            preview += "..."
        print(preview)
    
    return extracted_message

def import_datetime():
    """Hàm nhỏ để import module datetime"""
    import datetime
    return datetime

def main():
    """
    Hàm chính
    """
    print("=== BƯỚC 4: TRÍCH XUẤT THÔNG ĐIỆP TỪ ẢNH ===")
    
    # Nhập đường dẫn đến ảnh đã giấu tin
    use_previous = input("Bạn có muốn sử dụng ảnh từ bước 3 không? (y/n): ").strip().lower()
    
    if use_previous == 'y':
        # Đọc thông tin từ bước 3
        output_info = "stego_output.json"
        
        if not os.path.exists(output_info):
            print(f"Lỗi: Không tìm thấy file {output_info}")
            print("Vui lòng chạy bước 3 trước hoặc nhập đường dẫn thủ công.")
            stego_image_path = input("Nhập đường dẫn đến ảnh đã giấu tin: ").strip()
        else:
            try:
                with open(output_info, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                stego_image_path = data['stego']['output_image']
                print(f"Đọc đường dẫn ảnh từ file trước: {stego_image_path}")
            except:
                print("Lỗi khi đọc thông tin từ file trước.")
                stego_image_path = input("Nhập đường dẫn đến ảnh đã giấu tin: ").strip()
    else:
        stego_image_path = input("Nhập đường dẫn đến ảnh đã giấu tin: ").strip()
    
    if not os.path.exists(stego_image_path):
        print(f"Lỗi: Không tìm thấy file {stego_image_path}")
        return
    
    # Đường dẫn để lưu thông điệp trích xuất
    output_text = input("Nhập đường dẫn để lưu thông điệp trích xuất (Enter để mặc định): ").strip()
    if not output_text:
        output_text = f"extracted_{os.path.basename(stego_image_path)}.txt"
    
    # Đường dẫn để lưu thông tin trích xuất
    output_info = "stego_extract.json"
    
    # Trích xuất thông điệp
    extracted_message = extract_message(stego_image_path, output_text, output_info)
    
    if extracted_message:
        print(f"\nBước 4 hoàn tất. Thông điệp đã được trích xuất thành công.")
        print(f"Thông điệp đã được lưu vào: {output_text}")
    else:
        print("\nBước 4 thất bại. Không thể trích xuất thông điệp.")

if __name__ == "__main__":
    main() 