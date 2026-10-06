# Dataset Methodology

## Benchmark Source
This project utilizes `CampusFAQ-50K` as a controlled, synthetic benchmark.

## Synthetic Nature
The queries and intents are procedurally generated and synthetically curated. They do NOT represent real student conversations.

## Schema
- `query`: Text string representing the student question.
- `intent`: Categorical label for classification.

## Split
The dataset is divided into training (80%) and testing (20%) sets using stratified splitting.
