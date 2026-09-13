# Verification of the 2026-09-13 research map, primary sources only

Date: 2026-09-13
Companion files: docs/research_map_2026-09-13.md (the input, unedited),
docs/claude_code_handoff_research_map_verify.md (the task brief).

Method. Every item below was re-derived from the primary page named in
its row, fetched 2026-09-13. The session container's egress policy
blocks direct HTTPS to the primary domains, so every fetch was made
through the Exa crawler (mcp Exa web_fetch tool), which live-crawls the
named URL server side and returns its text; WebSearch was used only to
locate URLs, never as verification. The map's own citations were not
used as verification. All keyword counts and letter tallies below were
computed by script runs shown in the session, not by reading. Verbatim
quotes reproduce the source's words; where a source prints an em dash
or en dash, this file substitutes a plain hyphen and says so if the
distinction matters. Row tags name the section of the research map the
claim came from.

Fetch caveat, recorded once: an Exa live-crawl reads the URL at fetch
time but is a third-party renderer; PDF text is its extraction. Counts
were reproduced from saved extractions by an independent script run in
the session (630 of 630 term-count cells matched).

Summary. Item 1: CONFIRMED, no stop condition. Paragraphs .B28 to .B33
exist under "Benchmarking of Automated Controls" in Appendix B of both
the currently effective AS 2201 and the version effective 2026-12-15,
with the substance the map describes, and paragraph .60 points to .B28
in both. Item 2: all 71 letters enumerated from the docket page; 70 of
71 fetched and censused (68 clean, 2 partial); 1 letter (33) could not
be retrieved. No letter makes, or comes close to making, the argument
that AS 2201 benchmarking cannot apply to vendor-hosted AI or LLM
controls. Zero letters use "automated control", "automated application
control", or "model version" anywhere.

## CONFIRMED

Each row: claim (map section); source URL; note. Fetch date for every
row: 2026-09-13.

1. AS 2201 Appendix B contains "Benchmarking of Automated Controls" at
   paragraphs .B28 through .B33 in the currently effective standard,
   with the substance the map describes: .B28 human-failure rationale;
   .B29 baseline reliance conditions; .B30 dependence on files,
   tables, data, and parameters; .B31 risk factors including the
   compilation-date report; .B32 purchased software with remote change
   possibility; .B33 baseline re-establishment factors. (Sections 2, 3)
   https://pcaobus.org/oversight/standards/auditing-standards/details/AS2201
   Note: live text numbers the paragraphs with a dot prefix (".B28");
   the map writes "B28". Same paragraphs, cosmetic difference. .B29
   conditions ITGCs effective "and continue to be tested" plus auditor
   verification that the control has not changed since the baseline;
   the map's summary omits "and continue to be tested". .B30 says
   "files, tables, data, and parameters"; the map omits "data".
2. The same section, byte-for-byte after whitespace normalization,
   appears in the AS 2201 version effective 2026-12-15. The December
   2026 amendment touches only paragraph .09 and adds new paragraph
   .99 (engagement deficiencies, AS 2901); Appendix B is untouched.
   (Section 3)
   https://pcaobus.org/oversight/standards/auditing-standards/details/as-2201--an-audit-of-internal-control-over-financial-reporting-that-is-integrated-with-an-audit-of-financial-statements-(effective-on-12-15-2026)
   Note: banner on the current-version page names the amended
   paragraphs; the amended page marks changes in gray boxes. A diff of
   the two benchmarking sections run in session: identical.
3. Paragraph .60 of both versions reads: "Benchmarking is described
   further beginning at paragraph .B28." The map's claim that .60
   points to B28 holds in the live text; no archived-page inference is
   needed. (Sections 2, 3) Both URLs above.
4. RFC 2026-001 was issued March 31, 2026 with seven numbered
   questions; question 6 reads "In what ways should the PCAOB consider
   deploying technology, including AI, to help further its
   investor-protection mission?"; first-round comments were due
   May 15, 2026. (Section 3)
   https://assets.pcaobus.org/pcaob-dev/docs/default-source/about/administration/documents/strategic_plans/pcaob-no-2026-001-rfc-sp.pdf
5. 71 comment letters, numbered 1 through 71 with no gaps, are listed
   on the PCAOB docket page ("Status: The comment period is closed").
   The map's "71 letters total" is exact. (Section 3)
   https://pcaobus.org/about/strategic-plan-budget/public-comments-on-pcaob-strategic-priorities
   Note: letter 69 is dated Feb. 26, 2026, before the RFC issuance
   date; letters 67, 68, 70, 71 are dated after the May 15 deadline
   (May 18, May 21, Jun. 22, Jun. 23). Dates as printed on the docket.
6. The map's claim "No letter found making the AS 2201
   benchmarking-vs-served-LLM argument" survives the full census: in
   the 70 letters read, a script found zero occurrences of B28 through
   B33 and zero uses of "Appendix B" referring to AS 2201 (the three
   letters that say "Appendix B", numbers 44, 56, 59, all mean the
   AICPA appendix on GAAS-ISA differences). See RFC LETTER CENSUS.
   (Section 3)
7. IIA letter 39 references AS 2201 in passing, on internal audit:
   "the PCAOB has acknowledged the profession's importance through
   standards like AS 2201 and AS 2605." (Section 3)
   https://assets.pcaobus.org/pcaob-dev/docs/default-source/about/administration/strategic-plan-comments-2026/39_iia.pdf
8. Liu letter 27 is about AI in inspections, as the map says: it
   discusses "the potential use of AI and automation" in the Board's
   inspection approach and its deterrence effects. (Section 3)
   https://assets.pcaobus.org/pcaob-dev/docs/default-source/about/administration/strategic-plan-comments-2026/27_liu.pdf
9. PwC letter 24 offers general support and contains no
   benchmarking-vs-LLM argument; its single "benchmark" is a firm
   using inspection information "to benchmark and improve its system
   of quality control." (Sections 2, 3)
   https://assets.pcaobus.org/pcaob-dev/docs/default-source/about/administration/strategic-plan-comments-2026/24_pwc.pdf
10. The COSO guidance exists, titled "Achieving Effective Internal
    Control Over Generative AI (GenAI)", linked from
    coso.org/generative-ai. Author block prints, verbatim: David A.
    Wood, Brigham Young University, davidwood@byu.edu; Marc Eulerich,
    University of Duisburg-Essen, marc.eulerich@uni-due.de; Scott
    Emett, Arizona State University, scottemett@asu.edu; Jason
    Guthrie (asterisked), Ernst & Young Global Limited,
    jason.guthrie@ey.com; Jason Pikoos, Meta Platforms Inc.,
    jpikoos@meta.com. The block prints no job titles and no
    locations. Guthrie's asterisk footnote states the views are his
    own. (Section 1)
    https://www.coso.org/_files/ugd/719ba0_08f358f2c8f946fa9d26bd51d37b7117.pdf
11. Eulerich is Chair of Internal Auditing and currently Dean of the
    Mercator School of Management, University of Duisburg-Essen; the
    uni-due.de email domain and personal site eulerich.com check out.
    (Section 1)
    https://www.msm.uni-due.de/en/faculty-management/deanships-office/marc-eulerich/
    Note: UDE person directory lists marc.eulerich@uni-due.de.
12. The International Conference on Auditing and Artificial
    Intelligence is organized by MAARC (Mercator Audit & Artificial
    Intelligence Research Center) at the University of Duisburg-Essen
    and held in Duisburg, as the map says. (Section 1)
    https://www.uni-due.de/2025-08-13-internationale-konferenz-zu-ki-und-auditing
    Note: the uni-ulm.de page the map cites is Ulm University's own
    news report about attending; it itself names MAARC as organizer.
13. Emett is an Associate Professor at Arizona State University; the
    ASU directory prints "Associate Professor, School of Accountancy"
    and his bio ties him to the W. P. Carey School of Business.
    (Section 1) https://search.asu.edu/profile/3008917
14. Map-cited paper confirmed on the publisher page: "Leveraging
    ChatGPT for Enhancing the Internal Audit Process", Accounting
    Horizons (2025) 39 (2): 125-135 (publisher prints an en dash in
    the page range). (Section 1)
    https://publications.aaahq.org/accounting-horizons/article/39/2/125/12864/Leveraging-ChatGPT-for-Enhancing-the-Internal
15. Wood has 2025 AI-and-internal-audit work with resolvable DOIs:
    Eulerich and Wood, "A Demonstration of How ChatGPT and Generative
    AI Can be Used in the Internal Auditing Process", JETA (2025)
    22 (2): 47-77, DOI 10.2308/JETA-2023-041 (published 2025-04-25).
    (Section 1)
    https://publications.aaahq.org/jeta/article/22/2/47/13595/A-Demonstration-of-How-ChatGPT-and-Generative-AI
16. Further Eulerich 2025 AI internal-controls paper with DOI:
    Eulerich, Bamberg, Bonrath, Kordes, Wagener, on Deutsche
    Telekom's AI-supported internal control system, DOI
    10.2308/JETA-2023-054 (published 2025-06-26). (Section 1)
    https://doi.org/10.2308/JETA-2023-054
17. Guthrie's EY bio confirms he "leads the digital audit standards,
    methodology and enablement activities in the Americas" and is
    "responsible for the internal certification of new software audit
    tools" in the US. (Section 1)
    https://www.ey.com/en_us/people/jason-guthrie
18. Guthrie served on the PCAOB Data and Technology Task Force: the
    roster in footnote 7 of Board Member Kara M. Stein's June 26,
    2023 remarks on pcaobus.org lists "Jason Guthrie, Managing
    Director, Ernst & Young LLP". (Section 1)
    https://pcaobus.org/news-events/speeches/speech-detail/algorithms-audits-and-the-auditor
19. Guthrie is named in the AICPA Guide to Audit Data Analytics
    Recognition section under the Audit Data Analytics Working Group
    (AICPA publication, hosted in the AICPA Historical Collection at
    University of Mississippi eGrove). (Section 1)
    https://egrove.olemiss.edu/cgi/viewcontent.cgi?article=2737&context=aicpa_guides
20. WCARS: the 69th ran November 7-8, 2025 at Rutgers Business
    School, Newark, NJ; this supplies the year the map's "Nov 7-8"
    lacked. (Section 4) https://raw.rutgers.edu/69wcars.html
21. WCARS: the next symposium after the fetch date is the 73rd,
    Durham, England, September 16-17, 2026; also announced on the
    same pages: 74th, Chengdu, China, October 17, 2026; 75th, Newark,
    NJ, November 6-7, 2026. (Section 4)
    https://raw.rutgers.edu/73wcars.html
    Note: WCARS numbering on raw.rutgers.edu does not track
    chronology; the 76th (Duisburg) ran before the 73rd through 75th.
22. WCARS: a call for papers is open now for the 75th (Newark,
    November 6-7, 2026), submission deadline September 30, 2026.
    Who may submit, verbatim from the call: "We welcome submissions
    from practitioners, academics, and regulators." Its opening line
    also invites papers, case studies, and presentation proposals.
    (Section 4)
    https://raw.rutgers.edu/75wcars/75th_WCARS_callforpaper.pdf
23. Kognitos post "What Your SOX Auditor Will Ask About Your AI
    Automation" published May 15, 2026 (byline "Kognitos May 15,
    2026 12 min read"); full on-page title adds "(and How to Answer
    It)". Its table "Probabilistic AI vs. deterministic AI, from a
    SOX auditor's perspective" carries the verbatim row "AS 2201
    benchmarking | Difficult, logic changes with each model version"
    against the deterministic column, and question 9 closes: "'We use
    the latest version of GPT' is not a satisfactory answer." A grep
    of the full text finds zero citations of B28 through B33 and no
    "Appendix" or paragraph citations; "2201" appears 10 times, only
    ever as the standard's name. The map's read that it is adjacent,
    not an exact match, holds. (Section 2)
    https://www.kognitos.com/blog/sox-auditor-questions-ai-automation/
24. Finrep "SOX 404 Compliance Checklist for AI-Assisted Controls
    (2026)" is dated Tue Jul 07 2026, by Gana Misra, CEO. Step 6
    opens: "When an AI vendor updates the underlying model mid-year,
    does that trigger a change-in-control event requiring
    re-testing?" and answers, verbatim: "No regulator has answered
    this question directly." (Section 2)
    https://www.finrep.ai/blog/sox-404-compliance-checklist-for-ai-assisted-controls-2026
25. EisnerAmper's COSO GenAI summary is published May 13, 2026
    (inside the map's "~May 2026"), authors Mohammad Khan and
    R. Charles Waring. Verbatim bullet: "Models, prompts, and
    underlying data can change frequently, sometimes without notice
    from a vendor, making annual review cycles insufficient." The
    map's paraphrase drops "underlying"; otherwise word for word.
    (Section 2)
    https://www.eisneramper.com/insights/artificial-intelligence-insights/coso-ai-governance-internal-control-framework-0526/
26. arXiv:2602.11083 is "Token-Efficient Change Detection in LLM
    APIs" (map title exact); authors on the abs page: Timothee
    Chauvin, Clement Lalanne, Erwan Le Merrer, Jean-Michel Loubes,
    Francois Taiani, Gilles Tredan (accented spellings in the
    original). The abstract, unreadable to the map's run, is now
    recorded in the session transcript and available on the abs
    page. (Section 5) https://arxiv.org/abs/2602.11083
27. arXiv:2605.15377 is "Ensemble Monitoring for AI Control: Diverse
    Signals Outweigh More Compute" (map title exact); authors:
    Eugene Koran, Yejun Yun, Samantha Tetef, Benjamin Arnav, Pablo
    Bernabeu-Perez (accent in original). Abstract now readable on
    the v1 abs page. (Section 5) https://arxiv.org/abs/2605.15377v1
28. arXiv:2511.07585 maps LLM output drift to financial-workflow
    auditability, as the map says; a grep of the full paper finds
    zero occurrences of "PCAOB", consistent with the map's "not
    PCAOB" framing. (Section 5) https://arxiv.org/abs/2511.07585v1
29. The SEC posted the SOX Group positions on March 16, 2026:
    Supervisory General Attorney (usajobs.gov job 861178200) and
    Supervisory Trial Counsel (job 861204200), Division of
    Enforcement. The remit sentence the map carried from the Foley
    summary matches the primary posting verbatim: "The SOX Group
    will investigate and litigate matters involving potential
    violations of auditing and related professional standards..."
    (first sentence of the Duties section, Announcement
    26-EX-12903718-MJB). The map's own caution that this was a
    job-posting authorization, not a press release, is consistent
    with what exists on the primary record. (Section 3)
    https://www.usajobs.gov/job/861178200
30. The FRC published "Generative and Agentic AI Guidance" plus a
    factsheet on 30 March 2026; its news release describes guidance
    for audit firms on generative and agentic AI in audit
    engagements, and the Babington quote in the map matches the
    release verbatim, ellipsis included, attributed to "Mark
    Babington, Executive Director of Regulatory Standards".
    (Section 3)
    https://www.frc.org.uk/news-and-events/news/2026/03/innovative-new-guidance-supports-audit-firm-adoption-of-emerging-ai-technologies/
31. PCAOB Spotlight "Staff Priorities for 2025 Inspections"
    (December 2024) says, verbatim: "We will continue to be alert
    broadly for public companies that disclose significant
    investment in AI and will continue to evaluate the audit
    procedures over information technology general controls and
    other related controls..." (Use of Technology by Public
    Companies section). The map's paraphrase is accurate.
    (Section 3)
    https://assets.pcaobus.org/pcaob-dev/docs/default-source/documents/2025-priorities-spotlight_v3.pdf
32. No "Staff Priorities for 2026 Inspections" or other 2026
    inspection-priorities document exists on pcaobus.org as of
    2026-09-13: the Staff Publications index lists no such item
    under 2026. This confirms the map's caution that the vendor-blog
    "2026" attribution is imprecise and the December 2024 Spotlight
    is the verifiable source. (Section 3)
    https://pcaobus.org/resources/staff-publications
33. The draft 2026-2030 strategic plan went out July 20, 2026
    (Release No. 2026-006) for a further comment round with deadline
    September 4, 2026. AI language in the draft, verbatim (Objective
    1.2): "We also intend to assess whether additional guidance is
    needed to address the use of AI and other emerging technologies
    used in financial reporting and the audit process." The map's
    "71 comment letters informed the draft plan" matches the docket
    count. (Section 3)
    https://pcaobus.org/news-events/news-releases/news-release-detail/pcaob-advances-strategic-planning-process-with-request-for-comment-on-draft-2026-2030-goals-and-objectives
34. KPMG's FRV piece is the Defining Issues PDF "COSO releases GenAI
    roadmap", cover-dated May 1, 2026; the map's "~May 1, 2026"
    guess, flagged unverified, is exactly right. (Section 2, gaps)
    https://kpmg.com/kpmg-us/content/dam/kpmg/frv/pdf/2026/coso-releases-gen-ai-roadmap.pdf
35. The IIA webinar on the COSO guidance exists on theiia.org:
    "Achieving Effective Internal Control Over Generative AI:
    Applying COSO's New Guidance", labeled "Archived Webinar |
    May 7, 2026". (Section 2, gaps)
    https://www.theiia.org/en/content/videos/webinar/2026/achieving-effective-internal-control-over-generative-ai-applying-cosos-new-guidance/
36. Deloitte Heads Up title and date confirmed from the public DART
    landing page, no gate bypass attempted: "COSO Releases
    Publication on Internal Controls Related to Generative AI
    (April 3, 2026)". (Section 2)
    https://dart.deloitte.com/USDART/home/publications/deloitte/heads-up/2026/coso-internal-controls-generative-ai

## CORRECTED

Each row: the claim as stated in the map; the corrected claim; source
URL. Fetch date for every row: 2026-09-13.

1. Map: Pikoos "Listed as Meta (Mega Platforms, Inc., Menlo Park) in
   the journal author block." Corrected: the COSO PDF author block
   prints exactly "Jason Pikoos", "Meta Platforms Inc.",
   "jpikoos@meta.com". No "Mega", no comma before "Inc.", no "Menlo
   Park", no parenthetical, no title. Identical in three independent
   extractions of the PDF. (Section 1)
   https://www.coso.org/_files/ugd/719ba0_08f358f2c8f946fa9d26bd51d37b7117.pdf
2. Map: Pikoos has the "least public professional footprint of the
   five; no institutional research page" and "no obvious channel".
   Corrected in part: no institutional research page, SSRN page, or
   Scholar profile exists, but public professional channels beyond
   the printed email do: an FEI event speaker bio opening "Jason
   Pikoos is the Director of Modern Finance at Meta." and an AAA 2026
   AIS/SET Midyear Meeting speakers page. (Section 1)
   https://my.financialexecutives.org/Events/Calendar-Of-Events/Meeting-Home-Page?meetingid=%7BA676F9FD-6A7C-F111-AB0F-6045BD074963%7D
3. Map: Wood is "Glenn D. Ardis Professor of Accounting, BYU Marriott
   School." Corrected wording per the BYU directory: "Glenn D. Ardis
   Professor, School of Accountancy" (BYU Marriott School of
   Business). Substance right, printed wording differs. (Section 1)
   https://marriott.byu.edu/directory/details?id=1076
4. Map: Wood's "public email davidwood@byu.edu appears on his own bio
   pages and he explicitly invites contact." Corrected: the email is
   confirmed (his BYU vita page prints "Email: davidwood@byu.edu"),
   but no invitation-to-contact wording appears on his BYU pages; the
   directory gates contact details behind human verification.
   (Section 1)
   https://marriott.byu.edu/directory/details/vita?id=1076
5. Map: conference "2nd edition Aug 21-22, 2025". Corrected: the 2nd
   International Conference on Auditing and Artificial Intelligence
   took place August 20-22, 2025 at the University of Duisburg-Essen,
   Campus Duisburg. (Section 1)
   https://www.conftool.com/ai-auditing2025/about.php
6. Map (Sections 1, 4, gaps): "a 3rd was referenced" and action item
   2 says to check the 3rd-conference CFP date as a pitch target.
   Corrected, and this changes the plan: the 3rd edition has already
   happened. It ran September 2-4, 2026 in Duisburg; the submission
   deadline was July 1, 2026 and no call for contributions is open
   as of 2026-09-13. A pitch now targets a 4th edition, none yet
   announced. (Sections 1, 4)
   https://www.maarc.msm.uni-due.de/ai-conference/3rd-international-conference-on-auditing-and-artificial-intelligence-2026/
7. Map: Guthrie's title "Partner, Americas Professional Practice -
   Auditing". Corrected per his EY people page: "Partner,
   Professional Practice - Audit, Ernst & Young LLP" (the Americas
   scope appears in the bio's role description, not the title;
   Partner rank confirmed; the map's note that earlier materials say
   Managing Director also checks out on pcaobus.org). (Section 1)
   https://www.ey.com/en_us/people/jason-guthrie
8. Map: Emett paper "The Development of a Generative AI Governance
   Framework (Accounting Horizons 2026, DOI
   10.2308/HORIZONS-2025-056)". Corrected title as the publisher
   states it: "The Development of a Generative Artificial
   Intelligence (AI) Governance Framework"; DOI and journal and 2026
   confirmed; the DOI page shows no volume, issue, or page numbers
   yet (online article not yet in an issue). Authors: Scott A.
   Emett, Marc Eulerich, Jason Pikoos, David A. Wood. (Section 1)
   https://doi.org/10.2308/horizons-2025-056
9. Map: "The 69th WCARS ran Nov 7-8" as the most recent symposium.
   Corrected: the 69th ran November 7-8, 2025, and it is no longer
   the most recent; the 76th WCARS ran September 2-4, 2026 in
   Duisburg, Germany (co-located with the MAARC conference dates and
   venue). (Section 4) https://raw.rutgers.edu/wcars
10. Map: WCARS "selected papers considered for a JETA special
    section." Corrected: no standing JETA special-section
    arrangement is stated on raw.rutgers.edu; the one JETA
    arrangement found is in the 67th WCARS Call for Abstracts, which
    welcomes accepted papers to submit to JETA. (Section 4)
    https://raw.rutgers.edu/67wcars/Call%20for%20Abstracts.pdf
11. Map: SOX Group positions "closing April 3, 2026". Corrected:
    April 3, 2026 is the closing date of the Supervisory General
    Attorney posting only; the Supervisory Trial Counsel posting
    shows open 03/16/2026 to 03/27/2026. (Section 3)
    https://www.usajobs.gov/job/861204200
12. Map: the IBM drift paper is titled "LLM Output Drift".
    Corrected: that is a truncation; the full title on the abs page
    is "LLM Output Drift: Cross-Provider Validation & Mitigation for
    Financial Workflows". (Section 5)
    https://arxiv.org/abs/2511.07585v1

## UNVERIFIABLE

Each row: claim; what was tried; why it failed. Attempt date for every
row: 2026-09-13.

1. Content of comment letter 33 (The FINRA Small Firm Advisory
   Committee, dated May 14, 2026 per the docket). Tried: some
   fourteen slug guesses against the assets.pcaobus.org naming
   pattern, Exa and WebSearch queries on the author and path, and
   the Wayback CDX index of the strategic-plan-comments-2026 prefix
   (which holds only two letter PDFs). Failed because the docket
   page's PDF links do not survive text extraction and the letter's
   filename slug is not derivable. The letter's existence, author,
   and date are confirmed from the docket listing itself; its
   keyword census is the one gap in the 71-letter table.
2. Kognitos post "updated June 26, 2026". Tried: full-page fetch
   (shows only "May 15, 2026"), the site's sitemap files. Failed:
   no updated date is printed anywhere on the page and the sitemap
   was not retrievable. Publication date stands confirmed.
3. A printed publication date for the COSO GenAI PDF. Tried:
   full-text search of the extracted PDF. Failed: the PDF prints no
   month or day; the only date is "Copyright (c) 2026". The release
   was announced 2026-02-23 via COSO's press release distributed on
   PR Newswire, which is a distribution channel rather than the
   document itself.
4. An SSRN page, Google Scholar profile, or personal site for Jason
   Pikoos. Tried: WebSearch restricted to ssrn.com,
   papers.ssrn.com, scholar.google.com; open Exa searches excluding
   LinkedIn. Failed: nothing exists under his name (the only Pikoos
   Scholar profile is an unrelated researcher).
5. Ryan Wolfe highlighting the SOX Group at SEC Speaks, March
   19-20, 2026. Tried: sec.gov-restricted searches for SOX Group
   speeches and the SEC Speaks 2026 events page. Failed: sec.gov
   publishes no transcript or statement making the link; the
   conference dates themselves are primary-confirmed. The claim
   rests on consistent secondary accounts only. (Section 3)
   https://www.sec.gov/newsroom/meetings-events/sec-speaks-2026
6. The FRC guidance is "60 pages". Tried: the FRC news release, the
   FRC library page (states only "PDF, 583.2 KB"), the factsheet;
   a direct PDF download for a page count is blocked by this
   session's egress policy. Failed: no primary statement of page
   count. Secondary sources are consistent with 60 pages but do not
   verify it. (Section 3)
7. "Five themes in the letters included technology and AI." Tried:
   the July 20, 2026 news release, Release No. 2026-006, and the
   board members' statements on pcaobus.org. Failed: the five-theme
   count appears only in secondary reporting (Thomson Reuters,
   Jul. 21, 2026); no primary PCAOB document states it. The
   technology-and-AI substance is separately confirmed in the draft
   plan text (CONFIRMED row 33). (Section 3)
8. Deloitte Heads Up national-office contacts beyond Amy Steele
   (Donahue, Hittner, Kovesdy, Lindsey). Not attempted beyond the
   public landing page: the handoff forbids bypassing the DART
   gate. Remains the gap the map flagged. (Section 2, gaps)

## RFC LETTER CENSUS

Map section for every row in this census: Section 3 (and Section 2
for the PwC row). Handoff item 2.

Enumeration. Docket page (fetched 2026-09-13):
https://pcaobus.org/about/strategic-plan-budget/public-comments-on-pcaob-strategic-priorities
71 letters, numbered 1 to 71, no gaps. 70 of 71 fetched and censused
(68 clean, 2 partial: letter 25's two-page cover sheet plus paper
body extracted with some scrambling, letter 47's Question 3 response
scrambled in extraction); 1 not retrievable (letter 33, see
UNVERIFIABLE row 1). Letter 36 was recovered in the main session
after the range worker could not locate its slug (36_rac.pdf).

Counting rules. Case-insensitive substring for every term except
"LLM", which was matched case-sensitively (catching "LLMs"); an
occurrence inside a longer phrase counts under every term it
contains. All counts computed by script; an independent recount in
the main session reproduced all 630 term-count cells, with ligature
normalization checked (letter 55's PDF renders "ti" and "tt" as
single glyphs; normalization changes zero cells).

Corpus totals across the 70 fetched letters (occurrences / letters
with at least one):

  benchmark: 71 / 11
  automated control: 0 / 0
  automated application control: 0 / 0
  model version: 0 / 0
  change management: 4 / 4
  continuous monitoring: 5 / 5
  generative AI: 11 / 9
  LLM: 2 / 2
  large language model: 4 / 4

Of the 71 "benchmark" occurrences, 56 are in letter 25 (a University
of Mannheim academic paper submitted as a comment, where
"benchmark" is the economics-model usage); none of the 71 refers to
AS 2201 Appendix B benchmarking of automated controls.

The question. Does any letter argue, or come close to arguing, that
AS 2201 benchmarking cannot apply to vendor-hosted AI or LLM
controls? Answer: No. No letter cites Appendix B of AS 2201,
paragraphs B28 to B33, the benchmarking strategy, or the
unchanged-baseline and compilation-date mechanics at all (script
grep across all 70 fetched letters; the three "Appendix B" hits,
letters 44, 56, 59, all mean the AICPA appendix on GAAS-ISA
differences). What exists is scattered premises of the argument,
never assembled. The full argument is unclaimed territory in this
comment file.

Three closest, ranked by distance:

1. Letter 45, Deloitte & Touche LLP. Distance: adjacent. The
   sentence that makes it close: "For example, unique risks may be
   introduced when issuers embed AI into internal control over
   financial reporting, i.e., as they move from manual or automated
   deterministic controls to AI-based probabilistic controls." It
   also says auditors may need to "review governance over model
   changes". This is the sharpest premise of the thesis on the
   issuer side, but it never connects to AS 2201 benchmarking or
   unchanged-baseline reliance.
2. Letter 13, Jake Sigler, Ph.D., Xavier University. Distance:
   adjacent. The sentence: "In AI-enabled settings, auditors face
   specific risks that are not fully addressed by existing
   procedures, including model risk, non-deterministic outputs,
   data lineage breaks, and the potential for system-generated
   outputs to misrepresent underlying economic activity." Supplies
   the technical premise (drift, non-reproducibility) but frames it
   as evidence reliability under AS 1105/2110/2301, not control
   reliance.
3. Letter 24, PricewaterhouseCoopers LLP. Distance: tangential. The
   sentence: "The use of service organizations continues to grow,
   as does those organizations' use of AI, which may warrant PCAOB
   consideration of how auditors evaluate service auditor's reports
   in an audit, as well as wider stakeholder discussion about the
   nature, scope, and oversight of those attestation engagements."
   The only letter to pair vendor-hosted AI on the issuer side with
   third-party control assurance, but it asks for AS 2601 work and
   discussion, with no benchmarking or baseline content.

Near miss worth recording: letter 30 (Agentic CPA Inc.) is the only
letter to name AS 2201 in an AI context, saying AI-enabled audit
execution affects "the nature, timing, extent, population coverage,
and control-reliance strategy of audit procedures" with AS 2201
applicable "where applicable". The range reader scored it very
close; the ranking pass placed it below the three above because its
AI is the auditor's own tooling, not issuer AI-based controls, and
its direction is reduced control reliance, not benchmarking
inapplicability. Recorded here so the judgment call is visible.

Docket date anomalies, as printed: letter 69 (Committee on Capital
Markets Regulation) is dated Feb. 26, 2026, before the RFC issuance
date of Mar. 31, 2026; letters 67, 68, 70, 71 are dated after the
May 15, 2026 deadline (May 18, May 21, Jun. 22, Jun. 23).

Per-letter census. PDF base URL:
https://assets.pcaobus.org/pcaob-dev/docs/default-source/about/
administration/strategic-plan-comments-2026/ (filename given per
letter; all fetched 2026-09-13).

Letters with at least one occurrence of a census term (20):

Letter 2: Arun Kumar, FCA, Chartered Accountant (ICAI)
  File: 2_ak.pdf  Status: ok
  continuous monitoring: 1
    - "audit ecosystem through audit data integration and continuous
    monitoring, rather than episodic inspections"
  Closeness to the B28-B33 argument: tangential. Continuous monitoring here
  means PCAOB real-time inspection of firms, not reliance on an automated-
  control baseline; no AI, AS 2201, or control-change content.

Letter 6: ICR Inc.
  Author: Gabriel Hasson, Global Head of Governance & Activism Advisory
  File: 6_gh.pdf  Status: ok
  benchmark: 1
    - "More structured trend analysis, clearer benchmarking across firms,
    and a more direct linkage"
  Closeness to the B28-B33 argument: tangential. Mentions AI, data
  analytics, and automated tools in audit execution, but its 'benchmarking'
  is cross-firm inspection comparison; nothing on control-change or baseline
  reliance.

Letter 13: Jake Sigler, Ph.D., Assistant Professor of Accounting, Xavier
  University
  File: 13_js.pdf  Status: ok
  benchmark: 1
    - "to source data and known benchmarks; perform reasonableness checks
    against external"
  change management: 1
    - "« Evaluate completeness and representativeness change management
    limitations and judgment consistency in reporting"
  generative AI: 1
    - "across runs, increasing detection risk Generative AI produces
    different exception lists across repeated"
  Closeness to the B28-B33 argument: adjacent. Argues model drift, non-
  deterministic/non-reproducible AI outputs, and change controls undermine
  reliance on system-generated evidence, which bears directly on baseline
  reliance; but its lone AS 2201 mention is only in a list of
  specialist/internal-control standards re IT-auditor roles, never Appendix
  B benchmarking or unchanged-baseline reliance. Closest letter in this
  batch.

Letter 14: Rechtman CPA PLLC
  Author: Yigal M. Rechtman, CPA, CFE, CITP, CISM, Managing Partner
  File: 14_rechtman.pdf  Status: ok
  large language model: 1
    - "privately held AI databases and large language models, in addition to
    publicly filed"
  Closeness to the B28-B33 argument: tangential. Discusses AI/LLM training
  bias and AI augmenting judgment, plus auditor independence; nothing on
  benchmarking, control change, or baseline reliance.

Letter 15: Center for Audit Quality
  Author: Dennis J. McGowan, CPA, Vice President, Professional Practice
  File: 15_caq.pdf  Status: ok
  generative AI: 1
    - "Achieving Effective Internal Control Over Generative AI and the GAO’s
    Artificial Intelligence: An"
  Closeness to the B28-B33 argument: tangential. Treats AI as a fast-
  evolving area needing principles-based guidance and governance for PCAOB's
  own use; no discussion of model change, versioning, or reliance on an
  automated-control baseline.

Letter 17: Auditing Standards Committee, Auditing Section - American
  Accounting Association
  File: 17_aaa.pdf  Status: ok
  continuous monitoring: 1
    - "Research on analytics-based fraud detection and continuous monitoring
    highlights both the potential for improved"
  LLM: 1
    - "processing (NLP) and large language model (LLM) tools can efficiently
    identify themes across comment"
  large language model: 1
    - "natural language processing (NLP) and large language model (LLM)
    tools can efficiently identify themes"
  Closeness to the B28-B33 argument: tangential. Calls for AI/analytics
  standard setting and notes model-driven evidence gaps, but never touches
  benchmarking or control-change reliance.

Letter 20: ASML Netherlands B.V.
  Author: An Lommers, Corporate Chief Accountant; Nancy Mac Gillavry, Head
  of Finance
  File: 20_asml.pdf  Status: ok
  benchmark: 2
    - "of great significance o Incorporate industry-level benchmarking to
    highlight leading practices, emerging risk areas,"
    - "risks or standardized indicators o Consider benchmarking the
    auditor's identified significant audit risk areas"
  continuous monitoring: 1
    - "to complement retrospective inspections with more continuous
    monitoring approaches that provide earlier risk insights"
  Closeness to the B28-B33 argument: tangential. Benchmarking here means
  industry-level inspection comparisons and continuous monitoring refers to
  PCAOB inspections, not automated-control baselines or AI.

Letter 21: Pennsylvania Institute of CPAs
  Author: Allison M. Henry, CPA, VP Professional & Technical Standards
  File: 21_picpa.pdf  Status: ok
  continuous monitoring: 1
    - "pilot testing of innovative concepts (e.g., continuous monitoring)."
  generative AI: 1
    - "documentation of audit evidence generated through generative AI."
  Closeness to the B28-B33 argument: tangential. Wants standards updated for
  AI-driven processes and generative AI evidence, but nothing on control
  baselines or model change reliance.

Letter 24: PricewaterhouseCoopers LLP
  File: 24_pwc.pdf  Status: ok
  benchmark: 1
    - "may look to such information to benchmark and improve its system of
    quality control."
  generative AI: 3
    - "guidance grounding new concepts such as generative AI in existing
    principles-based standards, as well"
    - "publication, Achieving Effective Internal Control over Generative AI.
    The implementation of QC 1000 provides"
    - "guidance grounding new concepts such as generative AI in existing
    principles-based standards can be"
  Closeness to the B28-B33 argument: adjacent. Ties vendor-hosted AI at
  service organizations to how auditors rely on third-party control
  assurance, and flags over-reliance on AI output, but never invokes AS 2201
  benchmarking or an unchanged-baseline argument.

Letter 25: Dirk Simons; Sebastian Kronenberger; Yasmin Kuhlmann, University
  of Mannheim Business School
  File: 25_skk.pdf  Status: partial
  benchmark: 56
    - "deskilling causes audit quality to fall below the no-AI benchmark as
    standards tighten"
    - "we begin with a benchmark in which the auditor has no access to AI"
    - "In the benchmark without AI, there exists a unique welfare-maximizing
    human-effort"
    - "the benchmark eventually overtakes the AI world’s audit quality
    level"
    - "audit quality under a human-effort floor weakly exceeds the no-AI
    benchmark"
    - "audit quality under a total-effort floor lies strictly below the no-
    AI benchmark"
    - "The benchmark audit quality overtakes the AI world at an intermediate
    threshold"
    - "the deskilling region where audit quality drops below the benchmark"
    - "quality in the AI world falls below the no-AI benchmark"
    - "audit quality remains strictly above the no-AI benchmark at every
    level"
    (46 further occurrences unquoted; see fetch note)
  generative AI: 1
    - "The use of generative AI can also demotivate workers"
  large language model: 1
    - "market impact potential of large language models"
  Closeness to the B28-B33 argument: tangential. Economic model of AI use in
  audit effort standards (AS 1201 supervision); its 'benchmark' is a no-AI
  model baseline, never AS 2201 control benchmarking or control-change
  reliance.

Letter 28: Members of the IAG
  File: 28_miag.pdf  Status: ok
  benchmark: 2
    - "Stewardship: Proxy Voting Guidelines for Benchmark Policies"
    - "publication/blackrock-investment-stewardship-benchmark-guidelines-
    us.pdf"
  Closeness to the B28-B33 argument: tangential. Extensive AI oversight
  discussion (AI Task Force, AI governance in inspections, Form AP style AI
  reporting) but nothing on control baselines, benchmarking, or AS 2201
  reliance.

Letter 34: KPMG LLP
  File: 34_kpmg.pdf  Status: ok
  benchmark: 1
    - "Audit firms also may use other firms’ reports for benchmarking and
    quality management"
  Closeness to the B28-B33 argument: tangential. Raises AI in ICFR and SOC
  reports for service organizations, but never touches benchmarking,
  baselines, or control-change reliance; its lone benchmark hit is about
  firms comparing inspection reports.

Letter 38: CBIZ CPAs P.C.
  Author: Jeffrey Gluck
  File: 38_cbiz.pdf  Status: ok
  change management: 1
    - "governance, risk assessment, model/tool approval, testing/validation,
    change management, vendor management, training, and
    monitoring/remediation"
  generative AI: 1
    - "adoption of artificial intelligence, including predictive models,
    generative AI, and agentic AI"
  Closeness to the B28-B33 argument: adjacent. Its proposed AI framework
  ties model drift, change management, vendor management of third-party AI
  tools, and monitoring evidence to supporting reliance, bearing on
  baseline-reliance concerns without ever invoking AS 2201 or benchmarking.

Letter 39: The Institute of Internal Auditors
  Author: Anthony J. Pugliese, CIA, CPA, CGMA, CITP, President and CEO
  File: 39_iia.pdf  Status: ok
  benchmark: 1
    - "replacing the current subjective evaluation criteria with an
    objective, profession based benchmark"
  continuous monitoring: 1
    - "increasingly incorporating AI, automation, data analytics, and
    continuous monitoring capabilities into their work"
  Closeness to the B28-B33 argument: tangential. Its benchmark hit is an AS
  2605 competence benchmark and its continuous monitoring is internal audit
  reliance under AS 2605, not reliance on an unchanged automated control
  baseline.

Letter 47: RSM US LLP
  File: 47_rsm.pdf  Status: partial
  benchmark: 2
    - "utilized by the PCAOB for benchmarking and analysis of data.
    Technology"
    - "potential to use technology for benchmarking to identify outliers
    related to"
  generative AI: 1
    - "Achieving Effective Internal Control Over Generative AI; the IFIAR
    released a report,"
  Closeness to the B28-B33 argument: tangential. Discusses AI in audit
  performance and cites COSO's generative AI control guidance, but its
  'benchmarking' means PCAOB data analysis; nothing connects AI to AS 2201
  benchmarking or baseline reliance on unchanged controls.

Letter 51: Illinois CPA Society
  Author: Jon Roberts, CPA, Chair; Erik De Vries, CPA, Vice Chair, Audit and
  Assurance Services Committee
  File: 51_icpasa-a.pdf  Status: ok
  LLM: 1
    - "than any common Large Language Models (LLMs), which may not have been
    trained on"
  large language model: 1
    - "systems rather than any common Large Language Models (LLMs), which
    may not have been"
  Closeness to the B28-B33 argument: tangential. Distrusts common LLMs, but
  only for the PCAOB's own tooling; never touches AS 2201, benchmarking, or
  control-change reliance.

Letter 58: BDO USA, P.C.
  File: 58_bdo.pdf  Status: ok
  generative AI: 1
    - "PCAOB staff outreach confirms that generative AI is already being
    explored both"
  Closeness to the B28-B33 argument: tangential. Asks PCAOB to clarify when
  AI-enabled and application controls give sufficient evidence, and flags
  consistency and third-party model risks, but never discusses control
  change, versioning, or baseline reliance.

Letter 59: Grant Thornton LLP
  File: 59_gt.pdf  Status: ok
  change management: 1
    - "quality control related to methodology change management. This would
    prioritize significant methodology"
  generative AI: 1
    - "obtain audit evidence (for example, generative AI or AI-enabled
    workflows). We urge"
  Closeness to the B28-B33 argument: tangential. Wants principle-based AI
  guidance and applies unchanged-since-last-review logic only to firm audit
  methodology in inspections, never to automated controls or AI baselines.

Letter 63: Council of Institutional Investors
  Author: Jeffrey Mahoney, General Counsel
  File: 63_cii.pdf  Status: ok
  benchmark: 3
    - "Investment Stewardship: Proxy Voting Guidelines for Benchmark
    Policies"
    - "stewardship-benchmark-guidelines-us.pdf; see, e.g., Ohio Public
    Employees Retirement"
    - "Investment Stewardship: Proxy Voting Guidelines for Benchmark
    Policies"
  Closeness to the B28-B33 argument: tangential. AI discussion is general
  (ongoing evaluation of technology, an AI answer-bot for PCAOB data);
  benchmark hits are proxy-voting policy citations, nowhere near AS 2201 or
  baseline reliance.

Letter 66: American Bankers Association
  Author: Joshua Stein, VP, Accounting and Financial Management
  File: 66_aba.pdf  Status: ok
  benchmark: 1
    - "a single quantitative materiality benchmark derived from income-
    statement measures can distort judgments"
  change management: 1
    - "risk-based approach to ITGC, including change management, IT
    operations, incident response, and monitoring"
  Closeness to the B28-B33 argument: tangential. Discusses ITGC change
  management scoping, bank model-governance, and PCAOB use of AI, but never
  links AI or model change to automated-control baseline reliance or
  benchmarking.

Letters fetched with zero occurrences of every census term (50):

  1. Stuart Burgdoerfer (1_sb.pdf, ok)
  3. Gary Crittenden (3_gc.pdf, ok)
  4. Dennis R. Beresford, CPA (4_drb.pdf, ok)
  5. Jathin Bandari, M.D. (5_jb.pdf, ok)
  7. RiskGraphs (7_an.pdf, ok)
  8. St. Bernard Financial Services, Inc. (8_rk.pdf, ok)
  9. S&P Global (9_s-p.pdf, ok)
  10. Schroders Investment Management (10_sim.pdf, ok)
  11. R.G. Associates, Inc. (11_rga.pdf, ok)
  12. Cherry Bekaert LLP (12_cherrybekaert.pdf, ok)
  16. Members of the Audit Committee Council (16_acc.pdf, ok)
  18. Texas Society of Certified Public Accountants (18_txcpa.pdf, ok)
  19. Auditchain Labs AG (19_auditchain.pdf, ok)
  22. XBRL US (22_xbrl.pdf, ok)
  23. International Corporate Governance Network (ICGN) (23_icgn.pdf, ok)
  26. U.S. Federal Housing (FHFA) (26_fhfa.pdf, ok)
  27. Lisa Yao Liu, Assistant Professor, Accounting Division, Columbia
  Business School (27_liu.pdf, ok)
  29. MindBridge Inc. (29_mindbridge.pdf, ok)
  30. Agentic CPA Inc. (30_agentic.pdf, ok)
  31. Sarah M. Madris (31_madris.pdf, ok)
  32. Roberta F. Brzezinski (32_rfb.pdf, ok)
  35. MNP LLP (35_mnp.pdf, ok)
  36. Robert A. Conway (36_rac.pdf, ok)
  37. CPA Club Inc. (37_cpaclub.pdf, ok)
  40. Yount, Hyde & Barbour, P.C. (40_yhb.pdf, ok)
  41. Investment Company Institute (41_ici.pdf, ok)
  42. Forvis Mazars, LLP (42_forvis-mazars.pdf, ok)
  43. Johnson Global Advisory (43_jga.pdf, ok)
  44. National Association of State Boards of Accountancy (NASBA)
  (44_nasba.pdf, ok)
  45. Deloitte & Touche LLP (45_dt.pdf, ok)
  46. Ernst & Young LLP (46_ey.pdf, ok)
  48. North American Securities Administrators Association, Inc.
  (48_nasaa.pdf, ok)
  49. United States Senate Committee on Banking, Housing, and Urban Affairs
  (49_senatorwarren.pdf, ok)
  50. Better Markets, Inc. (50_bettermarkets.pdf, ok)
  52. Tapestry Networks, Inc. (52_tapestrynetworks.pdf, ok)
  53. Eldar Maksymov, Professor of Accounting, Arizona State University, et
  al. (53_aa.pdf, ok)
  54. Crowe LLP (54_crowe.pdf, ok)
  55. U.S. Chamber of Commerce, Center for Capital Markets Competitiveness
  (55_ccmc.pdf, ok)
  56. AICPA (56_asb.pdf, ok)
  57. Financial Executives International, Committee on Corporate Reporting
  (57_fei.pdf, ok)
  60. Cerex Advisory (60_cerex.pdf, ok)
  61. California State Teachers Retirement System (61_calstrs.pdf, ok)
  62. Americans for Financial Reform Education Fund, et al. (62_afref.pdf,
  ok)
  64. Lark Research (64_percoco.pdf, ok)
  65. Baker Tilly US, LLP (65_bakertilly.pdf, ok)
  67. CohnReznick LLP (67_cohnreznick.pdf, ok)
  68. International Bancshares Corporation (68_ibc.pdf, ok)
  69. Committee on Capital Markets Regulation (69_ccmr.pdf, ok)
  70. Sanville & Company, LLC (70_sanville.pdf, ok)
  71. American Bar Association, Business Law Section (71_aba.pdf, ok)

  Not fetched: letter 33, The FINRA Small Firm Advisory Committee, dated per
  docket. Direct PDF URL could not be determined; the url given is the PCAOB
  docket listing page (fetched 2026-09-13), which confirms Letter 33, author
  The FINRA Small Firm Advisory Committee, dated May 14, 2026, but the Exa-
  rendered page strips the (PDF) hyperlinks. Slug guesses all returned
  CRAWL_NOT_FOUND (HTTP 404) from mcp__Exa__web_fetch_exa on 2026-09-13
  under https://assets.pcaobus.org/pcaob-dev/docs/default-
  source/about/administration/strategic-plan-comments-2026/ : 33_finra.pdf,
  33_sfac.pdf, 33_finrasfac.pdf, 33_finra-sfac.pdf, 33_smallfirm.pdf,
  33_finrasmallfirmadvisorycommittee.pdf, 33_smallfirmadvisorycommittee.pdf,
  33_finra-small-firm-advisory-committee.pdf, 33_fsfac.pdf,
  33_finracommittee.pdf, 33_sfacfinra.pdf,
  33_thefinrasmallfirmadvisorycommittee.pdf, 33-finra.pdf,
  33_finra_sfac.pdf, 33_smallfirms.pdf, 33_sfac2026.pdf, 33_finrasf.pdf,
  33_smallfirmac.pdf, 33_finrasmallfirmcommittee.pdf, 33_finraslfac.pdf,
  plus number-offset probes 31_finra.pdf, 32_finra.pdf, 34_finra.pdf.
  Control test: a known-good file in the same folder (12_cherrybekaert.pdf,
  including with a cache-busting query param) live-crawled fine, so the 404s
  are genuine, and a wrong sfvrsn value on a working file still fetched, so
  the missing sfvrsn is not the cause. Searches found no copy:
  WebSearch/Google site:assets.pcaobus.org queries, Exa searches on author
  and content, Bing exact-path search for "strategic-plan-comments-2026/33_"
  (zero pages contain that path), finra.org search and FINRA weekly archives
  (no link), Wayback/availability/CDX and Common Crawl index (no captures or
  timeouts through the Exa fetcher; direct curl blocked by egress proxy
  403). LinkedIn was not used per instructions.