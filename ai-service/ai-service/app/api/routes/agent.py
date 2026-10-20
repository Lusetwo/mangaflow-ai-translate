import uuid
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from app.agent.context import AgentContext
from app.api.schemas.response import AgentExecutionResponse
from app.core.config import settings
from app.core.exceptions import MangaFlowError
from app.services.artifact_service import encode_image
from app.services.image_service import InvalidImageError, validate_image
from app.workflow.translation_workflow import TranslationWorkflow


router = APIRouter()
workflow = TranslationWorkflow()

"""
客户端上传图片 + 语言
        │
        ▼
① content_type 校验 ── 不是图片 → 400
        │
        ▼
② 读字节（限长 +1）── 空 → 400；超限 → 413
        │
        ▼
③ validate_image 真解析 ── 非法 → 400
        │
        ▼
④ 构建 AgentContext（uuid task_id）
        │
        ▼
⑤ workflow.run()  OCR → 翻译 → 擦除 → 嵌字
        │ MangaFlowError → 502
        ▼
⑥ 无输出图 → 500
        │
        ▼
⑦ 生成 notice（区分 demo / 正常模式）
        │
        ▼
⑧ 返回 AgentExecutionResponse（含 base64 图片）
"""
@router.post("/api/v1/translate",response_model=AgentExecutionResponse)
async def translate_image(file: UploadFile = File(...), source_lang: str = Form("ja"), target_lang: str = Form("zh-CN")):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image uploads are supported")
    data = await file.read(settings.max_image_bytes + 1)
    if not data:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")
    if len(data) > settings.max_image_bytes:
        raise HTTPException(status_code=413, detail="Image exceeds configured size limit")
    try:
        width,height,image_format = validate_image(data)

    except InvalidImageError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    context = AgentContext(task_id=str(uuid.uuid4()), image_bytes=data, source_lang=source_lang,
                               target_lang=target_lang,
                               metadata={"width": width, "height": height, "format": image_format})
    try:
        result = await workflow.execute(context)
    except MangaFlowError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    if result.result_image_bytes is None:
        raise HTTPException(status_code=500, detail="Agent did not produce an output image")
    demo_mode = (
        settings.ocr_provider != "rapidocr"
        or settings.llm_provider == "demo"
        or settings.inpaint_provider == "demo"
    )
    if demo_mode:
        notice = "Demo mode active: OCR/translation/inpaint may be mocked; composed output quality is limited."
    elif settings.inpaint_provider == "opencv":
        notice = "OCR, translation, OpenCV inpaint and typesetting executed; LaMa AI inpaint is not enabled."
    else:
        notice = "OCR, translation, LaMa inpaint and typesetting executed; output embeds translated text."
    return AgentExecutionResponse(status=result.state.status.value, sourceLang=source_lang, targetLang=target_lang,
                                  ocrMode=settings.ocr_provider, translationMode=settings.llm_provider,
                                  regions=result.regions,
                                  translations=result.translations,
                                  resultImageBase64=encode_image(result.result_image_bytes),
                                  resultMimeType="image/png", notice=notice, executionTrace=result.state.trace)