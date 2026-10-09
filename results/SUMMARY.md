# Results

92 questions across 5 databases. Execution accuracy: the generated query returns the same rows as the gold query (row and column order ignored, numbers compared at one decimal). Relaxed also accepts extra columns.

| model | condition | answered | strict | relaxed | ran without error | median s/question |
|---|---|---:|---:|---:|---:|---:|
| qwen2.5-coder:3b | schema | 92 | **1.1%** | 1.1% | 76.1% | 12.7 |
| qwen2.5-coder:3b | schema+repair | 92 | **1.1%** | 1.1% | 80.4% | 15.1 |
| qwen2.5-coder:3b | schema+rows | 92 | **0.0%** | 0.0% | 84.8% | 3.2 |
| qwen2.5-coder:3b | schema+rows+repair | 92 | **0.0%** | 0.0% | 87.0% | 3.3 |
| qwen2.5-coder:7b | schema | 92 | **2.2%** | 2.2% | 84.8% | 16.3 |
| qwen2.5-coder:7b | schema+repair | 92 | **2.2%** | 2.2% | 90.2% | 19.9 |
| qwen2.5-coder:7b | schema+rows | 92 | **1.1%** | 1.1% | 87.0% | 13.1 |
| qwen2.5-coder:7b | schema+rows+repair | 92 | **1.1%** | 1.1% | 92.4% | 13.3 |

## By database (strict)

| model | condition | crime | fraud | ics | identity | network |
|---|---|---:|---:|---:|---:|---:|
| qwen2.5-coder:3b | schema | 0.0% | 0.0% | 5.6% | 0.0% | 0.0% |
| qwen2.5-coder:3b | schema+repair | 0.0% | 0.0% | 5.6% | 0.0% | 0.0% |
| qwen2.5-coder:3b | schema+rows | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| qwen2.5-coder:3b | schema+rows+repair | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| qwen2.5-coder:7b | schema | 0.0% | 0.0% | 5.6% | 0.0% | 5.6% |
| qwen2.5-coder:7b | schema+repair | 0.0% | 0.0% | 5.6% | 0.0% | 5.6% |
| qwen2.5-coder:7b | schema+rows | 0.0% | 0.0% | 0.0% | 0.0% | 5.6% |
| qwen2.5-coder:7b | schema+rows+repair | 0.0% | 0.0% | 0.0% | 0.0% | 5.6% |

## Why answers failed

| model | condition | unknown table/column | SQL syntax | other runtime error | timed out | wrong number of rows | wrong values | right rows, extra columns |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| qwen2.5-coder:3b | schema | 21 | 1 | 0 | 0 | 54 | 15 | 0 |
| qwen2.5-coder:3b | schema+repair | 18 | 0 | 0 | 0 | 58 | 15 | 0 |
| qwen2.5-coder:3b | schema+rows | 10 | 4 | 0 | 0 | 62 | 16 | 0 |
| qwen2.5-coder:3b | schema+rows+repair | 11 | 1 | 0 | 0 | 64 | 16 | 0 |
| qwen2.5-coder:7b | schema | 10 | 3 | 1 | 0 | 54 | 22 | 0 |
| qwen2.5-coder:7b | schema+repair | 6 | 2 | 1 | 0 | 58 | 23 | 0 |
| qwen2.5-coder:7b | schema+rows | 10 | 2 | 0 | 0 | 55 | 24 | 0 |
| qwen2.5-coder:7b | schema+rows+repair | 6 | 1 | 0 | 0 | 58 | 26 | 0 |

## Questions no configuration answered (90)

- `crime/01_incidents_by_year_and_category`: How has each major crime category trended year over year since 2014?
- `crime/02_yoy_change_by_category`: Year-over-year % change per category. Which category had the biggest single-year jump?
- `crime/03_seasonality_index`: Is crime seasonal? Index each calendar month against the annual monthly average (100 = average).
- `crime/04_peak_hours_by_category`: What are the three peak hours for each category?
- `crime/05_weekday_hour_heatmap`: Day-of-week x hour grid for assaults (dashboard heatmap input).
- `crime/06_neighbourhood_rank_change`: Top 15 neighbourhoods by incidents in 2024, and how their rank moved since 2019.
- `crime/07_crime_rate_per_1000`: Raw counts favour big neighbourhoods. Which have the highest and lowest 2024 rate per 1,000 residents?
- `crime/08_auto_theft_rolling_12m`: Monthly auto thefts with a trailing 12-month average to smooth seasonality.
- `crime/09_premises_share_by_category`: Where does each type of crime happen? Share of incidents by premises type within category.
- `crime/10_reporting_lag_percentiles`: How long after a crime is it reported? Percentiles of the lag, by category.
- `crime/11_multi_offence_events`: One police event can carry several offence rows. How common is that, and what does it mean for "counting crimes"?
- `crime/12_division_cumulative_share`: Police divisions ranked by 2024 volume with running cumulative share (Pareto view).
- `crime/13_fastest_growing_auto_theft_neighbourhoods`: Where did auto theft grow fastest between 2019 and 2023 (the peak)? Minimum 50 thefts in 2019 to avoid small-base noise.
- `crime/14_nia_vs_non_nia`: Do Neighbourhood Improvement Areas (the City's designated priority neighbourhoods) have higher crime rates?
- `crime/15_weekend_vs_weekday`: Per-day rate on weekends vs weekdays, by category. (Normalised: 2 weekend days vs 5 weekdays.)
- `crime/16_neighbourhood_monthly_spikes`: Anomaly detection in SQL: months where a neighbourhood's incidents were > 3 standard deviations above its own mean.
- `crime/17_break_and_enter_premises_trend`: Break and enters: is the shift toward commercial vs residential premises real?
- `crime/18_top_offences_within_category`: The five most common specific offences inside each category, with share of category.
- `crime/19_hotspot_persistence`: Are hotspots persistent? Of the top-20 neighbourhoods in 2014, how many are still top-20 in 2024?
- `crime/20_data_quality_profile`: Before trusting any of the above: what is wrong with the data?
- `network/01_attack_mix`: What is the benign and attack-class distribution?
- `network/02_daily_mix`: How does traffic composition change by source day?
- `network/03_hourly_attack_rate`: How does labeled attack rate vary by hour?
- `network/04_peak_attack_hours`: Which hours carry the highest attack volume?
- `network/05_attacked_ports`: Which destination ports receive the most labeled attacks?
- `network/06_port_risk`: Which common destination ports have the highest attack share?
- `network/08_duration_by_label`: How does flow duration differ by label?
- `network/09_bytes_by_label`: How much data does a typical flow carry by label?
- `network/10_upload_asymmetry`: Which labels have unusually upload-heavy flows?
- `network/11_packet_asymmetry`: Which labels have forward-heavy packet patterns?
- `network/12_flow_rate`: How does packet rate vary by label?
- `network/13_syn_flags`: Which labels feature SYN-heavy flows?
- `network/14_short_flows`: What share of flows are short and packet-light?
- `network/15_hour_port_hotspots`: Which hour-port combinations concentrate attack volume?
- `network/16_daily_port_change`: How do top attacked ports change across days?
- `network/17_simple_flag_tradeoff`: How does a simple short-SYN rule perform against dataset labels?
- `network/18_data_quality`: How many curated flow values are missing or nonfinite?
- `ics/01_split_overview`: How much normal and attack data is in each split?
- `ics/02_attack_episodes`: When do contiguous attack episodes start and end?
- `ics/03_attack_by_hour`: When is attack activity concentrated?
- `ics/04_target_subsystems`: Which plant subsystems carry labeled attack intervals?
- `ics/06_outside_normal_range`: How often do readings fall outside training 1st–99th percentiles?
- `ics/07_attack_z_scores`: Which sensors diverge most during labeled attacks?
- `ics/08_highest_scored_seconds`: Which test seconds have the largest sensor deviation?
- `ics/09_threshold_tradeoff`: How do simple maximum-z thresholds trade off recall and alert volume?
- `ics/10_p1_b2016`: How does P1_B2016 shift between normal and attack test periods?
- `ics/11_p1_flow`: How does P1 flow change during labeled attacks?
- `ics/12_p1_level`: How does P1 level change during labeled attacks?
- `ics/13_p2_rpm`: How does P2 turbine RPM change during labeled attacks?
- `ics/14_p2_sensor`: How does P2_SIT01 change during labeled attacks?
- `ics/15_p3_pressure`: How does P3 pressure change during labeled attacks?
- `ics/16_p4_pressure`: How does P4 pressure change during labeled attacks?
- `ics/17_sensor_correlation`: Do selected subsystem signals move together in normal and attack periods?
- `ics/18_data_quality`: Are timestamps, labels, or selected sensor values missing?
- `fraud/01_monthly_fraud`: How do volume and labeled fraud rate change by month?
- `fraud/02_month_over_month`: Which months have the largest fraud-rate change?
- `fraud/03_source`: Which application source has the higher labeled fraud rate?
- `fraud/04_device_os`: How does fraud rate vary by device operating system?
- `fraud/05_foreign_request`: How does a foreign request relate to labeled fraud?
- `fraud/06_free_email`: Is a free email domain associated with a higher fraud rate?
- `fraud/07_age`: How does fraud rate vary by age band?
- `fraud/08_income`: How does fraud rate vary across income values?
- `fraud/09_name_email_similarity`: What is the fraud gradient for name-email similarity?
- `fraud/10_session_length`: What is the fraud gradient for session length?
- `fraud/11_velocity`: How does six-hour application velocity relate to fraud?
- `fraud/12_device_email_reuse`: Does reuse of a device across emails raise fraud rates?
- `fraud/13_risk_score`: How does credit-risk score rank fraud prevalence?
- `fraud/14_simple_rules`: How do transparent review rules compare on precision and recall?
- `fraud/15_review_budget`: How much fraud can a fixed review budget capture?
- `fraud/16_source_drift`: How does fraud rate drift over time by application source?
- `fraud/17_missing_sentinels`: How often do sentinel values appear in selected fields?
- `fraud/18_employment_segment`: How do labeled rates and review-rule hit rates vary by employment segment?
- `identity/01_daily_logons`: How do logon volume and failure rate change from day 1 to day 2?
- `identity/02_hourly_failures`: When are failed logons concentrated by dataset hour?
- `identity/03_logon_types`: Which logon types account for human-account activity?
- `identity/04_auth_packages`: How do authentication packages differ in failure rate?
- `identity/05_remote_vs_local`: What share of logons is remote in the mirrored fields?
- `identity/06_top_failed_users`: Which anonymized users have the most failures?
- `identity/07_top_failed_sources`: Which source devices have the most failed logons?
- `identity/08_user_failure_bursts`: Which user-quarter-hour windows have repeated failures?
- `identity/09_fail_then_success`: Which user-source-destination windows contain failures before a success?
- `identity/10_new_user_host_pairs`: Which day-2 user-destination pairs were absent on day 1?
- `identity/11_new_pair_count`: How many day-2 user-destination pairs are new relative to day 1?
- `identity/12_source_fanout`: Which day-2 accounts log in from the most distinct source devices?
- `identity/13_destination_fanout`: Which day-2 accounts reach the most distinct destination devices?
- `identity/14_failure_reasons`: Which reported reasons accompany failed logons?
- `identity/15_night_activity`: Which accounts shift toward overnight remote logons on day 2?
- `identity/16_type_drift`: How does logon-type mix change between the two days?
- `identity/17_user_failure_rate`: Which high-volume accounts have elevated failure rates?
- `identity/18_data_quality`: How complete are user, source, destination, and logon type fields?
