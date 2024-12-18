from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from starlette.middleware.cors import CORSMiddleware
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.units import inch
from fastapi import FastAPI, Request, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 定义请求体模型
class RecordsRequest(BaseModel):
    records: list

# DeepSeek API 的配置
DEEPSEEK_API_KEY = "sk-c053fa65c63846b9be3b82277ef1a1c8"  # 替换为你的 DeepSeek API Key
BASE_URL = "https://api.deepseek.com"  # DeepSeek API 的基础 URL

# 初始化 ChatOpenAI 模型
model = ChatOpenAI(
    model="deepseek-chat",
    api_key=DEEPSEEK_API_KEY,
    base_url=BASE_URL,
    temperature=1.5,
)

# 动态生成提示词
def generate_prompt(records: list) -> str:
    # 将 records 转换为字符串
    records_text = "\n".join([f"{record['speaker']}: {record['content']}" for record in records])
    # 生成提示词
    prompt = f"请根据以下会议记录生成总结：\n{records_text}"
    return prompt

# 调用 DeepSeek API 生成总结
async def call_deepseek_api(prompt: str) -> str:
    try:
        # 构建消息
        messages = [
            ("system", "你是一个会议记录总结助手。"),
            ("human", prompt),
        ]
        prompt_template = ChatPromptTemplate.from_messages(messages=messages)
        prompt = prompt_template.invoke({"prompt": prompt})

        # 调用模型生成总结
        result = model.invoke(prompt)
        return result.content  # 返回生成的总结内容
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-summary")
async def generate_summary_endpoint(request: RecordsRequest):
    try:
        # 动态生成提示词
        prompt = generate_prompt(request.records)

        # 调用 DeepSeek API 生成总结
        summary = await call_deepseek_api(prompt)
        return {"summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# 注册中文字体
# 注册中文字体
pdfmetrics.registerFont(TTFont('simsun', 'C:/Windows/Fonts/simsun.ttc'))

class ReportData(BaseModel):
    records: list  # 说话人信息
    summaryText: str  # 总结文本
    blinkCount: int  # 眨眼次数
    mouthOpenCount: int  # 张嘴次数

def generate_pdf(data: ReportData) -> BytesIO:
    # 创建 PDF 画布对象
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)

    # 设置字体和字号
    pdf.setFont("simsun", 16)  # 使用支持中文的字体
    pdf.drawString(50, 800, "对话报告")  # 大标题

    # 设置正文字体和字号
    pdf.setFont("simsun", 12)

    # 写入说话人信息
    y = 750
    for record in data.records:
        pdf.drawString(50, y, f"{record['speaker']}: {record['content']}")
        y -= 20  # 更新 y 坐标

    # 写入总结文本（支持自动换行）
    pdf.setFont("simsun", 14)
    # pdf.drawString(50, y - 30, "总结:")
    pdf.setFont("simsun", 12)

    # 使用 Paragraph 实现自动换行
    styles = getSampleStyleSheet()
    style = styles["Normal"]
    style.fontName = "simsun"  # 设置字体
    style.fontSize = 12  # 设置字号
    style.leading = 14  # 设置行间距

    # 将总结文本包装为 Paragraph
    summary_paragraph = Paragraph(data.summaryText, style)
    summary_paragraph.wrapOn(pdf, 500, 100)  # 设置宽度
    summary_paragraph.drawOn(pdf, 50, y - 50)  # 绘制到 PDF
    y -= summary_paragraph.height + 30  # 更新 y 坐标

    # 写入眨眼次数和张嘴次数
    pdf.drawString(50, y - 30, f"眨眼次数: {data.blinkCount}")
    pdf.drawString(50, y - 50, f"张嘴次数: {data.mouthOpenCount}")

    # 保存 PDF 文件
    pdf.save()
    buffer.seek(0)
    return buffer

@app.post("/generate-pdf")
async def generate_pdf_endpoint(request: Request, data: ReportData):
    # 生成 PDF 文件
    pdf_buffer = generate_pdf(data)

    # 返回 PDF 文件
    return Response(content=pdf_buffer.getvalue(), media_type="application/pdf")



# 主函数，用于启动 FastAPI 应用
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)