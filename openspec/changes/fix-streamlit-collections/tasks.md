# Tasks

## 1. Sequence rows keep stable identities

- [ ] 1.1 Store ordered row ids per collection property in the wizard state and allocate ids for rows that come from the stored value or the default; verify with the add-item and item-default scenarios
- [ ] 1.2 Address sequence rows by stable row id instead of position and build the output in id order; verify with a scenario that removing a middle row keeps the remaining values
- [ ] 1.3 Keep duplicate set rows across the rerun while returning the de-duplicated set; verify with the duplicate-entries scenarios

## 2. Item defaults and dictionary rows

- [ ] 2.1 Seed sequence item defaults from the row value and label rows `Item #n`; verify with the item-default scenarios
- [ ] 2.2 Treat dict keys as row identity, rename by moving the value, and overwrite on rename onto an existing key; verify with the rename scenarios

## 3. Widget disabling follows the schema limits

- [ ] 3.1 Fix the clear-button inversion, and make `Add Item` and `Remove` respect the max and min counts; verify with the sequence size-limit scenarios
- [ ] 3.2 Use `maxProperties` and `minProperties` for dicts; verify with the dict-limit scenarios

## Workflow follow-up

- Archive the change after the project's review requirements are satisfied.
