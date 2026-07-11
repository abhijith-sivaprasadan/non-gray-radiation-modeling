# Project 3 Extension: DOM Scattering Sensitivity Study

`solve_wsgg_dom` couples particle *absorption* into the local extinction coefficient but has
no scattering source term (documented in `docs/derivation_note.md`). This re-solves the
Project 3 radial-midline case with and without a real isotropic-scattering term
(`dom1d.solve_gray_dom_with_isotropic_scattering`, added for this study) for a representative
dilute particle loading (Johansson coal/char at r=20 um, volume
fraction 1.0e-06) and reports the actual difference, rather than just
asserting scattering matters.

## Scope

Isotropic scattering is a simplification - real particle scattering is forward-peaked,
especially for particles large compared to the relevant wavelengths. This answers "how much
does *some* scattering change the answer", not "what does the *correct* phase function
give" - a smaller, honestly-scoped question.

## Result

Mean single-scattering albedo (sigma / (kappa+sigma), averaged over the domain):
0.101.

Mean absolute heat-flux difference (with-scattering vs. absorption-only), as a percentage
of the domain's peak |flux| (normalized this way, not against the local flux value, because
this profile crosses exactly zero at the domain center - a local-value normalization blows
up to a meaningless percentage there for a near-zero absolute difference):
0.073%. Worst case at x=0.000 m:
-0.309%.

Full profile in `tables/scattering_sensitivity.csv`; figure in
`figures/scattering_sensitivity.png`.

## Interpretation

At this particle loading, the single-scattering albedo above indicates how much of the
particles' extinction is scattering rather than true absorption - a value near 0 means
scattering is negligible here regardless of whether the solver includes it; a value
approaching 1 means most of what the particles do to radiation is redirect it, not absorb
it, and the current absorption-only solver's blind spot matters more. The heat-flux error
reported above is the direct, measured consequence for this specific loading - not a general
claim about all particle loadings, which would need this same comparison repeated across
the loading/size range Project 2 covers.
