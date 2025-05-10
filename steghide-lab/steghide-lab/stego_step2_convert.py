"""
Bước 2: Chuyển đổi thông điệp thành dạng nhị phân

Chức năng:
    - Đọc dữ liệu từ bước 1
    - Chuyển đổi thông điệp thành chuỗi nhị phân
    - Phân tích khả năng chứa thông điệp của ảnh
    - Lưu chuỗi nhị phân vào file trung gian
"""

import os
import json
import pickle

def textToBinary(text):
    """
    Chuyển đổi văn bản thành dạng nhị phân
    
    Args:
        text (str): Văn bản cần chuyển đổi
        
    Returns:
        str: Chuỗi nhị phân tương ứng
    """
    binary_text = ""
    for char in text:
        # Chuyển mỗi ký tự thành mã nhị phân 8 bit
        binary_char = bin(ord(char))[2:]
        # Đảm bảo mỗi ký tự có đủ 8 bit
        binary_char = (8 - len(binary_char)) * "0" + binary_char
        binary_text += binary_char
    
    return binary_text

def convert_message(stego_data_path, output_json=None):
    """
    Chuyển đổi thông điệp từ dữ liệu đã chuẩn bị
    
    Args:
        stego_data_path (str): Đường dẫn đến file dữ liệu từ bước 1
        output_json (str, optional): Đường dẫn để lưu kết quả chuyển đổi
        
    Returns:
        dict: Dữ liệu đã chuyển đổi
    """
    # Đọc dữ liệu từ bước 1
    print(f"Đọc dữ liệu từ: {stego_data_path}")
    with open(stego_data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Lấy thông điệp
    message = data['message']
    
    # Đọc danh sách pixels
    pickle_path = "stego_pixels.bin"
    if os.path.exists(pickle_path):
        print(f"Đọc danh sách pixels từ: {pickle_path}")
        with open(pickle_path, 'rb') as f:
            pixels = pickle.load(f)
        data['pixels_available'] = True
    else:
        print(f"Cảnh báo: Không tìm thấy file {pickle_path}. Sẽ không kiểm tra khả năng chứa thông điệp.")
        pixels = None
        data['pixels_available'] = False
    
    # Chuyển đổi thông điệp thành chuỗi nhị phân
    print("Chuyển đổi thông điệp thành chuỗi nhị phân...")
    binary_message = textToBinary(message)
    
    # Đảm bảo độ dài chuỗi nhị phân là bội số của 6
    padding = 0
    if len(binary_message) % 6 != 0:
        padding = (6 - (len(binary_message) % 6))
        binary_message = padding * "0" + binary_message
    
    # Tính toán số pixel cần thiết
    num_bits = len(binary_message)
    bits_per_pixel = 6  # 2 bit LSB × 3 kênh màu
    num_pixels_needed = (num_bits // bits_per_pixel) + 4  # +4 cho header
    
    # Kiểm tra khả năng chứa thông điệp
    can_embed = True
    reason = None
    
    if pixels is not None:
        num_pixels_available = len(pixels)
        if num_pixels_needed > num_pixels_available:
            can_embed = False
            reason = "Ảnh không đủ lớn để chứa thông điệp"
    
    # Thêm thông tin vào dữ liệu
    data['binary'] = {
        "message": binary_message,
        "length": len(binary_message),
        "padding": padding,
        "pixels_needed": num_pixels_needed,
        "can_embed": can_embed,
        "reason": reason
    }
    
    # Lưu dữ liệu
    if output_json:
        print(f"Lưu kết quả chuyển đổi vào: {output_json}")
        with open(output_json, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    # Hiển thị thông tin
    print("\nKết quả chuyển đổi:")
    print(f"- Thông điệp: {len(message)} ký tự")
    print(f"- Chuỗi nhị phân: {len(binary_message)} bit")
    print(f"  + Padding: {padding} bit")
    print(f"- Số pixel cần thiết: {num_pixels_needed}")
    
    if pixels is not None:
        print(f"- Số pixel có sẵn: {len(pixels)}")
        if can_embed:
            print(f"- Khả năng chứa thông điệp: CÓ THỂ ✓")
        else:
            print(f"- Khả năng chứa thông điệp: KHÔNG THỂ ✗")
            print(f"  + Lý do: {reason}")
    
    return data

def main():
    """
    Hàm chính
    """
    print("=== BƯỚC 2: CHUYỂN ĐỔI THÔNG ĐIỆP ===")
    
    # Đường dẫn đến file dữ liệu từ bước 1
    stego_data_path = "stego_data.json"
    
    if not os.path.exists(stego_data_path):
        print(f"Lỗi: Không tìm thấy file {stego_data_path}")
        print("Vui lòng chạy bước 1 trước: python stego_step1_prepare.py")
        return
    
    # Đường dẫn để lưu kết quả chuyển đổi
    output_json = "stego_binary.json"
    
    # Chuyển đổi thông điệp
    data = convert_message(stego_data_path, output_json)
    
    # Kiểm tra xem có thể tiếp tục không
    if data['binary']['can_embed'] is False:
        print("\nKhông thể tiếp tục vì ảnh không đủ lớn để chứa thông điệp.")
        print("Vui lòng sử dụng ảnh lớn hơn hoặc thông điệp ngắn hơn.")
        return
    

if __name__ == "__main__":
    main() 