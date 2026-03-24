"""
display.py — Terminal formatting
"""

ESC   = "\033["
RESET  = f"{ESC}0m"
BOLD   = f"{ESC}1m"
DIM    = f"{ESC}2m"
RED    = f"{ESC}91m"
GREEN  = f"{ESC}92m"
YELLOW = f"{ESC}93m"
CYAN   = f"{ESC}96m"
WHITE  = f"{ESC}97m"

VERDICT_COLOR = {
    "STRONG":      GREEN,
    "CONDITIONAL": YELLOW,
    "RISKY":       YELLOW,
    "STOP":        RED,
}

BAR_WIDTH = 20


def b(t):   return f"{BOLD}{t}{RESET}"
def dim(t): return f"{DIM}{t}{RESET}"
def red(t): return f"{RED}{t}{RESET}"
def grn(t): return f"{GREEN}{t}{RESET}"
def ylw(t): return f"{YELLOW}{t}{RESET}"
def cyn(t): return f"{CYAN}{t}{RESET}"


def hr(char="─", width=72):
    print(dim(char * width))


def header(title: str):
    print()
    hr("═")
    print(f"  {b(title.upper())}")
    hr("═")


def section(title: str):
    print()
    print(cyn(f"▸ {title.upper()}"))
    hr("─", 50)


def score_bar(score: float, max_score: float = 12) -> str:
    filled = int((score / max_score) * BAR_WIDTH)
    bar    = "█" * filled + "░" * (BAR_WIDTH - filled)
    s_disp = round(score, 1)
    pct    = int((score / max_score) * 100)
    color  = GREEN if pct >= 70 else (YELLOW if pct >= 45 else RED)
    return f"{color}{bar}{RESET} {b(str(s_disp))}/{int(max_score)}  ({pct}%)"


def dim_score_dot(score: float, max_score: int = 2) -> str:
    s_int = int(round(score))
    bar   = "●" * s_int + "○" * (max_score - s_int)
    color = GREEN if score >= 1.5 else (YELLOW if score >= 0.5 else RED)
    return f"{color}{bar}{RESET}"


def print_idea_summary(idea):
    from domains import get_domain
    dom    = get_domain(idea.domain)
    dims   = dom["dimensions"]
    vc     = VERDICT_COLOR.get(idea.verdict, WHITE)

    print()
    print(f"  {b(idea.name.upper())}")
    print(f"  {dim(idea.description)}")
    print(f"  Domain : {cyn(dom['label'])}  ({dom['idea_noun']})")
    print()

    for key, dim_def in dims.items():
        score = idea.scores.get(key, 0)
        dots  = dim_score_dot(score)
        label = dim_def["name"].ljust(28)
        # Use integer for description lookup
        s_idx = int(round(score))
        note  = dim(dim_def["scores"][s_idx][:58])
        print(f"    {label} {dots}  {note}")

    print()
    print(f"  Total Score : {score_bar(idea.total_score)}")
    print(f"  Verdict     : {vc}{b(idea.verdict)}{RESET}  —  {idea.verdict_action}")
    print(f"  Knowledge   : {b(idea.knowledge_status)}")
    print(f"  Est. Cost   : {b(str(idea.estimated_cost))}")
    roi_val = idea.roi()
    roi_color = grn if roi_val > 10 else (ylw if roi_val > 0 else red)
    print(f"  ROI         : {roi_color(b(str(round(roi_val, 1))))}")

    iv = idea.idea_value()
    if iv > 0:
        print(f"  Idea Value  : {grn(b(str(int(iv))))} (non-zero — has live value)")
    else:
        print(f"  Idea Value  : {red('0')}  (untested, unexecuted, or blocked multiplier)")

    if idea.test:
        t = idea.test
        s = grn("✔ PASSED") if t.result == "pass" else (
            red("✘ FAILED") if t.result == "fail" else ylw("⏳ PENDING"))
        print(f"  Test        : {s}")

    exe = grn("✔ EXECUTED") if idea.executed else red("✘ NOT EXECUTED")
    print(f"  Executed    : {exe}")

    if idea.killed:
        print(f"  {red('☠  KILLED')} — {dim(idea.kill_reason)}")
    print()


def print_idea_card(idea, index: int):
    vc  = VERDICT_COLOR.get(idea.verdict, WHITE)
    iv  = int(idea.idea_value())
    exe = grn("✔") if idea.executed else red("✘")
    tst = (grn("✔") if (idea.test and idea.test.result == "pass") else
           red("✘") if (idea.test and idea.test.result == "fail") else
           ylw("?") if idea.test else dim("-"))
    killed = red(" [KILLED]") if idea.killed else ""

    from domains import get_domain
    dom_label = get_domain(idea.domain)["label"][:14].ljust(14)
    s_disp = f"{idea.total_score:.1f}"

    print(f"  {dim(str(index).rjust(2))}  {b(idea.name[:28].ljust(28))} "
          f"{cyn(dom_label)}  "
          f"{vc}{idea.verdict.ljust(12)}{RESET}"
          f"Score:{b(s_disp.rjust(4))}  "
          f"Test:{tst} Exe:{exe}  Val:{b(str(iv).rjust(4))} ROI:{b(str(round(idea.roi(), 1)).rjust(4))}"
          f"{killed}")
