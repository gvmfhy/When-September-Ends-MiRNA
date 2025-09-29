Austin Morrissey

Aug 5 2025

This document outlines the opportunity, requirements, and execution plan
for a microRNA-based forensic assay. Its purpose is to help the team
align on four critical fronts: (1) the scientific landscape we're
operating in, (2) the legal constraints we must overcome, (3) the market
conditions that determine scale, and (4) the cost, timeline, and data
needed to reach admissibility in court.

.

## Key Questions This Document Aims to Answer

1.  **Technical**: Can microRNA reliably identify body fluids where
    current methods fail?

2.  **Legal**: What validation will courts require, and how long will it
    take?

3.  **Financial**: Is there a venture-scale opportunity here, or should
    we pursue alternative funding?

4.  **Strategic**: Should we position as a replacement or complement to
    existing tests?

5.  **Practical**: What will it actually cost and how long will it take
    to bring this to market?

**Section 1: Background of the problem space**

**Current Forensic Evidence Collection**

When a forensic team arrives at a crime scene, their first priority is
creating an unbroken record of every sample that might reach a
courtroom. This written log, known as the [chain of custody]{.mark},
documents who collected each piece of evidence, records the time of each
transfer and tracks where each item travels throughout the investigative
process. Courts require this continuous documentation to ensure no
tampering or contamination occurred before testing begins. Likewise, any
software we develop with our assay will need to keep this in mind.

Once the scene is properly documented, investigators open sterile
evidence collection kits. These contain swabs designed to absorb
biological samples, along with disposable scissors that are used to cut
pieces of stained fabric, such as bloodied jeans. The challenge facing
investigators is that biological materials degrade rapidly under
real-world conditions. Messenger RNA, for instance, breaks down within
hours at room temperature, making immediate preservation critical for
successful analysis.

![Forensic Evidence Collection
Process](media/image1.png){width="2.622807305336833in"
height="3.933755468066492in"} ![Biological Sample Transfer and Lysis
Mechanism](media/image2.png){width="2.6204669728783903in"
height="3.9307010061242345in"}

Cold-chain shipping provides the ideal solution for sample preservation
but is a formidable logistic challenge at crime scenes. Refrigerated
sample transport is expensive, requires specialized equipment, and
moreover, is bound by a limited capacity. Even in coastal cities with
abundant resources, it is not feasible to refrigerate all samples.
Therefore, investigators must triage evidence and decide which merit
this premium handling.

To guide these decisions, officers perform [presumptive chemical
assays]{.mark} on scene. Take note of this term, as it these assays we
will either compliment or eliminate. These rapid tests indicate whether
a stain contains biomarkers associated with blood, saliva, or semen,
though they cannot provide definitive identification.

The inherent limitation of presumptive tests resembles that of
preliminary drug screening. They serve as low-confidence indicators that
suggest, but cannot prove, the presence of target substances. This
uncertainty means presumptive results alone cannot are not admissible in
court as evidence without additional laboratory confirmation.

Consider the standard blood detection method, known as the Kastle-Meyer
test, that leverages hemoglobin's peroxidase-like activity. In this
test, investigators apply reduced colorless reagent (phenolphthalein) to
a swab sample, followed by H₂O₂. If blood is present, these reagents
will oxidize the substrate and cause the swab to turn bright pink.

While this non-destructive test can detect less than a microliter of
blood, it suffers from significant false positive rates. Rust, plant
peroxidases, certain cleaning products, and oxidized copper surfaces all
produce identical color changes, necessitating DNA analysis before any
sample can serve as courtroom evidence.

![Presumptive Blood Test
Kit](media/image3.jpeg){width="2.188888888888889in"
height="1.6423611111111112in"}Saliva detection relies on α-amylase, an
enzyme present in saliva at concentrations several thousand times higher
than in other body fluids. The Phadebas Press Test employs filter paper
embedded with dye-linked starch molecules. When saliva contacts the
paper, α-amylase cleaves the starch, releasing blue dye that creates a
visible spot within minutes. However, feces, certain foods**,** and
other amylase-containing materials can generate false positives, again
requiring laboratory verification.

**SEX-CRIME PRESUMPTIVE ASSAYS: Most relevant!**

Lastly, and of most interest to our startup, are forensics tests
relevant to semen. This has the highest social value, as there majority
of forensic backlog cases are from sexual assault evidence. There is
upward of 90,000 to 400,000 kits waiting to be tested. A rapid, reliable
assay would speed up the justice process for these victims and their
families.

The first test most U.S. laboratories run is the acid-phosphatase spot
assay. Acid phosphatase concentrations in semen are hundreds to
thousands of times higher than in other body fluids, a fact noted in
current National Institute of Justice training materials. This relevant
physiology is that the prostate epithelium secretes large quantities of
the enzyme directly into prostatic fluid**,** and in turn makes up part
the ejaculate volume. Like the Kastle--Meyer test for blood, this is a
colorimetric assay and produces a colored product.

![A document with text on it AI-generated content may be
incorrect.](media/image4.png){width="6.288194444444445in"
height="3.9659722222222222in"}A 2024 state protocol directs analysts to
"examine with an alternate light source, test areas of interest with the
Acid Phosphatase test, then decide on DNA or further work-ups". Another
2024 SOP entitled *Screening Test for Semen (Acid Phosphatase/Brentamine
Test)* describes the reaction chemistry, limitations, and report wording
and lists the AP test as purpose "to perform a screening test for the
presence of semen in forensic samples"
[[CT.gov]{.underline}](https://portal.ct.gov/dmv/-/media/despp-beta/pdf/scientific-services/sop/dna/fb/fb-12/fb-sop-12-screening-test-for-semen-2272-10.pdf).
These documents confirm that the AP spot test remains the routine,
first-pass assay because it costs only cents per swab and yields a
visible purple color in under a minute. It is **quick, cheap, and not
specific.**

Please See attached document for further info on assay workflow

![A screenshot of a document AI-generated content may be
incorrect.](media/image5.png){width="4.159722222222222in"
height="3.7180555555555554in"}Despite its speed and price, the acid
phosphatase test misses evidence in three common situations.

(1) **Low-enzyme stains**---vasectomized or severely oligospermic donors
    contribute less enzyme, so partial crime-scene swabs often fall
    below the 30-second threshold for reactivity. A comparative
    biochemical study showed activity falling in the order *normal \>
    oligospermic \> vasectomized \> azoospermic*.

(2) **Environmental decay**---heat, humidity, or laundering denature the
    enzyme and thus cause a rapid decline in activity.

(3) **Cross-reactivity**---contraceptive creams and vaginal secretions
    are common causes are false positives, reports one [state police
    forensic
    units](https://www.nj.gov/njsp/division/investigations/forensic-serology.shtml?utm_source=chatgpt.com).
    And oddly, one study out of a forensics unit in India found cross
    reactivity in amongst saliva, ear-wax, sweat and some plant juices.

**What is the 'Gold standard?' presumptive test for semen?**

To refine screening, crime labs employ two more robust assays. Take
careful note that while these assays are more robust than acid
phosphatase, [they have the same failure nodes that microRNA can
overcome.]{.mark} Moreover, both are over 25 years old. If you suspect
science has improved in the past quarter century, you should suspect
that we can develop a better technical solution.

![PPT - Forensic Biology Screening Workshop Semen PowerPoint
Presentation \...](media/image6.jpeg){width="1.788888888888889in"
height="1.3416666666666666in"}The presumptive gold-standard for semen
screening now consists of two lateral-flow strips that superseded the
old acid-phosphatase spot. The first, **ABAcard p30**, targets
prostate-specific antigen; a [[National Institute of
Justice]{.underline}](https://nij.ojp.gov/nij-hosted-online-training-courses/laboratory-orientation-and-testing-body-fluids-and-tissues/testing-body-fluids-tissues/semen/screening-and-identification-tests?utm_source=chatgpt.com)
document from June 2023 still describes it as \'the currently accepted
method of choice for identification of semen in all circumstances.\'
This kit reached the market in the late 1990s and became routine in U.S.
laboratories during the early-2000s. The second, **RSID-Semen™**,
targets semenogelin and was released in 2007.

<figure>
<img src="media/image7.png" style="width:2.79213in;height:1.11094in"
alt="A close-up of a test AI-generated content may be incorrect." />
<figcaption><p>RSID Internal study is on the left. Observe that target
analyte concentration is increasing from 1 to 9, yet peaks and falls
after sample 6.</p></figcaption>
</figure>

**How the gold standard kits work**

The two assays behave identically. They differ only in which biomarker
their antibodies recognize. They share the same architecture, which is
diagramed below. Depicted is a a sample pad, a conjugate pad, a
nitrocellulose membrane with a test line and a control line, and a final
absorbent wick. A lateral-flow semen strip contains **one mobile
antibody species and two immobilized antibody species**.

![A screenshot of a computer AI-generated content may be
incorrect.](media/image8.png){width="6.193500656167979in"
height="2.5144553805774277in"}

- **Mobile antibody + nanoparticle (conjugate-pad)**\
  *Mouse monoclonal IgG* is covalently attached to a gold nanoparticle.
  This antibody is specific for an epitope of the forensic biomarker and
  will refer to its target as **Epitope A** (PSA/semenogelin). This
  moves with the fluid front, regardless of whether the analyte is
  present.

- **Immobilized antibody #1 -- the test line**\
  A second antibody say goat or rabbit IgG that recognizes **Epitope B**
  on the same antigen, is immobilized across the nitrocellulose membrane
  at the test line. When the gold-antibody--antigen complex reaches this
  stripe, the capture antibody grabs the antigen's free epitope and
  anchors the entire complex. Thousands of gold particles accumulate,
  producing the colored test bar. Take note that the color is produced
  by accumulation of the gold nanoparticle, not by the analyte itself.

- **Immobilized antibody #2 -- the control line**\
  Farther downstream, another embedded set of antibodies is designed to
  binds the constant-region (Fc) of any gold-labeled probe that was not
  caught at the test line, proving that the conjugate was active and
  that capillary flow traversed the full strip.

Given this assay design, what do you expect would occur when there is a
high condition of target analyte? What would you observe visually on the
strip and why? Ask yourself: in capillary flow, what moves faster---a
small unbound protein or a bulky gold-antibody-protein complex?

In high analyte conditions, every antibody at the conjugate pad
saturates with antigen, leaving no free binding sites. Meanwhile, excess
free protein rushes ahead and saturates the test line. Since the gold
nanoparticle creates the visible signal---not the protein
itself---excess of the target protein blocking the binding sites at the
test line prevents sandwich formation.

**In cases with high concentrations of the sample, there is the test
line will appear blank.** This false negative in the present of high
concentrations is known as the hook effect. Other causes of false
negatives, The 2024 Connecticut p30 assay SOP flags as a cause of false
negatives---and when PSA degrades in hot, wet environments; undiluted
adult urine or breast milk can also give weak
positives.[[CT.gov]{.underline}](https://portal.ct.gov/dmv/-/media/despp-beta/pdf/scientific-services/sop/dna/fb/fb-15/fb-sop-15-ria-for-semen-2275-11.pdf)

![A pink card with black text AI-generated content may be
incorrect.](media/image9.png){width="6.5in" height="2.21875in"}

**Chemical differences, distinct false-positive profiles, shared weak
points**

Although PSA and semenogelin strips use the same lateral flow assay
design, the proteins they detect behave differently in biological
contexts, resulting in distinct assay characteristics. PSA is known to
circulate at low levels outside of semen in fluids such as breast milk,
urine, and some vaginal secretions. As a result, PSA-based tests are
expected to show broader cross-reactivity and a higher likelihood of
false positives. In contrast, semenogelin is produced exclusively in the
seminal vesicles and is believed to be specific to seminal fluid, making
it theoretically less prone to cross-reactivity with other body fluids.

In a 2024 study titled *A Comparative Analysis of Accuracy and
Sensitivity in Semen Presumptive* *Testing*, Heather Rogers tested three
commercial kits---ABAcard P30 (PSA), Seratec PSA, and RSID Semen
(semenogelin)---against a range of real-world substrates. While
PSA-based strips did produce false positives with female urine, the
**semenogelin-based RSID™ strip also returned unexpected positives.** As
Rogers writes, there were

> "...false positives occurring to some degree with all methods. RSID
> Semen, Seratec PSA, and ABAcard P30 all had issues detecting semen in
> a 1:10,000 dilution. Additionally, [RSID Semen could not detect semen
> when it was mixed with dirt.]{.mark} There was an issue of
> non-specificity with all three of the test kits with various absorbent
> hygiene products. RSID Semen, Seratec PSA, and ABAcard P30 all had
> several false positive test results with tampons, menstrual pads with
> blood, and diapers with urine samples. Additionally, ABAcard P30 had
> false positive test results with female urine samples".
>
> The below figure is from her paper.
>
> ![A graph of test results AI-generated content may be
> incorrect.](media/image10.png){width="5.266247812773403in"
> height="3.4140583989501314in"}

A second study by Melanie Chang (2011) further complicates the
specificity claims around RSID™. In testing under various extraction
conditions, she found that "RSID -- Semen gave positive results with
female urine and vaginal samples*,"* and noted that the test produced "a
false positive result with PBS and a failed test with ultrapure
autoclaved water.*"* These findings suggest that both buffer composition
and biological contaminants can interfere with RSID's reliability,
despite its intended specificity.

Taken together, these theses indicate that while PSA and semenogelin
differ in origin, neither yields a truly fluid-specific presumptive
result under field-relevant conditions. Both proteins are liable for
environmental degradation, false positives, and false negatives. This
reinforces the need for a next-generation confirmatory assay---such as
one based on tissue-specific microRNAs---that is robust to mixed
matrices, environmentally stable, and chemically agnostic to buffer
conditions.

**SUMMARY**

In summary, there are consistent limitations that persist across all
presumptive body fluid assays. They generate false positives, miss
degraded or dilute samples, and produce variable results depending on
environmental conditions and operator technique. This systematic
weakness in current methodology creates a clear market opportunity for
more reliable field-deployable technologies that can withstand
environmental stress while avoiding cross-reactivity pitfalls.

**COSTS OF THESE AFORMENTIONED ASSAYS**

  ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  Product               Tests          Price          Price per Test Source
  --------------------- -------------- -------------- -------------- --------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  **ABAcard             25 tests       \$346.80       ≈ \$13.90      ([Fisher Scientific](https://www.fishersci.com/shop/products/abacard-p30-semen-test-25t-kit-1/NC1699451?utm_source=chatgpt.com))
  P30™** (PSA)                                                       

  **Seratec PSA         40 tests       \$185.00       ≈ \$4.60       ([serological.com](https://serological.com/forensic-dna-testing/facility-items/r564-seratec-psa-semiquant-165/?utm_source=chatgpt.com))
  SemiQuant™** (PSA)                                                 

  **RSID™ Semen --      25 tests       \$267.60       ≈ \$10.70      [[(Fisher Scientific)]{.underline}](https://www.fishersci.com/shop/products/rsid-semen-kit-w-universl-buf/NC0396091?utm_source=chatgpt.com)
  Universal Buffer                                                   
  kit** (semenogelin)                                                

  RSID™ Semen Field kit 5 tests        \$95.00        ≈ \$19.00      [[(store.ifi-test.com)]{.underline}](https://store.ifi-test.com/product/fluid-id/rsid-semen-field-kit-5-packs-kit-complete-kit-for-use-in-field/?utm_source=chatgpt.com)
  (5-pack)                                                           

  **Seratec PAM™        40 tests       \$300.00       ≈ \$7.50       [[(serological.com)]{.underline}](https://serological.com/forensic-dna-testing/facility-items/r615pam/?utm_source=chatgpt.com)
  duplex** (semen +                                                  
  saliva)†                                                           
  ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

**SECTION 3: MicroRNA**

MicroRNAs (miRNAs) are short, 19-25 nt, non-coding RNA molecules that
regulate gene expression and travel through the body inside
ribonucleoprotein complexes and extracellular vesicles. These complexes
shield the molecules from nucleases, heat, and UV light, which explains
their remarkable persistence on clothing, soil, and aged evidence.
Studies that compared matched samples show miRNAs remain detectable
after conditions that erase most mRNA signals and severely fragment DNA 

**Core forensic capabilities**

MicroRNAs represent an emerging frontier in forensic science with
significant potential to enhance investigative capabilities beyond
traditional analytic method. These small, non-coding RNA molecules,
typically 19-25 nucleotides in length, offer unique advantages due to
their remarkable stability and tissue-specific expression patterns. This
includes body fluid identification and better estimates of time of death
(Post mortem interval)

For investigators, microRNA analysis dramatically enhances the ability
to reconstruct crime scenes and establish accurate narratives of events.
Consider a sexual assault investigation where multiple individuals had
consensual contact with the victim prior to the assault. Traditional DNA
analysis might identify multiple contributors but cannot distinguish
between biological fluids deposited during consensual versus
non-consensual contact. MicroRNA profiling can identify whether detected
sample originates from saliva, semen, or skin cells, allowing
investigators to differentiate between a shared drink and sexual
assault.

Different microRNAs break down at predictable, tissue-specific rates.
Some remain stable for months (miR-16), while others degrade within days
(miR-10b). By measuring the ratio of stable to unstable markers,
forensic scientists can estimate post-mortem intervals with
unprecedented precision. In cases where bodies are discovered weeks or
months after death, traditional decomposition-based timing methods often
provide only broad estimates. MicroRNA analysis can narrow these windows
significantly. For instance, in a case where a missing person\'s remains
are discovered, establishing whether death occurred shortly after
disappearance or weeks later can completely redirect an investigation,
potentially excluding or implicating suspects based on their alibis
during the refined timeframe.

Please see below relevant studies

+------------------------------+---------------------------------------+
| **Hyperlinked study**        | **Finding**                           |
+==============================+=======================================+
|   ----------------------     | Blood-specific miR-451a and miR-16    |
| ---------------------------- | stayed detectable after 90 °C heat    |
| ---------------------------- | shocks, UV irradiation, and 28 days   |
|      [**mRNA and microR      | at 80 % RH, while matched mRNAs       |
| NA stability validation of b | dropped below detection within 24 h.  |
| lood samples under different |                                       |
|      envir                   |                                       |
| onmental conditions**. Foren |                                       |
| sic Sci Int Genet 2021. *DOI |                                       |
|      10.1016/j.fsigen.       |                                       |
| 2021.102567*](https://pubmed |                                       |
| .ncbi.nlm.nih.gov/34403952/) |                                       |
|   -- -------------------     |                                       |
| ---------------------------- |                                       |
| ---------------------------- |                                       |
|                              |                                       |
|   ----------------------     |                                       |
| ---------------------------- |                                       |
| ---------------------------- |                                       |
+------------------------------+---------------------------------------+
| [**The stability and         | Six-month trial of 37 °C heat,        |
| persistence of blood and     | tropical humidity, direct sunlight,   |
| semen mRNA and miRNA targets | and machine-laundering: miRNA markers |
| for body fluid               | for blood and semen remained          |
| identification in            | amplifiable for the full 6 months;    |
| environmentally challenged   | all mRNA targets disappeared after    |
| and laundered samples**.     | ≤30 days.                             |
| Legal Medicine 2019. *PubMed |                                       |
| 30959396*](https://pubmed    |                                       |
| .ncbi.nlm.nih.gov/30959396/) |                                       |
+------------------------------+---------------------------------------+
| [**Forensic stability        | miR-451a, miR-144-3p, and miR-888-5p  |
| evaluation of selected miRNA | survived 12 weeks of freeze--thaw     |
| and mRNA markers in          | cycling, 60 °C dry heat, and outdoor  |
| blood-stained samples under  | weathering; corresponding mRNAs lost  |
| different conditions**.      | \>90 % signal.                        |
| Forensic Sci Int Genet 2024. |                                       |
| *PubMed                      |                                       |
| 39094222*](https://pubmed    |                                       |
| .ncbi.nlm.nih.gov/39094222/) |                                       |
+------------------------------+---------------------------------------+
| [**Estimation of the         | let-7e and miR-16 remained            |
| post-mortem interval using   | quantifiable in patella bone for **up |
| microRNA in the bones**. J   | to 2 years** post-mortem, providing a |
| Forensic & Legal Med 2020.   | molecular clock after extensive       |
| *DOI                         | decomposition.                        |
| 10.1016/j.jflm.              |                                       |
| 2020.102049*](https://pubmed |                                       |
| .ncbi.nlm.nih.gov/32861958/) |                                       |
+------------------------------+---------------------------------------+
| [**Distinct spectrum of      | Core fluid markers (e.g., miR-451a,   |
| microRNA expression in       | miR-888-5p) still classified samples  |
| forensically relevant body   | with \>95 % accuracy after 8 weeks of |
| fluids and probabilistic     | UV exposure and 37 °C/80 % RH         |
| discriminant approach**. Sci | incubation on porous substrates.      |
| Rep 2019. *DOI               |                                       |
| 10.1038/s41598-019-          |                                       |
| 50796-8*](https://www.nature |                                       |
| .com/articles/s41598-019-507 |                                       |
| 96-8?utm_source=chatgpt.com) |                                       |
+------------------------------+---------------------------------------+
| [**Best of both: A           | After 30 days of alternating sun/rain |
| simultaneous analysis of     | outdoor cycles, miRNA markers showed  |
| mRNA and miRNA markers for   | ≥95 % detection while mRNA signals    |
| body fluid identification**. | fell below 40 %, confirming the       |
| Forensic Sci Int Genet 2022. | benefit of hybrid panels for degraded |
| *DOI                         | evidence.                             |
| 10.1016/j.                   |                                       |
| fsigen.2022.102709*](https:/ |                                       |
| /www.sciencedirect.com/scien |                                       |
| ce/article/pii/S187249732200 |                                       |
| 0485?utm_source=chatgpt.com) |                                       |
+------------------------------+---------------------------------------+
| [**Differentiation of five   | The 18-marker panel retained ≥96 %    |
| forensically relevant body   | classification accuracy after 6 weeks |
| fluids using an 18-miRNA     | at 60 °C, 80 % RH, and continuous UV  |
| panel under environmental    | exposure.                             |
| stress**. Forensic Sci Int   |                                       |
| Genet 2024. *PubMed          |                                       |
| 39076047*](https://pubmed    |                                       |
| .ncbi.nlm.nih.gov/39076047/) |                                       |
+------------------------------+---------------------------------------+

The NIJ article *"Direct Comparison of Body Fluid Identification
Technologies"* (published Nov 21 2024) reports the first NIJ-funded
head-to-head evaluation of six body-fluid tests: two traditional
immunoassays, DNA-methylation PCR, mRNA RT-qPCR, shotgun proteomics, and
targeted proteomics.

![Figure 1. Comparison of specificity, sensitivity, and error rates of
the body fluid identification assays](media/image11.jpeg){width="6.5in"
height="2.4055555555555554in"}

**Source:** National Institute of Justice - [Direct Comparison of Body
Fluid Identification
Technologies](https://nij.ojp.gov/topics/articles/direct-comparison-body-fluid-identification-technologies)

**MARKET OPPORUTTINIY**

The U.S. forensic system is straining under the weight of a substantial
evidence-processing backlog. According to the Bureau of Justice
Statistics, publicly funded crime laboratories received approximately
3.3 million forensic service requests in 2020, yet concluded the year
with over 710,000 cases still unresolved after 30 days. [At the
BJS-reported average cost of \$620 per
case,](https://bjs.ojp.gov/document/pffcl20.pdf) this backlog represents
roughly \$440 million in stranded forensic work annually---an unmet need
that creates a natural entry point for new technology. **If a microRNA
assay were able to unlock just 10 percent of this degraded-evidence
segment, it would generate approximately \$44 million in new U.S.
billings each year.**

![Global Forensic Technology market share and size,
2022](media/image12.png){width="3.1395833333333334in"
height="2.0548611111111112in"}This opportunity sits within a growing
global market[. The forensic technology sector was valued at \$5.51
billion in 2023 and is projected to grow to \$10.65 billion by 2030,
reflecting a compound annual growth rate (CAGR) of 9.9
percent](https://www.grandviewresearch.com/industry-analysis/forensic-technology-market).
Within this market, consumable kits and reagents account for
approximately 67 percent of all revenue, underscoring a structural bias
toward recurring-purchase assay platforms over one-time instrumentation
sales. This consumables-heavy dynamic creates favorable conditions for
platforms like microRNA cartridges that drive high-margin, repeatable
sales through laboratory workflows.

Importantly, crime laboratories and public agencies have already
demonstrated a willingness to pay premium prices for tools that deliver
speed and certainty in forensic outcomes. In the case of Rapid DNA
instruments, for example, agencies such as the [Florida Sheriffs
Association have invested roughly \$250,000 per
unit](https://flsheriffs.org/blog/entry/public-safety-tip-what-you-need-to-know-about-rapid-dna/?utm_source=chatgpt.com),
with consumables priced at over \$100 per cartridge---more than ten
times the cost of standard STR reagents. Similarly, ABAcard p30 strips
for semen detection are widely adopted despite costing over ten times
more than legacy acid phosphatase tests. In both cases, the premium is
justified by either courtroom admissibility or turnaround time,
illustrating the high value placed on decisiveness and reliability in
forensic contexts. A microRNA assay priced between \$80 and \$100 per
use would occupy a commercially viable middle ground: offering novel
evidentiary capabilities at a price point aligned with existing spending
patterns.

The funding environment further supports innovation in this space. The
U.S. National Institute of Justice (NIJ) consistently allocates between
\$12 and \$14 million annually to support forensic science research and
development. [In fiscal year 2024, the NIJ awarded \$13.6 million across
24](https://nij.ojp.gov/funding/nij-awards-14m-support-forensic-science-research?utm_source=chatgpt.com)
projects focused specifically on method validation, prototype
development, and inter-laboratory studies. This funding stream can be
used to offset the cost of critical early-stage activities, including
multi-site validation studies under ISO 17025, the generation of
error-rate reference datasets required for Daubert admissibility, and
the piloting of field-ready qPCR cartridges in state laboratories**. By
leveraging NIJ support, our startup can reduce capital intensity and
significantly de-risk the pathway to courtroom acceptance.**

Downstream market validation comes from recent M&A activity. Once a
specialized forensic assay demonstrates courtroom viability and
generates recurring kit sales, it becomes a prime acquisition target for
large life sciences firms seeking to expand their footprint in forensic
genomics. [In January 2023, QIAGEN acquired Verogen---a spinout from
Illumina focused on forensic next-generation sequencing---for \$150
million in
cash](https://www.nasdaq.com/articles/qiagen-completes-acquisition-of-verogen?utm_source=chatgpt.com).
Verogen's flagship products include ForenSeq kits, which enable
simultaneous analysis of thousands of STRs and SNPs, and GEDmatch PRO, a
database used in investigative genetic genealogy. At the time of
acquisition, Verogen was projected to generate \$20 million in revenue
for 2023, implying a deal multiple of approximately 7.5× sales.

Together, these factors create a compelling case for investment. The
U.S. backlog alone offers an immediate, underserved demand signal. The
global market for forensic technology is growing quickly and
structurally favors consumable-driven models. Public funding is
available to subsidize validation, reducing execution risk. And once
product-market fit is achieved, the acquisition pathway is well
established and supports attractive exit multiples. **In sum, the
development of a microRNA-based forensic assay is well aligned with both
unmet need and proven commercial dynamics, positioning it as a
high-upside opportunity within a defensible and expanding market
segment**

**Implicit question:** Your technology is new, perhaps promising, but
has failed to reproduce,

## Overcoming the Reproducibility Barrier: Lessons from Forensic History

Investors and forensic decision-makers naturally question the
reproducibility of emerging technologies---particularly when early
results, however promising, have not yet demonstrated consistent
performance across laboratories. This concern is valid. However, it is
not disqualifying. In fact, history suggests that reproducibility
challenges are a predictable phase in the life cycle of transformative
forensic technologies. Those who anticipate and strategically navigate
this phase often emerge as long-term market leaders.

The path of microRNA assays today closely parallels the early
trajectories of DNA profiling and PCR---two technologies that now define
modern molecular forensics.

When Alec Jeffreys introduced DNA fingerprinting in 1985, the method
faced widespread reproducibility issues. Laboratories used different
restriction enzymes, gel conditions, and probe sequences, making
cross-institutional comparisons nearly impossible. Acceptance by the
courts and forensic community required years of coordinated
standardization. This culminated in the formation of the [Technical
Working Group on DNA Analysis Methods (TWGDAM)
in](https://www.swgdam.org/about-us?utm_source=chatgpt.com) 1988, which
established consensus protocols, mandated inter-lab proficiency testing,
and eventually standardized the CODIS core loci. What began as a
fragmented field matured into a global gold standard.

PCR experienced a similar trajectory. First described by Kary Mullis in
1985, early PCR reactions were notoriously difficult to reproduce.
Amplification results varied widely, contamination was common, and many
researchers dismissed the method as unreliable. PCR's transition into a
trusted forensic mainstay required a series of strategic advances: the
development of stable, commercially available reagents; introduction of
hot-start polymerases; buffer optimization; and the articulation of good
laboratory practices designed specifically for PCR workflows. These
efforts transformed PCR from a fragile research tool into a foundational
method in life sciences.

Currently, the microRNA field lacks shared extraction protocols,
reference materials, amplification conditions, and marker panels.
Detection methods vary widely---from qPCR to sequencing to
microarray---each with distinct sensitivity profiles. As with early DNA
methods, inconsistency stems not from flawed science but from the
absence of coordinated infrastructure. That gap represents both a risk
and an opportunity.

Once reproducibility is established, the first successful platform often
captures dominant market share, as Promega did with STR kits by
investing early in validation and interoperability. Against this
backdrop, a microRNA startup has three viable strategic pathways, each
aligned to different capital profiles and exit timelines:

**1. Establish the Standard (High Capital, High Defensibility)**

> This approach treats reproducibility as the main strategic focus. It
> involves leading the charge on standardization through ISO
> 17025-aligned validation, multi-lab reproducibility trials, reference
> dataset creation, and active engagement with forensic working groups.
> This is likely capital-intensive and on the span of 5--7 years, but
> this strategy positions the company as the default platform in an
> emerging modality. It converts scientific friction into long-term
> defensibility, potentially leading to exclusive procurement contracts,
> kit mandates, or acquisition by a major life sciences player.

**Pursue Tactical Niches (Moderate Capital, Near-Term Revenue)**

> Alternatively, the company can target less-regulated domains where
> reproducibility standards are lighter but technical need is high. Use
> cases include military forensics, disaster victim identification
> (DVI), or research-use-only contexts. This pathway enables revenue
> generation while building scientific credibility. Successful forensic
> firms such as
> [InnoGenomics](https://innogenomics.com/products/innotyper-21/) and
> [DNA
> Solutions](https://www.dnasolutionsusa.com/services/forensic_mass_disaster)
> began with this approach, using it to fund development and eventually
> expand into court-admissible applications.

**Position as Complementary, Not Competitive (Low Barrier, Unique
Value)**

> The third strategy avoids head-to-head comparison with established
> tools. Instead, it positions microRNA as an orthogonal
> solution---particularly for body fluid identification in degraded
> samples where STR profiling, or presumptive chemical assays, fail This
> approach addresses a well-documented forensic gap without triggering
> direct challenges to existing workflows or admissibility precedents.
> By solving a problem that current tools cannot, the technology can be
> introduced earlier and with less resistance, especially if paired with
> conventional DNA evidence in a hybrid workflow.

**What do we need to do to get into a courtroom?**

The **Daubert standard** stems from the 1993 Supreme Court decision
*Daubert v. Merrell Dow Pharmaceuticals* and governs the admissibility
of expert testimony under Federal Rule of Evidence 702. It places the
judge in the role of *gatekeeper*, requiring that any scientific method
offered in court must be both **reliable** and **relevant**.

To determine reliability, courts consider five core factors:

1.  **Testability** --- Can the method be empirically tested and
    falsified?

2.  **Peer Review** --- Has it been published and subjected to
    scientific scrutiny?

3.  **Known Error Rate** --- Are accuracy and precision statistically
    quantified?

4.  **Standards and Controls** --- Does the method follow a validated
    protocol?

5.  **General Acceptance** --- Is the method recognized by experts in
    the relevant scientific community?

Judges evaluate methodology not just the expert's qualifications to
determine if the evidence is scientifically sound. Somestates still uses
a simpler standard, known as Frye, where scientific evidence is
admissible once the underlying methodology is "generally accepted"
within its field. No error-rate calculation or peer-review proof is
required.

As of May 2025, California, New York, Pennsylvania, Washington,
Illinois, Minnesota, and a handful of smaller jurisdictions still apply
Frye for state cases, while their federal counterparts follow Daubert. 

**Sample costs**

Samples can also be sourced from Partner crime-labs (future validation)
or the red cross.

  -----------------------------------------------------------------------
  **Fluid**                         **Vendor & catalog    **Unit
                                    code**                price\***
  --------------------------------- --------------------- ---------------
  Whole blood (10 mL, K2-EDTA)      Innovative Research   **\$98** 
                                    --- IWB1K2E10MLC      

  Saliva (single donor, ≥1 mL)      Lee Bio 991-05-M-1    **\$76.88** 

  Semen (pooled donors, 1 mL)       Lee Bio 991-04-P-1    **\$77.49** 

  Vaginal fluid (100 µL, single     Innovative Research   **\$728.00** 
  donor)                            --- IRHUSVF100UL      

  Menstrual blood (≥1 mL, single    Lee Bio 991-15-S-1    **\$245.00** 
  donor)                                                  
  -----------------------------------------------------------------------

**Stakeholder list**

  --------------------------------------------------------------------------
  **Stakeholder**         **Primary need / pain   **How the assay addresses
                          point**                 it**
  ----------------------- ----------------------- --------------------------
  State & local crime     Low-complexity          Provide turnkey kit, SOP,
  laboratories (e.g.,     workflow, ISO           QC chart, and
  Texas DPS, NY State     17025-ready validation  developmental-validation
  Police Forensic Sci.    package, compatibility  data for rapid scope
  Center)                 with existing           addition
                          thermocyclers           

  Federal labs (FBI, ATF, Early-adopter           Supply multi-site data
  USACIL)                 innovations that set    package; invite
                          national practice, data participation in
                          for policy briefs       method-development
                                                  round-robin

  Prosecutors & district  Clear, reliable         Publish peer-reviewed
  attorneys               evidence that survives  error-rate tables,
                          Daubert, helps          ANSI/ASB standard
                          establish activity      citation, expert-witness
                          level (what body fluid, bench book
                          where)                  

  Public defenders &      Transparent method,     Make raw validation data
  innocence-project       accessible discovery    and assay software open
  lawyers                 files for independent   for defense replication;
                          review                  offer low-cost proficiency
                                                  tests

  Kit vendors &           Proven market demand,   License the marker panel
  diagnostics OEMs        defensible IP, clear    and locked dataset;
  (Thermo Fisher, Qiagen, standards moat          co-brand under ANSI/ASB
  Promega)                                        standard to secure reagent
                                                  exclusivity

  Grant funders (NIJ      High-impact technology  Frame proposal around
  Forensic Science R&D)   that closes critical    documented STR failure
                          evidence gaps           cases and projected
                                                  cost-savings per
                                                  investigation

  Accreditation bodies    Robust validation       Deliver complete
  (ANAB, A2LA)            dossiers to approve     developmental- and
                          scope expansions        internal-validation
                                                  templates aligned to ISO
                                                  17025 § 7.2
  --------------------------------------------------------------------------

**SUPPLEMENTAL SECTION : How Did RSID get validated? Can we copy their
study design?**

Forensic testimony in U.S. courts follows Frye or Daubert standards.
Neither standard requires a *single* peer-reviewed "developmental
validation"; they require that the method be *generally accepted* (Frye)
or have *reliable scientific grounding* (Daubert). Once a crime
laboratory completes its own internal validation---often guided by
SWGDAM or ASB standards---the strip's results can be introduced. Labs
began adopting RSID-Semen soon after the 2006--2007 studies; published
case reports using semenogelin strips appear in the literature before
2010, indicating courtroom use well ahead of the 2017 update.

**Timeline of validation work**

- **2006 -- manufacturer "Rev. B" developmental-validation report.**
  Independent Forensics published a 70-page internal study titled
  *Developmental Validation Studies of RSID-Semen* that documented
  sensitivity, species specificity, substrate effects, temperature
  stability, and the high-dose hook phenomenon.
  [[seidden.com]{.underline}](https://www.seidden.com/Develp_Validation_RSID_Semen_03_22_06.pdf?utm_source=chatgpt.com)

- **2007 -- first peer-reviewed comparison with ABAcard.** Pang et al.
  evaluated RSID-Semen alongside a PSA strip and showed that the new
  test detected semenogelin in samples where sperm were absent.
  [[ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S037907380600524X?utm_source=chatgpt.com)[PubMed](https://pubmed.ncbi.nlm.nih.gov/16949235/?utm_source=chatgpt.com)]{.underline}

- **2011--2012 -- Journal of Forensic Sciences developmental-validation
  article.** Old et al. reported \< 2.5 nL detection limits, no
  cross-reactivity, and performance on casework-like samples.
  [[PubMed](https://pubmed.ncbi.nlm.nih.gov/22211796/?utm_source=chatgpt.com)[ResearchGate](https://www.researchgate.net/publication/51974933_Developmental_Validation_of_RSID_TM-Semen_A_Lateral_Flow_Immunochromatographic_Strip_Test_for_the_Forensic_Detection_of_Human_Semen?utm_source=chatgpt.com)]{.underline}

- **2017 -- updated manufacturer validation ("Rev. D").** This later
  study expanded the stress tests (laundering, UV, detergents) but was
  not the first validation.
  [[ifi-test.com]{.underline}](https://www.ifi-test.com/documents/RSID_Semen_Validation.pdf?utm_source=chatgpt.com)

![A table of contents with text AI-generated content may be
incorrect.](media/image13.png){width="6.5in"
height="6.423611111111111in"}

**PITCH SETUP**

This project seeks to design, validate, and operationalize a forensic
assay using microRNA (miRNA) expression profiles to identify biological
fluids left at crime scenes. Our core objective is to demonstrate that
miRNA-based fluid identification is scientifically reliable but also
legally admissible under the Daubert standard and scalable for routine
deployment in forensic laboratories. 

Our co-founders met while working on an RNA therapeutics team at a major
U.S. pharmaceutical company. Their shared obsession with RNA, and
bringing drugs to patients, formed the genesis of this startup. They had
been working on RNA\'s biggest unsolved problem: current RNA therapies
distribute throughout the body indiscriminately, causing off-target
effects and limiting therapeutic potential. Their research, along with
mounting public evidence, showed that microRNAs could solve this
problem.

MicroRNAs are small, non-coding RNA molecules that regulate gene
expression by silencing specific messenger RNAs. Each cell type
expresses a distinct combination of these microRNAs, creating a unique
molecular fingerprint that reveals a cell\'s tissue of origin,
physiological state, and developmental stage. We can exploit these
fingerprints by engineering therapeutic RNAs with artificial binding
sites that match specific microRNA patterns. This creates biological
logic gates that can be used to create next generation therapeutics for
patients.

Our co-founders met while working on an RNA therapeutics team at a major
U.S. pharmaceutical company. Their shared obsession with RNA, and
bringing drugs to patients, formed the genesis of this startup. They had
been working on RNA\'s biggest unsolved problem: current RNA therapies
distribute throughout the body indiscriminately, causing off-target
effects and limiting therapeutic potential

When the company disbanded its U.S. RNA division during global
restructuring, our co-founders faced barriers to continuing their work.
The U.S. political and investment climate has grown increasingly hostile
toward RNA science, and despite mRNA vaccines\' success, public
skepticism and regulatory uncertainty make investors wary of RNA
platforms. Moreover, creating viable therapeutic platforms requires
navigating a high-capital, long-horizon development cycle. And while
such work holds clear value to human health, its risk and cost often
render it invisible to investors focused on short-term returns

Therefore, the capital and political realities prompted us to seek
alternative markets where RNA technology could generate reliable revenue
while still advancing the state of the art. We turned to forensic
science, where many core assays have remained unchanged for over two
decades. This field offered a rare alignment of technical need, a viable
addressable market, and social impact.

When investigators find biological evidence at a crime scene, a stain on
clothing, a swab from an assault victim, dried material on a weapon,
they must answer two separate questions: whose is it, and what is it?
DNA tells you who, but not what. It can match a suspect to a sample, but
it cannot distinguish whether that sample was blood, semen, or
saliva. This distinction is crucial because the type of fluid reveals
the nature of the activity.

Consider a sexual assault case where the suspect admits prior consensual
contact with the victim. His DNA will be present regardless. But is it
saliva from conversation? Skin cells from physical contact? Or semen
from assault? The fluid type establishes the activity and therefore is
evidence of the crime. Yet current presumptive tests, based on 1990s
protein chemistry, fail on degraded samples and produce false positives
inadmissible in court.

Today's presumptive tests for body fluids are chemical color reactions
that suffer from false positives, degrade rapidly, and cannot be used
once samples have aged. MicroRNAs offer a precise molecular alternative.
Because their expression patterns are tissue-specific and remain
detectable even in degraded material, they can identify the source of
biological fluids with greater accuracy and longer post-event viability.
Better forensic assays directly prevent violent crimes by linking
perpetrators earlier in their offending cycle, before further escalation
to the next victim.

The market opportunity for microRNA-based body fluid identification is
substantial and immediate. [The forensic technology sector was valued at
\$5.51 billion in 2023 and is projected to grow to \$10.65 billion by
2030, reflecting a compound annual growth rate (CAGR) of 9.9
percent](https://www.grandviewresearch.com/industry-analysis/forensic-technology-market).
Within this market, consumable kits and reagents account for
approximately 67 percent of all revenue, underscoring a structural bias
toward recurring-purchase assay platforms over one-time instrumentation
sales. This consumables-heavy dynamic creates favorable conditions for
platforms like microRNA cartridges that drive high-margin, repeatable
sales through laboratory workflows.

According to the Bureau of Justice Statistics, publicly funded crime
laboratories received approximately 3.3 million forensic service
requests in 2020, yet concluded the year with over 710,000 cases still
unresolved after 30 days. At the Bureau of Justice Statistics-reported
average cost of \$620 per case. this backlog represents roughly \$440
million in stranded forensic work annually. This is an unmet need that
creates a natural entry point for new technology. **If a microRNA assay
were able to unlock just 10 percent of this degraded-evidence segment,
it would generate approximately \$44 million in new U.S. billings each
year.**

The funding environment further supports innovation in this space. The
U.S. National Institute of Justice (NIJ) consistently allocates between
\$12 and \$14 million annually to support forensic science research and
development. **By leveraging NIJ support, our startup can reduce capital
intensity and significantly de-risk the pathway to courtroom
acceptance.**

This established funding pathway enables us to leverage initial ACX
support into substantially larger NIJ grants for expanded validation and
field deployment.

Downstream market validation comes from recent M&A activity. Once a
specialized forensic assay demonstrates courtroom viability and
generates recurring kit sales, it becomes a prime acquisition target for
large life sciences firms seeking to expand their footprint in forensic
genomics. [In January 2023, QIAGEN acquired Verogen---a spinout from
Illumina focused on forensic next-generation sequencing---for \$150
million in
cash](https://www.nasdaq.com/articles/qiagen-completes-acquisition-of-verogen?utm_source=chatgpt.com).
Verogen's flagship products include ForenSeq kits, which enable
simultaneous analysis of thousands of STRs and SNPs, and GEDmatch PRO, a
database used in investigative genetic genealogy. At the time of
acquisition, Verogen was projected to generate \$20 million in revenue
for 2023, implying a deal multiple of approximately 7.5× sales.

Together, these factors create a compelling case for investment. The
U.S. backlog alone offers an immediate, underserved demand signal. The
global market for forensic technology is growing quickly and
structurally favors consumable-driven models. Public funding is
available to subsidize validation, reducing execution risk. And once
product-market fit is achieved, the acquisition pathway is well
established and supports attractive exit multiples. In sum, the
development of a microRNA-based forensic assay is well aligned with both
unmet need and proven commercial dynamics, positioning it as a
high-upside opportunity within a defensible and expanding market segment

Our hypothesis is that miRNA markers, due to their tissue-specific
expression and post-mortem stability, can enable a reliable molecular
signature for each body fluid. Our project will execute the foundational
steps required to transition this technique from academic literature
into a deployable, court-validated forensic product.

The path from validation to market adoption is well-established. Unlike
medical devices requiring FDA approval, forensic tests operate under
enforcement discretion, needing only to meet evidentiary standards.
Recent market validation comes from QIAGEN\'s \$150 million acquisition
of Verogen at 7.5 times revenue, demonstrating strong exit multiples for
validated forensic technologies. More importantly, similar technologies
like RSID-Semen achieved nationwide court admissibility through
systematic validation between 2006 and 2017, providing a proven roadmap
we can accelerate.

We are requesting \$57k for our initial pilot study, to get groundwork
data needed for NIJ grants.

uster**55,957**

Our co-founders met while developing RNA therapeutics at a major
pharmaceutical company. They were solving RNA therapy\'s biggest
problem: current treatments distribute indiscriminately throughout the
body, causing severe off-target effects. Their solution used
microRNAs---small RNA molecules that create unique molecular
fingerprints in each cell type. By engineering therapeutic RNAs with
artificial microRNA binding sites, they could create biological logic
gates: drugs that activate only in cancer cells while remaining dormant
in healthy tissue.

When the company shuttered its RNA division, they faced reality.
Developing RNA therapeutics requires \$200-500M---impossible without
clinical proof. The U.S. investment climate has turned hostile toward
RNA platforms despite mRNA vaccine success. But they realized the same
microRNA signatures that enable drug targeting also solve critical
forensic problems.

Forensic science relies on presumptive tests unchanged since the 1990s.
When investigators find biological evidence, they must answer: whose is
it, and what is it? DNA identifies WHO but not WHAT. This distinction
matters---in sexual assault cases where suspects admit prior contact,
proving the fluid is semen versus saliva determines guilt. Current
protein-based tests fail on degraded samples and produce false positives
inadmissible in court.

MicroRNAs solve this. Each body fluid has distinct microRNA
patterns---blood expresses miR-451a, semen contains miR-888-5p. These
signatures survive six months after proteins degrade, enabling
definitive identification of previously untestable evidence. This
capability transforms investigations and prevents crimes---studies show
the average rapist commits 5.8 assaults before identification.

The market opportunity is immediate. The forensic technology sector,
valued at \$5.51B growing at 9.9% annually, derives 67% of revenue from
consumable tests. U.S. labs face 710,900 backlogged cases worth \$440M
at \$620 per case. Labs already pay \$14 per test for methods with 15%
error rates, establishing price acceptance for superior technology at
\$80-100. Capturing 10% of degraded evidence generates \$44M annually.

The funding pathway is clear. This \$50K grant enables preliminary
validation for NIJ grants averaging \$500K. NIJ allocated \$13.6M across
24 forensic projects in 2024. Unlike FDA-regulated therapeutics,
forensic tests need only Daubert standards---documented error rates and
peer review. RSID-Semen achieved nationwide admissibility following this
path from 2006-2017. Recent validation: QIAGEN acquired Verogen for
\$150M at 7.5x revenue.

Critically, forensics funds our return to therapeutics. Every body fluid
signature identified for courtrooms maps tissue-targeting sequences for
drugs. Every optimization for degraded evidence improves our RNA
platform. The projected \$10-40M annual revenue eliminates dilutive
fundraising while advancing toward programmable cancer
therapeutics---our ultimate goal.

We\'re not abandoning our therapeutic vision but strategically
sequencing it. Build the technology through forensics, generate revenue,
prove the platform works, then return to therapeutics with credibility
and capital. The path to programmable cancer drugs runs through the
crime lab.

**\[4,889 characters\]**

Retry

Our co-founders met while working on an RNA therapeutics team at a major
U.S. pharmaceutical company. Their shared obsession with RNA, and
bringing drugs to patients, formed the genesis of this startup. They had
been working on RNA\'s biggest unsolved problem: current RNA therapies
distribute throu

pasted

AM

use though my langauge that i showed u here

Edit

Decoded document\'s voice while strategically condensing text.

7s

The user wants me to condense their document to 5000 characters or fewer
while maintaining their specific language/voice from the document they
just provided. Looking at their text, I can see they have a specific way
of writing that I should preserve - they use phrases like \"our
co-founders,\" specific technical explanations, and a particular
narrative flow. I need to keep their voice while cutting it down
significantly.

Key elements of their voice:

- \"Our co-founders met while working on an RNA therapeutics team\"

- \"Their shared obsession with RNA\"

- Specific technical details about the market

- The narrative about the company shuttering

- Their specific phrasing about forensics and the market opportunity

I need to preserve their exact language where possible while condensing.

**Condensed to \~5000 characters using your language:**

Our co-founders met while working on an RNA therapeutics team at a major
U.S. pharmaceutical company. Their shared obsession with RNA, and
bringing drugs to patients, formed the genesis of this startup. They had
been working on RNA\'s biggest unsolved problem: current RNA therapies
distribute throughout the body indiscriminately, causing off-target
effects and limiting therapeutic potential. Their research showed
microRNAs could solve this---each cell type expresses distinct microRNA
patterns creating molecular fingerprints. By engineering therapeutic
RNAs with artificial binding sites for specific microRNAs, drugs could
activate only in target cells.

When the company disbanded its U.S. RNA division during global
restructuring, our co-founders faced barriers to continuing their work.
The U.S. political and investment climate has grown increasingly hostile
toward RNA science. Despite mRNA vaccines\' success, public skepticism
and regulatory uncertainty make investors wary of RNA platforms.
Creating viable therapeutic platforms requires navigating a
high-capital, long-horizon development cycle. While such work holds
clear value to human health, its risk and cost often render it invisible
to investors focused on short-term returns.

Therefore, the capital and political realities prompted us to seek
alternative markets where RNA technology could generate reliable revenue
while still advancing the state of the art. We turned to forensic
science, where many core assays have remained unchanged for over two
decades.

When investigators find biological evidence at a crime scene---a stain
on clothing, a swab from an assault victim, dried material on a
weapon---they must answer two separate questions: whose is it, and what
is it? DNA tells you who, but not what. It cannot distinguish whether
that sample was blood, semen, or saliva. This distinction is crucial
because the type of fluid reveals the nature of the activity.

Consider a sexual assault case where the suspect admits prior consensual
contact with the victim. His DNA will be present regardless. But is it
saliva from conversation? Skin cells from physical contact? Or semen
from assault? The fluid type establishes the activity and therefore is
evidence of the crime. Yet current presumptive tests, based on 1990s
protein chemistry, fail on degraded samples and produce false positives
inadmissible in court.

MicroRNAs offer a precise molecular alternative. Because their
expression patterns are tissue-specific and remain detectable even in
degraded material, they can identify the source of biological fluids
with greater accuracy and longer post-event viability. Better forensic
assays directly prevent violent crimes by linking perpetrators earlier
in their offending cycle, before further escalation to the next victim.

The market opportunity is substantial and immediate. The forensic
technology sector was valued at \$5.51 billion in 2023 and is projected
to grow to \$10.65 billion by 2030, reflecting a 9.9% CAGR. Within this
market, consumable kits and reagents account for approximately 67% of
all revenue, underscoring a structural bias toward recurring-purchase
assay platforms over one-time instrumentation sales.

According to the Bureau of Justice Statistics, publicly funded crime
laboratories received approximately 3.3 million forensic service
requests in 2020, yet concluded the year with over 710,000 cases still
unresolved after 30 days. At \$620 per case, this backlog represents
roughly \$440 million in stranded forensic work annually. If a microRNA
assay were able to unlock just 10% of this degraded-evidence segment, it
would generate approximately \$44 million in new U.S. billings each
year.

The U.S. National Institute of Justice consistently allocates \$12-14
million annually to support forensic science R&D. By leveraging NIJ
support, our startup can reduce capital intensity and significantly
de-risk the pathway to courtroom acceptance. This established funding
pathway enables us to leverage initial ACX support into substantially
larger NIJ grants for expanded validation.

Downstream market validation comes from recent M&A activity. In January
2023, QIAGEN acquired Verogen for \$150 million in cash. At the time of
acquisition, Verogen was projected to generate \$20 million in revenue
for 2023, implying a deal multiple of approximately 7.5× sales.

These factors create a compelling case for investment. The U.S. backlog
alone offers an immediate, underserved demand signal. The global market
for forensic technology is growing quickly and structurally favors
consumable-driven models. Public funding is available to subsidize
validation, reducing execution risk. Once product-market fit is
achieved, the acquisition pathway is well established and supports
attractive exit multiples.
