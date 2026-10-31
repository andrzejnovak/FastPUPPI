You are reviewing a results page before it is shown to a CMS postdoc, a CMS PI, and a physicist from ATLAS (who knows
collider triggers, b-tagging and pixel detectors, but not CMS internals). Read-only: do not modify anything.

Inputs in this directory:
- page_source.html: the page (8 tabs; inline SVG diagrams; figures referenced as figs/*.png, attached as images).
- Data and code it cites live under /work/submit/novaka/l1pixels/analysis, /work/submit/novaka/l1pixels/offline and
  /scratch/submit/cms/novaka/l1pixels/derived (JSON outputs: plots_page/recovery.json, rate_case.json,
  derived/scout4b.json, derived/scout_kin.json, derived/offline_lowmass_w.json, derived/norm_check.json,
  derived/chip_readout/readout_queue.json, tag_chain*.json, derived/curves_noL1.json). Internal notes with the full
  derivations: /work/submit/novaka/l1pixels/ngv2/CMSSW_17_0_0_pre2/src/FastPUPPI/NtupleProducer/test_pixels/studies/feasibility_2026-10-27.md
  The RD53B manual text is in /scratch/submit/cms/novaka/l1pixels/derived/rd53b_manual_v2.21.txt.

Deliver (markdown, as your final answer), concise and specific (quote the sentence, give the fix):
1. Clarity for the ATLAS reader: every place where CMS jargon, an undefined term, an unexplained number or a figure
   label would stop them. Suggest the replacement text. Also: places where the page explains too much.
2. Numbers: check every number on the page against the cited JSON/notes. List mismatches, rounding issues and numbers
   with no traceable source.
3. Claims: any statement that is stronger than the evidence (especially the readout-chip argument against the manual
   text, the scouting bound, and the ATLAS comparisons: ATLAS Phase-2 L0 rate/latency, no tracking at L0, ITkPix /
   CROC relationship, the two-level mode history). Flag anything factually doubtful.
4. Structure: does each tab answer its question in the first sentence? Anything missing that this audience will ask?
5. The 5 most important fixes, ranked.
