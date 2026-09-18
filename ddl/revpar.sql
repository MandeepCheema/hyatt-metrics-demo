-- Generated from Atlan glossary term "RevPAR" (guid 57822b58-926f-4ef3-8473-e2accfde008f).
-- Do not hand-edit: change the term in Atlan, approval fires the webhook, this file is regenerated.
-- Last changed by seed at 2026-09-18T00:00:00Z.
CREATE OR REPLACE VIEW ANALYTICS.METRICS.REVPAR
  COMMENT = 'Revenue per available room. Total room revenue divided by available room nights for the period. Excludes out-of-order rooms from the denominator.'
AS
SELECT
  property_id,
  business_date,
  SUM(room_revenue) / NULLIF(SUM(available_room_nights), 0) AS revpar
FROM ANALYTICS.CORE.FCT_ROOM_NIGHTS
GROUP BY
  property_id,
  business_date;
