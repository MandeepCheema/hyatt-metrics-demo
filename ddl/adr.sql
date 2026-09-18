-- Generated from Atlan glossary term "ADR" (guid c78cde9b-f4c9-482a-8cdc-1a98b2341bb1).
-- Do not hand-edit: change the term in Atlan, approval fires the webhook, this file is regenerated.
-- Last changed by seed at 2026-09-18T00:00:00Z.
CREATE OR REPLACE VIEW ANALYTICS.METRICS.ADR
  COMMENT = 'Average daily rate. Room revenue divided by rooms sold. Complimentary and house-use rooms are excluded from rooms sold.'
AS
SELECT
  property_id,
  business_date,
  SUM(room_revenue) / NULLIF(SUM(rooms_sold), 0) AS adr
FROM ANALYTICS.CORE.FCT_ROOM_NIGHTS
GROUP BY
  property_id,
  business_date;
