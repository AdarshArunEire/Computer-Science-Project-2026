My 2026 computer science submission# Forest Fire Risk Monitoring and Scenario Modelling

An end-to-end environmental risk modelling project combining embedded systems, data processing, and rule-based modelling.

This project was built to collect live environmental data from a microcontroller-based sensor system, clean and aggregate the resulting time series, and model forest fire risk under both observed and hypothetical conditions. The goal was not just to read sensors, but to turn imperfect real-world measurements into a usable decision system.

## Overview

The system has two linked parts.

The first is an embedded monitoring device built around a micro:bit and external sensors. It captures environmental variables associated with fire risk and gives immediate feedback when conditions become dangerous.

The second is a Python-based analysis pipeline that stores, cleans, aggregates, and models that data on a computer. This makes it possible to move beyond simple threshold alerts and study how combinations of variables affect overall risk.

This project sits at the intersection of software engineering, mathematical modelling, and data analysis. It was especially useful as an exercise in working with noisy inputs, constrained hardware, feature interactions, and explainable risk scoring.

## What the project does

- Collects live environmental data from sensors
- Transfers that data for further analysis
- Cleans and structures raw readings into a usable dataset
- Aggregates data into higher-level time intervals
- Models fire risk from multiple inputs rather than a single threshold
- Tests "what-if" scenarios to explore how risk changes under different conditions
- Produces visual outputs to make the model easier to interpret

## Why this is interesting technically

Many beginner projects stop at “read sensor -> show value”. This one goes further.

The main technical challenge was turning low-level sensor readings into a risk model that is both usable and interpretable. That required thinking about:

- how to handle raw values that are noisy or indirect
- how to map physical measurements onto a meaningful risk scale
- how multiple factors interact rather than act independently
- how to balance model simplicity with realism
- how to make scenario analysis possible without retraining a complex black-box model

The result is a system that is deliberately explainable. Every stage, from input collection to final risk output, can be inspected and justified.

## Inputs used

The model uses environmental variables collected by the system and transformed into model inputs. These are intended to represent conditions linked to fire risk.

Examples include:

- temperature
- light level
- soil moisture
- user-defined scenario changes for future or extreme conditions

These variables are combined into an overall risk estimate rather than treated as isolated indicators.

## Modelling approach

The modelling side of the project uses a structured risk-scoring approach rather than a black-box ML model.

That choice was deliberate.

Given the dataset size, the nature of the inputs, and the need for interpretability, a transparent model made more sense than forcing a more complex machine learning method. The objective was to build something mathematically reasoned, explainable, and easy to stress-test.

The modelling workflow includes:

1. collecting raw sensor observations  
2. cleaning invalid or inconsistent values  
3. aggregating data into more stable time-based summaries  
4. transforming inputs into a common modelling format  
5. combining variables into a fire-risk score  
6. mapping the score into interpretable risk bands  
7. testing the model under hypothetical scenarios  

This is closer to an applied quantitative modelling workflow than a simple electronics demo.

## Scenario analysis

One of the strongest parts of the project is that it does not only model current data. It also supports scenario generation.

This allows the system to answer questions such as:

- what happens if conditions become much drier?
- how would a sustained hot period affect the risk score?
- how sensitive is the output to changes in individual variables?
- which factors drive the model most strongly?

That makes the project more interesting from a mathematical and decision-making perspective, because it introduces sensitivity analysis rather than only reporting current values.

## Engineering stack

### Embedded side
- BBC micro:bit
- sensor inputs
- live monitoring / alert behaviour

### Software side
- Python
- data cleaning and transformation
- tabular time-series handling
- scenario generation
- risk modelling
- visualisation

## Key ideas demonstrated

This project demonstrates experience with:

- building an end-to-end pipeline rather than an isolated script
- working with real, imperfect data rather than idealised examples
- translating physical measurements into model features
- designing an interpretable scoring model
- handling scenario-based analysis
- thinking carefully about assumptions, limitations, and trade-offs
- presenting technical work clearly

## What I learned

A major takeaway from this project was that modelling is not just about formulas. The hardest part is often deciding how data should be represented, cleaned, weighted, and interpreted.

I also learned that simple models can still be powerful if they are well designed. In many practical settings, an explainable model with good structure is more useful than a more complex method that is harder to justify.

From an engineering perspective, this project also reinforced the importance of modular design. Separating data collection, cleaning, modelling, and scenario generation made the system easier to test and improve.

## Limitations

This is not presented as a production wildfire forecasting system.

Some limitations include:

- a relatively small and project-scale dataset
- sensor constraints and measurement noise
- simplified assumptions in the risk model
- limited external validation against large real-world fire datasets

These limitations are important, but they also reflect a real modelling lesson: useful systems often begin as constrained prototypes, and the quality of the design depends on how honestly those constraints are handled.

## Future improvements

There are several natural extensions:

- integrate additional environmental variables
- calibrate the model against larger external datasets
- compare the current rule-based model with statistical or ML approaches
- add sensitivity analysis and uncertainty estimates more formally
- deploy the software side as an interactive dashboard
- extend from local monitoring to spatial risk estimation

## Repository structure

This repository contains the embedded and Python components of the project, including data handling, modelling, and scenario analysis.

A typical workflow is:

1. collect raw readings  
2. clean and aggregate the data  
3. run the risk model  
4. generate and compare alternative scenarios  
5. inspect the outputs visually  

 it was built with the same mindset I find most interesting in quantitative and technical fields: take a messy real-world problem, formalise it carefully, and build something transparent that can be tested and improved.
