# Facts Financial

## Atomic Facts

Facts are the things being measured in a process. The terms `measurement` or `metric` are often used instead of fact to describe what is happening in the model. The Atomic Facts are modeled at the lowest level of the process they are measuring. They do not filter out any data and include all the rows that have been generated from the process the Atomic Fact table is describing. The documentation for the models would include details about the fact table being an atomic one or a derived one.

## Derived Facts

Derived Facts are built on top of the Atomic Facts. The Derived Fact directly references the Atomic Fact thereby creating an auditable, traceable lineage. The documentation for the models would include details about the fact table being an atomic one or a derived one.