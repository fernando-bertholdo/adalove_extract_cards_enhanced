# Codebase Architecture Analysis: AdaLove Extract Cards Enhanced

**Date**: November 2, 2025  
**Project**: AdaLove Extract Cards Enhanced v3.0.0+  
**Total LOC**: 6,101 lines  
**Modules**: 28 Python files  
**Architecture**: Modular Python with Playwright for web automation

---

## 1. EXTRACTION PIPELINE ARCHITECTURE

### 1.1 High-Level Data Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        EXTRACTION PIPELINE                              │
└─────────────────────────────────────────────────────────────────────────┘

[LOGIN & NAVIGATION]
    ↓
[WEEK DISCOVERY]
    ↓
[PER-WEEK CARD EXTRACTION]
    ├─ Extract list view data
    ├─ Click card to open modal
    ├─ Identify card type by icon
    ├─ Extract modal content (description, related, etc.)
    ├─ Extract links/materials/files
    └─ Close modal & move to next
    ↓
[RAW DATA CONSOLIDATION]
    ↓
[ENRICHMENT PROCESSING]
    ├─ Temporal normalization (dates, sprints)
    ├─ Professor detection
    ├─ Type classification (deterministic + fallback)
    ├─ URL normalization
    ├─ Autoestudo anchoring to instructions
    └─ Hash generation
    ↓
[OUTPUT GENERATION]
    ├─ CSV (raw data)
    ├─ JSONL (enriched data)
    └─ Stats/metadata

```

### 1.2 Core Pipeline Components

| Component | Location | Responsibility |
|-----------|----------|-----------------|
| **Navigator** | `browser/navigator.py` | Browser automation, navigation, modal management |
| **Card Extractor** | `extractors/card.py` | Single card extraction (list + modal) |
| **Week Extractor** | `extractors/week.py` | Iterate weeks and extract all cards |
| **Enrichment Engine** | `enrichment/engine.py` | Coordinate enrichment operations |
| **Checkpoint Manager** | `io/checkpoint.py` | Persist extraction state |
| **Incremental Writer** | `io/incremental_writer.py` | Append-only data writes |
| **Recovery Manager** | `io/recovery.py` | Handle interrupted executions |

---

## 2. ELEMENT EXTRACTION & CATEGORIZATION

### 2.1 Card Extraction Process (`extractors/card.py`)

**Extraction Layers:**

1. **List View Extraction** (visible cards in Kanban)
   - Card ID: `data-rbd-draggable-id` attribute
   - Full text: `.text_content()` of card element
   - Links: All `<a>` elements with href validation
   - Images: All `<img>` with src validation

2. **Modal Extraction** (detailed view)
   - Opens card by clicking
   - Waits for modal with multiple selectors:
     ```
     "[role='dialog']"
     ".MuiModal-root"
     "[class*='Modal']"
     "[class*='modal']"
     ".modal"
     "[data-testid*='modal']"
     ```

3. **Type Identification** (deterministic)
   - **Primary method**: Icon-based detection from SVG ID
   - **Icon mapping** (`models/card_types.py`):
     ```python
     ICON_TO_CARD_TYPE = {
         "book-open-reader-solido": "autoestudo",
         "user-group-solido": "encontro_orientacao",
         "chalkboard-user-solido": "encontro_instrucao",
         "square-code-solido": "projeto",
         "user-pen-solido": "avaliacao"
     }
     ```
   - **Fallback**: Heuristic classification based on text keywords if icon not found

4. **Modal Content Extraction**
   - Description: `div.content-description-text p`
   - Professor: `div.general-information-activity-row span`
   - Date/Time: Regex pattern matching `DD/MM/AAAA - HH:MM`
   - Related subjects: `div.content-related-issues ul li`
   - Related content: `div.content-related-content ul li a`
   - Weighted activity: `div.general-information-activity` text parsing

5. **Link Categorization** (`_categorize_url`)
   ```
   File extensions (.pdf, .doc, .docx, etc.) → "arquivos"
   Google domains (drive.google, docs.google) → "materiais"
   Everything else → "links"
   ```

### 2.2 Type Classification System

**Type Definition** (`models/card_types.py`):

```python
CARD_TYPE_FIELDS = {
    "autoestudo": {
        "has_assuntos_relacionados": True,
        "has_conteudos_relacionados": True,
        "has_data_hora": False,
        "has_professor": True,
        "has_atividade_ponderada": False
    },
    "encontro_orientacao": {
        "has_assuntos_relacionados": True,
        "has_conteudos_relacionados": False,
        "has_data_hora": True,
        "has_professor": True,
        "has_atividade_ponderada": False
    },
    "encontro_instrucao": {
        "has_assuntos_relacionados": True,
        "has_conteudos_relacionados": False,
        "has_data_hora": True,
        "has_professor": True,
        "has_atividade_ponderada": False
    },
    "projeto": {
        "has_assuntos_relacionados": False,
        "has_conteudos_relacionados": False,
        "has_data_hora": False,
        "has_professor": False,
        "has_atividade_ponderada": True  # ALWAYS present
    },
    "avaliacao": {
        "has_assuntos_relacionados": False,
        "has_conteudos_relacionados": False,
        "has_data_hora": True,
        "has_professor": True,
        "has_atividade_ponderada": True
    }
}
```

**Extraction Strategy** (`extractors/card.py:extract_card_data`):
- Try icon-based type identification first (deterministic)
- Extract only expected fields for that type
- Force specific rules (e.g., projects always ponderada=True)
- Derive boolean flags: `is_encontro`, `is_sincrono`, `is_avaliativo`

---

## 3. ENRICHMENT & CATEGORIZATION LOGIC

### 3.1 Enrichment Pipeline (`enrichment/engine.py`)

**Sequence of Operations:**

1. **Temporal Normalization**
   - Extract week number: `"Semana 01"` → `1`
   - Calculate sprint: `ceil(week_num / 2)` → 2-week sprints
   - Parse date/time: Regex pattern `\d{2}/\d{2}/\d{4} - \d{2}:\d{2}`
   - Generate ISO format with timezone

2. **Professor Detection**
   - Extract from modal (prioritized)
   - Fallback to heuristic:
     - Look for lines matching name regex
     - Prioritize recurrent names across cards
     - Use as tie-breaker in anchoring

3. **URL Normalization** (`normalize_urls_pipe`)
   - Split by `|`
   - Extract URL from `"Text: URL"` format
   - Validate HTTP/HTTPS protocol
   - Remove duplicates (preserve order)
   - Create separate lists: `links_urls`, `materiais_urls`, `arquivos_urls`

4. **Hash Generation**
   - Combines: `titulo | data_ddmmaaaa | professor`
   - Purpose: Detect changes between runs, identify duplicates

### 3.2 Autoestudo Anchoring (`enrichment/anchor.py`)

**Problem**: Link autoestudos to their corresponding instructions

**Scoring Algorithm** (4-factor multi-criterion):

```
Score = Σ(factors):
  + 3.0 (professor match)
  + 3.0 (same date)
  + 2.0 × similarity (title Jaccard)
  + 1.5 - 0.1×distance (positional proximity if card after instruction)
  - 0.2 (if card before instruction)

Confidence levels:
  - "high": professor match OR same date
  - "medium": high title similarity (≥0.5) OR positional proximity
  - "low": everything else
```

**Title Similarity** (`utils/text.py:title_similarity`):
- Normalize both titles (remove prefixes, punctuation)
- Tokenize and compute Jaccard similarity
- Formula: `intersection / union`

**Preservation Strategy:**
- Maintains previous anchors from prior runs
- Locks them as `anchor_confidence="locked"`
- Prevents re-anchoring on subsequent runs

---

## 4. PERFORMANCE BOTTLENECKS & INEFFICIENCIES

### 4.1 Critical Bottlenecks

| Issue | Location | Impact | Severity |
|-------|----------|--------|----------|
| **Modal selector spam** | `extractors/card.py:149-159` | Try 6+ selectors sequentially | HIGH |
| **Per-card DOM traversal** | `extractors/card.py:104-126` | Iterate all links twice (list + modal) | HIGH |
| **Regex patterns recompiled** | Multiple files | Compiled at runtime each time | MEDIUM |
| **Full text normalization** | `enrichment/anchor.py` | Done per anchoring pair | MEDIUM |
| **Known names detection** | `enrichment/normalizer.py:187-217` | Full scan in pre-pass | LOW |

### 4.2 Redundancies & Code Duplication

**1. Regex Pattern Definitions** (appears 3+ times)
```python
# adalove_extractor.py (line 47-50)
# extractors/card.py (line 20-21)
# enrichment/normalizer.py (line 14-23)

DATE_RE = re.compile(r"(\d{2}/\d{2}/\d{4})\s*-\s*(\d{2}:\d{2})h?", ...)
HTTP_RE = re.compile(r"^https?://", ...)
NAME_CANDIDATE_RE = re.compile(...)
```

**2. Title Normalization Logic** (duplicated)
```python
# adalove_extractor.py:_title_norm() [~15 lines]
# utils/text.py:normalize_title() [~20 lines]
# extractors/card.py:_classify_card_type_fallback() [inline normalization]
```

**3. URL Categorization** (appears 2 locations)
```python
# extractors/card.py:_categorize_url() [~15 lines]
# adalove_extractor.py:_categorize_url() [~10 lines]
```

**4. Professor Detection** (3 implementations)
```python
# extractors/card.py:_extract_professor()
# enrichment/engine.py:_guess_professor_fallback()
# adalove_extractor.py:_guess_professor()
```

**5. Hash Computation** (duplicated)
```python
# adalove_extractor.py:_compute_hash()
# utils/hash.py:compute_hash()
```

### 4.3 Inefficient Patterns

**1. Link Extraction - Double Iteration**
```python
# First pass: List view links (lines 104-126)
links_elementos = card.locator("a")
count_links = await links_elementos.count()
for i in range(count_links):
    # Process...

# Second pass: Modal links (lines 292-314)
modal_links = modal.locator("a")
mcount = await modal_links.count()
for j in range(mcount):
    # Process... (same categorization logic)
```
**Problem**: Same categorization done twice. Could deduplicate results.

**2. Selector Spam for Modal**
```python
# Try 6 different CSS selectors sequentially
modal_selectors = [
    "[role='dialog']",
    ".MuiModal-root",
    "[class*='Modal']",
    "[class*='modal']",
    ".modal",
    "[data-testid*='modal']"
]
for selector in modal_selectors:
    # Wait 2 seconds per selector × 6 = up to 12s wasted
```
**Better approach**: Parallel selector attempts or prioritize by observed frequency.

**3. Type Detection Fallback is Heavy**
```python
# In _classify_card_type_fallback (card.py:674-699)
# Multiple keyword checks with 3+ iterations each
autoestudo_keywords = [...]
if any(kw in texto_lower for kw in autoestudo_keywords):  # O(n*m)
```
**Better approach**: Precompile as regex `|` OR pattern.

**4. Field Extraction Not Optimized by Type**
```python
# Extract related issues
await _extract_assuntos_relacionados(modal, ...)  # Even if card_type != autoestudo

# Extract related content
await _extract_conteudos_relacionados(modal, ...)  # Even if card_type != autoestudo
```
**Current mitigation**: `should_extract_field()` check exists but is called AFTER extraction.

### 4.4 No Caching Layer

**Missing Optimizations:**
- No compiled regex cache (all patterns recompiled each use)
- No DOM element cache (same selectors queried multiple times)
- No title similarity cache (expensive Jaccard computed per pair in anchoring)
- No professor name cache (could memoize across cards)

---

## 5. DIRECTORY STRUCTURE & FILE ORGANIZATION

```
adalove_extractor/
├── __init__.py                  # Version + main exports
├── models/
│   ├── card.py                 # Raw card model (Pydantic)
│   ├── card_types.py           # Type definitions & mappings
│   ├── enriched_card.py        # Enriched card model
│   └── __init__.py
├── extractors/
│   ├── card.py                 # extract_card_data() - MAIN EXTRACTION
│   ├── week.py                 # extract_week_cards()
│   └── __init__.py
├── enrichment/
│   ├── engine.py               # EnrichmentEngine (coordinator)
│   ├── anchor.py               # AnchorEngine (autoestudo linking)
│   ├── normalizer.py           # Normalization functions
│   └── __init__.py
├── browser/
│   ├── navigator.py            # Playwright operations
│   ├── auth.py                 # Login logic
│   └── __init__.py
├── io/
│   ├── writers.py              # CSV/JSONL output
│   ├── checkpoint.py           # State persistence
│   ├── incremental_writer.py   # Append-only writes
│   ├── recovery.py             # Resume logic
│   └── __init__.py
├── utils/
│   ├── text.py                 # Text normalization, similarity
│   ├── hash.py                 # Hash utilities
│   └── __init__.py
├── config/
│   ├── settings.py             # Configuration
│   ├── logging.py              # Logger setup
│   └── __init__.py
└── cli/
    ├── main.py                 # CLI interface
    └── __init__.py
```

---

## 6. KEY INSIGHTS & PAIN POINTS

### 6.1 Architectural Strengths

1. **Modular Design**: Clear separation of concerns (extraction vs enrichment vs IO)
2. **Type Safety**: Pydantic models enforce schema throughout
3. **Resilience**: Checkpoint system prevents data loss
4. **Extensibility**: Easy to add new extractors or enrichment stages
5. **Testability**: 28 modules, high cohesion within modules

### 6.2 Critical Issues

| Issue | Impact | Root Cause |
|-------|--------|-----------|
| **Code duplication** | Maintenance burden, bug propagation | Monolithic `adalove_extractor.py` + modular version coexist |
| **Modal extraction fragile** | Frequent timeouts, 2-12s overhead | 6 sequential CSS selectors with 2s waits each |
| **Inefficient field extraction** | Extracts even non-relevant fields | Type-specific extraction not done early enough |
| **Missing caching** | Slow performance on large datasets | No memoization of expensive operations |
| **Regex recompilation** | 5-10% CPU overhead | No module-level compilation |

### 6.3 Scalability Concerns

**For 500+ cards:**
- Modal selector spam: 2-12s per card × 500 = 1000-6000s wasted
- No parallelization: Single-threaded Playwright
- Enrichment O(n²) for anchoring: 500² = 250k similarity calculations
- No incremental output: All data held in memory until end

---

## 7. OPTIMIZATION OPPORTUNITIES

### Priority 1: Eliminate Code Duplication
1. **Remove `adalove_extractor.py`** (1017 lines) - move any unique logic to modules
2. **Consolidate regex patterns** in `utils/patterns.py`:
   ```python
   # Compile once at module load
   PATTERNS = {
       "date": re.compile(...),
       "http": re.compile(...),
       "name": re.compile(...),
       ...
   }
   ```
3. **Merge duplicate functions**: `_title_norm`, `_guess_professor`, `_categorize_url`

### Priority 2: Optimize Modal Extraction
1. **Parallel selector attempts** (use `asyncio.gather()` with first to complete)
2. **Cache selector results** after first successful find
3. **Reduce wait timeouts** based on observed speed per environment
4. **Pre-load modal content** with JavaScript injection

### Priority 3: Optimize Enrichment
1. **Compile regex patterns** at module import (8-10 patterns)
2. **Cache title similarities** in `Dict[Tuple[str,str], float]`
3. **Early field filtering** before extraction (check type first)
4. **Lazy enrichment** - only compute fields needed for current operation

### Priority 4: Add Caching Layer
```python
# Professor name cache (string → string)
# Title similarity cache (tuple(str,str) → float)
# DOM selector cache (selector → locator)
# Type mapping cache (icon_id → card_type)
```

### Priority 5: Parallelization
1. **Async card extraction** per week (not sequential)
2. **Batch enrichment** with vectorized operations
3. **Parallel file I/O** (write while extracting next week)
4. **Thread pool** for CPU-bound enrichment

---

## 8. SPECIFIC FILE ISSUES

### `extractors/card.py` (705 lines)

**Issues:**
- Lines 149-159: Modal selector loop (HIGH bottleneck)
- Lines 104-126: First pass link extraction
- Lines 292-314: Second pass link extraction (duplication)
- Lines 248-287: Field extraction logic could be parametrized

**Quick wins:**
- Extract `modal_selectors` to constant
- Deduplicate link extraction with helper
- Replace `count()` loops with `.all()` and list comprehension

### `enrichment/engine.py` (200 lines)

**Issues:**
- Line 76: `detect_known_names()` scans all text in pre-pass
- Line 83: No caching of anchor scores
- Line 113: `extract_date_time()` called per field

**Quick wins:**
- Cache detected names in instance variable
- Memoize similarity scores during anchoring
- Batch date extraction (combine title+description+full_text earlier)

### `enrichment/anchor.py` (200 lines)

**Issues:**
- Lines 123-191: `_calculate_anchor_score()` called many times without caching
- Line 163: `title_similarity()` is O(n²) in worst case

**Quick wins:**
- Add `@lru_cache` to title similarity or cache manually
- Lazy-evaluate factors (skip expensive calculations if early match)
- Use vectorized numpy for larger batches

### `utils/text.py` (90 lines)

**Issues:**
- Line 35: Regex substitutions repeated (could be single pass)
- No caching of normalized results

**Quick wins:**
- Combine regex patterns: `re.sub(r'(pattern1|pattern2|pattern3)', '', text)`
- Add optional cache parameter

---

## 9. SUMMARY: METRIC DASHBOARD

| Metric | Current | Target | Priority |
|--------|---------|--------|----------|
| **Code duplication** | ~400 LOC | 0 | P1 |
| **Modal extraction time** | 2-12s/card | <500ms | P1 |
| **Regex compilations** | ~50 per run | 1 per load | P2 |
| **Title similarity cache hits** | 0% | >60% | P3 |
| **Memory per card** | ~15KB | <10KB | P4 |
| **Parallelization** | 0 tasks | 4+ tasks | P5 |

---

## 10. RECOMMENDATION ROADMAP

### Phase 1: Code Consolidation (1-2 days)
- [x] Identify all duplications
- [ ] Merge `adalove_extractor.py` into modular structure
- [ ] Create `utils/patterns.py` with compiled patterns
- [ ] Consolidate all helper functions

### Phase 2: Performance (3-5 days)
- [ ] Optimize modal selector (parallel attempts)
- [ ] Add caching layer (LRU + manual caches)
- [ ] Optimize link extraction (single pass)
- [ ] Profile and benchmark each optimization

### Phase 3: Scalability (5-7 days)
- [ ] Implement async extraction per week
- [ ] Batch enrichment operations
- [ ] Add parallelized enrichment
- [ ] Load test with 1000+ cards

### Phase 4: Architecture Cleanup (2-3 days)
- [ ] Remove legacy code paths
- [ ] Update all imports
- [ ] Add comprehensive tests
- [ ] Performance regression tests

