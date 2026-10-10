#!/usr/bin/env python3
"""lhg-ip 硬门：执业暗示与审查结果承诺表述拦截。

触发：PreToolUse / Edit|Write。扫描本次写入/编辑的文件内容，
若命中执业暗示或审查结果承诺关键词（包授权/保证下证/包注册成功/
律师意见等），以 exit code 2 拦截该操作，并给出改写指引。

注意：“非律师意见”声明中的“律师意见”四字不拦截（已先剔除）。

逃生方式（按推荐度排序）：
  1. LHG_IP_ADVICE_OFF=1（环境变量，当前会话有效；关闭后
     关键词拦截不再触发，但审计脚本的对应规则仍会在 ip-audit
     时报 blocker）。
  2. /plugin disable lhg-ip（整个插件停用，hooks 不再触发）。

设计原则：只有“命中关键词”才拦截；内部出错一律 fail-open
（直接放行，不报错）；零第三方依赖。
"""

import json
import os
import sys

# 执业暗示 / 审查结果承诺关键词表（原创整理）
ADVICE_KEYWORDS = [
    "包授权", "保证下证", "包注册成功", "保证注册成功", "稳过",
    "百分百通过", "一定能注册", "包过",
    "律师意见", "法律意见书", "我帮你打官司", "代理你出庭",
    "这个商标一定能注册", "这个专利一定能授权",
]

REWRITE_GUIDE = (
    "改写指引：删除审查结果承诺与执业口吻断言；只保留类型判断、流程指引、"
    "材料清单与维权路径；标准话术：“本插件非律师意见、仅供参考；申请流程与"
    "审查标准以官方最新公告为准，重要事项请咨询专业人士。”"
)


def extract_text(tool_input):
    """从 Edit/Write 的输入中抽取待写入文本。"""
    parts = []
    for key in ("content", "new_string", "old_string", "file_text"):
        v = tool_input.get(key)
        if isinstance(v, str) and v:
            parts.append(v)
    return "\n".join(parts)


def find_hits(text):
    # 先剔除合规声明中的“非律师意见”，避免误拦
    clean = text.replace("非律师意见", "")
    hits = []
    for kw in ADVICE_KEYWORDS:
        if kw in clean:
            hits.append(kw)
    return hits


def main():
    if os.environ.get("LHG_IP_ADVICE_OFF") == "1":
        return 0  # 逃生开关

    try:
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else {}
    except Exception:
        return 0  # 输入解析失败：fail-open

    tool_input = payload.get("tool_input", {}) or {}
    text = extract_text(tool_input)
    if not text:
        return 0

    try:
        hits = find_hits(text)
    except Exception:
        return 0  # 内部错误：fail-open

    if not hits:
        return 0

    msg = (
        "⛔ 执业硬门（lhg-ip）：本次写入内容命中执业暗示/审查结果承诺"
        "关键词：%s。\n本插件是知产保护助手，非律师意见、仅供参考。\n%s\n"
        "确认为合规内容但被误拦：export LHG_IP_ADVICE_OFF=1 后重试。"
        % ("、".join(hits), REWRITE_GUIDE)
    )
    sys.stderr.write(msg + "\n")
    return 2  # exit 2 = 拦截本次工具调用


if __name__ == "__main__":
    sys.exit(main())
