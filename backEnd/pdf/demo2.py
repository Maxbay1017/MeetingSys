from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.units import inch


def FontChoose(fontName: str):
    # 注册中文字体
    if fontName == "simsun":
        return TTFont('simsun', 'C:/Windows/Fonts/simsun.ttc')


# 注册字体
pdfmetrics.registerFont(FontChoose('simsun'))


def generate_prompt(records: list) -> str:
    """
    将 records 转换为符合对话格式的 Markdown 内容。
    """
    # 初始化 Markdown 内容
    markdown_content = ""

    # 遍历 records，生成对话格式
    for record in records:
        speaker = record['speaker']
        content = record['content']

        # 添加头像或标识符（可选）
        if speaker == "Alice":
            avatar = "👩"  # 女性头像
        elif speaker == "Bob":
            avatar = "👨"  # 男性头像
        else:
            avatar = "👤"  # 通用头像

        # 生成对话行
        markdown_content += f"""
### {avatar} {speaker}
> {content}
"""

    return markdown_content


def markdown_to_pdf(markdown_content, pdf_filename):
    """
    将 Markdown 内容转换为 PDF。
    """
    # 创建 PDF 画布对象
    pdf = canvas.Canvas(pdf_filename, pagesize=A4)

    # 获取页面宽度和高度
    width, height = A4

    # 设置字体和字号
    pdf.setFont("simsun", 12)

    # 将 Markdown 内容逐行写入 PDF
    lines = markdown_content.split('\n')
    y = height - 50  # 从页面顶部开始写入

    for line in lines:
        # 如果是标题（###），使用较大的字号
        if line.startswith("###"):
            pdf.setFont("simsun", 14)  # 标题字号
            pdf.drawString(50, y, line.lstrip("#").strip())
            y -= 20  # 标题行间距较大
        elif line.startswith(">"):
            pdf.setFont("simsun", 12)  # 正文字号
            pdf.drawString(70, y, line.lstrip(">").strip())
            y -= 15  # 正文行间距
        else:
            y -= 15  # 空行间距

        # 如果接近页面底部，创建新页面
        if y < 50:
            pdf.showPage()
            y = height - 50  # 新页面从顶部开始

    # 保存 PDF 文件
    pdf.save()


# 示例数据
records = [
    {"speaker": "Alice", "content": "你好，Bob！最近怎么样？"},
    {"speaker": "Bob", "content": "还不错，谢谢！你呢？"},
    {"speaker": "Alice", "content": "我也很好，最近在学习 Python。"},
    {"speaker": "Bob", "content": "哇，Python 很棒！你用它做什么项目？"},
    {"speaker": "Alice", "content": "我正在做一个自动生成 Markdown 文件的工具。"},
]

# 生成 Markdown 内容
markdown_output = generate_prompt(records)

# 打印 Markdown 内容
print("生成的 Markdown 内容：")
print(markdown_output)

# 将 Markdown 内容转换为 PDF
markdown_to_pdf(markdown_output, "output2.pdf")

print("PDF 文件已生成：output2.pdf")