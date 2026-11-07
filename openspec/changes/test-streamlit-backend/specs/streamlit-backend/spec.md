## MODIFIED Requirements

### Requirement: Union fields
The Streamlit wizard SHALL render a union as a selector of its alternatives, labelled by alternative title or else type and format, and render the selected alternative below. A default preselects the alternative whose discriminator value matches it, or for plain unions the first alternative the default validates against.

#### Scenario: Discriminated default
- **WHEN** a discriminated union on `type` has a default whose `type` is `B`
- **THEN** the alternative whose `type` is `B` is preselected and its `type` field shows `B`

#### Scenario: Optional integer
- **WHEN** a property is `anyOf` integer and null
- **THEN** a selector offers `integer` and `null`
