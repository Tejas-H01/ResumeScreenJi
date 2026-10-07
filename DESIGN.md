# Resume Screening --- Frontend Design System

## 1. Purpose

This document is the visual source of truth for the frontend redesign of
the existing Resume Screening ML application.

The application is already functionally complete. This redesign is
**frontend-first** and must preserve the existing ML/backend
functionality.

The visual direction is inspired by the provided references:

-   Structured modern SaaS dashboard layouts
-   Playful editorial card systems
-   Warm cream/off-white surfaces
-   Controlled bright accent colors
-   Strong dark outlines
-   Rounded geometric shapes
-   Friendly illustrated micro-elements
-   A polished, classic interface with playful details

The goal is:

> **Professional enough for an AIML project demonstration, but visually
> memorable enough that it does not feel like another generic AI
> dashboard.**

------------------------------------------------------------------------

# 2. Core Design Direction

## Personality

The interface should feel:

-   Playful
-   Intelligent
-   Modern
-   Friendly
-   Confident
-   Premium
-   Approachable
-   Slightly editorial
-   Technically credible

It must **not** feel:

-   Corporate and sterile
-   Generic "AI SaaS"
-   Cyberpunk
-   Neon/futuristic
-   Overly childish
-   Randomly colorful
-   Like a WhatsApp/Instagram-style interface
-   Like a template assembled from unrelated UI components

The design should have personality through **composition, illustration,
color accents, typography, and micro-interactions**, rather than through
excessive decoration.

------------------------------------------------------------------------

# 3. Visual Philosophy

The key principle is:

## "Structured base + playful accents"

The majority of the interface should remain calm and highly readable.

Colorful elements should act as:

-   Highlights
-   Status indicators
-   Section anchors
-   Visual rewards
-   Micro-illustrations
-   Important CTAs
-   Feedback moments

Do NOT make every card a different bright color.

Use a restrained neutral foundation and introduce color intentionally.

------------------------------------------------------------------------

# 4. Reference Interpretation

The provided references establish the following visual language:

### Reference A --- Dashboard

Use as inspiration for:

-   Strong application frame
-   Sidebar/navigation hierarchy
-   Large primary content area
-   Clear dashboard sections
-   Large visual KPI elements
-   Compact information cards
-   Dense information presented cleanly
-   Strong visual hierarchy

Do NOT copy the healthcare/billing content or exact layout.

Adapt the structural principles to resume screening.

### Reference B --- Playful Card UI

Use as inspiration for:

-   Bold dark outlines
-   Large friendly typography
-   Modular card layouts
-   Strong color blocks
-   Editorial composition
-   Slightly playful proportions
-   Cards that feel like designed objects rather than generic containers

### Reference C --- Color Palette

Use as inspiration for the controlled accent palette:

-   Warm orange/red
-   Golden yellow
-   Soft yellow
-   Soft lavender
-   Soft pink
-   Muted green

The colors should work together rather than being randomly distributed.

### References D/E --- Decorative Elements

Use as inspiration for:

-   Hand-drawn / illustrated visual elements
-   Friendly faces
-   Abstract shapes
-   Stars
-   Hearts
-   Flowers
-   Eyes
-   Arrows
-   Clouds
-   Organic blobs
-   Small expressive illustrations

These should appear selectively as visual "cherry on top" details.

------------------------------------------------------------------------

# 5. Color System

## Base Colors

Use a warm, slightly creamy background rather than pure white.

Suggested foundation:

``` text
Background:       #F7EBD9
Surface:          #FFF9EF
Primary Ink:      #171717
Secondary Ink:    #4A4742
Muted Border:     #252525
```

The exact implementation may adjust these slightly for accessibility and
contrast, but the overall warm character must remain.

## Accent Palette

Use the reference palette:

``` text
Orange:           #FF552E
Golden Yellow:    #F2A815
Soft Yellow:      #FED170
Lavender:         #B6ACE4
Soft Pink:        #FFC1C6
Muted Green:      #ABCF82
```

Optional supporting accent:

``` text
Teal:             #14C3B3
```

## Color Usage Rules

Orange should be the strongest energetic accent.

Yellow should communicate:

-   Attention
-   Highlights
-   Quick actions
-   Important but non-dangerous states

Pink/lavender/green should be supporting accents.

Do not use all accent colors simultaneously in the same small area.

A section should generally have:

-   1 dominant accent
-   1 supporting accent
-   Neutral foundation

------------------------------------------------------------------------

# 6. Borders

Borders are a major part of the visual identity.

Prefer:

``` text
1.5px–2px solid #171717
```

for major cards and interactive components.

Borders should feel intentional and visible.

Avoid:

-   Extremely thin gray borders
-   Generic Tailwind gray borders everywhere
-   Excessive glassmorphism
-   Excessive shadows

------------------------------------------------------------------------

# 7. Shadows

Use compact, slightly offset shadows inspired by the references.

Preferred:

``` text
box-shadow: 0 3px 0 #171717;
```

or similarly subtle hard-offset shadows.

Avoid:

-   Huge soft shadows
-   Floating glass cards
-   Excessive blur
-   Strong neumorphism

The interface should feel slightly tactile.

------------------------------------------------------------------------

# 8. Corner Radius

Use moderately rounded corners.

Suggested range:

``` text
12px–20px
```

Large feature cards may use:

``` text
20px–28px
```

Small controls may use:

``` text
8px–12px
```

Do not make every element pill-shaped.

Pills should be reserved for:

-   Status
-   Tags
-   Filters
-   Small metadata
-   Compact controls

------------------------------------------------------------------------

# 9. Typography

Typography should be bold, friendly, and highly legible.

Preferred visual character:

-   Strong rounded/geometric sans-serif
-   Bold display headings
-   Clear body text
-   Compact metadata

Recommended font direction:

-   Use an existing project font if already established.
-   Otherwise prefer a modern rounded/geometric sans-serif such as
    **Plus Jakarta Sans, Manrope, or similar**.

Do not introduce a decorative handwritten font for the primary
interface.

### Headings

Large headings should be:

-   Bold
-   Compact
-   Confident
-   Slightly expressive

Example:

``` text
Screen your next
great candidate.
```

### Body

Body text must remain straightforward and professional.

------------------------------------------------------------------------

# 10. Overall Application Structure

The application should feel like a polished product rather than a
collection of forms.

Preferred high-level structure:

``` text
Application Shell
│
├── Navigation / Sidebar
│
└── Main Workspace
    │
    ├── Header / Intro
    │
    ├── Resume + Job Input Workspace
    │
    ├── Screening Action
    │
    └── Results Workspace
        │
        ├── Final Score
        ├── Fit Level
        ├── Role Prediction
        ├── Job Match
        ├── Screening Decision
        ├── Skill Analysis
        ├── Score Breakdown
        └── ML Explanation
```

The actual existing application structure should be inspected before
implementation.

Do not unnecessarily rewrite the application architecture.

------------------------------------------------------------------------

# 11. Navigation

Navigation should be simple and compact.

If the current application has a sidebar, redesign it into a visually
strong but restrained navigation panel.

Possible sections:

-   Screening
-   Results
-   How It Works
-   Model Insights
-   Feedback

The navigation should not dominate the application.

Use small line icons with strong typography.

Avoid excessive icon-only navigation.

------------------------------------------------------------------------

# 12. Main Screening Workspace

The screening workspace is the primary interaction.

It should immediately communicate:

> "Give me a resume and a job description, and I'll evaluate the
> candidate."

The input area should feel like a designed workspace rather than a
standard form.

Use two strong content blocks:

``` text
RESUME
Upload / paste resume
        +
JOB DESCRIPTION
Paste / select job description
```

These can visually resemble two coordinated cards.

------------------------------------------------------------------------

# 13. Resume Input

The resume input should support the existing functionality.

Visual treatment:

-   Large drop/upload zone
-   Clear upload affordance
-   File type information
-   Uploaded file state
-   Optional extracted-text preview if already supported

Use a subtle illustration or small decorative icon.

Do not use generic stock AI imagery.

------------------------------------------------------------------------

# 14. Job Description Input

The JD area should visually balance the resume area.

Use:

-   Clear heading
-   Text area
-   Character/length feedback if already supported
-   Job description presets if existing functionality supports them

Keep it visually calm.

------------------------------------------------------------------------

# 15. Quick Fill Demo

The existing **Quick Fill Demo** feature should feel like a deliberate
demo shortcut.

Style:

-   Small but noticeable
-   Accent-colored
-   Friendly
-   Clearly secondary to the primary screening action

Possible treatment:

``` text
✨ Quick Fill Demo
```

Use an illustrated micro-icon or tasteful symbol rather than a standard
emoji glyph if possible.

Clicking it should populate the existing demo data without automatically
submitting.

------------------------------------------------------------------------

# 16. Primary Screening CTA

The main action should be visually prominent.

Possible label:

``` text
Screen Candidate →
```

or retain the application's existing wording if already established.

Use the strongest accent color, preferably orange.

Button should have:

-   Dark outline
-   Slight hard-offset shadow
-   Strong typography
-   Clear hover state
-   Clear loading state

Loading state should feel polished and playful without becoming
distracting.

------------------------------------------------------------------------

# 17. Results Experience

Results are the most important part of the application.

Do NOT present them as a boring wall of statistics.

The result should have a clear hierarchy:

``` text
Candidate Evaluation

82
GOOD FIT

Machine Learning Engineer
84% role confidence

81% job match

HIRE
88% probability
```

Use large typography for the primary score.

The user should understand the result within approximately 2 seconds.

------------------------------------------------------------------------

# 18. Final Score Card

The final score should be the visual hero of the results.

Use:

-   Large numeric score
-   Circular/ring visualization if already available
-   Fit-level badge
-   Short supporting description
-   Accent color based on score category

Suggested visual logic:

``` text
Strong Fit      → Green / warm positive accent
Good Fit        → Yellow / orange
Moderate Fit    → Lavender / yellow
Weak Fit        → Pink / restrained red
```

Do not use harsh red/green dashboard aesthetics.

------------------------------------------------------------------------

# 19. Role Prediction Card

Display:

``` text
Predicted Role
Machine Learning Engineer

Confidence
84%
```

Use a small illustrated/abstract visual element where appropriate.

The actual values must always come from the backend.

------------------------------------------------------------------------

# 20. Job Match Card

Display:

-   Match percentage
-   Match label
-   Short contextual explanation if already available

Use a visual progress/ring/bar system.

Avoid generic progress bars with no personality.

------------------------------------------------------------------------

# 21. Screening Decision

The Hire/Reject result should be visually obvious but not alarming.

Use:

-   Strong label
-   Probability
-   Small supporting explanation

Avoid making the interface feel like an HR surveillance system.

------------------------------------------------------------------------

# 22. Skill Analysis

The skill section should be visually engaging.

Use three groups:

``` text
✓ Matched Skills
! Missing Skills
+ Additional Skills
```

Matched skills can use green/teal.

Missing skills can use yellow/orange.

Additional skills can use lavender/pink.

Skill tags should have dark outlines and compact typography.

------------------------------------------------------------------------

# 23. Score Breakdown

Show the actual hybrid scoring logic:

``` text
Resume–Job Match       35%
Skill Match             25%
Screening Score         25%
Role Confidence         15%
```

Present this as a visually interesting composition rather than a plain
table.

A horizontal segmented bar, stacked blocks, or four colorful cards are
preferred.

The weights must remain exactly as defined by the existing system.

------------------------------------------------------------------------

# 24. ML Explanation

The existing "How our ML works" feature should feel like part of the
product rather than documentation.

Use a visual pipeline:

``` text
Resume + JD
     ↓
Preprocessing
     ↓
TF-IDF
     ↓
Role Model
     +
Matching Model
     +
Screening Model
     +
Score Model
     ↓
Skill Analysis
     ↓
Hybrid Score
```

Use small cards and connectors.

The section should be understandable to a professor while remaining
technically accurate.

Do not describe the system as using an LLM or generative AI.

------------------------------------------------------------------------

# 25. Decorative Illustration System

This is a key part of the redesign.

Use **curated illustrated micro-elements** inspired by the supplied
references.

Potential visual vocabulary:

-   Small expressive faces
-   Eyes
-   Stars
-   Hearts
-   Flowers
-   Arrows
-   Abstract blobs
-   Clouds
-   Sparkles
-   Check marks
-   Tiny characters
-   Organic geometric shapes

However:

## Do NOT use standard operating-system emoji glyphs everywhere.

Avoid:

``` text
😀 🚀 🔥 🎉 🤖
```

as generic decoration.

Prefer:

-   Custom/illustrated symbols
-   Hand-drawn SVG elements
-   Consistent sticker-style illustrations
-   Small line-art characters
-   Curated iconography

The decorative language must feel like one coherent illustration set.

------------------------------------------------------------------------

# 26. Micro-Interaction Philosophy

Playfulness should appear when something happens.

Examples:

### Successful upload

A tiny illustrated check/sparkle can appear.

### Quick Fill

Small playful visual feedback.

### Screening completed

The score can animate into view.

### Strong Fit

A subtle celebratory micro-animation can appear.

### Missing skills

Use gentle visual emphasis rather than aggressive warning styling.

### Errors

Keep errors professional and clear.

Animations must be:

-   Short
-   Purposeful
-   Subtle
-   Fast

Never turn the application into an animated toy.

------------------------------------------------------------------------

# 27. Card System

Cards should feel like a coherent family.

Use:

-   Warm surfaces
-   Dark outlines
-   Moderate radius
-   Slight hard shadows
-   Strong headings
-   Compact metadata
-   Occasional accent fills

Do not make every card colorful.

Recommended pattern:

``` text
Neutral card
+ colored heading/icon

or

Colored card
+ neutral/dark content

but not

colored card + colored card + colored card + colored card
```

------------------------------------------------------------------------

# 28. Charts

Existing charts should be redesigned to match the visual system.

Charts should use:

-   Warm neutral backgrounds
-   Dark labels
-   Controlled accent palette
-   Strong readability

Avoid default chart-library aesthetics.

Use the project palette consistently.

------------------------------------------------------------------------

# 29. Buttons

Primary:

-   Orange or strongest accent
-   Dark border
-   Hard-offset shadow
-   Bold text

Secondary:

-   Cream/white
-   Dark border
-   Subtle shadow

Tertiary:

-   Minimal
-   Text or icon based

Buttons should feel tactile.

Hover:

-   Slight upward movement
-   Shadow shift

Pressed:

-   Shadow compresses
-   Slight downward movement

------------------------------------------------------------------------

# 30. Inputs

Inputs should not look like default browser controls.

Use:

-   Warm surface
-   Dark border
-   Comfortable padding
-   Strong focus state
-   Clear labels

Focus states should use an accent outline rather than generic blue
browser focus.

------------------------------------------------------------------------

# 31. Background

The background should have subtle personality.

Preferred:

-   Warm cream foundation
-   Occasional subtle abstract shapes
-   Very light decorative linework

Do not use:

-   Heavy gradients
-   Neon backgrounds
-   Animated backgrounds
-   Dense patterns behind text

The background must remain readable.

------------------------------------------------------------------------

# 32. Responsive Design

Desktop:

-   Use a spacious dashboard composition.
-   Allow multiple result cards to sit side-by-side.
-   Preserve visual hierarchy.

Tablet:

-   Reduce columns.
-   Maintain card proportions.

Mobile:

-   Stack major sections.
-   Keep score prominent.
-   Keep CTA accessible.
-   Preserve decorative elements selectively.
-   Never allow decoration to push important content below the fold
    unnecessarily.

The mobile experience must feel intentionally designed, not merely
collapsed.

------------------------------------------------------------------------

# 33. Accessibility

Despite the playful design:

-   Maintain strong text contrast.
-   Do not communicate important states using color alone.
-   Buttons must have readable labels.
-   Interactive elements must remain keyboard accessible.
-   Decorative illustrations should not interfere with screen readers.
-   Respect reduced-motion preferences.

------------------------------------------------------------------------

# 34. Anti-Patterns --- Strictly Avoid

Do NOT create:

-   Generic purple-gradient AI UI
-   Neon cyberpunk styling
-   Excessive glassmorphism
-   Excessive gradients
-   Excessive rounded pills
-   Every card in a different color
-   Huge decorative emoji everywhere
-   Cartoonish children's-app styling
-   Excessive animations
-   Random illustrations with unrelated styles
-   Stock AI robot imagery
-   Generic dashboard templates
-   Excessive drop shadows
-   Tiny unreadable typography
-   Visually noisy result screens

------------------------------------------------------------------------

# 35. Functional Protection

This redesign must NOT alter the application's underlying functionality.

Do not modify:

-   ML models
-   Model artifacts
-   Training logic
-   Hybrid scoring weights
-   FastAPI endpoints
-   API contracts
-   Resume parsing
-   Skill extraction
-   Screening calculations
-   Recommendation logic
-   CSV export
-   Feedback functionality
-   Existing Quick Fill data
-   Existing ML Explanation data

If an existing component already provides the required functionality,
redesign its presentation rather than replacing its behavior.

------------------------------------------------------------------------

# 36. Implementation Philosophy

Before changing code:

1.  Inspect the existing frontend structure.
2.  Identify all current components.
3.  Identify the existing application state and API calls.
4.  Identify reusable components.
5.  Map existing functionality to this design system.
6.  Then implement the visual redesign.

Do not rewrite the frontend from scratch unless a specific existing
component genuinely prevents the design from being implemented.

The redesign should be an evolution of the working product.

------------------------------------------------------------------------

# 37. Final Visual Target

The finished product should feel like:

> **A serious AIML resume-screening product designed by a creative
> product designer.**

It should be:

**Clean + colorful + intelligent + playful + polished.**

The visual personality should come from:

``` text
Warm cream foundation
        +
Bold dark outlines
        +
Controlled accent colors
        +
Strong typography
        +
Editorial card composition
        +
Curated illustrations
        +
Small moments of delightful interaction
```

The result must remain professional enough to present to a college
professor and credible enough to feel like a real product.
