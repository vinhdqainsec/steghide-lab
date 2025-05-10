"""
Bước 5: Kiểm tra tính chính xác của quá trình giấu và trích xuất

Chức năng:
    - Đọc thông điệp gốc và thông điệp đã trích xuất
    - So sánh hai thông điệp
    - Hiển thị thống kê về quá trình giấu tin và trích xuất
"""

import os
import json
import difflib
from datetime import datetime

def read_file(file_path):
    """
    Đọc nội dung từ file
    
    Args:
        file_path (str): Đường dẫn đến file
        
    Returns:
        str: Nội dung của file, None nếu có lỗi
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Lỗi khi đọc file {file_path}: {e}")
        return None

def compare_messages(original, extracted):
    """
    So sánh thông điệp gốc và thông điệp đã trích xuất
    
    Args:
        original (str): Thông điệp gốc
        extracted (str): Thông điệp đã trích xuất
        
    Returns:
        dict: Kết quả so sánh
    """
    if original is None or extracted is None:
        return {
            "match": False,
            "original_length": len(original) if original else 0,
            "extracted_length": len(extracted) if extracted else 0,
            "diff_ratio": 0,
            "error": "Một trong hai thông điệp bị trống"
        }
    
    # So sánh độ dài
    original_length = len(original)
    extracted_length = len(extracted)
    
    # Tính toán mức độ khác biệt
    matcher = difflib.SequenceMatcher(None, original, extracted)
    diff_ratio = matcher.ratio()
    
    # Xác định xem hai thông điệp có trùng khớp không
    match = (original == extracted)
    
    # Nếu không trùng khớp, tìm vị trí đầu tiên khác nhau
    first_diff_pos = None
    first_diff_original = None
    first_diff_extracted = None
    
    if not match:
        min_len = min(original_length, extracted_length)
        for i in range(min_len):
            if original[i] != extracted[i]:
                first_diff_pos = i
                # Lấy một đoạn nhỏ xung quanh vị trí khác biệt
                start = max(0, i-10)
                end = min(min_len, i+10)
                first_diff_original = original[start:end]
                first_diff_extracted = extracted[start:end]
                break
    
    return {
        "match": match,
        "original_length": original_length,
        "extracted_length": extracted_length,
        "diff_ratio": diff_ratio,
        "first_diff_pos": first_diff_pos,
        "first_diff_original": first_diff_original,
        "first_diff_extracted": first_diff_extracted
    }

def verify_steganography(original_data_path=None, extracted_data_path=None, output_report=None):
    """
    Kiểm tra tính chính xác của quá trình giấu và trích xuất
    
    Args:
        original_data_path (str, optional): Đường dẫn đến file thông tin ban đầu
        extracted_data_path (str, optional): Đường dẫn đến file thông tin trích xuất
        output_report (str, optional): Đường dẫn để lưu báo cáo
        
    Returns:
        dict: Kết quả kiểm tra
    """
    report = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "files": {
            "original_data": original_data_path,
            "extracted_data": extracted_data_path
        },
        "status": "Initialized"
    }
    
    # Tìm các file thông tin
    if original_data_path is None:
        # Tìm trong các file mặc định
        for path in ["stego_data.json", "stego_binary.json", "stego_output.json"]:
            if os.path.exists(path):
                original_data_path = path
                report["files"]["original_data"] = path
                break
    
    if extracted_data_path is None:
        if os.path.exists("stego_extract.json"):
            extracted_data_path = "stego_extract.json"
            report["files"]["extracted_data"] = extracted_data_path
    
    # Kiểm tra xem có file thông tin không
    if original_data_path is None or not os.path.exists(original_data_path):
        print("Không tìm thấy file thông tin ban đầu.")
        report["status"] = "Failed"
        report["error"] = "Không tìm thấy file thông tin ban đầu"
        return report
    
    if extracted_data_path is None or not os.path.exists(extracted_data_path):
        print("Không tìm thấy file thông tin trích xuất.")
        report["status"] = "Failed"
        report["error"] = "Không tìm thấy file thông tin trích xuất"
        return report
    
    # Đọc thông tin
    try:
        print(f"Đọc thông tin ban đầu từ: {original_data_path}")
        with open(original_data_path, 'r', encoding='utf-8') as f:
            original_data = json.load(f)
        
        print(f"Đọc thông tin trích xuất từ: {extracted_data_path}")
        with open(extracted_data_path, 'r', encoding='utf-8') as f:
            extracted_data = json.load(f)
    except Exception as e:
        print(f"Lỗi khi đọc file thông tin: {e}")
        report["status"] = "Failed"
        report["error"] = f"Lỗi khi đọc file thông tin: {e}"
        return report
    
    # Lấy thông tin về file thông điệp gốc
    if "message_info" in original_data and "path" in original_data["message_info"]:
        original_message_path = original_data["message_info"]["path"]
        report["files"]["original_message"] = original_message_path
    else:
        original_message_path = None
        print("Không tìm thấy thông tin về file thông điệp gốc.")
    
    # Lấy thông tin về file thông điệp đã trích xuất
    if "extract" in extracted_data and "output_file" in extracted_data["extract"]:
        extracted_message_path = extracted_data["extract"]["output_file"]
        report["files"]["extracted_message"] = extracted_message_path
    else:
        # Tìm file có tiền tố "extracted_"
        extracted_message_path = None
        for file in os.listdir():
            if file.startswith("extracted_") and file.endswith(".txt"):
                extracted_message_path = file
                report["files"]["extracted_message"] = file
                break
        
        if extracted_message_path is None:
            print("Không tìm thấy thông tin về file thông điệp đã trích xuất.")
    
    # Kiểm tra xem có file thông điệp không
    if original_message_path is None or not os.path.exists(original_message_path):
        print("Không tìm thấy file thông điệp gốc.")
        report["status"] = "Incomplete"
        report["error"] = "Không tìm thấy file thông điệp gốc"
    else:
        report["files"]["original_message_exists"] = True
    
    if extracted_message_path is None or not os.path.exists(extracted_message_path):
        print("Không tìm thấy file thông điệp đã trích xuất.")
        report["status"] = "Incomplete"
        report["error"] = "Không tìm thấy file thông điệp đã trích xuất"
    else:
        report["files"]["extracted_message_exists"] = True
    
    # Đọc thông điệp
    original_message = None
    extracted_message = None
    
    if original_message_path and os.path.exists(original_message_path):
        original_message = read_file(original_message_path)
    else:
        # Thử đọc thông điệp từ dữ liệu JSON
        if "message" in original_data:
            original_message = original_data["message"]
            print("Đọc thông điệp gốc từ dữ liệu JSON.")
    
    if extracted_message_path and os.path.exists(extracted_message_path):
        extracted_message = read_file(extracted_message_path)
    
    # So sánh thông điệp
    if original_message is not None and extracted_message is not None:
        print("So sánh thông điệp gốc và thông điệp đã trích xuất...")
        comparison = compare_messages(original_message, extracted_message)
        report["comparison"] = comparison
        
        # Hiển thị kết quả
        print("\n=== KẾT QUẢ SO SÁNH ===")
        print(f"- Độ dài thông điệp gốc: {comparison['original_length']} ký tự")
        print(f"- Độ dài thông điệp trích xuất: {comparison['extracted_length']} ký tự")
        print(f"- Tỷ lệ giống nhau: {comparison['diff_ratio'] * 100:.2f}%")
        
        if comparison["match"]:
            print("- Kết quả: TRÙNG KHỚP HOÀN TOÀN ✓")
            report["status"] = "Success"
        else:
            print("- Kết quả: KHÔNG TRÙNG KHỚP ✗")
            report["status"] = "Partial Success"
            
            if comparison["first_diff_pos"] is not None:
                print(f"- Vị trí khác biệt đầu tiên: ký tự thứ {comparison['first_diff_pos'] + 1}")
                if comparison["first_diff_original"] and comparison["first_diff_extracted"]:
                    print(f"  + Gốc: \"{comparison['first_diff_original']}\"")
                    print(f"  + Trích xuất: \"{comparison['first_diff_extracted']}\"")
    else:
        print("Không thể so sánh thông điệp do thiếu dữ liệu.")
        report["status"] = "Incomplete"
        report["error"] = "Không thể so sánh thông điệp do thiếu dữ liệu"
    
    # Thu thập thông tin hiệu suất
    print("\n=== THÔNG TIN HIỆU SUẤT ===")
    
    # Thông tin từ file gốc
    if "image_info" in original_data:
        image_info = original_data["image_info"]
        print(f"- Ảnh gốc: {image_info.get('path', 'N/A')}")
        print(f"- Kích thước ảnh: {image_info.get('width', 'N/A')}x{image_info.get('height', 'N/A')}")
        print(f"- Số pixel: {image_info.get('pixel_count', 'N/A')}")
        report["performance"] = {
            "image": {
                "path": image_info.get('path', 'N/A'),
                "width": image_info.get('width', 'N/A'),
                "height": image_info.get('height', 'N/A'),
                "pixel_count": image_info.get('pixel_count', 'N/A')
            }
        }
    
    # Thông tin từ file trích xuất
    if "extract" in extracted_data:
        extract_info = extracted_data["extract"]
        print(f"- Ảnh đã giấu tin: {extract_info.get('stego_image', 'N/A')}")
        print(f"- Độ dài thông điệp đọc được: {extract_info.get('message_length', 'N/A')} ký tự")
        print(f"- Số bit đã đọc: {extract_info.get('bits_read', 'N/A')}/{extract_info.get('bits_needed', 'N/A')}")
        
        if "performance" not in report:
            report["performance"] = {}
        
        report["performance"]["extraction"] = {
            "stego_image": extract_info.get('stego_image', 'N/A'),
            "message_length": extract_info.get('message_length', 'N/A'),
            "bits_read": extract_info.get('bits_read', 'N/A'),
            "bits_needed": extract_info.get('bits_needed', 'N/A')
        }
    
    # Lưu báo cáo
    if output_report:
        print(f"\nLưu báo cáo vào: {output_report}")
        with open(output_report, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
    
    return report

def main():
    """
    Hàm chính
    """
    print("=== BƯỚC 5: KIỂM TRA TÍNH CHÍNH XÁC ===")
    
    original_data_path = None
    for path in ["stego_output.json", "stego_binary.json", "stego_data.json"]:
        if os.path.exists(path):
            original_data_path = path
            break
    
    extracted_data_path = "stego_extract.json"
    
    if original_data_path is None:
        print("Không tìm thấy file thông tin ban đầu.")
        custom_path = input("Nhập đường dẫn đến file thông tin ban đầu: ").strip()
        if custom_path and os.path.exists(custom_path):
            original_data_path = custom_path
        else:
            print("Không thể tiếp tục. Vui lòng chạy các bước trước.")
            return
    
    if not os.path.exists(extracted_data_path):
        print("Không tìm thấy file thông tin trích xuất.")
        custom_path = input("Nhập đường dẫn đến file thông tin trích xuất: ").strip()
        if custom_path and os.path.exists(custom_path):
            extracted_data_path = custom_path
        else:
            print("Không thể tiếp tục. Vui lòng chạy bước 4 trước.")
            return
    
    # Đường dẫn để lưu báo cáo
    output_report = "stego_verification.json"
    
    # Kiểm tra tính chính xác
    report = verify_steganography(original_data_path, extracted_data_path, output_report)
    
    print("\n=== KẾT LUẬN ===")
    if report["status"] == "Success":
        print("Quá trình giấu tin và trích xuất THÀNH CÔNG HOÀN TOÀN.")
        print("Thông điệp trích xuất TRÙNG KHỚP với thông điệp gốc.")
    elif report["status"] == "Partial Success":
        print("Quá trình giấu tin và trích xuất THÀNH CÔNG MỘT PHẦN.")
        print("Thông điệp trích xuất KHÔNG TRÙNG KHỚP HOÀN TOÀN với thông điệp gốc.")
    else:
        print("Quá trình giấu tin và trích xuất KHÔNG HOÀN THÀNH.")
        if "error" in report:
            print(f"Lỗi: {report['error']}")
    
    print("\nBước 5 hoàn tất. Quá trình kiểm tra đã kết thúc.")

if __name__ == "__main__":
    main() 