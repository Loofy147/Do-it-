"""
domains.py — Domain taxonomy with adaptive dimension profiles.

Every domain redefines what each of the 6 dimensions MEANS,
what a valid TEST looks like, and what EXECUTED means.
"""

# ── DOMAIN REGISTRY ────────────────────────────────────────────────────────────
# Each domain has:
#   label       — display name
#   description — one-line description
#   idea_noun   — what an "idea" is called in this domain
#   dimensions  — 6 adaptive dimension profiles (name, question, scores 0/1/2)
#   test_guide  — what a valid test looks like in this domain
#   execute_guide — what execution means in this domain
#   kill_dim    — which dimension key kills the idea if scored 0

DOMAINS = {
    # ── 13. DEEP RESEARCH ────────────────────────────────────────────────
    "deep_research": {
        "label":       "Deep Research",
        "description": "A high-complexity, multi-stage investigation into a recurring problem or novel field.",
        "idea_noun":   "Research Initiative",
        "test_guide":  "Phase 1: literature review and problem decomposition. Phase 2: pilot experiment or case study. "
                       "Verify findings with peer experts or through cross-methodology triangulation.",
        "execute_guide": "Publish a comprehensive research report with raw data, methodology, and peer-reviewed conclusions.",
        "kill_dim":    "problem_novelty",
        "dimensions": {
            "problem_novelty": {
                "name":     "PROBLEM NOVELTY",
                "question": "Is the problem either undocumented or recurring despite prior attempts?",
                "scores": {
                    0: "Problem is well-understood and solved. Research adds no new value.",
                    1: "Problem is known but prior solutions are incomplete or failing.",
                    2: "Novel problem or documented recurring failure with no known root cause.",
                },
            },
            "methodological_rigor": {
                "name":     "METHODOLOGICAL RIGOR",
                "question": "Is the research plan rigorous enough to produce verifiable, non-obvious insights?",
                "scores": {
                    0: "Surface-level inquiry only. No distinct methodology.",
                    1: "Solid plan but lacks multi-method triangulation or external validation.",
                    2: "Rigorous, multi-stage methodology with clear bias controls and peer check-ins.",
                },
            },
            "falsifiability": {
                "name":     "FALSIFIABILITY",
                "question": "Can the central hypothesis or finding be proven wrong by specific data?",
                "scores": {
                    0: "Claims are descriptive only and cannot be disproven.",
                    1: "Partially falsifiable. Some findings could challenge the thesis.",
                    2: "Strictly falsifiable. Specific evidence would conclusively invalidate the results.",
                },
            },
            "resource_reachability": {
                "name":     "ACCESS & INSTRUMENTATION",
                "question": "Do you have access to the data, experts, and instruments needed for deep inquiry?",
                "scores": {
                    0: "Requires data or access you cannot obtain.",
                    1: "Access is possible but requires significant negotiation or long-tail collection.",
                    2: "Full access to data, subjects, and tools confirmed.",
                },
            },
            "impact_significance": {
                "name":     "SIGNIFICANCE",
                "question": "Does resolving this unlock significant downstream value or clarify a major field?",
                "scores": {
                    0: "Incremental insight with minimal impact on the field.",
                    1: "Moderate impact. Clarifies a specific sub-problem.",
                    2: "High impact. Resolves a recurring blocker or establishes a new foundation.",
                },
            },
            "investigator_fit": {
                "name":     "INVESTIGATOR FIT",
                "question": "Do you have the patience, rigor, and background to lead this recurring inquiry?",
                "scores": {
                    0: "Outside your domain or temperament. Likely to abandon or oversimplify.",
                    1: "Domain-aligned but requires developing deeper methodological skills.",
                    2: "Perfect fit. Proven track record in complex, long-tail investigations.",
                },
            },
        },
    },

    # ── 1. QUESTION / ANSWER ────────────────────────────────────────────────
    "qa": {
        "label":       "Question / Answer",
        "description": "A question seeking a resolved, verifiable answer.",
        "idea_noun":   "Question",
        "test_guide":  "Research, cite sources, verify with domain expert or cross-reference "
                       "multiple independent authoritative sources.",
        "execute_guide": "Document and publish the answer in a form that can be used, taught, or referenced.",
        "kill_dim":    "question_clarity",
        "dimensions": {
            "question_clarity": {
                "name":     "QUESTION CLARITY",
                "question": "Is the question precise enough to have a definitive or falsifiable answer?",
                "scores": {
                    0: "The question is vague, circular, or unanswerable by nature.",
                    1: "The question is understandable but has multiple valid interpretations.",
                    2: "The question is precise, bounded, and answerable with evidence.",
                },
            },
            "prior_research": {
                "name":     "PRIOR RESEARCH CHECK",
                "question": "Has this question already been answered definitively?",
                "scores": {
                    0: "You have not checked. You may be reinventing the wheel.",
                    1: "Partial answers exist. Yours adds a missing dimension.",
                    2: "You have surveyed the field. Your question fills a documented gap.",
                },
            },
            "falsifiability": {
                "name":     "FALSIFIABILITY",
                "question": "Can the proposed answer be proven wrong by evidence or logic?",
                "scores": {
                    0: "The answer is opinion or unfalsifiable belief.",
                    1: "Partially testable — some claims could be checked.",
                    2: "Fully testable. A specific piece of evidence could disprove it.",
                },
            },
            "source_reachability": {
                "name":     "SOURCE REACHABILITY",
                "question": "Can you actually access the evidence or expertise needed to answer this?",
                "scores": {
                    0: "Requires access to restricted data, rare experts, or dead knowledge.",
                    1: "Sources exist but require significant effort to obtain.",
                    2: "Sources are accessible now — papers, experts, data you can reach.",
                },
            },
            "answer_originality": {
                "name":     "ORIGINALITY",
                "question": "Does answering this add value beyond what already exists?",
                "scores": {
                    0: "Fully answered and documented elsewhere.",
                    1: "Answered but scattered — your synthesis adds value.",
                    2: "Not answered clearly anywhere. Genuine gap.",
                },
            },
            "capability_fit": {
                "name":     "CAPABILITY FIT",
                "question": "Do you have the knowledge, tools, or access to research this credibly?",
                "scores": {
                    0: "Outside your domain. You cannot credibly research or verify this.",
                    1: "Peripheral to your expertise. Manageable with effort.",
                    2: "Within your domain or you have clear access to required expertise.",
                },
            },
        },
    },

    # ── 2. METHODOLOGY ──────────────────────────────────────────────────────
    "methodology": {
        "label":       "Methodology",
        "description": "A proposed process, framework, or systematic approach to doing something.",
        "idea_noun":   "Methodology",
        "test_guide":  "Apply the methodology to a real case. Measure output quality against "
                       "a defined success metric. Compare to the previous approach if one exists.",
        "execute_guide": "Document the methodology fully, apply it in a real context, and publish or deploy results.",
        "kill_dim":    "problem_reality",
        "dimensions": {
            "problem_reality": {
                "name":     "PROBLEM REALITY",
                "question": "Does the problem this methodology solves actually exist and cause measurable friction?",
                "scores": {
                    0: "The problem is assumed. No evidence it exists at scale.",
                    1: "Observed anecdotally in limited contexts.",
                    2: "Documented friction with measurable impact — time, error rate, cost.",
                },
            },
            "process_specificity": {
                "name":     "PROCESS SPECIFICITY",
                "question": "Is the methodology specific enough that two people would apply it the same way?",
                "scores": {
                    0: "A set of vague principles. Not replicable.",
                    1: "Partially defined. Requires significant interpretation to apply.",
                    2: "Fully defined steps. Two independent practitioners reach comparable outputs.",
                },
            },
            "falsifiability": {
                "name":     "MEASURABILITY",
                "question": "Can the methodology's effectiveness be measured against a clear benchmark?",
                "scores": {
                    0: "No metric exists. Effectiveness is subjective.",
                    1: "Metric exists but is qualitative or hard to measure consistently.",
                    2: "Clear quantitative metric. Before/after comparison is possible.",
                },
            },
            "execution_reachability": {
                "name":     "APPLICATION REACHABILITY",
                "question": "Can you apply this methodology to a real case within 30 days?",
                "scores": {
                    0: "Requires resources, access, or conditions you cannot obtain.",
                    1: "Possible but requires arranging significant access or data.",
                    2: "You have a real case available to apply it to right now.",
                },
            },
            "competition_resistance": {
                "name":     "IMPROVEMENT OVER EXISTING",
                "question": "How much better is this than the current approach?",
                "scores": {
                    0: "Established methods already solve this well. Marginal gain at best.",
                    1: "Better in specific conditions. Not universally superior.",
                    2: "Demonstrably superior in speed, accuracy, cost, or scalability.",
                },
            },
            "capability_fit": {
                "name":     "DOMAIN AUTHORITY",
                "question": "Do you have the expertise to design and validate this methodology?",
                "scores": {
                    0: "Outside your domain. You cannot credibly validate it.",
                    1: "Adjacent expertise. Requires significant outside validation.",
                    2: "Core domain. You can design, apply, and defend it.",
                },
            },
        },
    },

    # ── 3. PROJECT ──────────────────────────────────────────────────────────
    "project": {
        "label":       "Project",
        "description": "A bounded initiative with a defined output, timeline, and resources.",
        "idea_noun":   "Project",
        "test_guide":  "Define an MVP or prototype. Build the smallest version that proves "
                       "the core output is achievable. Validate against defined acceptance criteria.",
        "execute_guide": "Deliver the full project output to its intended audience or use case.",
        "kill_dim":    "objective_clarity",
        "dimensions": {
            "objective_clarity": {
                "name":     "OBJECTIVE CLARITY",
                "question": "Is the project output defined precisely enough to know when it is done?",
                "scores": {
                    0: "The goal is vague. 'Done' is undefined.",
                    1: "Goal is understandable but acceptance criteria are missing.",
                    2: "Output is fully defined. Completion criteria are binary and clear.",
                },
            },
            "scope_specificity": {
                "name":     "SCOPE SPECIFICITY",
                "question": "Are the boundaries of the project clearly defined — what's in and what's out?",
                "scores": {
                    0: "Scope is unlimited or undefined. Scope creep is inevitable.",
                    1: "Core scope defined but edges are fuzzy.",
                    2: "Explicit in-scope and out-of-scope defined. Dependencies identified.",
                },
            },
            "falsifiability": {
                "name":     "TESTABILITY",
                "question": "Can you validate the output against defined acceptance criteria before calling it done?",
                "scores": {
                    0: "No acceptance criteria. Quality is subjective.",
                    1: "Some criteria defined but incomplete.",
                    2: "Full acceptance criteria documented. Output is testable objectively.",
                },
            },
            "execution_reachability": {
                "name":     "RESOURCE REACHABILITY",
                "question": "Do you have the people, tools, time, and budget to complete this?",
                "scores": {
                    0: "Missing critical resources with no clear path to obtain them.",
                    1: "Resources mostly available. One or two significant gaps.",
                    2: "All critical resources confirmed. Timeline is realistic.",
                },
            },
            "competition_resistance": {
                "name":     "NECESSITY",
                "question": "Does this project need to exist? Is there a clear need or mandate?",
                "scores": {
                    0: "Nice to have. No pressing need.",
                    1: "Needed but not urgent. Could be deferred.",
                    2: "Clear mandate or urgent need from an identified stakeholder.",
                },
            },
            "capability_fit": {
                "name":     "TEAM CAPABILITY",
                "question": "Does the team have the skills and experience to execute this project?",
                "scores": {
                    0: "Critical skill gaps with no plan to fill them.",
                    1: "Core skills present. Some gaps being addressed.",
                    2: "All required skills confirmed on the team.",
                },
            },
        },
    },

    # ── 4. LAW / POLICY ─────────────────────────────────────────────────────
    "law": {
        "label":       "Law / Policy",
        "description": "A proposed legal rule, regulation, or public policy.",
        "idea_noun":   "Law / Policy",
        "test_guide":  "Pilot the policy in a limited jurisdiction or context. Review existing "
                       "precedents and analogous laws. Conduct stakeholder consultation and "
                       "model the second-order effects.",
        "execute_guide": "Draft, submit, debate, enact, and enforce the law or policy.",
        "kill_dim":    "problem_evidence",
        "dimensions": {
            "problem_evidence": {
                "name":     "PROBLEM EVIDENCE",
                "question": "Is there documented, measurable evidence that the problem this law addresses exists?",
                "scores": {
                    0: "Anecdotal or ideological. No data.",
                    1: "Some documented cases but limited scale or rigor.",
                    2: "Statistical evidence, documented harm, or clear systemic gap.",
                },
            },
            "legal_specificity": {
                "name":     "LEGAL SPECIFICITY",
                "question": "Is the proposed law/policy precise enough to be drafted and enforced?",
                "scores": {
                    0: "A principle or wish. Cannot be written into law as stated.",
                    1: "Direction is clear but ambiguities would create enforcement problems.",
                    2: "Specific enough to draft. Definitions, scope, and penalties clear.",
                },
            },
            "falsifiability": {
                "name":     "MEASURABLE IMPACT",
                "question": "Can the law's success or failure be measured after implementation?",
                "scores": {
                    0: "No metric. Impossible to evaluate if it worked.",
                    1: "Metric exists but hard to isolate from other variables.",
                    2: "Clear KPI. Counterfactual comparison is possible.",
                },
            },
            "execution_reachability": {
                "name":     "LEGISLATIVE PATHWAY",
                "question": "Is there a realistic pathway to get this enacted and enforced?",
                "scores": {
                    0: "Requires political conditions, coalitions, or resources not obtainable.",
                    1: "Path exists but requires significant political or institutional work.",
                    2: "Clear legislative pathway. Sponsors, jurisdiction, and process identified.",
                },
            },
            "competition_resistance": {
                "name":     "PRECEDENT & CONFLICT",
                "question": "Does this conflict with existing laws, constitutional limits, or entrenched opposition?",
                "scores": {
                    0: "Conflicts with existing law or faces overwhelming opposition.",
                    1: "Some conflicts. Requires amendments or exceptions.",
                    2: "Consistent with existing framework. Opposition is manageable.",
                },
            },
            "capability_fit": {
                "name":     "INSTITUTIONAL AUTHORITY",
                "question": "Do you or your organization have the standing and knowledge to propose and advance this?",
                "scores": {
                    0: "No standing, expertise, or institutional access.",
                    1: "Adjacent standing. Requires partnering with those who have authority.",
                    2: "Direct standing, legal expertise, and institutional relationships.",
                },
            },
        },
    },

    # ── 5. MATHEMATICS ──────────────────────────────────────────────────────
    "mathematics": {
        "label":       "Mathematics",
        "description": "A conjecture, theorem, proof, or mathematical structure.",
        "idea_noun":   "Conjecture / Theorem",
        "test_guide":  "Formal proof or disproof. Verify with peer mathematicians. "
                       "Check for counterexamples. Submit for peer review.",
        "execute_guide": "Publish a rigorous proof or disproof in a peer-reviewed form.",
        "kill_dim":    "statement_precision",
        "dimensions": {
            "statement_precision": {
                "name":     "STATEMENT PRECISION",
                "question": "Is the mathematical statement precise, unambiguous, and well-defined?",
                "scores": {
                    0: "Vague or uses undefined terms. Cannot be formally stated.",
                    1: "Mostly precise but requires clarification of edge cases.",
                    2: "Fully rigorous. Can be written in formal notation without ambiguity.",
                },
            },
            "novelty": {
                "name":     "NOVELTY",
                "question": "Has this been proven, disproven, or documented before?",
                "scores": {
                    0: "Already proven. This is a known result.",
                    1: "Related results exist. This is a meaningful extension or generalization.",
                    2: "Open problem or undocumented. Genuine contribution if proven.",
                },
            },
            "falsifiability": {
                "name":     "PROVABILITY PATH",
                "question": "Is there a plausible strategy or approach toward proof or disproof?",
                "scores": {
                    0: "No known strategy. No tools or methods that could tackle it.",
                    1: "Partial strategy. One or more approaches are plausible but incomplete.",
                    2: "Clear proof strategy. Existing theorems and tools are applicable.",
                },
            },
            "execution_reachability": {
                "name":     "PROOF REACHABILITY",
                "question": "Can you construct a complete proof or find a counterexample with current knowledge?",
                "scores": {
                    0: "Beyond current mathematical knowledge or your competency.",
                    1: "Challenging but tractable with significant work.",
                    2: "Achievable with current tools and your mathematical background.",
                },
            },
            "competition_resistance": {
                "name":     "SIGNIFICANCE",
                "question": "How significant is this result to the field if proven?",
                "scores": {
                    0: "Minor lemma. Useful only within a narrow sub-problem.",
                    1: "Moderate significance. Advances a specific area.",
                    2: "High significance. Unlocks further results or resolves an important open problem.",
                },
            },
            "capability_fit": {
                "name":     "MATHEMATICAL COMPETENCY",
                "question": "Do you have the mathematical background to pursue this proof rigorously?",
                "scores": {
                    0: "Requires expertise well beyond your current level.",
                    1: "At the edge of your competency. Requires significant study.",
                    2: "Within your mathematical domain and current skill level.",
                },
            },
        },
    },

    # ── 6. SCIENTIFIC HYPOTHESIS ────────────────────────────────────────────
    "science": {
        "label":       "Scientific Hypothesis",
        "description": "A testable explanation or prediction about a natural or empirical phenomenon.",
        "idea_noun":   "Hypothesis",
        "test_guide":  "Design a controlled experiment or observational study with a defined "
                       "null hypothesis, sample size, and significance threshold. "
                       "Run it. Record results. Attempt to replicate.",
        "execute_guide": "Publish findings — positive or negative — in a peer-reviewed venue.",
        "kill_dim":    "hypothesis_precision",
        "dimensions": {
            "hypothesis_precision": {
                "name":     "HYPOTHESIS PRECISION",
                "question": "Is the hypothesis stated precisely — with a clear independent variable, dependent variable, and prediction?",
                "scores": {
                    0: "Vague claim. Cannot be operationalized into an experiment.",
                    1: "Direction is clear but variables are not fully operationalized.",
                    2: "Fully operationalized. IV, DV, and predicted relationship are explicit.",
                },
            },
            "prior_evidence": {
                "name":     "PRIOR EVIDENCE",
                "question": "Does existing literature support the plausibility of this hypothesis?",
                "scores": {
                    0: "Contradicts established findings with no basis for challenge.",
                    1: "Mixed evidence. Plausible but contested.",
                    2: "Supported by prior work. This study advances or confirms a plausible mechanism.",
                },
            },
            "falsifiability": {
                "name":     "FALSIFIABILITY",
                "question": "Can this hypothesis be definitively disproven by a specific experimental result?",
                "scores": {
                    0: "Cannot be disproven. Not a scientific hypothesis.",
                    1: "Partially falsifiable. Some results could weaken but not kill it.",
                    2: "Fully falsifiable. A specific result would conclusively disprove it.",
                },
            },
            "execution_reachability": {
                "name":     "EXPERIMENTAL REACHABILITY",
                "question": "Can you design and run the experiment with available resources?",
                "scores": {
                    0: "Requires unavailable equipment, samples, funding, or approval.",
                    1: "Possible with significant effort to secure access and resources.",
                    2: "Resources, equipment, and access are confirmed or obtainable.",
                },
            },
            "competition_resistance": {
                "name":     "CONTRIBUTION",
                "question": "Does this hypothesis, if confirmed, fill a genuine gap in the literature?",
                "scores": {
                    0: "Already studied and settled. Confirming it adds no new knowledge.",
                    1: "Adds a marginal extension to known findings.",
                    2: "Fills a documented gap or challenges a poorly-tested assumption.",
                },
            },
            "capability_fit": {
                "name":     "RESEARCH COMPETENCY",
                "question": "Do you have the domain knowledge, lab skills, and methodology to run this study credibly?",
                "scores": {
                    0: "Outside your field. You cannot design or run this credibly.",
                    1: "Adjacent field. Requires significant collaboration with domain experts.",
                    2: "Core domain. You can design, execute, and interpret independently.",
                },
            },
        },
    },

    # ── 7. PHILOSOPHY / ARGUMENT ────────────────────────────────────────────
    "philosophy": {
        "label":       "Philosophy / Argument",
        "description": "A philosophical thesis, ethical argument, or logical claim.",
        "idea_noun":   "Thesis / Argument",
        "test_guide":  "Submit the argument to logical consistency check: identify premises, "
                       "map inference steps, stress-test with strongest known counterarguments. "
                       "Seek peer challenge from those who disagree.",
        "execute_guide": "Publish a written argument that can be engaged with, challenged, and cited.",
        "kill_dim":    "thesis_clarity",
        "dimensions": {
            "thesis_clarity": {
                "name":     "THESIS CLARITY",
                "question": "Can the central claim be stated in one sentence that others could agree or disagree with?",
                "scores": {
                    0: "Cannot be stated precisely. It is a mood, not a claim.",
                    1: "Stateable but requires significant unpacking to evaluate.",
                    2: "Clear, precise claim. Agreement and disagreement are both possible.",
                },
            },
            "premise_validity": {
                "name":     "PREMISE VALIDITY",
                "question": "Are the foundational premises of the argument defensible?",
                "scores": {
                    0: "Premises are contested or demonstrably false.",
                    1: "Premises are reasonable but some require defense.",
                    2: "Premises are well-grounded in evidence, logic, or widely-accepted prior work.",
                },
            },
            "falsifiability": {
                "name":     "LOGICAL CONSISTENCY",
                "question": "Is the argument free of internal contradictions and valid in its logical form?",
                "scores": {
                    0: "Contains identifiable logical fallacies or internal contradictions.",
                    1: "Mostly valid. Minor gaps in the inferential chain.",
                    2: "Logically valid. Inference from premises to conclusion is sound.",
                },
            },
            "execution_reachability": {
                "name":     "ARGUMENT COMPLETENESS",
                "question": "Can you construct and document the full argument now?",
                "scores": {
                    0: "Critical pieces of the argument are missing. Cannot be written yet.",
                    1: "Core argument possible but important supporting sections need work.",
                    2: "Full argument can be written and defended now.",
                },
            },
            "competition_resistance": {
                "name":     "COUNTERARGUMENT RESISTANCE",
                "question": "How well does this argument survive its strongest known counterarguments?",
                "scores": {
                    0: "Defeated by well-known counterarguments already in the literature.",
                    1: "Survives most counterarguments. One significant challenge remains.",
                    2: "Survives all known counterarguments. Rebuttals are prepared.",
                },
            },
            "capability_fit": {
                "name":     "PHILOSOPHICAL COMPETENCY",
                "question": "Do you have sufficient grounding in the relevant tradition to argue this credibly?",
                "scores": {
                    0: "Outside your philosophical training. Argument risks fundamental errors.",
                    1: "Familiar with the field but gaps in relevant literature.",
                    2: "Well-grounded. You have read the relevant tradition and can defend it.",
                },
            },
        },
    },

    # ── 8. BUSINESS / STARTUP ───────────────────────────────────────────────
    "business": {
        "label":       "Business / Startup",
        "description": "A commercial idea — product, service, or business model.",
        "idea_noun":   "Business Idea",
        "test_guide":  "Minimum viable test: landing page, 10 customer conversations, "
                       "one attempted sale, or a prototype. Define pass/fail in numbers before running.",
        "execute_guide": "Build, launch, and generate first revenue or measurable user adoption.",
        "kill_dim":    "problem_reality",
        "dimensions": {
            "problem_reality": {
                "name":     "PROBLEM REALITY",
                "question": "Does the problem exist with documented, external evidence?",
                "scores": {
                    0: "Assumed. No external evidence.",
                    1: "Observed personally or from a few people.",
                    2: "Documented — data, interviews, churn, search volume, complaints.",
                },
            },
            "solution_specificity": {
                "name":     "SOLUTION SPECIFICITY",
                "question": "Is your solution concrete enough that someone else could build it?",
                "scores": {
                    0: "A direction. Not a solution. ('We'll use AI to fix it.')",
                    1: "Defined but major components are still open.",
                    2: "Fully specced. Someone could build it without asking you a question.",
                },
            },
            "falsifiability": {
                "name":     "FALSIFIABILITY",
                "question": "Can this idea be proven wrong by a specific, cheap test?",
                "scores": {
                    0: "Cannot fail a test. ('We'll iterate until it works.')",
                    1: "Test exists but success criteria are vague.",
                    2: "Specific binary test. Exact pass/fail numbers defined.",
                },
            },
            "execution_reachability": {
                "name":     "EXECUTION REACHABILITY",
                "question": "Can you ship a first version in 30 days with what you currently have?",
                "scores": {
                    0: "Requires capital, skills, or access you have no path to.",
                    1: "Possible but requires obtaining significant missing resources.",
                    2: "Executable in 30 days with current or easily obtainable resources.",
                },
            },
            "competition_resistance": {
                "name":     "COMPETITION RESISTANCE",
                "question": "If this shows traction, who is motivated and able to crush it?",
                "scores": {
                    0: "Large incumbent does this and can copy you in a week.",
                    1: "Competition exists. You have a defensible angle.",
                    2: "Structural advantage that is hard to replicate.",
                },
            },
            "capability_fit": {
                "name":     "PERSONAL EDGE",
                "question": "Why specifically are you the one to execute this?",
                "scores": {
                    0: "No specific reason. You just think it is a good business.",
                    1: "Motivated but no specific edge in knowledge, network, or access.",
                    2: "Specific and real reason you see or can do this better than others.",
                },
            },
        },
    },

    # ── 9. EDUCATIONAL CONCEPT ──────────────────────────────────────────────
    "education": {
        "label":       "Educational Concept",
        "description": "A new way of teaching, explaining, or structuring learning for a topic.",
        "idea_noun":   "Educational Concept",
        "test_guide":  "Teach it to a small group. Measure comprehension before and after "
                       "using a defined test. Compare to the previous teaching method if one exists.",
        "execute_guide": "Deploy the concept in a real learning environment and document learning outcomes.",
        "kill_dim":    "learning_gap",
        "dimensions": {
            "learning_gap": {
                "name":     "LEARNING GAP",
                "question": "Is there a documented gap in how this topic is currently taught or understood?",
                "scores": {
                    0: "No gap. Existing resources are adequate.",
                    1: "Gap exists but is limited to specific audiences or formats.",
                    2: "Documented gap — high failure rates, persistent misconceptions, or absent coverage.",
                },
            },
            "concept_specificity": {
                "name":     "CONCEPT SPECIFICITY",
                "question": "Is the teaching approach defined precisely enough that another teacher could replicate it?",
                "scores": {
                    0: "Vague. Another teacher would implement it differently.",
                    1: "Core idea is clear but key materials or steps are missing.",
                    2: "Fully specified. Replicable by any qualified teacher.",
                },
            },
            "falsifiability": {
                "name":     "MEASURABLE LEARNING",
                "question": "Can learning improvement be measured against a specific benchmark?",
                "scores": {
                    0: "No metric. Improvement is subjective.",
                    1: "Metric exists but is hard to isolate from other factors.",
                    2: "Clear before/after metric. Comprehension can be measured objectively.",
                },
            },
            "execution_reachability": {
                "name":     "DEPLOYMENT REACHABILITY",
                "question": "Can you teach this to a real group within 30 days?",
                "scores": {
                    0: "No access to learners or the required environment.",
                    1: "Access possible but requires significant arrangement.",
                    2: "Group available now. Materials can be prepared in time.",
                },
            },
            "competition_resistance": {
                "name":     "SUPERIORITY",
                "question": "How much better is this than how the topic is currently taught?",
                "scores": {
                    0: "Existing approaches are equivalent. No clear advantage.",
                    1: "Better for a specific audience or context.",
                    2: "Demonstrably superior in comprehension, retention, or efficiency.",
                },
            },
            "capability_fit": {
                "name":     "TEACHING AUTHORITY",
                "question": "Do you understand the subject and the learners well enough to design this?",
                "scores": {
                    0: "Neither the subject matter nor the learner group is in your domain.",
                    1: "Familiar with one but not the other.",
                    2: "Deep knowledge of both the subject and the target learner.",
                },
            },
        },
    },

    # ── 10. TECHNOLOGY / ENGINEERING ────────────────────────────────────────
    "technology": {
        "label":       "Technology / Engineering",
        "description": "A technical system, tool, architecture, or engineering solution.",
        "idea_noun":   "Technical Solution",
        "test_guide":  "Build a working prototype or proof of concept. Benchmark it against "
                       "defined performance criteria. Stress test failure modes.",
        "execute_guide": "Deploy to production or deliver the system to its intended users/environment.",
        "kill_dim":    "technical_requirement",
        "dimensions": {
            "technical_requirement": {
                "name":     "TECHNICAL REQUIREMENT",
                "question": "Is the technical problem and required system behavior precisely defined?",
                "scores": {
                    0: "Requirements are vague. What the system must do is undefined.",
                    1: "Core function defined. Edge cases and constraints not specified.",
                    2: "Full requirements: inputs, outputs, performance targets, constraints.",
                },
            },
            "solution_specificity": {
                "name":     "ARCHITECTURE SPECIFICITY",
                "question": "Is the proposed technical approach concrete enough to begin building?",
                "scores": {
                    0: "Concept only. No technical approach decided.",
                    1: "Approach chosen. Major implementation decisions still open.",
                    2: "Architecture defined. Stack, data flow, and interfaces specified.",
                },
            },
            "falsifiability": {
                "name":     "TESTABILITY",
                "question": "Are there defined acceptance tests that prove the system works or fails?",
                "scores": {
                    0: "No acceptance criteria. 'It works' is subjective.",
                    1: "Some tests defined. Edge cases and failure modes not covered.",
                    2: "Full test suite defined. Pass/fail is objective and automated.",
                },
            },
            "execution_reachability": {
                "name":     "BUILD REACHABILITY",
                "question": "Can you build a working prototype with current skills and tools?",
                "scores": {
                    0: "Requires unavailable hardware, APIs, expertise, or infrastructure.",
                    1: "Possible with significant effort to acquire missing elements.",
                    2: "Stack and tools are in hand. Prototype is buildable now.",
                },
            },
            "competition_resistance": {
                "name":     "TECHNICAL ADVANTAGE",
                "question": "Does this solution offer a technical advantage over existing alternatives?",
                "scores": {
                    0: "Existing tools do this. No meaningful technical differentiation.",
                    1: "Better in specific conditions. Not universally superior.",
                    2: "Measurable improvement in performance, cost, or capability.",
                },
            },
            "capability_fit": {
                "name":     "ENGINEERING COMPETENCY",
                "question": "Does the team have the technical skills to build, test, and maintain this?",
                "scores": {
                    0: "Critical skill gaps. Core technology is outside team expertise.",
                    1: "Mostly covered. One or two significant gaps.",
                    2: "Full competency. Team has built comparable systems before.",
                },
            },
        },
    },

    # ── 11. SOCIAL / BEHAVIORAL ─────────────────────────────────────────────
    "social": {
        "label":       "Social / Behavioral",
        "description": "An observation, intervention, or claim about human behavior or social systems.",
        "idea_noun":   "Behavioral Claim",
        "test_guide":  "Design an observational study, survey, or behavioral experiment. "
                       "Define sample, measurement instrument, and significance threshold. Run it.",
        "execute_guide": "Apply the insight or intervention at scale and document behavioral outcomes.",
        "kill_dim":    "claim_precision",
        "dimensions": {
            "claim_precision": {
                "name":     "CLAIM PRECISION",
                "question": "Is the behavioral claim stated precisely enough to be studied?",
                "scores": {
                    0: "Vague generalization. Cannot be operationalized.",
                    1: "Direction is clear but key variables are undefined.",
                    2: "Precise claim with defined population, behavior, and context.",
                },
            },
            "evidence_base": {
                "name":     "EXISTING EVIDENCE",
                "question": "What does existing research say about this claim?",
                "scores": {
                    0: "Contradicts established behavioral research with no basis.",
                    1: "Mixed evidence. Plausible but underdetermined.",
                    2: "Supported by prior research. New study adds rigor or scale.",
                },
            },
            "falsifiability": {
                "name":     "FALSIFIABILITY",
                "question": "Can a specific study result disprove this claim?",
                "scores": {
                    0: "Unfalsifiable. Can be explained away by any result.",
                    1: "Partially falsifiable. Weak results could reduce but not end it.",
                    2: "Fully falsifiable. A defined result would conclusively disprove it.",
                },
            },
            "execution_reachability": {
                "name":     "STUDY REACHABILITY",
                "question": "Can you design and run a study with accessible participants and resources?",
                "scores": {
                    0: "Requires population, equipment, or approvals not obtainable.",
                    1: "Study possible but requires significant access arrangements.",
                    2: "Participants and resources are accessible. Study can begin now.",
                },
            },
            "competition_resistance": {
                "name":     "CONTRIBUTION",
                "question": "Does this add meaningfully to the existing body of knowledge?",
                "scores": {
                    0: "Already well-established. Repeating known results.",
                    1: "Extends existing work in a useful but limited way.",
                    2: "Fills a genuine gap or challenges a poorly-tested consensus.",
                },
            },
            "capability_fit": {
                "name":     "RESEARCH COMPETENCY",
                "question": "Do you have the methodological skills to design and analyze this study?",
                "scores": {
                    0: "Outside your research training. Results would not be credible.",
                    1: "Adjacent. Requires significant collaboration.",
                    2: "Core competency. You can design, run, and analyze independently.",
                },
            },
        },
    },

    # ── 12. CREATIVE / ARTISTIC ─────────────────────────────────────────────
    "creative": {
        "label":       "Creative / Artistic",
        "description": "A creative concept — story, artwork, design, music, film, or other creative work.",
        "idea_noun":   "Creative Concept",
        "test_guide":  "Produce a draft, prototype, or sketch. Share with a defined audience. "
                       "Measure response against a defined success criterion — not 'did they like it' "
                       "but a specific behavioral response (read to the end, shared it, bought it).",
        "execute_guide": "Complete and publish/release the full creative work.",
        "kill_dim":    "concept_clarity",
        "dimensions": {
            "concept_clarity": {
                "name":     "CONCEPT CLARITY",
                "question": "Can you state the core creative idea in one sentence that makes someone want to engage?",
                "scores": {
                    0: "Vague aesthetic or mood. No distinct concept.",
                    1: "Concept exists but is generic or underdeveloped.",
                    2: "Distinct, specific concept. Someone hearing it wants to see it made.",
                },
            },
            "originality": {
                "name":     "ORIGINALITY",
                "question": "Does this bring a perspective, form, or combination that hasn't been done?",
                "scores": {
                    0: "Derivative. Follows an established formula without a new element.",
                    1: "Familiar form with one original element.",
                    2: "Distinct combination of form, voice, or subject that stands alone.",
                },
            },
            "falsifiability": {
                "name":     "AUDIENCE TESTABILITY",
                "question": "Can you define what a successful audience response looks like before creating it?",
                "scores": {
                    0: "Success is undefined. You'll know it when you see it.",
                    1: "Rough goal defined. Somewhat vague.",
                    2: "Specific behavioral metric defined. (e.g. 70% read to the end, 20% share rate.)",
                },
            },
            "execution_reachability": {
                "name":     "PRODUCTION REACHABILITY",
                "question": "Can you produce this with the skills and resources you have now?",
                "scores": {
                    0: "Requires budget, collaborators, or tools you cannot access.",
                    1: "Possible with significant missing resources.",
                    2: "Fully producible with current resources and skills.",
                },
            },
            "competition_resistance": {
                "name":     "AUDIENCE NEED",
                "question": "Is there a defined audience with an unmet need this work addresses?",
                "scores": {
                    0: "No specific audience. Made for everyone means made for no one.",
                    1: "Audience identified but need is vague.",
                    2: "Specific audience with a documented gap in existing work.",
                },
            },
            "capability_fit": {
                "name":     "CRAFT COMPETENCY",
                "question": "Do you have the craft skills to execute this at the quality the concept demands?",
                "scores": {
                    0: "Concept requires craft beyond your current level.",
                    1: "Within reach with significant development.",
                    2: "Fully within your current craft level.",
                },
            },
        },
    },
}


def get_domain(key: str) -> dict:
    return DOMAINS.get(key, DOMAINS["business"])


def list_domains() -> list[tuple[str, str, str]]:
    """Returns [(key, label, description)] sorted for display."""
    return [(k, v["label"], v["description"]) for k, v in DOMAINS.items()]
