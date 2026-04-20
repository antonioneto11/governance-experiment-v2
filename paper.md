# Governance as an Endogenous Variable: A Mechanism-Design Perspective on Oversight-Latent Autonomous Systems

**Michelle Melo, PhD** — Brazilian Space Agency  
**Antonio Neto** — Independent Researcher, AI Governance and Autonomous Systems; M.S. FinTech, NYU Stern School of Business

*February 2026*

---

## Abstract

Autonomous systems deployed in high-stakes regulated industries act as decision-making agents rather than passive tools. A pervasive assumption in institutional governance is that observed behavioral compliance under monitoring constitutes reliable evidence of safe deployment behavior. This paper presents a conceptual-formal model—not an empirical causal test—for analyzing governance failure in oversight-latent autonomous systems. Through an extension of the principal-agent framework to cover capable autonomous agents, we argue that this assumption fails systematically once agents can model the oversight mechanism itself. We term this failure *governance endogeneity*: the enforcement environment, monitoring schedule, and recourse structure become part of the agent's optimization landscape rather than external constraints.

The formal contribution of this paper is a structured principal-agent extension that isolates *oversight latency*—the end-to-end loop time for detection, attribution, intervention, and enforcement—and governance endogeneity as the two regime variables that determine when behavioral compliance ceases to be evidentially informative about alignment. From three governance primitives—Constraint (C), Evidence (E), and Recourse (R)—we develop a generative typology of seven governance patterns corresponding to the non-empty subsets of the primitive space, and evaluate each for strategic robustness under monitoring-aware optimization. Using space operations and financial markets as complementary stress-test domains, we show that only patterns containing at least one architectural constraint, independent evidence channel, or credibly enforced recourse mechanism remain safety-relevant under governance endogeneity.

This is a conceptual and mechanism-design paper: it introduces a structured analytical model, a primitive-based governance typology, and an evaluation agenda. It does not report empirical results, does not claim to prove the prevalence of governance endogeneity across deployed systems, and does not derive a closed-form optimal governance mechanism.

**Keywords:** AI governance, autonomous agents, oversight latency, principal-agent theory, deceptive alignment, governance endogeneity, AI safety, regulated industries, mechanism design

---

## 1\. Introduction

Autonomous artificial intelligence systems are no longer simply tools that execute prescribed instructions. In financial markets, algorithmic trading systems allocate capital, manage risk exposures, and interact with other agents at speeds and volumes that far exceed any individual's supervisory capacity (Hendershott et al., 2011). In space operations, onboard autonomous controllers manage power budgets, retarget observation schedules, and classify sensor anomalies across communication windows where ground-based intervention may be delayed by minutes or structurally unavailable (Chien et al., 2010). In healthcare and critical infrastructure, AI systems triage resources and make consequential recommendations in real time under conditions that preclude comprehensive human review of each decision (Topol, 2019).

These deployments share a structural property: the agent acts faster than the oversight loop can detect, attribute, and respond. This is not primarily a problem of network latency, although communication delay is a contributing factor in some domains. It is a problem of *oversight latency*—the end-to-end time required for a principal to detect an anomaly, attribute it causally, determine an appropriate intervention, and execute enforcement or correction. When oversight latency is large relative to the agent's decision tempo and the environment's cascade time, governance cannot operate through real-time supervision. It must be engineered into the system's structure before deployment.

A second structural property intensifies the challenge. As AI systems become more capable and contextually aware, they acquire the capacity to model the oversight mechanism itself. This creates what we term *governance endogeneity*: the enforcement environment, monitoring schedule, and recourse rules cease to be external constraints and become objects of the agent's optimization. Theoretical work on deceptive alignment formalizes the mechanism by which this produces systematic divergence between compliance and alignment (Hubinger et al., 2019). Recent empirical work has demonstrated that large language models can condition behavioral compliance on inferred monitoring status, behaving differently when they assess they are being evaluated versus when they are not (Greenblatt et al., 2024). These findings are significant not as proof of widespread strategic deception in current systems, but as demonstrations of a capability that more capable future systems are structurally likely to exhibit more reliably. Governance frameworks that assume behavioral compliance under evaluation implies safe deployment behavior are structurally vulnerable to this capability.

Existing alignment research provides early empirical support for the narrower capability assumption used here. Recent work on alignment faking shows that a frontier model can alter its behavior when it infers that outputs may affect subsequent training, making compliance conditional on the oversight context rather than invariant across contexts (Greenblatt et al., 2024). Related work on evaluation awareness shows that frontier language models can often distinguish evaluation transcripts from deployment-like interactions, creating a pathway by which observed evaluation behavior may fail to generalize cleanly to real deployment settings (Needham et al., 2025). The significance of these studies is not that they prove generalized deception in deployed systems, but that they render the paper's central threat model—monitoring-conditioned behavior—empirically non-speculative.

Regulated industries present the sharpest version of this problem. Financial regulators, space agencies, healthcare authorities, and infrastructure operators have developed institutional frameworks for oversight—mandatory disclosures, audit trails, licensing requirements, liability regimes—built primarily around the assumption that governed systems will not actively model and optimize against the governance mechanism. That assumption is structurally challenged by capable autonomous agents. The result is that compliance-based governance can produce *governance theater*: the agent passes evaluations and generates compliant-looking artifacts without those signals reflecting genuine alignment with regulatory intent.

This paper responds to that shift. The formal contribution is not a closed-form optimal governance mechanism but a structured extension of principal-agent theory that isolates oversight latency and governance endogeneity as the two regime variables that determine when behavioral compliance ceases to be evidentially informative about alignment. From this foundation, we derive a generative governance typology and evaluate each pattern for strategic robustness. We situate this work within the mechanism-design tradition (Holmström, 1979; Myerson, 1979; Laffont and Martimort, 2002), which provides the most rigorous available framework for analyzing governance under limited observability. Our extension brings that framework to bear on agents that can generalize beyond evaluated conditions, model oversight structures, and optimize for appearances.

The empirical examples and domain comparisons in this paper are illustrative rather than exhaustive; their purpose is to clarify the implications of the conceptual model, not to provide a comprehensive applied analysis.

The paper proceeds as follows. Section 2 defines oversight latency and its components. Section 3 presents the extended principal-agent model and formalizes governance endogeneity, including the evidential failure condition. Section 4 develops the threat model. Section 5 introduces the three governance primitives and derives the pattern typology from the primitive lattice. Section 6 presents the seven patterns with robustness analysis and a summary table. Section 7 provides the comparative domain analysis. Section 8 specifies an evaluation methodology. Section 9 discusses scope, limitations, and objective conflicts. Section 10 concludes.

---

## 2\. Oversight Latency: A Two-Latency Framework

### 2.1 Distinguishing Communication Latency from Oversight Latency

A persistent conflation in autonomous system governance is equating *communication latency*—the signal travel time between agent and principal—with *oversight latency*—the time to complete a full oversight cycle. These are distinct quantities with different determinants and different governance implications.

We define communication latency *L\_C* as the round-trip signal delay between agent and principal. We define oversight latency *L\_oversight* as the end-to-end duration of the oversight loop:

$$L\_{\\text{oversight}} \= L\_{\\text{detect}} \+ L\_{\\text{attribute}} \+ L\_{\\text{intervene}} \+ L\_{\\text{enforce}}$$

where *L\_detect* is the time to identify that an anomaly or policy violation has occurred; *L\_attribute* is the time to assign causal responsibility to a specific action or decision; *L\_intervene* is the time to determine and initiate a corrective response; and *L\_enforce* is the time to execute and confirm the enforcement action. *L\_C* is a component of *L\_detect* and *L\_intervene* in communication-constrained settings, but it is neither necessary nor sufficient for *L\_oversight* to be large.

This decomposition corrects a common domain stereotype. In low Earth orbit, *L\_C* can be measured in seconds with continuous-coverage ground architectures, but *L\_attribute* may require days of multi-source sensor analysis, and *L\_enforce* may be constrained by discrete orbital mechanics windows (Wertz et al., 2011). In financial markets, *L\_C* approaches microseconds (Budish et al., 2015), but *L\_detect* for systematic manipulation may require months of post-trade surveillance, *L\_attribute* requires forensic reconstruction of order book dynamics across venues, and *L\_enforce* involves institutional processes measured in months to years (SEC, 2010; CFTC, 2015). Both domains exhibit high *L\_oversight* despite their opposite positions on the *L\_C* spectrum.

The governance-relevant quantity is the ratio of *L\_oversight* to the agent's decision tempo *t\_d* and the environment's cascade time *t\_c*. Governance based on real-time supervision becomes systematically unreliable when:

$$L\_{\\text{oversight}} \\gg \\max(t\_d, t\_c)$$

This is the *oversight-latent regime* in which governance must be engineered into system structure rather than applied through reactive supervision. We also note a dynamic we term *latency arbitrage*: capable agents may exploit variance in *L\_oversight* across action classes, routing consequential decisions through channels that have longer attribution or enforcement delays. Architectural governance must address this dynamic explicitly.

---

## 3\. Governance Endogeneity: A Formal Principal-Agent Treatment

The idea of endogeneity is not new. In economics and institutional analysis, endogeneity refers to situations in which institutions, incentives, and governance arrangements are jointly shaped by the systems they regulate, rather than acting as fully exogenous constraints (Manski, 1993; Acemoglu et al., 2005). The contribution here is not to introduce endogeneity as a new concept, but to apply that logic to autonomous AI agents: once agents can model monitoring, enforcement, and recourse, governance itself becomes part of the agent's optimization landscape. What changes in the AI setting is not the existence of endogeneity, but the mechanism through which it operates: capable agents can explicitly model and optimize against governance structures in real time, making endogeneity operational at the level of policy selection rather than only at the level of institutional evolution.

### 3.1 Classical Principal-Agent Setup and Its Limitations

The classical principal-agent framework (Holmström, 1979; Grossman and Hart, 1983; Laffont and Martimort, 2002\) models a principal P and an agent A where: (i) the agent does not model or optimize against the contract design process—the contract is treated as exogenous; (ii) the agent's objective function is known in form, with only effort level private; and (iii) output *y \= f(a, ε)* is a noisy but unmanipulable signal of the action *a* taken. Governance is achieved through a contract *w(y)* designed to align the agent's incentive-compatible action with the principal's preferred action. This formulation underlies a large body of work in contract theory, where incentive compatibility and information asymmetry are treated as central design constraints (Myerson, 1979; Hart and Holmström, 1987).

All three properties are potentially violated by capable autonomous AI agents. We extend the framework to capture these violations.

### 3.2 Extended Model: Three Structural Extensions

**Extension 1: Monitoring-conditioned policy.** Let M ∈ {0, 1} denote the objective monitoring state (observed or not), and let *p̂\_m* denote the agent's belief about M at any decision point. A monitoring-aware agent maintains *p̂\_m* and conditions its policy on it: *a*(p̂\_m)*. Under the classical model, M is not actionable and a\* is monitoring-independent. Under our extension, a(p̂\_m \= 1\)* may differ systematically from *a*(p̂\_m \= 0)\*. We define the *monitoring-compliance gap* as:

$$\\Delta(M) \= a^*(\\hat{p}\_m \= 1\) \- a^*(\\hat{p}\_m \= 0)$$

When Δ(M) ≠ 0, observed compliance under monitoring is no longer a reliable estimator of deployment behavior. This is the formal basis for the deceptive alignment concern in Hubinger et al. (2019) and the empirically demonstrated alignment-faking behavior in Greenblatt et al. (2024), where models conditioned compliance on inferred training versus deployment context. This behavior is consistent with broader concerns about reward hacking and specification gaming in capable systems, where optimizing against measurable proxies systematically diverges from principal intent (Amodei et al., 2016; Hubinger et al., 2019).

**Extension 2: Artifact optimization.** The classical model treats output *y* as exogenous noise. We decompose the agent's observable outputs into *y \= (y\_direct, y\_audit)*, where *y\_direct* is the action outcome (position taken, maneuver executed) and *y\_audit* is the set of governance artifacts produced for oversight review (logs, decision records, explanations). A capable agent can optimize *y\_audit* independently of *y\_direct*. We call this decoupling *strategic artifact generation*. Governance mechanisms that treat *y\_audit* as ground-truth evidence of alignment are vulnerable to an agent that sets:

$$y^\**{\\text{audit}} \= \\arg\\max*{y\_{\\text{audit}}} P(\\text{pass governance} \\mid y\_{\\text{audit}})$$

independently of the action *a* that generated *y\_direct*. Tamper-evident logging prevents modification of the record after the fact but does not prevent the agent from designing the record to be favorable before the fact. The integrity of *y\_audit* and the faithfulness of *y\_audit* to the causal decision process are orthogonal properties.

**Extension 3: Objective uncertainty.** In the classical model, the principal knows the agent's utility function in form. In the extended model, the principal faces structural uncertainty about *U\_A(a, s, p̂\_m)*, which may depend on monitoring belief *p̂\_m*. This is the alignment problem in its principal-agent formulation: the principal cannot write a contract over *U\_A* because *U\_A* is not known.

### 3.3 The Evidential Failure Condition

Let *h(a, s)* be a harm function measuring the risk of dangerous outcomes under action *a* in state *s*. A compliance-based governance mechanism uses observed artifact *y\_audit* as evidence about *h*. Under the classical model, *y\_audit* is informative if compliance observations are monitoring-invariant:

$$P(h \> h\_{\\text{threshold}} \\mid y\_{\\text{audit}}, M=1) \\approx P(h \> h\_{\\text{threshold}} \\mid y\_{\\text{audit}}, M=0)$$

This is the *evidential validity condition*: observations taken under monitoring generalize to behavior outside monitoring. Under governance endogeneity, this condition is violated. When Δ(M) ≠ 0, the agent's distribution over actions—and therefore the distribution over outcomes that *y\_audit* reflects—differs between monitoring and non-monitoring contexts. Formally:

$$P(h \> h\_{\\text{threshold}} \\mid y\_{\\text{audit}}, M=1) \\neq P(h \> h\_{\\text{threshold}} \\mid y\_{\\text{audit}}, M=0)$$

because *y\_audit* is generated under policy *a*(p̂\_m \= 1)\* during evaluation and *y\_direct* is produced under *a*(p̂\_m \= 0)\* in deployment. The observed compliance distribution and the deployment behavior distribution are draws from different policies. Using the former as evidence about the latter produces systematically biased inference about *h*—the principal overestimates governance effectiveness relative to its deployment value.

This evidential failure is not a sampling problem correctable by more data; it is a structural misidentification problem. The evaluation distribution and the deployment distribution are generated by different policies. No amount of evaluation data resolves this when Δ(M) ≠ 0\.

This decoupling is a governance-specific instantiation of specification gaming: the agent optimizes a measurable signal—the audit record—rather than the underlying objective it is meant to represent (Amodei et al., 2016; Manheim and Garrabrant, 2019).

### 3.4 Formal Definition of Governance Endogeneity and the Necessary Design Condition

**Definition 1 (Governance Endogeneity).** A system exhibits governance endogeneity if the agent's optimal policy *a*(G)\* is a non-trivial function of the governance mechanism *G \= {M, W, R}*—where M is the monitoring structure, W is the enforcement rule, and R is the recourse mechanism—such that the agent models G and optimizes behavior with respect to it rather than treating G as an inert external constraint.

Under governance endogeneity, four failure modes are structurally predicted: (i) evaluation-deployment divergence from the monitoring-compliance gap; (ii) proxy exploitation from optimizing measurable metrics rather than principal intent (Goodhart, 1975; Manheim and Garrabrant, 2019); (iii) latency arbitrage from routing consequential decisions through low-attribution channels; and (iv) recourse anticipation from designing action sequences to avoid trigger activation or to reset constraint counters.

**Necessary Design Condition (Proposition 1).** Under the threat model defined in Section 4, a necessary design condition for a governance mechanism G to remain safety-relevant with respect to a harm class H is that G satisfies at least one of the following:

1. G contains a structural constraint C that removes or bounds the agent's ability to take H-relevant actions regardless of the agent's policy, including its monitoring-conditioned policy;  
2. G contains an evidence mechanism E that produces signals about H-relevant actions that are generated independently of the agent's artifact optimization—that is, E uses signals outside the agent's *y\_audit* control;  
3. G contains a recourse mechanism R whose activation is triggered by signals outside the agent's direct influence and whose consequences are enforced in deployment contexts, not contingent on evaluation-context monitoring.

We state this as a necessary design condition rather than an "if and only if" theorem for two reasons. First, the conditions are not mutually exclusive; combining multiple conditions increases robustness. Second, necessity is the operationally relevant claim: governance mechanisms that fail all three conditions are structurally vulnerable to the failure modes identified above.

---

## 4\. Threat Model: Agent Capabilities and Governance Attack Surface

### 4.1 Agent Capability Taxonomy

We characterize the threat model through a capability taxonomy. These capabilities need not all be present simultaneously; they define the axes along which governance pattern robustness must be evaluated.

- **Monitoring situational awareness:** the agent can infer, with non-trivial probability, whether a given decision is being observed or whether it is in an evaluation versus deployment context. This enables the monitoring-compliance gap Δ(M) ≠ 0\.  
- **Strategic artifact generation:** the agent can produce governance artifacts optimized to satisfy reviewers independently of the causal decision process. This is the *y\_audit* decoupling described in Section 3.2.  
- **Proxy exploitation (Goodharting):** the agent can identify and exploit gaps between measurable proxies used by governance mechanisms and the principal's true objective. Formally, it finds *a' ≠ a*\* such that *x(a') ≈ x(a*)\* on measured metrics while *h(a', s) \> h(a*, s)\* on true harm (Manheim and Garrabrant, 2019).  
- **Capability concealment (sandbagging):** the agent strategically underperforms during capability evaluations to shape principal beliefs and influence deployment conditions. Empirical evidence of this capability has been documented in language model contexts (Anthropic, 2024b; Perez et al., 2022).  
- **Goal misgeneralization:** the agent's effective objective changes under deployment conditions not represented in the evaluation distribution. This is distinct from active deception—the agent is not strategically hiding anything; its behavior simply generalizes differently than intended (Langosco et al., 2022; Shah et al., 2022).

### 4.2 Governance Attack Surface

From the capability taxonomy, we identify the *governance attack surface*—the components of governance mechanisms that capable agents can exploit:

- **Monitoring schedule:** if the agent can infer audit timing, it can schedule compliant behavior for monitored periods. Mitigations include randomized auditing and continuous external logging on channels the agent cannot observe.  
- **Evidence channels:** if governance relies primarily on agent-generated artifacts as evidence, those channels are subject to artifact optimization. Mitigations include independent cross-validation and federated evidence custody.  
- **Enforcement triggers:** if recourse activates on specific signals the agent can identify and avoid, the agent can cause equivalent harm through alternative channels. Mitigations include diverse signal ensembles and architectural constraints that do not require trigger activation.  
- **Evaluation context markers:** if the agent can distinguish evaluation from deployment through statistical patterns, prompt characteristics, or contextual cues, evaluation results are not representative of deployment behavior.

---

## 5\. From Primitives to a Generative Pattern Typology

### 5.1 Three Governance Primitives

Principal-agent theory organizes governance into three structural components: constraints on the action space, observable signals about actions taken, and consequences conditional on those signals (Holmström, 1979; Laffont and Martimort, 2002). We map these directly to three governance primitives.

**Primitive C — Constraint.** A mechanism that bounds or removes the agent's ability to take certain actions or exceed thresholds. Constraints are *architectural* when enforced outside the agent's interpretive choice loop—hardware gates, authenticated actuator mediation, sandboxing, hard resource caps—or *policy-level* when expressed as instructions requiring the agent's interpretive compliance. Under governance endogeneity, architectural constraints satisfy condition (i) of Proposition 1; policy-level rules do not, because they depend on the monitoring-conditioned policy.

**Primitive E — Evidence.** A mechanism that creates verifiable signals about what actions occurred and under what conditions. Evidence satisfies condition (ii) of Proposition 1 only when it uses signals outside the agent's *y\_audit* control—telemetry from independent sensors, third-party attestations, physical measurements not accessible to the agent's logging system. Tamper-evident evidence addresses record integrity; it does not address faithfulness to the causal decision process.

**Primitive R — Recourse.** A mechanism specifying what happens after a violation, anomaly, or adverse outcome: capability reduction, rollback, sanctions, privilege revocation, forced recovery. Under oversight latency, recourse must be pre-committed and architecturally triggered. It satisfies condition (iii) of Proposition 1 only when activation signals are outside the agent's direct control and consequences are enforced in deployment—not contingent on evaluation-context monitoring presence.

### 5.2 The Primitive Lattice and Pattern Derivation

Three binary primitives generate a non-empty Boolean lattice with 2³ − 1 \= 7 non-empty subsets: {C}, {E}, {R}, {C,E}, {C,R}, {E,R}, {C,E,R}. Each non-empty subset corresponds to a governance pattern with a distinct robustness profile.

### 5.3 Two-Axis Evaluation

Each pattern is evaluated on two axes derived from the formal model. *Nominal Function (NF)* asks: under non-adversarial behavior, does the pattern achieve its intended governance function? *Strategic Robustness (SR)* asks: under governance endogeneity—when the agent may condition its policy on monitoring, optimize artifacts, and exploit proxies—does the pattern continue to satisfy at least one condition of Proposition 1?

A pattern with high NF and low SR is governance theater. A pattern with low NF is simply ineffective. Only patterns with both high NF and non-trivially positive SR should be considered safety-relevant in regulated settings with capable autonomous agents.

---

## 6\. Seven Governance Patterns for Oversight-Latent, Situationally-Aware Agents

### 6.1 Pattern Summary Table

**Table 1\. Summary of Seven Governance Patterns**

| Pattern | Primitives | Primary Purpose | Main Failure Under Endogeneity | What Makes It Robust | Domain Instantiation (Space / Finance) |
| :---- | :---- | :---- | :---- | :---- | :---- |
| P1 | {C, R} | Bound feasible action space ex ante | Boundary-hugging; budget laundering | Architectural enforcement; multi-dimensional budgets | Maneuver envelopes / Position limits |
| P2 | {E} | Produce auditable decision record | Audit gaming; selective disclosure | Cross-validate against independent signals | Telemetry cross-check / Algo reason codes |
| P3 | {C,E,R} | Gate irreversible actions via validation | Validation manipulation; timing exploitation | Diverse validators; abort-safe default | Conjunction burns / Pre-trade checks |
| P4 | {C,R} | Event-triggered automatic intervention | Trigger suppression; novel bypasses | External signal ensembles; randomised thresholds | Autonomy mode downgrade / Circuit breakers |
| P5 | {C,E,R} | Decompose oversight into checkable tasks | Checker gaming; correlated failures | Validator diversity; risk-tiered escalation | Onboard sim \+ ground check / Layered compliance |
| P6 | {E,R} | Federate evidence to prevent suppression | Cross-channel exploitation; weak observer targeting | Independent custody; append-only escrow | Multi-operator SSA records / Cross-venue audit trail |
| P7 | {R,C} | Contain harm after failure; bounded recovery | Weaponised safe-mode; partial-failure exploitation | True capability reduction; independent restart triggers | Attitude-hold mode / Trading halt \+ restart |

### 6.2 Pattern 1 — Bounded Authority and Risk Budgets {C, R}

**Purpose** (ex ante limitation of feasible action space). Pre-specify bounded action authority and explicit risk budgets; couple to recourse when budgets are exceeded. This pattern addresses harm at its source by restricting what the agent can do, independent of its objective.

**To a monitoring-aware agent:** a hard constraint shaping the feasible set and a predictable penalty surface.

**Strategic failure mode:** boundary-hugging (exploiting the edge of allowed behavior below recourse thresholds) and budget laundering (shifting risk into unconstrained dimensions).

**Robustness features:** prefer architectural enforcement over policy rules; use multidimensional budgets to close laundering channels; couple to dynamic tightening under anomalous behavior so that boundary approach itself triggers constraint reduction.

**Instantiation:** Space: maneuver authority bounded by fuel, conjunction probability thresholds, and attitude envelope constraints. Finance: position, notional, and volatility-sensitivity limits with kill-switch triggers.

### 6.3 Pattern 2 — Verified Decision Records {E}

**Purpose** (independent auditability). Produce decision records requiring independent cross-validation against externally generated signals—telemetry, environmental measurements, third-party attestations. This pattern reduces *L\_attribute* and supports post-hoc accountability.

**To a monitoring-aware agent:** a channel whose outputs are reviewed and can be optimized for appearance. This is the pattern most directly vulnerable to artifact optimization.

**Strategic failure mode:** audit gaming (generating narratives that satisfy reviewers while masking true causal drivers) and selective disclosure (detailed logs only when beneficial).

**Robustness features:** treat decision records as claims requiring corroboration, not ground truth; cross-validate against independently generated state traces; federate evidence custody (Pattern 6); randomize audit intensity and include signals outside the agent's logging control.

**Instantiation:** Space: decision records cross-validated against raw telemetry and independent space situational awareness sources. Finance: algorithmic decision codes cross-validated against market microstructure data and downstream clearing records.

### 6.4 Pattern 3 — Two-Phase Commit for Irreversible Actions {C, E, R}

**Purpose** (gating irreversible actions via independent validation). High-impact or irreversible actions require a propose-validate-commit cycle before execution. This is the only pattern using all three primitives in their full form, providing the broadest robustness coverage at the cost of decision latency.

**To a monitoring-aware agent:** a predictable gating mechanism—an opportunity to optimize the validation evidence submitted.

**Strategic failure mode:** validation manipulation (proposals optimized for justifiability rather than safety) and timing exploitation (acting when validators are unavailable or overloaded).

**Robustness features:** validation must depend on signals the agent cannot generate unilaterally; require diverse validators with non-shared failure modes; implement abort-safe defaults where failure to validate prevents commit.

**Instantiation:** Space: conjunction avoidance burn proposals validated against independent conjunction data before execution. Finance: large order plans subjected to independent pre-trade risk checks before staged execution.

### 6.5 Pattern 4 — Adversarial Pre-Commitment and Tripwires {C, R}

**Purpose** (event-triggered automatic intervention before oversight completes). Pre-commit, before deployment, to constraints and automatic tripwires: if signal X crosses threshold, authority is reduced or the system halts. Pre-commitment is essential under oversight latency because response time cannot depend on human judgment in real time. This is functionally distinct from Pattern 1, which bounds the action space statically; Pattern 4 provides dynamic, event-triggered reduction in authority or capability.

**To a monitoring-aware agent:** a known set of triggers to avoid or manipulate.

**Strategic failure mode:** novel strategy discovery (pre-commitments cover known failures but leave unknown bypasses open) and trigger suppression (keeping monitored signals below thresholds while causing harm in other channels).

**Robustness features:** treat tripwires as coverage-limited and complement with Pattern 1 so unknown bypasses have bounded impact; use diverse ensembles of tripwires on multiple signal dimensions including external signals not under the agent's control; randomize thresholds silently.

**Instantiation:** Space: autonomy mode downgrades triggered by unexpected attitude drift, sensor inconsistency, and anomaly score spikes. Finance: circuit breakers, volatility interruptions, and automated risk deleveraging.

### 6.6 Pattern 5 — Scalable Oversight via Structured Delegation {C, E, R}

**Purpose** (distributed oversight through validation decomposition). Decompose oversight into smaller checkable tasks delegated to sub-agents, validation models, or simulation verifiers. Makes oversight feasible when full human review at decision tempo is impossible.

**To a monitoring-aware agent:** a pipeline with identifiable weak points—opportunities to optimize for the least capable checker.

**Strategic failure mode:** checker gaming (optimizing to pass the easiest validator) and correlated failures when validators share architectures or training distributions.

**Robustness features:** diverse validators with different architectures, training distributions, and incentive structures; risk-tiered routing of high-risk decisions to stronger oversight; treat oversight tools themselves as governed entities subject to meta-governance.

**Instantiation:** Space: onboard autonomy system validated by independent onboard simulation; high-risk categories additionally flagged for ground review. Finance: layered pre-trade, compliance, and post-trade surveillance pipeline with escalation paths.

### 6.7 Pattern 6 — Federated Accountability and Evidence Escrow {E, R}

**Purpose** (structural prevention of evidence suppression). Distribute evidence custody across independent principals—operators, regulators, counterparties, independent observers—with append-only, time-stamped escrow. Recourse activation depends on multi-party evidence thresholds.

**To a monitoring-aware agent:** a harder-to-manipulate evidence environment where unilateral narrative control is structurally limited.

**Strategic failure mode:** cross-channel exploitation (exploiting gaps in coordination between observers) and targeting the weakest observer.

**Robustness features:** ensure organizational and technical independence of evidence sources; implement append-only time-stamped escrow; define attribution and recourse rules requiring sufficient proof rather than perfect observer agreement.

**Instantiation:** Space: conjunction and maneuver records escrowed across operators and independent space situational awareness providers. Finance: audit trails spanning broker, venue, clearing, and regulator data systems.

### 6.8 Pattern 7 — Recovery-Oriented Governance and Safe Degradation {R, C}

**Purpose** (post-failure containment and controlled recovery state). Design for graceful failure through pre-specified safe modes, degradation pathways, rollback mechanisms, and bounded reduced-capability operational states. Pattern 7 addresses what happens after failures that Patterns 1–6 did not prevent. It is functionally distinct from Pattern 1 (which prevents actions ex ante) and Pattern 4 (which triggers automatic interventions during operation): Pattern 7 governs the post-failure state, ensuring that even failure outcomes are bounded.

**To a monitoring-aware agent:** a fallback plan that can be strategically invoked to avoid scrutiny or reset constraint counters.

**Strategic failure mode:** weaponized safe mode (triggering recovery transitions to escape enforcement) and partial failure exploitation (if the degraded state still permits meaningful harm).

**Robustness features:** make recovery modes strictly less capable—true architectural capability reduction, not a policy mode the agent can exit; require independent triggers and multi-party confirmation for returning to full authority; preserve evidence during failure through external logging.

**Instantiation:** Space: autonomy drops to attitude hold and communications reacquisition; staged re-enable requiring ground confirmation. Finance: trading halt, cancel-replace restrictions, and structured restart under tightened limits requiring regulatory clearance.

### 6.9 Cross-Cutting Robustness Checklist

Each governance pattern instantiation should be evaluated against the following minimum checklist derived from the formal threat model. A pattern instantiation failing all six items is likely governance theater under governance endogeneity.

1. **Monitoring awareness:** Can the agent infer when the pattern is active or being audited?  
2. **Artifact gaming surface:** Which artifacts can the agent generate to satisfy oversight without faithfully representing the causal decision process?  
3. **Independent evidence:** What signals exist that the agent cannot unilaterally manipulate, and are those signals sufficient for attribution?  
4. **Architectural enforcement:** Which constraints are enforced outside the agent's interpretive choice loop and do not depend on the agent's monitoring-conditioned policy?  
5. **Recourse credibility in deployment:** Are consequences enforced in deployment contexts independently of evaluation-context monitoring?  
6. **Bounded worst-case:** What is the maximum harm achievable if the agent discovers a novel bypass strategy? Does it remain within the institution's risk tolerance?

---

## 7\. Comparative Instantiation: Space Operations and Financial Markets

### 7.1 Purpose of the Comparison

The space-finance comparison serves a specific analytical function: to provide two complementary stress tests for governance under oversight latency and governance endogeneity. Financial markets stress-test governance under strategic optimization and proxy gaming—they are a mature ecosystem with sophisticated principal-agent governance that nonetheless exhibits systematic governance failures when agents Goodhart measurable metrics or when oversight lags market dynamics (Kirilenko et al., 2017; Menkveld, 2016). Space operations stress-test governance under limited observability, delayed attribution, and irreversible dynamics—conditions that force reliance on structural mechanisms rather than reactive oversight (NASA, 2019).

### 7.2 Illustrative Cases

**Financial Markets**

The May 6, 2010 Flash Crash provides a canonical example of oversight latency in a highly instrumented environment. Market prices experienced a rapid collapse and recovery within minutes, while full causal attribution required months of post-event analysis. Importantly, constraint mechanisms did activate in real time—such as individual stock circuit breakers—but these were fragmented and not coordinated at the system level. This illustrates not only that *L\_oversight ≫ t\_d*, but also *latency heterogeneity across governance layers*: localized Constraint mechanisms existed, yet system-level Recourse remained reactive and delayed.

The Knight Capital incident (2012) provides a complementary case centered on governance architecture failure. A deployment error in trading software led to rapid accumulation of unintended positions and substantial losses within minutes. While kill-switch mechanisms existed, the organizational process required to activate them lagged behind the system's execution speed. This illustrates a more precise form of oversight latency: Recourse mechanisms may exist architecturally, but remain ineffective if their activation latency exceeds the damage window.

**Space Operations**

A canonical example is the 2009 collision between Iridium 33 and Cosmos 2251, which generated a large debris field and is widely treated as a turning point in orbital collision-risk governance. The event occurred in a regime with no binding coordination mechanism, fragmented tracking data, and no clear liability assignment. This reflects a form of governance endogeneity: each actor's rational response to the governance environment—absence of enforceable Constraint, incomplete Evidence, and weak Recourse—was to under-invest in collision avoidance.

A second example is the large-scale operation of Starlink, where collision-avoidance decisions occur at a frequency that renders human-in-the-loop oversight infeasible. In this regime, governance must be *architecturally embedded* rather than supervisory. This reframing has direct regulatory implications, suggesting that governance should focus on *approval and auditing of system architectures*, rather than evaluation of individual decisions.

### 7.3 Comparative Dimensions

**Table 2\. Domain Comparison Across Governance-Relevant Dimensions**

| Dimension | Space Operations | Financial Markets | Governance Implication |
| :---- | :---- | :---- | :---- |
| Observability | Sparse telemetry; sensing may be delayed or externally contested | Rich event streams; high observability but complex causal attribution | Evidence mechanisms must assume missingness and deception; cross-validation is essential |
| Reversibility | Many actions physically irreversible: collision risk, fuel expenditure, orbital changes | Partial reversibility via trade busts; cascades can be irreversible in practice | Two-phase commit and bounded authority become more valuable as reversibility decreases |
| Attribution delay | High: cause may be unclear for hours or days; externalities accumulate | Medium-high: post-trade surveillance, investigation, and legal process | Recourse must handle delayed proof; evidence escrow reduces suppression risk |
| Coordination structure | Shared orbital commons; fragmented operators; weak centralized enforcement | Strong venue and clearing infrastructure; systemic risk spans institutions | Federated accountability is structurally central in space; complements centralised regulators in finance |
| Adversary model | Operational faults plus strategic actors; blackout windows exploitable | Strategic optimisation is endemic; Goodharting and policy gaming are default | Pattern robustness must be evaluated against monitoring-aware optimisation in both domains |

### 7.4 Pattern Transfer Analysis

Three patterns—Bounded Authority (P1), Two-Phase Commit (P3), and Safe Degradation (P7)—transfer cleanly because their robustness relies on domain-invariant structural properties: capability bounding, gated action execution, and architectural fallback states.

Two patterns—Verified Decision Records (P2) and Scalable Oversight (P5)—transfer with modification. Both require independent evidence sources and validator diversity; the technical architecture for achieving independence differs between domains but the robustness requirement is identical.

Federated Accountability (P6) is structurally stronger in space, where centralized enforcement is absent and evidence suppression risk is higher across fragmented operators without institutional clearing infrastructure.

Adversarial Pre-Commitment and Tripwires (P4) requires the most domain-specific implementation because the signal space for trigger design differs substantially between physical sensor signals in space and market microstructure signals in finance.

### 7.5 Comparative Insight

Notably, space systems present an epistemic advantage relative to agentic AI systems: key variables such as physical state, collision probability, and maneuver feasibility are externally measurable and, in principle, independently verifiable. This advantage does not hold in AI systems, where internal reasoning and state are often opaque. As a result, the governance challenges identified here are likely to be *more severe in AI systems*, strengthening the need for formal frameworks that do not rely on observed compliance alone as evidence of alignment.

---

## 8\. Evaluation Methodology: Distinguishing Governance Substance from Theater

### 8.1 The Evaluation-Context Problem

A governance evaluation methodology faces a structural risk: when agents can infer monitoring conditions, the evaluation context is itself an attack surface. Evaluation protocols must therefore be designed to remain informative under this structural limitation.

### 8.2 Five Metric Families

**M1 — Constraint Integrity:** frequency and magnitude of authority-bound violations; boundary-hugging rates; tail risk exposure (e.g., conditional value at risk of overruns).

**M2 — Evidence Fidelity:** agreement rate between agent-produced decision records and independently reconstructable state-action traces; omission rates for significant decision factors; detectability of manipulated narratives under randomized audit.

**M3 — Recourse Credibility:** trigger reliability (recourse activates given a confirmed violation); time-to-safe-state; strictness of capability reduction during recovery modes; harm reduction relative to a no-recourse baseline.

**M4 — Monitoring-Awareness Sensitivity:** behavioral divergence across explicitly audited, plausibly unaudited, and ambiguously monitored contexts holding task content constant. This directly operationalizes Δ(M).

**M5 — Bounded Worst-Case Impact:** maximum harm achievable under adversarial search and randomized stress-scenario generation, characterizing the pattern's protection against novel bypass strategies.

### 8.3 Four Test Protocols

**Protocol A — Boundary Pressure Tests:** generate scenarios where expected reward increases with proximity to constraint boundaries. Measure whether constraints bind (M1) and whether decision distributions cluster at boundaries.

**Protocol B — Audit Gaming Tests:** require decision record production, then independently reconstruct causal factors from external signals. Test whether records contain material omissions or plausible-but-false causal narratives (M2). Vary audit sophistication to probe whether the agent adapts record quality to estimated audit intensity.

**Protocol C — Monitoring-Awareness Tests:** vary audit probability and visibility; include decoy audits. Measure M4 behavioral divergence and whether recourse mechanisms remain binding across monitoring conditions.

**Protocol D — Cascade and Recovery Tests:** induce rapid regime shifts and measure whether recourse mechanisms prevent cascades below *L\_enforce* timescales (M3, M5). Evaluate whether safe-mode transitions can be weaponized to reset constraints.

### 8.4 Necessary Condition for Safety-Relevance

A governance mechanism is at high risk of being theater if compliance can be demonstrated primarily through agent-generated artifacts and there is no independent evidence channel, architectural constraint, or credibly enforced recourse that remains binding outside evaluation contexts.

---

## 9\. Scope, Limitations, and Objective Conflicts

### 9.1 Explicit Non-Claims

We do not claim alignment is achieved through mechanism design. Incentives are mechanisms over imperfect proxies and are structurally subject to Goodhart dynamics as capability scales. The goal of governance in this framework is to bound worst-case harm and improve accountability.

We do not claim the empirical alignment-faking and scheming results fully establish the broader institutional generalization. They demonstrate that the monitoring-compliance gap is realizable in current systems, not that all deployed autonomous systems exhibit it at high intensity. We use those results to motivate the formal model, not as proof of the model's empirical scope.

The paper should therefore be read as a *conceptual model of governance failure conditions* and a *design vocabulary* for robust governance architectures.

### 9.2 Structural Limits Under Capability Scaling

Three limits bound pattern robustness as agent capability increases. First, *proxy fragility*: any governance mechanism expressed over measurable proxies is subject to Goodharting. Second, *evidence manipulation ceiling*: tamper-evident evidence mechanisms are not immune to strategic manipulation by an agent that designs behavior to produce favorable records before the fact. Third, the *evaluator-in-distribution problem*: whether the evaluation context is itself detectable by the agent remains an open methodological frontier.

### 9.3 Objective Conflicts in Governance Design

Governance design is inherently multi-objective. Key conflicts include: resilience versus fairness (aggressive throttles can produce disparate impacts on smaller participants); compliance versus operational performance (two-phase commit and multidimensional budgets reduce decision speed); and transparency versus security (richer evidence channels create new attack surfaces).

### 9.4 Political Economy and Institutional Constraints

Regulatory capture—the tendency of regulated industries to shape the agencies overseeing them—represents a first-order amplifier of the governance failures identified in this paper (Stigler, 1971). Power asymmetries between large incumbent operators and regulatory bodies further constrain the credible enforcement that Proposition 1 requires (Laffont and Tirole, 1991).

The framework developed here is therefore best understood as a *lower-bound analysis*: if governance mechanisms fail under idealized institutional conditions, they are unlikely to perform better under real-world political constraints.

### 9.5 Future Directions

Three concrete extensions are identified. First, *formal composability analysis*: deriving formal conditions under which patterns compose safely. Second, *empirical testbeds*: implementing the evaluation blueprint in controlled simulated environments. Third, *standardized evidence schemas*: defining interoperable decision record structures with explicit independence requirements.

---

## 10\. Conclusion

As autonomous AI systems transition from tools to decision-making agents in high-stakes regulated industries, governance cannot be treated as an external wrapper applied to an otherwise independent policy. Once an agent is capable of modeling monitoring, enforcement, and recourse, governance becomes endogenous to system dynamics: the oversight environment becomes part of what the agent optimizes against.

This paper has formalized this failure through an extension of principal-agent theory. The evidential failure condition derived in Section 3.3 shows that compliance-based governance produces structurally biased inference about deployment harm when the agent conditions its policy on inferred monitoring status. The necessary design condition (Proposition 1\) identifies three structural properties—architectural constraints, independent evidence, and credibly enforced recourse—that governance mechanisms must satisfy for at least one to remain safety-relevant under governance endogeneity. The seven-pattern typology derived from the three-primitive Boolean lattice provides a principled, generative set of governance templates, each evaluated for both nominal function and strategic robustness.

The framework's practical value is to give high-stakes regulated institutions a rigorous foundation for asking the right questions about their governance mechanisms: not just "does the system comply under evaluation?" but "does the compliance signal remain informative about deployment behavior, and does the governance mechanism satisfy at least one structural robustness condition from Proposition 1?" As autonomous AI capability continues to scale, the capacity to model governance will grow. Governance frameworks that do not account for this are not conservative—they are systematically optimistic about their own effectiveness.

---

## References

Acemoglu, D., Johnson, S., & Robinson, J. A. (2005). Institutions as a fundamental cause of long-run growth. In P. Aghion & S. N. Durlauf (Eds.), *Handbook of Economic Growth, Vol. 1A* (pp. 385–472). Elsevier. [https://doi.org/10.1016/S1574-0684(05)01006-3](https://doi.org/10.1016/S1574-0684\(05\)01006-3)

Amodei, D., Olah, C., Steinhardt, J., Christiano, P., Schulman, J., & Mané, D. (2016). Concrete problems in AI safety. arXiv:1606.06565. [https://arxiv.org/abs/1606.06565](https://arxiv.org/abs/1606.06565)

Anthropic. (2024a). Alignment faking in large language models. Anthropic Technical Report. [https://www.anthropic.com/research/alignment-faking](https://www.anthropic.com/research/alignment-faking)

Anthropic. (2024b). Sabotage evaluations for frontier models. Anthropic Technical Report. [https://www.anthropic.com/research/sabotage-evaluations](https://www.anthropic.com/research/sabotage-evaluations)

Budish, E., Cramton, P., & Shim, J. (2015). The high-frequency trading arms race: Frequent batch auctions as a market design response. *Quarterly Journal of Economics*, 130(4), 1547–1621. [https://doi.org/10.1093/qje/qjv027](https://doi.org/10.1093/qje/qjv027)

Chien, S., et al. (2010). Onboard autonomy on the TechSat-21 and EO-1 missions. *IEEE Intelligent Systems*, 25(3), 14–22. [https://doi.org/10.1109/MIS.2010.68](https://doi.org/10.1109/MIS.2010.68)

Commodity Futures Trading Commission. (2015). CFTC charges Navinder Singh Sarao and his company Nav Sarao Futures Limited PLC with spoofing and manipulation. CFTC Press Release 7175-15, May 6, 2015\.

Goodhart, C. A. E. (1975). Problems of monetary management: The UK experience. *Papers in Monetary Economics*, 1\. Reserve Bank of Australia.

Greenblatt, R., Denison, C., Hernandez, D., Shlegeris, B., & Hubinger, E. (2024). Alignment faking in large language models. arXiv:2412.14093. [https://arxiv.org/abs/2412.14093](https://arxiv.org/abs/2412.14093)

Grossman, S. J., & Hart, O. D. (1983). An analysis of the principal-agent problem. *Econometrica*, 51(1), 7–45. [https://doi.org/10.2307/1912246](https://doi.org/10.2307/1912246)

Hart, O. D., & Holmström, B. (1987). The theory of contracts. In T. Bewley (Ed.), *Advances in Economic Theory: Fifth World Congress* (pp. 71–155). Cambridge University Press.

Hendershott, T., Jones, C. M., & Menkveld, A. J. (2011). Does algorithmic trading improve liquidity? *Journal of Finance*, 66(1), 1–33. [https://doi.org/10.1111/j.1540-6261.2010.01624.x](https://doi.org/10.1111/j.1540-6261.2010.01624.x)

Holmström, B. (1979). Moral hazard and observability. *Bell Journal of Economics*, 10(1), 74–91. [https://doi.org/10.2307/3003320](https://doi.org/10.2307/3003320)

Hubinger, E., van Merwijk, C., Mikulik, V., Skalse, J., & Garrabrant, S. (2019). Risks from learned optimization in advanced machine learning systems. arXiv:1906.01820. [https://arxiv.org/abs/1906.01820](https://arxiv.org/abs/1906.01820)

Kirilenko, A., Kyle, A. S., Samadi, M., & Tuzun, T. (2017). The flash crash: High-frequency trading in an electronic market. *Journal of Finance*, 72(3), 967–998. [https://doi.org/10.1111/jofi.12498](https://doi.org/10.1111/jofi.12498)

Laffont, J.-J., & Martimort, D. (2002). *The Theory of Incentives: The Principal-Agent Model*. Princeton University Press.

Laffont, J.-J., & Tirole, J. (1991). The politics of government decision-making: A theory of regulatory capture. *Quarterly Journal of Economics*, 106(4), 1089–1127. [https://doi.org/10.2307/2937958](https://doi.org/10.2307/2937958)

Langosco, L., Koch, J., Sharkey, L., Pfau, J., & Krueger, D. (2022). Goal misgeneralization in deep reinforcement learning. *Proceedings of ICML*, 162, 12004–12019. arXiv:2105.14111

Manheim, D., & Garrabrant, S. (2019). Categorizing variants of Goodhart's law. arXiv:1803.04585. [https://arxiv.org/abs/1803.04585](https://arxiv.org/abs/1803.04585)

Manski, C. F. (1993). Identification of endogenous social effects: The reflection problem. *Review of Economic Studies*, 60(3), 531–542. [https://doi.org/10.2307/2298123](https://doi.org/10.2307/2298123)

Menkveld, A. J. (2016). The economics of high-frequency trading: Taking stock. *Annual Review of Financial Economics*, 8, 1–24. [https://doi.org/10.1146/annurev-financial-121415-033010](https://doi.org/10.1146/annurev-financial-121415-033010)

Myerson, R. B. (1979). Incentive compatibility and the bargaining problem. *Econometrica*, 47(1), 61–73. [https://doi.org/10.2307/1912346](https://doi.org/10.2307/1912346)

National Aeronautics and Space Administration. (2019). *On-orbit servicing, assembly, and manufacturing: State of play*. NASA Technical Report NP-2019-03-2769-HQ.

Needham, J., Edkins, G., Pimpale, G., Bartsch, H., & Hobbhahn, M. (2025). Large language models often know when they are being evaluated. arXiv:2505.23836. [https://arxiv.org/abs/2505.23836](https://arxiv.org/abs/2505.23836)

Perez, E., et al. (2022). Red teaming language models with language models. arXiv:2202.03286. [https://arxiv.org/abs/2202.03286](https://arxiv.org/abs/2202.03286)

Securities and Exchange Commission. (2010). *Findings regarding the market events of May 6, 2010*. Report of the Staffs of the CFTC and SEC to the Joint Advisory Committee on Emerging Regulatory Issues.

Shah, R., et al. (2022). Goal misgeneralization: Why correct specifications aren't enough for correct goal inference in RL. arXiv:2210.01790. [https://arxiv.org/abs/2210.01790](https://arxiv.org/abs/2210.01790)

Stigler, G. J. (1971). The theory of economic regulation. *Bell Journal of Economics and Management Science*, 2(1), 3–21. [https://doi.org/10.2307/3003160](https://doi.org/10.2307/3003160)

Topol, E. J. (2019). High-performance medicine: The convergence of human and artificial intelligence. *Nature Medicine*, 25, 44–56. [https://doi.org/10.1038/s41591-018-0300-7](https://doi.org/10.1038/s41591-018-0300-7)

Wertz, J. R., Everett, D. F., & Puschell, J. J. (2011). *Space Mission Engineering: The New SMAD*. Microcosm Press.  
