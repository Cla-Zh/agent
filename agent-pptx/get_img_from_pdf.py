import fitz  # PyMuPDF
import os
from PIL import Image, ImageDraw
import numpy as np
import cv2

def detect_image_regions(page, dpi=300):
    """
    检测页面中的图片区域，包括复合图片和矢量图形
    
    参数:
    page: PyMuPDF页面对象
    dpi: 渲染分辨率
    
    返回:
    list: 图片区域的边界框列表 [(x0, y0, x1, y1), ...]
    """
    
    # 获取页面尺寸
    page_rect = page.rect
    
    # 方法1: 检测嵌入的图片对象
    embedded_images = []
    image_list = page.get_images()
    
    for img in image_list:
        try:
            # 获取图片在页面上的位置
            img_rects = page.get_image_rects(img[0])
            for rect in img_rects:
                embedded_images.append((rect.x0, rect.y0, rect.x1, rect.y1))
        except:
            continue
    
    # 方法2: 检测绘图对象（矢量图形、组合图形）
    drawing_regions = []
    
    # 获取页面上的绘图元素
    drawings = page.get_drawings()
    if drawings:
        # 将绘图元素按位置聚类
        drawing_groups = cluster_drawings(drawings)
        for group in drawing_groups:
            x0 = min(d['rect'].x0 for d in group)
            y0 = min(d['rect'].y0 for d in group)
            x1 = max(d['rect'].x1 for d in group)
            y1 = max(d['rect'].y1 for d in group)
            
            # 过滤掉太小的区域
            if (x1 - x0) > 50 and (y1 - y0) > 50:
                drawing_regions.append((x0, y0, x1, y1))
    
    # 方法3: 使用图像处理检测视觉上的图片区域
    visual_regions = detect_visual_regions(page, dpi)
    
    # 合并所有检测到的区域
    all_regions = embedded_images + drawing_regions + visual_regions
    
    # 去重和合并重叠区域
    merged_regions = merge_overlapping_regions(all_regions)
    
    return merged_regions

def cluster_drawings(drawings, distance_threshold=50):
    """
    将邻近的绘图元素聚类成组
    """
    if not drawings:
        return []
    
    groups = []
    used = set()
    
    for i, drawing in enumerate(drawings):
        if i in used:
            continue
            
        group = [drawing]
        used.add(i)
        
        # 查找邻近的绘图元素
        for j, other_drawing in enumerate(drawings):
            if j in used or i == j:
                continue
                
            # 计算两个绘图元素的距离
            rect1 = drawing['rect']
            rect2 = other_drawing['rect']
            
            # 计算中心点距离
            center1 = ((rect1.x0 + rect1.x1) / 2, (rect1.y0 + rect1.y1) / 2)
            center2 = ((rect2.x0 + rect2.x1) / 2, (rect2.y0 + rect2.y1) / 2)
            
            distance = ((center1[0] - center2[0]) ** 2 + (center1[1] - center2[1]) ** 2) ** 0.5
            
            if distance < distance_threshold:
                group.append(other_drawing)
                used.add(j)
        
        if len(group) > 0:  # 至少包含一个元素
            groups.append(group)
    
    return groups

def detect_visual_regions(page, dpi=300):
    """
    使用图像处理技术检测视觉上的图片区域
    """
    try:
        # 渲染页面为图像
        pix = page.get_pixmap(matrix=fitz.Matrix(dpi/72, dpi/72))
        img_data = pix.tobytes("png")
        
        # 转换为OpenCV格式
        nparr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            return []
        
        # 转换为灰度图
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 检测文本区域（用于排除）
        text_mask = detect_text_regions(page, img.shape, dpi)
        
        # 使用边缘检测
        edges = cv2.Canny(gray, 50, 150)
        
        # 排除文本区域
        edges = cv2.bitwise_and(edges, cv2.bitwise_not(text_mask))
        
        # 形态学操作连接边缘
        kernel = np.ones((5, 5), np.uint8)
        edges = cv2.dilate(edges, kernel, iterations=2)
        edges = cv2.erode(edges, kernel, iterations=1)
        
        # 查找轮廓
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        regions = []
        page_rect = page.rect
        scale_x = page_rect.width / img.shape[1]
        scale_y = page_rect.height / img.shape[0]
        
        for contour in contours:
            # 获取边界框
            x, y, w, h = cv2.boundingRect(contour)
            
            # 过滤太小的区域
            if w < 100 or h < 100:
                continue
            
            # 转换回PDF坐标
            x0 = x * scale_x + page_rect.x0
            y0 = y * scale_y + page_rect.y0
            x1 = (x + w) * scale_x + page_rect.x0
            y1 = (y + h) * scale_y + page_rect.y0
            
            regions.append((x0, y0, x1, y1))
        
        return regions
        
    except Exception as e:
        print(f"视觉检测出错: {e}")
        return []

def detect_text_regions(page, img_shape, dpi):
    """
    检测文本区域，返回掩码
    """
    try:
        # 获取文本块
        text_blocks = page.get_text("dict")
        
        # 创建文本掩码
        mask = np.zeros((img_shape[0], img_shape[1]), dtype=np.uint8)
        
        page_rect = page.rect
        scale_x = img_shape[1] / page_rect.width
        scale_y = img_shape[0] / page_rect.height
        
        for block in text_blocks["blocks"]:
            if "lines" in block:  # 文本块
                bbox = block["bbox"]
                
                # 转换到图像坐标
                x0 = int((bbox[0] - page_rect.x0) * scale_x)
                y0 = int((bbox[1] - page_rect.y0) * scale_y)
                x1 = int((bbox[2] - page_rect.x0) * scale_x)
                y1 = int((bbox[3] - page_rect.y0) * scale_y)
                
                # 在掩码上标记文本区域
                cv2.rectangle(mask, (x0, y0), (x1, y1), 255, -1)
        
        return mask
        
    except Exception as e:
        print(f"文本检测出错: {e}")
        return np.zeros((img_shape[0], img_shape[1]), dtype=np.uint8)

def merge_overlapping_regions(regions, overlap_threshold=0.3):
    """
    合并重叠的区域和同一行的区域
    """
    if not regions:
        return []
    
    def calculate_overlap(rect1, rect2):
        x0_1, y0_1, x1_1, y1_1 = rect1
        x0_2, y0_2, x1_2, y1_2 = rect2
        
        # 计算交集
        x_overlap = max(0, min(x1_1, x1_2) - max(x0_1, x0_2))
        y_overlap = max(0, min(y1_1, y1_2) - max(y0_1, y0_2))
        intersection = x_overlap * y_overlap
        
        # 计算并集
        area1 = (x1_1 - x0_1) * (y1_1 - y0_1)
        area2 = (x1_2 - x0_2) * (y1_2 - y0_2)
        union = area1 + area2 - intersection
        
        return intersection / union if union > 0 else 0
    
    def is_same_row(rect1, rect2, row_threshold=30):
        """
        判断两个区域是否在同一行
        """
        y0_1, y1_1 = rect1[1], rect1[3]
        y0_2, y1_2 = rect2[1], rect2[3]
        
        # 计算垂直重叠
        y_overlap = max(0, min(y1_1, y1_2) - max(y0_1, y0_2))
        min_height = min(y1_1 - y0_1, y1_2 - y0_2)
        
        # 如果垂直重叠超过较小高度的50%，认为在同一行
        return y_overlap > min_height * 0.5
    
    def is_horizontally_close(rect1, rect2, distance_threshold=100):
        """
        判断两个区域是否水平相近
        """
        x1_1, x0_2 = rect1[2], rect2[0]  # rect1的右边界和rect2的左边界
        x1_2, x0_1 = rect2[2], rect1[0]  # rect2的右边界和rect1的左边界
        
        # 计算水平距离
        if x0_2 >= x1_1:  # rect2在rect1右边
            distance = x0_2 - x1_1
        elif x0_1 >= x1_2:  # rect1在rect2右边
            distance = x0_1 - x1_2
        else:  # 有重叠
            distance = 0
        
        return distance <= distance_threshold
    
    merged = []
    used = set()
    
    for i, region1 in enumerate(regions):
        if i in used:
            continue
        
        current_region = region1
        used.add(i)
        merged_any = True
        
        # 持续查找可以合并的区域，直到没有新的可合并区域
        while merged_any:
            merged_any = False
            
            for j, region2 in enumerate(regions):
                if j in used or i == j:
                    continue
                
                # 检查是否需要合并：重叠或同一行且水平相近
                should_merge = False
                
                # 条件1：区域重叠
                if calculate_overlap(current_region, region2) > overlap_threshold:
                    should_merge = True
                
                # 条件2：同一行且水平相近
                elif (is_same_row(current_region, region2) and 
                      is_horizontally_close(current_region, region2)):
                    should_merge = True
                
                if should_merge:
                    # 合并区域
                    x0 = min(current_region[0], region2[0])
                    y0 = min(current_region[1], region2[1])
                    x1 = max(current_region[2], region2[2])
                    y1 = max(current_region[3], region2[3])
                    current_region = (x0, y0, x1, y1)
                    used.add(j)
                    merged_any = True
        
        merged.append(current_region)
    
    return merged

def extract_image_regions_from_pdf(pdf_path, output_folder, dpi=300, merge_same_row=True):
    """
    从PDF中提取完整的图片区域，包括复合图片和矢量图形
    
    参数:
    pdf_path: PDF文件路径
    output_folder: 输出文件夹路径
    dpi: 渲染分辨率，越高质量越好但处理越慢
    merge_same_row: 是否合并同一行的图片
    """
    
    # 创建输出文件夹
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # 打开PDF文件
    pdf_document = fitz.open(pdf_path)
    
    total_images = 0
    
    print(f"开始处理PDF文件: {pdf_path}")
    print(f"总页数: {pdf_document.page_count}")
    print(f"渲染DPI: {dpi}")
    print(f"同行图片合并: {'开启' if merge_same_row else '关闭'}")
    
    # 遍历每一页
    for page_num in range(pdf_document.page_count):
        page = pdf_document[page_num]
        
        print(f"\n处理第 {page_num + 1} 页...")
        
        # 检测图片区域
        raw_regions = detect_image_regions(page, dpi)
        
        # 如果启用同行合并，则进行额外的同行合并处理
        if merge_same_row:
            image_regions = merge_same_row_regions(raw_regions)
            print(f"原始检测到 {len(raw_regions)} 个区域，合并同行后得到 {len(image_regions)} 个图片区域")
        else:
            image_regions = raw_regions
            print(f"检测到 {len(image_regions)} 个图片区域")
        
        # 渲染整个页面
        mat = fitz.Matrix(dpi/72, dpi/72)
        pix = page.get_pixmap(matrix=mat)
        
        # 转换为PIL图像
        img_data = pix.tobytes("png")
        page_image = Image.open(io.BytesIO(img_data))
        
        # 计算缩放比例
        page_rect = page.rect
        scale_x = page_image.width / page_rect.width
        scale_y = page_image.height / page_rect.height
        
        # 按垂直位置排序图片区域
        image_regions.sort(key=lambda r: r[1])  # 按y0排序
        
        # 提取每个图片区域
        for region_idx, (x0, y0, x1, y1) in enumerate(image_regions):
            # 转换为图像坐标
            img_x0 = int((x0 - page_rect.x0) * scale_x)
            img_y0 = int((y0 - page_rect.y0) * scale_y)
            img_x1 = int((x1 - page_rect.x0) * scale_x)
            img_y1 = int((y1 - page_rect.y0) * scale_y)
            
            # 确保坐标在有效范围内
            img_x0 = max(0, img_x0)
            img_y0 = max(0, img_y0)
            img_x1 = min(page_image.width, img_x1)
            img_y1 = min(page_image.height, img_y1)
            
            # 裁剪图片区域
            if img_x1 > img_x0 and img_y1 > img_y0:
                cropped_image = page_image.crop((img_x0, img_y0, img_x1, img_y1))
                
                # 过滤太小的图片
                if cropped_image.width < 50 or cropped_image.height < 50:
                    continue
                
                total_images += 1
                
                # 生成文件名 - 如果是合并的图片，在文件名中标注
                if merge_same_row and was_merged_region(raw_regions, (x0, y0, x1, y1)):
                    filename = f"figure_{total_images:03d}_page{page_num+1:03d}_merged_row{region_idx+1:02d}.jpg"
                else:
                    filename = f"figure_{total_images:03d}_page{page_num+1:03d}_region{region_idx+1:02d}.jpg"
                
                output_path = os.path.join(output_folder, filename)
                
                # 转换为RGB模式并保存
                if cropped_image.mode != 'RGB':
                    cropped_image = cropped_image.convert('RGB')
                
                cropped_image.save(output_path, 'JPEG', quality=95)
                
                width_cm = cropped_image.width * 2.54 / dpi
                height_cm = cropped_image.height * 2.54 / dpi
                print(f"保存图片: {filename}")
                print(f"  尺寸: {cropped_image.width}x{cropped_image.height} 像素 ({width_cm:.1f}x{height_cm:.1f} cm)")
    
    # 关闭PDF文档
    pdf_document.close()
    
    print(f"\n提取完成！共保存了 {total_images} 张图片到文件夹: {output_folder}")

def merge_same_row_regions(regions, row_threshold=30, horizontal_gap_threshold=100):
    """
    专门用于合并同一行的图片区域
    
    参数:
    regions: 原始区域列表
    row_threshold: 判断同行的垂直距离阈值
    horizontal_gap_threshold: 水平间距阈值
    """
    if not regions:
        return []
    
    # 按垂直位置排序
    sorted_regions = sorted(regions, key=lambda r: r[1])
    
    merged_regions = []
    current_row_regions = [sorted_regions[0]]
    
    for i in range(1, len(sorted_regions)):
        current_region = sorted_regions[i]
        last_region = current_row_regions[-1]
        
        # 检查是否在同一行
        if is_same_horizontal_line(last_region, current_region, row_threshold):
            # 检查水平距离
            if get_horizontal_distance(last_region, current_region) <= horizontal_gap_threshold:
                current_row_regions.append(current_region)
            else:
                # 距离太远，结束当前行
                merged_regions.append(merge_regions_in_row(current_row_regions))
                current_row_regions = [current_region]
        else:
            # 不在同一行，结束当前行
            merged_regions.append(merge_regions_in_row(current_row_regions))
            current_row_regions = [current_region]
    
    # 处理最后一行
    if current_row_regions:
        merged_regions.append(merge_regions_in_row(current_row_regions))
    
    return merged_regions

def is_same_horizontal_line(region1, region2, threshold=30):
    """
    判断两个区域是否在同一水平线上
    """
    y1_center = (region1[1] + region1[3]) / 2
    y2_center = (region2[1] + region2[3]) / 2
    
    return abs(y1_center - y2_center) <= threshold

def get_horizontal_distance(region1, region2):
    """
    计算两个区域的水平距离
    """
    if region1[2] < region2[0]:  # region1在左边
        return region2[0] - region1[2]
    elif region2[2] < region1[0]:  # region2在左边
        return region1[0] - region2[2]
    else:  # 有重叠
        return 0

def merge_regions_in_row(regions):
    """
    合并一行中的所有区域
    """
    if len(regions) == 1:
        return regions[0]
    
    x0 = min(r[0] for r in regions)
    y0 = min(r[1] for r in regions)
    x1 = max(r[2] for r in regions)
    y1 = max(r[3] for r in regions)
    
    return (x0, y0, x1, y1)

def was_merged_region(original_regions, merged_region):
    """
    判断一个区域是否是由多个原始区域合并而成
    """
    count = 0
    for orig_region in original_regions:
        # 检查原始区域是否在合并区域内
        if (orig_region[0] >= merged_region[0] - 10 and 
            orig_region[1] >= merged_region[1] - 10 and
            orig_region[2] <= merged_region[2] + 10 and 
            orig_region[3] <= merged_region[3] + 10):
            count += 1
    
    return count > 1

def batch_extract_image_regions(pdf_folder, output_base_folder, dpi=300, merge_same_row=True):
    """
    批量处理文件夹中的所有PDF文件
    """
    
    if not os.path.exists(pdf_folder):
        print(f"错误: PDF文件夹 '{pdf_folder}' 不存在")
        return
    
    # 获取所有PDF文件
    pdf_files = [f for f in os.listdir(pdf_folder) if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        print(f"在文件夹 '{pdf_folder}' 中没有找到PDF文件")
        return
    
    print(f"找到 {len(pdf_files)} 个PDF文件")
    
    for pdf_file in pdf_files:
        pdf_path = os.path.join(pdf_folder, pdf_file)
        
        # 为每个PDF创建单独的输出文件夹
        pdf_name = os.path.splitext(pdf_file)[0]
        output_folder = os.path.join(output_base_folder, f"{pdf_name}_figures")
        
        print(f"\n{'='*60}")
        print(f"处理文件: {pdf_file}")
        print(f"{'='*60}")
        
        try:
            extract_image_regions_from_pdf(pdf_path, output_folder, dpi, merge_same_row)
        except Exception as e:
            print(f"处理PDF文件 '{pdf_file}' 时出错: {str(e)}")

# 使用示例
if __name__ == "__main__":
    import io  # 添加缺失的导入
    
    print("PDF完整图片区域提取工具")
    print("可以检测并提取:")
    print("- 嵌入的原始图片")
    print("- 由多个小图片组成的复合图形")
    print("- 矢量图形和图标")
    print("- 图表和示意图")
    
    print("\n请选择操作方式:")
    print("1. 处理单个PDF文件")
    print("2. 批量处理文件夹中的PDF文件")
    
    choice = input("请选择 (1/2): ").strip()
    
    # 同行合并选项
    print("\n同行图片处理:")
    print("1. 自动合并同一行的图片 (推荐)")
    print("2. 保持原始分块")
    
    merge_choice = input("请选择 (1/2, 默认1): ").strip()
    merge_same_row = merge_choice != "2"
    
    # DPI设置
    print("\n渲染质量设置:")
    print("1. 标准质量 (150 DPI) - 速度快")
    print("2. 高质量 (300 DPI) - 推荐")
    print("3. 超高质量 (600 DPI) - 速度慢但质量最佳")
    
    dpi_choice = input("请选择质量 (1/2/3, 默认2): ").strip()
    dpi_map = {"1": 150, "2": 300, "3": 600}
    dpi = dpi_map.get(dpi_choice, 300)
    
    if choice == "1":
        pdf_path = "1.pdf"
        output_folder = "./extr"
        if not output_folder:
            output_folder = "extracted_figures"
        
        if os.path.exists(pdf_path):
            extract_image_regions_from_pdf(pdf_path, output_folder, dpi, merge_same_row)
        else:
            print(f"错误: 文件 '{pdf_path}' 不存在")
    
    elif choice == "2":
        pdf_folder = input("请输入包含PDF文件的文件夹路径: ").strip()
        output_base_folder = input("请输入输出根文件夹路径 (默认: batch_extracted_figures): ").strip()
        
        if not output_base_folder:
            output_base_folder = "batch_extracted_figures"
        
        batch_extract_image_regions(pdf_folder, output_base_folder, dpi, merge_same_row)
    
    else:
        print("无效选择")