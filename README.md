# AI CRM Agent for Personalized Lifecycle Campaigns

This project turns raw customer transactional data into lifecycle marketing strategy and campaign execution. It samples real customer records, derives CRM-ready attributes such as churn risk and lifecycle stage, infers the most relevant campaign goal, and generates a three-email sequence for each selected customer.



## What The Project Does

1. Loads customer-level transactional data from `data/input/customer_transactional_data.csv`
2. Samples exactly 5 customers with a fixed seed for reproducibility
3. Derives marketing attributes from raw metrics
4. Infers a campaign goal such as onboarding, win-back, loyalty, or cross-sell
5. Generates a 3-email lifecycle sequence for each sampled customer
6. Writes outputs to JSON and CSV for inspection

## Example Use Case

The repo includes a polished example output for a real sampled customer at:

- `data/output/portfolio_example_customer_12677.json`

That record is useful for demos because it contains:

- raw customer metrics
- derived CRM attributes
- strategy rationale
- the exact generated 3-email sequence

## Input Schema

The transactional input currently uses these fields:

- `customer_id`
- `recency_days`
- `purchase_frequency`
- `avg_order_value`
- `total_revenue`
- `tenure`
- `repeat_customer`
- `avg_days_between_purchases`

## Outputs

Running the main workflow writes:

- `data/output/generated_customer_campaigns.json`
- `data/output/generated_customer_campaigns.csv`

Each record contains:

- customer identifier
- raw input metrics
- derived marketing fields
- customer brief
- campaign strategy
- three generated emails
- generation mode

## Core Flow

```text
Customer Transactional CSV
    -> validation and loading
    -> reproducible sampling
    -> metric-to-marketing transformation
    -> customer brief + business summary
    -> campaign goal inference
    -> OpenAI generation or fallback generation
    -> JSON / CSV outputs
```

## Project Structure

```text
src/load_data.py            # CSV loading and sampling
src/customer_logic.py       # heuristic CRM feature derivation
src/segment_logic.py        # campaign-goal inference and strategy rules
src/prompt_builder.py       # prompt construction for the LLM
src/llm_client.py           # OpenAI path + deterministic fallback
src/campaign_generator.py   # orchestration layer
main.py                     # main entry point
main_customer.py            # customer workflow implementation
app.py                      # print one sample campaign record
```

## Quick Start

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the main workflow:

```bash
python main.py
```

Preview one sampled customer campaign in the terminal:

```bash
python app.py
```

## OpenAI Setup

Set `OPENAI_API_KEY` if you want live model generation:

```bash
export OPENAI_API_KEY="your-key-here"
```

Optional:

- `OPENAI_MODEL` defaults to `gpt-5`

If the OpenAI package is not installed, the API call fails, or no API key is present, the project falls back to deterministic template generation so the pipeline still completes successfully.



## Notes

This repo is most suitable as a portfolio project when framed as:

- a CRM decision engine, not just an email writer
- a bridge between customer analytics and marketing activation
- a system that combines deterministic business logic with LLM generation

The checked-in generated outputs are useful as sample artifacts, while rerunning the workflow may regenerate them in either `openai` or `fallback_template` mode depending on local setup.
