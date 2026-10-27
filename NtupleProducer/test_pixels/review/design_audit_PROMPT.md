You are auditing the DESIGN AND CLARITY of a one-page, tabbed results dashboard (an HTML page) for a CMS Phase-2
Level-1 trigger pilot study. You are read-only: do not modify anything.

THE READER: a first-year graduate student on CMS. They know what a trigger, a b jet, pileup, HL-LHC and HH -> 4b are,
roughly; they do NOT know the Phase-2 L1 internals (correlator, PUPPI, seeded-cone jets, RoI requests, pixel readout
chips, lpGBT/e-links), offline taggers by name (UParT), or statistics jargon (Asimov, models A/B). The page must be
understandable AT A GLANCE: within ~10 seconds per section they should get what question is asked, what the answer is,
and why it matters; details are allowed behind toggles.

WHAT YOU HAVE (this directory):
- shots/tabN_<id>_KK.png: screenshots of each tab as the reader sees it, in order (tab 1 = HH->4b story, 2 = how
  path A works, 3 = getting the hits, 4 = rate, 5 = beyond HH->4b, 6 = code). Each tab is cut into ~1300 px tall pieces.
  These screenshots are attached to this prompt; you can also open them.
- page_text.html: the page source with figures replaced by [FIGURE] and their alt text (styles omitted).
- figures/*.png: every figure at full resolution.

THE INTENDED STORY: (1) the planned L1 menu has no b tag and misses many HH->4b events, mostly at low m_HH where the
Higgs self-coupling (kappa_lambda) information is; (2) today's plan adds an L1 neural-network b tagger; (3) path A adds
pixel hits to the real-time L1 decision and recovers most of the gap; (4) what that buys for kappa_lambda;
(5) path B, using pixel tags only in 40 MHz scouting, recovers nothing; (6) verdict. Later tabs: how path A works,
how the pixel hits would be read out, the rate case, other channels, code.

DELIVER a markdown report (print it as your final answer), concise, no filler:
1. A 5-line summary: does a first-year student get the story at a glance? What are the three biggest obstacles?
2. Per tab: (a) the takeaway a student would actually walk away with in 10 s vs the intended one; (b) undefined jargon
   and acronyms, with a one-line plain definition to add or a simpler word; (c) figures: is each readable at a glance
   (title, axis labels, legend, colours, too many series, tiny text, unclear units, misleading scales), and what single
   change would most improve it; (d) text: what to cut, merge, or turn into a figure; (e) ordering and flow problems.
3. Cross-cutting: consistency of numbers between tiles, text, tables and figures (flag any mismatch with where it
   appears); colour meaning consistency; whether the "How this was made" boxes work; whether tiles/headlines state
   conclusions or just labels; anything that reads as overclaiming or hedging too much.
4. A ranked list of the 15 most valuable concrete edits (most valuable first), each one actionable (e.g. "rename tile X
   to '...'", "add y-axis label '...' to figure Y", "move section Z above W", "replace the table with a 3-bar chart").
5. Optional: rewritten headline + tiles for tab 1 in your proposed wording.
Cite the screenshot file or figure name for every point.
