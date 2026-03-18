# Scenario Index

This file is generated deterministically by the builder sync tool.
Use it as the authoritative routing map for the skill. If `scenario-guide.md` exists, treat it as supplemental only.

## Core Concepts (6 docs)

Foundational Data Commons concepts, identifiers, schema, and graph model.

Routing note: Start here when an API, MCP, or custom-instance answer depends on shared concepts such as DCIDs, places, statistical variables, observations, or provenance.

- [Key concepts and common tasks](raw/data_model.md)
- [Glossary](raw/glossary.md)
- [How to use Data Commons](raw/index.md)
- [Place types](raw/place_types.md)
- [Statistical Variable Explorer](raw/statistical_variables.md)
- [What is Data Commons?](raw/what_is.md)

## API Clients and Integrations (38 docs)

REST and Python APIs plus Google Sheets and Web Components integrations.

Routing note: Prefer REST V2 and Python V2 by default. Use V1 only when the user explicitly asks for legacy behavior.

- [API - Query data programmatically](raw/api/index.md)
- [Set API Key](raw/api/python/api_key.md)
- [Python (V1)](raw/api/python/index.md)
- [Python (V2)](raw/api/python/v2/index.md)
- [Migrate from V1 to V2](raw/api/python/v2/migration.md)
- [Get node properties](raw/api/python/v2/node.md)
- [Get statistical observations](raw/api/python/v2/observation.md)
- [Get statistical observations as Pandas DataFrames](raw/api/python/v2/pandas.md)
- [Resolve entities](raw/api/python/v2/resolve.md)
- [Tutorials](raw/api/python/v2/tutorials.md)
- [REST (V2)](raw/api/rest/v2/index.md)
- [Migrate from V1 to V2](raw/api/rest/v2/migration.md)
- [Get node properties](raw/api/rest/v2/node.md)
- [Get statistical observations](raw/api/rest/v2/observation.md)
- [Resolve entities](raw/api/rest/v2/resolve.md)
- [Troubleshooting](raw/api/rest/v2/troubleshooting.md)
- [Get names associated with DCIDs](raw/api/sheets/get_name.md)
- [Get node property values](raw/api/sheets/get_property.md)
- [Get statistical variable values](raw/api/sheets/get_variable.md)
- [Analyze data with Google Sheets](raw/api/sheets/index.md)
- [Get places contained in another place](raw/api/sheets/places_in.md)
- [Tutorials](raw/api/sheets/tutorials/index.md)
- [Sheets COVID-19 analysis](raw/api/sheets/tutorials/sheets_covid.md)
- [Sheets South American latitudes](raw/api/sheets/tutorials/sheets_latitude.md)
- [Bar chart](raw/api/web_components/bar.md)
- [All Charts - Web Components Example](raw/api/web_components/examples/all-charts.md)
- [Dynamic Map - Web Components Example](raw/api/web_components/examples/dynamic-map.md)
- [Line Chart - Web Components Example](raw/api/web_components/examples/line-chart.md)
- [Map Styles - Web Components Example](raw/api/web_components/examples/map-styles.md)
- [Gauge chart](raw/api/web_components/gauge.md)
- [Highlight tile](raw/api/web_components/highlight.md)
- [Embed data and visualizations in your own website](raw/api/web_components/index.md)
- [Line chart](raw/api/web_components/line.md)
- [Map chart](raw/api/web_components/map.md)
- [Pie chart](raw/api/web_components/pie.md)
- [Ranking chart](raw/api/web_components/ranking.md)
- [Scatter plot](raw/api/web_components/scatter.md)
- [Slider control](raw/api/web_components/slider.md)

## BigQuery (5 docs)

SQL access patterns for querying Data Commons in BigQuery.

Routing note: Use this scenario for SQL, joining external data, or place-property query patterns.

- [Query with SQL/BigQuery](raw/bigquery/index.md)
- [Join with external data](raw/bigquery/query_join_your_data.md)
- [More complex queries](raw/bigquery/query_more_complex.md)
- [Query places](raw/bigquery/query_places.md)
- [Query observations and properties of places](raw/bigquery/query_property_places.md)

## MCP (3 docs)

Hosted and self-hosted MCP guidance for base Data Commons.

Routing note: Keep this scenario separate from custom-instance MCP guidance unless the user explicitly asks for a comparison.

- [Run an MCP Server](raw/mcp/host_server.md)
- [MCP - Query data interactively with an AI agent](raw/mcp/index.md)
- [Use MCP tools](raw/mcp/run_tools.md)

## Custom Data Commons (13 docs)

Building, configuring, deploying, and operating Custom Data Commons instances.

Routing note: Use this scenario for custom data loading, deployment, UI customization, and custom-instance MCP behavior.

- [Advanced (hybrid) setups](raw/custom_dc/advanced.md)
- [Build and run a custom image](raw/custom_dc/build_image.md)
- [Data config file reference](raw/custom_dc/config.md)
- [Prepare and load your own data](raw/custom_dc/custom_data.md)
- [Define custom entities](raw/custom_dc/custom_entities.md)
- [Customize the site](raw/custom_dc/custom_ui.md)
- [Deploy to Google Cloud](raw/custom_dc/deploy_cloud.md)
- [Frequently asked questions](raw/custom_dc/faq.md)
- [Build your own Data Commons](raw/custom_dc/index.md)
- [Launch your Data Commons](raw/custom_dc/launch_cloud.md)
- [Quickstart](raw/custom_dc/quickstart.md)
- [Run MCP tools](raw/custom_dc/run_mcp_tools.md)
- [Troubleshooting](raw/custom_dc/troubleshooting.md)
