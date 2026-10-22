import json
import logging
import re
from pathlib import Path
from typing import Sequence

from app.providers.llm.base import LLMProvider, TranslationProvider


log = logging.getLogger(__name__)

# prompt 文件路径：ai-service/app/agent/prompts/translation.txt
_PROMPTS_DIR = Path(__file__).resolve().parents[2] / "agent" / "prompts"
_TRANSLATION_PROMPT_PATH = _PROMPTS_DIR / "translation.txt"


def _load_translation_prompt() -> str:
    """加载漫画翻译专家 prompt（系统角色）；文件缺失时回退为简洁英文版。"""
    try:
        text = _TRANSLATION_PROMPT_PATH.read_text(encoding="utf-8").strip()
        if text:
            return text
    except OSError as exc:
        log.warning("translation prompt not found at %s: %s", _TRANSLATION_PROMPT_PATH, exc)
    return (
        "You are a professional manga localization translator. "
        "Translate each dialogue naturally, preserve tone and character voice, "
        "keep the translated text concise to fit in speech bubbles. "
        "Return only the translated content, no extra explanation."
    )


"""基于统一 LLMProvider 的翻译适配：业务侧只拼 prompt，不绑定具体模型厂商。"""
class LLMTranslationProvider(TranslationProvider):
    def __init__(self, llm: LLMProvider):
        self.llm = llm
        self.system_prompt = _load_translation_prompt()

    async def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        prompt = (
            f"Source language: {source_lang}. Target language: {target_lang}.\n\n"
            f"Text to translate:\n{text}\n\n"
            f"Translation:"
        )
        return await self.llm.complete(prompt, system_prompt=self.system_prompt)

    async def translate_batch(
        self, texts: Sequence[str], source_lang: str, target_lang: str
    ) -> list[str]:
        """把所有段落合并为一次 LLM 调用，返回与 texts 等长的译文列表。

        策略：让 LLM 返回 JSON 数组 {"translations": ["t1","t2",...]}。
        解析失败则降级为逐条 translate。
        """
        texts = list(texts)
        if not texts:
            return []

        # 全部为空 → 直接返回空串占位
        if all(not t.strip() for t in texts):
            return ["" for _ in texts]

        indexed = "\n".join(f"[{i}] {t}" for i, t in enumerate(texts))
        user_prompt = (
            f"Source language: {source_lang}. Target language: {target_lang}.\n\n"
            f"Translate all of the following manga dialogue segments. "
            f"Preserve tone, character voice and concise bubble-friendly wording.\n\n"
            f"Input segments:\n{indexed}\n\n"
            f"Respond ONLY with a valid JSON object exactly in this format, "
            f"where the array length equals the number of input segments:\n"
            f'{{"translations": ["translation for [0]", "translation for [1]", ...]}}'
        )
        # 覆盖 system prompt 的"仅返回译文"规则 —— 批量模式需要返回 JSON 数组
        batch_system_prompt = (
            self.system_prompt
            + "\n\n"
            + "批量翻译模式覆盖规则：当用户要求你返回 JSON 格式时，"
            + "忽略「仅返回译文」这条单轮规则，严格按用户指定的 JSON 结构输出，"
            + "不要在 JSON 外面添加任何解释文字。"
        )
        try:
            raw = await self.llm.complete(user_prompt, system_prompt=batch_system_prompt)
            parsed = self._parse_batch_json(raw, len(texts))
            if parsed is not None:
                return parsed
            log.warning("batch translate JSON parse failed (%d segs, len=%d), fallback to one-by-one",
                        len(texts), len(raw))
        except Exception as exc:
            log.warning("batch translate failed (%s), fallback to one-by-one", exc)

        # fallback：逐条翻译
        out: list[str] = []
        for t in texts:
            if not t.strip():
                out.append("")
            else:
                try:
                    out.append(await self.translate(t, source_lang, target_lang))
                except Exception as exc:
                    log.warning("single translate failed: %s", exc)
                    out.append(t)  # 兜底：原文占位，不让整批失败
        return out

    @staticmethod
    def _parse_batch_json(raw: str, expected: int) -> list[str] | None:
        """从 LLM 返回文本里抽取 JSON 数组；长度不符时返回 None 触发 fallback。"""
        text = raw.strip()
        # 优先直接解析
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            # 用正则抓取第一个 { ... } 块（处理 LLM 在 JSON 外面套了解释文字的情况）
            match = re.search(r"\{[\s\S]*\}", text)
            if not match:
                return None
            try:
                data = json.loads(match.group(0))
            except json.JSONDecodeError:
                return None

        if isinstance(data, dict):
            segs = data.get("translations") or data.get("translated") or data.get("results")
        elif isinstance(data, list):
            segs = data
        else:
            return None

        if not isinstance(segs, list):
            return None

        out: list[str] = []
        for item in segs:
            out.append(str(item).strip() if item is not None else "")

        # 长度必须匹配，否则说明 LLM 丢了段或加了额外段
        if len(out) != expected:
            log.info("batch translate length mismatch: got %d want %d", len(out), expected)
            return None
        return out
