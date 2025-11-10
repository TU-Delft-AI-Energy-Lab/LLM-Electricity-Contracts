# LLM-Electricity-Contracts
Tools and prototypes for automating customised electricity contracts using large language models. Includes integration with power-system studies, feasibility checks, contract negotiation workflows, and case studies for residential, SME, and transmission-level maintenance planning.

## Publication Customising Electricity Contracts at Scale with Large Language Models
This repository contains code for the paper:

*Jochen L. Cremer, "Customising Electricity Contracts at Scale with Large Language Models." [arXiv preprint arXiv:2505.19551](https://arxiv.org/abs/2505.19551)*

Cite this paper when using this code.

## Repository Structure

### Residential (Low Voltage)

Tools and examples for household-level electricity contract planning:

- **Electricityconsumption.nb** — Estimates an hourly household electricity load profile based on appliance usage, EV charging, and behavioral parameters.
- **checkphsicalfeasiblecontract.nb** — Validates whether a proposed household contract profile is physically feasible given network constraints.
- **Energysupplier.nb** — A Persona that orchestrates the residential workflow, combining estimation and feasibility feedback into a contract suggestion.
- **Example conversation electricity contract.nb** — A complete demonstration of an interaction with a residential customer.

---

### SME / Medium-Voltage Case Study

Tools for feasibility checks of commercial/industrial connection requests using AC power-flow simulations on the Oberrhein MV network:

- **smeOberrhein.py** — Python backend performing AC load-flow calculations on the 179-bus Oberrhein MV network to evaluate the feasibility of a 24-hour SME profile at a given bus location.
- **MVcontractplanner.nb** — Planner notebook that communicates with the Python backend, submits load profiles, and processes feasibility feedback.
- **DSO.nb** — Persona notebook modelling the Distribution System Operator; guides the user through required inputs and displays feasibility results.
- **example conversation.nb** — Full interaction example with an SME user requesting connection approval.

---

### Transmission-Level Outage Planning

Tools for multi-stage security-constrained outage feasibility checking using the IEEE-118 test system:

- **lineoutage.py** — Python backend that evaluates planned generator outages using multi-stage SCOPF logic across the requested outage window.
- **IEEE118New.xlsx & IEEE118_Load_Wind2.xlsx** — Network and time-series data files used by the outage-planning model.
- **outageplanner.nb** — Planner notebook that calls the Python tool, providing feasibility decisions and alternative outage windows.
- **TSO.nb** — Persona notebook modelling the Transmission System Operator; collects user inputs and presents the resulting schedule recommendations.
- **example conversation.nb** — Example TSO workflow interaction exploring outage window feasibility.


## License
This work is licensed under a
![BSD-3-Clause license](https://img.shields.io/badge/License-BSD_3--Clause-blue.svg)

