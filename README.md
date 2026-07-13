# How to Run the Social Media Data Visualizer

🎥 **[Watch the demo](https://www.loom.com/share/955d17e3480045909a610f69d96476d4)**

For a deeper look at how the system is put together (components, data flow, and scaling plans), see [ARCHITECTURE.md](ARCHITECTURE.md).

## 1. Prerequisites

Make sure Docker is installed on your machine before doing anything else.

- Install Docker and Docker Compose.
- Verify the installation:

  ```bash
  docker --version
  docker compose version
  ```

## 2. Start the containers

From the project root (where `compose.yml` lives), run:

```bash
docker compose up -d
```

This starts all services: the data ingestion server, Postgres (with TimescaleDB), and Grafana. Use `docker compose ps` to confirm everything is up, and `docker compose logs -f` to watch logs if something doesn't start correctly.

## 3. Upload your data

1. Visit **http://localhost:8000** in your browser.
2. Upload the CSV file containing the social media posts (e.g. TakaPay posts export) through the upload form.
3. The server will parse and load the rows into the `takapay_posts` table in Postgres.

## 4. Log in to Grafana

1. Visit **http://localhost:3000**.
2. Log in with the default credentials:
   - Username: `admin`
   - Password: `admin`
3. Grafana will prompt you to set a new password — you can skip this for local use.

## 5. Open the dashboard

1. Go to **Dashboards** in the left sidebar.
2. Open the only dashboard listed: **TakaPay Social Media Sentiment**.
3. Adjust the time range picker (top right) if needed — it defaults to a fixed window and may need to be widened to see your uploaded data.

---

## Panel Guide

| Panel | Purpose | Insight |
|---|---|---|
| **Sentiment Analysis** | Pie chart of overall sentiment (positive / negative / neutral) across all posts. | Quick read on overall public sentiment toward the brand/topic. |
| **Platforms Analysis** | Pie chart of post volume by platform (e.g. Twitter, Facebook, Reddit). | Shows where the conversation is happening, so effort can be focused on the right channels. |
| **Sentiment score analysis** | Bar chart bucketing posts by sentiment score range (0-25, 25-50, 50-75, 75-100). | Reveals the distribution/intensity of sentiment, not just the positive/negative label — e.g. are negative posts mildly negative or extremely negative. |
| **Topic Analysis** | Bar chart of post volume by topic. | Identifies which topics people are discussing most. |
| **Topic Score Analysis (Positive)** | Table of topics ranked by total positive sentiment score. | Shows which topics are driving the most positive sentiment — useful for identifying strengths to reinforce. |
| **Topic Score Analysis (Negative) (100-actual score)** | Table of topics ranked by total negative sentiment score (inverted so higher = worse). | Highlights which topics are generating the most negative sentiment — useful for identifying pain points to address first. |
| **Daily Sentiment Analysis** | Time series of sentiment counts (positive/negative/neutral) per day. | Tracks how sentiment trends over time, e.g. spikes in negativity around specific events or dates. |
| **Daily Data Collected** | Time series (bar) of total post volume collected per day. | Sanity check on data ingestion — confirms data is flowing in consistently and helps spot gaps or ingestion issues. |
| **Daily Topic Analysis** | Time series of post volume per topic per day. | Shows how attention to specific topics rises or falls over time. |
| **Inspection** | Raw, filterable/sortable table of all rows in `takapay_posts`. | Lets you drill into individual posts behind any aggregate number above, for spot-checking and manual review. |

Note: several panels (Daily Sentiment Analysis, Daily Data Collected, Daily Topic Analysis, Topic Score Analysis tables) respect the dashboard's time range picker — set it to cover your uploaded data's date range if panels appear empty.
