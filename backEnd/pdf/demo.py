from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
import re


def FontChoose(fontName: str):
    # 楷体
    if fontName == "simkai":
        return TTFont('simkai', 'C:/Windows/Fonts/simkai.ttf')
    if fontName == "simsun":
        return TTFont('simsun', 'C:/Windows/Fonts/simsun.ttc')


# 注册字体
pdfmetrics.registerFont(FontChoose('simkai'))
pdfmetrics.registerFont(FontChoose('simsun'))


def parse_markdown(markdown_text, variables):
    """
    解析 Markdown 内容，替换变量并返回纯文本内容。
    """
    # 替换变量
    for key, value in variables.items():
        markdown_text = markdown_text.replace(f"{{{key}}}", str(value))

    # 解析 Markdown 标题
    markdown_text = re.sub(r"^(#+)\s+(.*)$", r"\2", markdown_text, flags=re.MULTILINE)

    return markdown_text


def add_image(pdf, image_path, x, y, width=2*inch, height=2*inch):
    """
    在 PDF 中插入图片。
    """
    img = Image(image_path, width=width, height=height)
    img.wrapOn(pdf, width, height)
    img.drawOn(pdf, x, y)


def add_table(pdf, data, x, y, width=400, height=100):
    """
    在 PDF 中插入表格。
    """
    # 动态计算 rowHeights 的长度
    rowHeights = [25] * len(data)  # 每行高度为 25（增加行高）

    table = Table(data, colWidths=[100, 100, 100], rowHeights=rowHeights)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),  # 表头背景色
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),  # 表头文字颜色
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # 所有单元格居中对齐
        ('FONTNAME', (0, 0), (-1, -1), 'simsun'),  # 表格字体（支持中文）
        ('FONTSIZE', (0, 0), (-1, 0), 12),  # 表头字号
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),  # 表头下边距
        ('TOPPADDING', (0, 0), (-1, 0), 12),  # 表头上边距
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),  # 表格背景色
        ('GRID', (0, 0), (-1, -1), 1, colors.black),  # 表格网格线
    ]))
    table.wrapOn(pdf, width, height)
    table.drawOn(pdf, x, y)


def text_to_pdf(title, markdown_text, variables, image_path, table_data, filename):
    # 创建一个PDF画布对象
    pdf = canvas.Canvas(filename, pagesize=A4)

    # 获取页面宽度和高度
    width, height = A4

    # 设置标题字体和字号
    pdf.setFont("simsun", 16)
    pdf.drawString(50, height - 50, title)  # 写入标题

    # 设置正文字体和字号
    pdf.setFont("simsun", 12)

    # 解析 Markdown 内容为纯文本
    parsed_text = parse_markdown(markdown_text, variables)
    lines = parsed_text.split('\n')
    y = height - 80  # 从标题下方开始写入

    for line in lines:
        # 写入普通文本
        pdf.drawString(50, y, line)
        y -= 15  # 普通行间距

        # 如果接近页面底部，创建新页面
        if y < 50:
            pdf.showPage()
            y = height - 50  # 新页面从顶部开始

    # 插入图片
    if image_path:
        add_image(pdf, image_path, 50, y - 100)
        y -= 150  # 为图片留出空间

    # 插入表格
    if table_data:
        add_table(pdf, table_data, 50, y - 100)
        y -= 150  # 为表格留出空间

    # 保存PDF文件
    pdf.save()


# 示例变量
variables = {
    "name": "张三",
    "age": 25,
    "city": "北京"
}

# 示例 Markdown 内容
markdown_text = """
# 个人信息
姓名：{name}
年龄：{age}
城市：{city}

## 兴趣爱好
- 阅读
- 旅行

## 图片示例
这里插入一张图片。

## 表格示例
这里插入一个表格。
"""

# 示例图片路径
image_path = "example.jpg"  # 替换为你的图片路径

# 示例表格数据
table_data = [
    ["姓名", "年龄", "城市"],
    ["张三", "25", "北京"],
    ["李四", "30", "上海"],
    ["王五", "28", "广州"]
]

# 调用函数生成PDF
try:
    text_to_pdf("PDF 生成示例", markdown_text, variables, image_path, table_data, "output.pdf")
    print('pdf已生成')
except:
    print('生成失败')