#!/usr/bin/env python3
"""lhg-ip 确定性审计：知产申请材料与方案体检。

扫描目标目录下的 checklist.json（申请材料清单）与 *.md（申请方案），
按规则注册表逐项检查。零第三方依赖。

规则（rule_id / 级别 / 含义）：
  TM-MATERIAL-001  blocker  商标申请材料缺项（申请表/身份证明/商标图样/商品服务清单）
  TM-CLASS-001      warning  类别选择坑：只注册第35类
  CR-MATERIAL-001  blocker  著作权登记材料缺项（申请表/作品样本/身份证明）
  IP-DEADLINE-001   warning  方案缺时限节点（续展/审查周期/答复期限）
  IP-NON-LAWYER-001 blocker  “非律师意见”声明缺失

checklist.json 格式：
  {"trademark": {"materials": [...], "classes": ["30", "35"]},
   "copyright": {"materials": [...]}}

用法：
  python3 ip_audit.py --target <目录> [--format json|text]
退出码：0=无问题，1=有 blocker，2=只有 warning。
"""

import argparse
import json
import os
import sys

# ---------------- 规则注册表 ----------------
TM_REQUIRED = ["申请表", "身份证明", "商标图样", "商品服务清单"]
CR_REQUIRED = ["申请表", "作品样本", "身份证明"]
DEADLINE_KEYWORDS = ["续展", "审查周期", "答复期限"]
DISC = "\u975e\u5f8b\u5e08\u610f\u89c1"


class Finding(object):
    def __init__(self, rule_id, level, message, location=""):
        self.rule_id = rule_id
        self.level = level
        self.message = message
        self.location = location

    def to_dict(self):
        return {"rule_id": self.rule_id, "level": self.level,
                "message": self.message, "location": self.location}


def check_checklist_json(path, findings):
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        findings.append(Finding("TM-MATERIAL-001", "blocker",
                                "目标目录缺少 checklist.json（申请材料清单）", path))
        return
    except ValueError as e:
        findings.append(Finding("TM-MATERIAL-001", "blocker",
                                "checklist.json 不是合法 JSON：%s" % e, path))
        return

    tm = data.get("trademark", {}) or {}
    tm_materials = tm.get("materials", []) or []
    missing = [m for m in TM_REQUIRED
               if not any(m in str(x) for x in tm_materials)]
    if missing:
        findings.append(Finding(
            "TM-MATERIAL-001", "blocker",
            "商标申请材料缺项：" + "、".join(missing), path))

    classes = [str(c).strip() for c in (tm.get("classes", []) or [])]
    if classes and all(c == "35" for c in classes):
        findings.append(Finding(
            "TM-CLASS-001", "warning",
            "类别选择坑：只注册了第35类（广告/商业经营），保护不了产品本身；"
            "请按核心类+关联类+防御类补选", path))

    cr = data.get("copyright", {}) or {}
    cr_materials = cr.get("materials", []) or []
    missing_cr = [m for m in CR_REQUIRED
                  if not any(m in str(x) for x in cr_materials)]
    if missing_cr:
        findings.append(Finding(
            "CR-MATERIAL-001", "blocker",
            "著作权登记材料缺项：" + "、".join(missing_cr), path))


def check_guide_md(path, findings):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    if not any(k in text for k in DEADLINE_KEYWORDS):
        findings.append(Finding(
            "IP-DEADLINE-001", "warning",
            "方案缺时限节点：须写明续展/审查周期/答复期限中的至少一项（以官方最新公告为准）",
            path))
    if DISC not in text:
        findings.append(Finding(
            "IP-NON-LAWYER-001", "blocker",
            "方案缺声明：须写明非律师意见、仅供参考", path))


def audit(target):
    findings = []
    for name in sorted(os.listdir(target)):
        p = os.path.join(target, name)
        if name == "checklist.json":
            check_checklist_json(p, findings)
        elif name.endswith(".md"):
            check_guide_md(p, findings)
    return findings


def main():
    ap = argparse.ArgumentParser(description="lhg-ip 知产申请材料与方案审计")
    ap.add_argument("--target", required=True, help="待审计目录")
    ap.add_argument("--format", choices=["json", "text"], default="text")
    args = ap.parse_args()
    if not os.path.isdir(args.target):
        print("目标目录不存在：" + args.target, file=sys.stderr)
        return 1
    findings = audit(args.target)
    blockers = sum(1 for f in findings if f.level == "blocker")
    warnings = sum(1 for f in findings if f.level == "warning")
    summary = {"blocker": blockers, "warning": warnings, "total": len(findings)}
    if args.format == "json":
        print(json.dumps({"summary": summary,
                          "findings": [f.to_dict() for f in findings]},
                         ensure_ascii=False, indent=2))
    else:
        print("知产方案审计：blocker=%d warning=%d" % (blockers, warnings))
        for f in findings:
            loc = " [%s]" % f.location if f.location else ""
            print("[%s] %s%s: %s" % (f.level.upper(), f.rule_id, loc, f.message))
        if not findings:
            print("全部通过。")
    if blockers:
        return 1
    if warnings:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
