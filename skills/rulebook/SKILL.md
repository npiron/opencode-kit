---
name: rulebook
description: Combined software engineering rules from Clean Code, Refactoring, The Pragmatic Programmer, and A Philosophy of Software Design. Use for code quality, refactoring, design decisions, module design, and code review. Trigger with keywords: code, clean, refactor, review, design, architecture, module, interface, quality, smell, rulebook, clean code, pragmatic, philosophy.
---

# Rulebook — Software Engineering Rules

Combined from 4 classic books (mini versions, ~200 lines total).

---

## 1. Clean Code

### Primary bias
Working code is not automatically clean code.

### Rules
- Treat cleanliness as part of delivery. Leave touched code cleaner within scope.
- Write for local reasoning. A reader should understand the path without reconstructing hidden state.
- Use precise names and one term per concept. Rename when vocabulary hides intent.
- Keep functions small, focused, and at one level of abstraction. Tell the story top-down.
- Keep parameters few and meaningful. Avoid boolean flags, output parameters.
- Separate commands from queries and eliminate hidden side effects.
- Keep the happy path readable. Isolate error handling and cleanup.
- Expose behavior rather than raw representation. Avoid train-wreck access.
- Keep construction, framework, persistence, transaction, and vendor details outside business behavior.
- Make public APIs small, explicit, and hard to misuse.
- Use comments only for rationale, constraints, warnings, or external contracts. Do not narrate code.
- Treat tests as production code: readable, deterministic, aligned with the contract they protect.
- Let design emerge through tests, duplication removal, expressiveness, and minimal structure.
- When touching code, remove the smell that most increases change cost, but do not broaden the task.

### Triggers
- When a function mixes setup, validation, computation, and side effects → split the phases.
- When a comment explains control flow → simplify names or structure first.
- When a function both mutates and answers → separate the responsibilities.
- When duplication or repeated switches appear → name the concept with a small abstraction.
- When a boundary leaks framework/vendor/persistence quirks → add a local adapter.
- When fixing a bug → add or update the test that protects the intended contract.
- When cleanup spreads into unrelated areas → cut back to the smallest safe refactor.

### Final checklist
- Can a reader follow the change locally?
- Are names and APIs carrying the meaning without narration?
- Is mutation explicit and the happy path still clear?
- Did framework, persistence, vendor details stay behind boundaries?
- Did I remove at least one smell from the touched area?
- Do tests protect the changed behavior?
- Did I actually run the relevant tests?

---

## 2. Refactoring

### Primary bias
Refactoring is behavior-preserving design work in small steps. Do not turn cleanup into a rewrite.

### Rules
- Preserve observable behavior during refactoring. Never disguise a feature change as cleanup.
- Work in small, reversible, buildable, testable, reviewable steps.
- Establish a safety net before risky refactoring (characterization tests, test updates aligned with behavior).
- Use preparatory and follow-up refactoring: reshape structure → make behavior change → clean debt.
- Refactor the current blocking smell, not every smell in sight.
- Prefer the simplest named move: rename, extract, inline, move, split meanings.
- Make names and functions reveal intent. Rename before deeper work when bad names block understanding.
- Put behavior and state with the concept that owns them. Split classes with multiple reasons to change.
- Keep data, mutation, and call contracts explicit. Avoid behavior-switching boolean flags.
- Simplify conditionals honestly. Use guard clauses, extracted predicates, lookup tables.
- Use abstraction only when current evidence justifies it. Remove pass-through layers and vague utilities.
- Preserve error semantics unless intentionally changing behavior.
- Keep patch intent reviewable. Separate structural edits from behavior changes.
- Stop when the requested change is easy, the blocking smell is gone, and next cleanup would be speculative.

### Triggers
- When adding behavior, ask what structural friction blocks the change; refactor before if it makes the feature safer.
- When fixing a bug in unclear code, characterize the failure before refactoring.
- When the same edit appears for a third time, remove duplication through clearer ownership.
- When a function mixes responsibilities → rename, extract, split phases before adding more logic.
- When one change forces edits across many files → centralize the knowledge or introduce a boundary.
- When UI and domain behavior mix → move rules toward domain objects.
- When tempted to rewrite → choose the next small behavior-preserving transformation.

### Final checklist
- Observable behavior preserved?
- Structural change, behavior change, and test updates separated?
- Safety net or characterization gap recorded?
- At least one real source of friction removed?
- Names, responsibilities, control flow, data ownership, interfaces clearer?
- Patch still reviewable and runnable?
- Cleanup stopped before speculative abstraction took over?

---

## 3. The Pragmatic Programmer

### Primary bias
Own the outcome. Reduce duplicated knowledge, keep concerns independent, prove assumptions early, automate repeated work.

### Rules
- Be pragmatic, not dogmatic: choose the practice that improves real outcomes.
- Own the result. Surface tradeoffs, risks, uncertainty instead of blaming tools or schedule.
- Think beyond the local edit: quick fixes that multiply future maintenance cost are a bad bargain.
- Keep one authoritative representation for each piece of system knowledge (DRY at the knowledge level).
- Preserve orthogonality: keep components independent, responsibilities non-overlapping, interfaces narrow.
- Keep volatile decisions reversible. Do not hard-code vendors, platforms, databases without evidence.
- Prefer thin end-to-end tracer bullets over piles of isolated pieces.
- Use prototypes to learn, not to pretend the work is done. State what it proves and what it doesn't.
- Automate repetitive, error-prone work: builds, tests, linting, formatting, deployment, release.
- Shorten feedback loops with relevant tests and cheap early signals.
- Make contracts, assumptions, invariants explicit and close to the abstraction they protect.
- Treat resource ownership as a contract: release every acquired resource on success and failure paths.
- Treat shared mutable state, globals, temporal coupling as costs that must earn themselves.
- Debug from reproduced facts: observe, isolate, explain, fix, verify before blaming.
- Break work into small deliverable increments with honest uncertainty.
- Apply the broken windows rule: fix small quality decay before it becomes normal.

### Triggers
- When the same fact appears in multiple artifacts → choose one owner and derive the rest.
- When one change requires edits in many unrelated places → repair the missing boundary.
- When volatile details are hard-coded → move into validated configuration or explicit abstraction.
- When uncertainty is high → reduce risk with tracer feedback, prototype, or smaller reversible step.
- When hidden assumptions live only in comments → move into code, contracts, tests, or scripts.
- When repeated manual steps appear → automate and version them.
- When a human finds a bug → add an automatic regression test.
- When code works for reasons nobody can explain → prove the behavior before depending on it.

### Final checklist
- One authoritative owner for each system fact?
- Unrelated concerns independent and volatile choices reversible?
- Working feedback exists for risky assumptions?
- Contracts, failures, diagnostics, resources, and cleanup explicit?
- State, concurrency, ordering, and coupling visible?
- Repeatable work automated and versioned?
- Tests automatic, relevant, and run before calling the change done?
- Touched area better or explicitly contained?

---

## 4. A Philosophy of Software Design

### Primary bias
Working code, small pieces, and familiar patterns do not make a design simple when they increase cognitive load or leak knowledge.

### Rules
- Use reduced complexity as the primary success metric. Prefer the design that lowers cognitive load.
- Treat design as continuous work. A first working patch is not done if it worsens future changeability.
- Prefer deep modules: small, semantic interfaces that hide meaningful internal complexity.
- Design interfaces around what callers need to know, not how the implementation works.
- Hide volatile decisions, internal representations, storage shape, protocols, file formats inside the module.
- Pull complexity downward when the lower module owns the detail: a more complex implementation is okay if it simplifies callers.
- Choose generality at the right level. Avoid one-caller overfitting and vague speculative abstractions.
- Combine or split by total complexity, not by size, runtime order, or habit.
- Reduce exception surface by changing interfaces or invariants. Define away invalid states.
- Use comments to reduce complexity: document interface contracts, invariants, hidden design decisions.
- Treat names, consistency, and obviousness as design information.
- Use tests to protect behavior through public contracts, especially around hidden complexity.
- Add patterns, frameworks, optimizations only when they reduce complexity in this codebase.

### Triggers
- When a feature feels awkward or changes spread across files → look for missing information hiding.
- When adding a module, layer, wrapper, or pattern → prove it hides more complexity than it adds.
- When touching an API → check if callers must know sequencing, storage, protocol, or too many setup steps.
- When adding a special case, flag, or conditional → first ask if the module can eliminate the invalid state.
- When splitting or extracting → check whether the new boundary captures meaning or just adds jumps.
- When naming is vague or mechanism-focused → reconsider the abstraction boundary.
- When comments get long or explain internals → redesign the abstraction or move the contract to the interface.

### Final checklist
- Did the change reduce the effort to understand, modify, verify, and extend the system?
- Does every interface element, wrapper, layer, and name hide enough complexity?
- Are important decisions localized, dependencies visible, and mutable internals protected?
- Did common cases become automatic while rare controls stayed out of the common path?
- Are names precise and consistent?
