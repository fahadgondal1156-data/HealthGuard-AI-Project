# HealthGuard-AI User Guide

## Login

Open the dashboard address supplied by the administrator. Enter the application username and password. The login screen also displays API availability and latency. Application credentials are stored as password hashes in the database; they are not read from `.env` as user passwords.

## Main navigation

The final interface provides two navigation areas:

- a dark-blue command-center sidebar with role-aware pages and model status;
- a top navigation row containing a workspace selector, global patient search, notifications, profile menu and quick-action buttons.

## Overview

The Overview page summarizes monitored patients, high/critical patients, open alerts, average latest risk, model horizon and model availability. It adds a risk-distribution visualization, model snapshot, prioritized high-risk patients and recent auditable activity.

## Patient Monitor

Select a pseudonymous patient. The page presents the latest risk probability, risk band, age group and sex, then provides dedicated views for risk overview, timeline, latest feature values and observation history. The interface is designed for longitudinal review rather than single-value diagnosis.

## Alert Center

Authorized users can view open, high and critical alerts, filter by status/severity/patient, inspect severity and activity charts, export filtered results to CSV and acknowledge reviewed alerts. Acknowledgement records the user and timestamp and writes an audit event.

## AI Analytics

The model page displays stored research metrics including PR-AUC, AUROC, precision, sensitivity, F1 and Brier score. It visualizes validation PR-AUC by candidate model, patient-level train/validation/test split, an overall performance profile, model configuration, feature inventory and complete metadata.

## Security Audit

Administrators and auditors can review recent audit events, successful/failed outcomes, unique actors, frequent actions and activity by actor. Filters support actor, action and resource search. The filtered log can be exported to CSV.

## System

The System page shows API status, latency, model availability, patient-database readiness and service diagnostics. A live health-check button validates the API connection. The research-readiness panel highlights missing patient observations or model artifacts.

## Roles

- **Administrator:** broad operational access, alerts, acknowledgements and audit review.
- **Clinician:** patient monitoring, scoring and alert management.
- **Researcher:** read-only pseudonymous patient and model analytics.
- **Auditor:** monitoring visibility plus audit and alert review, without model scoring or alert acknowledgement.

## Important interpretation boundary

Risk probabilities are research outputs. A high or critical band means the stored research model crossed its configured probability threshold; it does not establish a diagnosis, emergency condition or treatment recommendation.
