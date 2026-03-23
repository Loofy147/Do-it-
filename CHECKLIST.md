# IDEA BENCHMARKING CHECKLIST

Follow these steps to ensure rigorous evaluation of any new initiative.

## 1. Capture & Classify
- [ ] Select the most specific domain (use `python3 idea_lab.py domains` for options).
- [ ] Provide a clear, one-sentence description.
- [ ] Assign initial scores ruthlessly (0, 1, or 2).

## 2. Research & Refine
- [ ] Record initial findings using `python3 idea_lab.py research <id>`.
- [ ] If new evidence challenges a score, use `python3 idea_lab.py pivot <id>`.
- [ ] Aim for at least **EXPLORING** status before designing a test.

## 3. Minimum Viable Test (MVT)
- [ ] Identify the **single most critical assumption** that could kill the idea.
- [ ] Design a test that is **cheap, fast, and binary**.
- [ ] Define success and failure criteria **before** running the test.
- [ ] Set a hard deadline.

## 4. Record & Pivot
- [ ] Enter the test result using `python3 idea_lab.py result <id>`.
- [ ] **If Failed**: Either KILL the idea immediately or PIVOT and redesign the test.
- [ ] **If Passed**: Move to Knowledgeable status and prepare for execution.

## 5. Execution
- [ ] Document the execution process in notes.
- [ ] Mark as executed using `python3 idea_lab.py execute <id>`.
- [ ] Verify the final **Idea Value** is non-zero in the portfolio report.

## 6. Portfolio Review
- [ ] Run `python3 idea_lab.py report` weekly.
- [ ] Analyze "Common Weaknesses" to identify systemic gaps in your thinking.
- [ ] Archive killed ideas to maintain focus on high-value initiatives.
