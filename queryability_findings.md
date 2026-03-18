# Queryability Findings from the India Mortality Investigation

## Executive Summary

The main issue in this investigation was not query syntax. The relation expression used for India states was valid for the Observation API. The hard part was discovering a statistical variable that both matched the intent behind "child mortality rate" and actually had observation coverage for India states.

In practice, the workflow required multiple steps: validate the Observation query shape, resolve several candidate indicators, probe coverage against India states, and then fall back from a semantically closer child-mortality variable to an infant-mortality variable that returned usable results. That is workable for an expert user, but it is harder than it should be for a common analytical question.

## What We Validated

We validated the following points during the investigation:

- Observation supports `entity.expression`.
- `country/IND<-containedInPlace+{typeOf:State}` is a valid Observation relation expression.
- The initial child-mortality variable `Count_Death_Upto14Years_AsAFractionOf_Count_Person_Upto14Years` returned no India-state observations.
- A fallback infant-mortality variable, `Count_Death_LessThan1Year_AsAFractionOf_Count_BirthEvent`, returned usable India-state observations.

The supported Observation query shape is documented in the REST docs. A representative request body is:

```json
{
  "date": "LATEST",
  "variable": {
    "dcids": ["Count_Death_LessThan1Year_AsAFractionOf_Count_BirthEvent"]
  },
  "entity": {
    "expression": "country/IND<-containedInPlace+{typeOf:State}"
  },
  "select": ["entity", "variable", "date", "value"]
}
```

## Key Findings

Natural-language indicator lookup did not produce a single obvious statistical variable for "child mortality rate." Instead, it returned a mix of `Topic` nodes and several similar statistical variables. That created a discovery problem before the observation query even started.

Coverage was also not obvious from resolve results. The semantically closer variable looked plausible, but the Observation API returned no India-state data for it. The API response did not explain whether the problem was missing coverage, the wrong geographic level, or the wrong variable family.

Even when data existed, the path to a usable answer was still more manual than expected. Observation responses were keyed by DCID, so converting results into a readable ranking required additional interpretation.

## Evidence

### Documented support

The following docs support the query shape used in the investigation:

- `api/rest/v2/observation.md`
- `api/rest/v2/index.md`

These docs establish that Observation accepts `entity.expression`, and that `<-containedInPlace+{typeOf:...}` is a supported filtered relation-expression pattern.

### Live investigation evidence

The first child-mortality variable tested was:

```text
Count_Death_Upto14Years_AsAFractionOf_Count_Person_Upto14Years
```

The observed response for India states was empty:

```json
{
  "byVariable": {
    "Count_Death_Upto14Years_AsAFractionOf_Count_Person_Upto14Years": {}
  }
}
```

The fallback variable that did return data was:

```text
Count_Death_LessThan1Year_AsAFractionOf_Count_BirthEvent
```

Observed top results from the live query on 2026-03-18:

| State | DCID | Value | Date |
| --- | --- | ---: | --- |
| Madhya Pradesh | `wikidataId/Q1188` | 0.048 | 2018 |
| Uttar Pradesh | `wikidataId/Q1498` | 0.043 | 2018 |
| Chhattisgarh | `wikidataId/Q1168` | 0.041 | 2018 |
| Assam | `wikidataId/Q1164` | 0.041 | 2018 |
| Odisha | `wikidataId/Q22048` | 0.040 | 2018 |

The returned facet was also informative: the results came from `OECDRegionalDemography_Mortality`.

## Why This Was Hard

- There is no coverage-aware ranking of candidate statistical variables for a target geography.
- Common analytical terms like "child mortality rate" map to multiple Topics and near-duplicate statistical variables.
- Empty Observation results are hard to interpret because they do not explain whether the issue is coverage, geography level, or variable choice.
- Similar mortality variables differ in small but important ways, including age bucket semantics and denominator semantics.
- Observation output is harder to use directly because the primary keys are DCIDs rather than readable names.

## Recommendations

- Add coverage-aware statistical-variable discovery so candidate ranking reflects both semantic match and geography coverage.
- Add better empty-result diagnostics in Observation, especially for cases where the variable exists but has no data for the requested geography.
- Improve canonical aliases for common public-health indicators such as child mortality, infant mortality, under-5 mortality, and neonatal mortality.
- Provide a simpler path from `Topic` results to recommended statistical variables with known coverage.
- Add an option to include entity names alongside DCIDs in Observation responses.

## Notes

This report separates documented support from live-query observations. The claims about supported query syntax come from the docs listed above. The conclusions about coverage gaps and fallback behavior are based on observed API responses during the investigation on 2026-03-18.
