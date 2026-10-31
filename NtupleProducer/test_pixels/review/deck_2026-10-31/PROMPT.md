You are reviewing a 27-slide group-meeting talk (16 main + 11 backup) before it is given. Audience: a first-year
particle-physics graduate student should follow it on first viewing; the room also has a postdoc and a PI. Read-only:
do not modify anything.

Inputs in this directory:
- deck_text.md: every slide as text in order, with [FIGURE: figs/x.png] and [DIAGRAM: description] markers and the
  speaker notes. Read it first.
- figs/*.png: the figures embedded in the slides. Look at them.
- project/slides/*.html: the slide sources (1920x1080 canvas, inline styles) if you need layout details;
  project/deck.json: order and sections.

Review for three things, concretely and per slide:
1. Train of thought: is the logic from slide to slide obvious? Where does a slide's point not follow from the previous
   slide, where is a step missing, where is something introduced before it is needed (or used before it is explained)?
   Propose a better order or a missing bridging slide/sentence if needed. Each slide title should state its point.
2. Understandability for a first-year grad student: undefined terms, numbers without context, figures that need
   explanation the slide does not give, too much text, jargon. Give replacement wording.
3. Show, don't tell: list every place where a claim is asserted in words but not shown (with a figure, diagram,
   number, or worked example), and say exactly what visual would show it (e.g. "sketch b-hadron decay with impact
   parameter d0", "plot of X vs Y from existing figure Z", "a two-row timeline"). Also flag slides that are mostly
   bullets and could be a single visual. Prioritise the ones that matter most for the argument.

Deliver (markdown, final answer): (a) the 3-5 biggest problems with the flow, (b) a per-slide table: slide | problem |
concrete fix (including the visual to add), (c) a proposed final slide order if it should change, (d) anything that is
confusing or likely to be misread in the figures themselves.
