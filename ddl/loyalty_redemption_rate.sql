-- Generated from Atlan glossary term "Loyalty Redemption Rate" (guid 72a8e8b7-444c-4bf2-81dd-557038cefc32).
-- Do not hand-edit: change the term in Atlan, approval fires the webhook, this file is regenerated.
-- Last changed by seed at 2026-09-18T00:00:00Z.
CREATE OR REPLACE VIEW ANALYTICS.METRICS.LOYALTY_REDEMPTION_RATE
  COMMENT = 'Share of room nights paid with loyalty points. Redemption nights divided by total rooms sold.'
AS
SELECT
  property_id,
  business_date,
  100.0 * SUM(redemption_nights) / NULLIF(SUM(rooms_sold), 0) AS loyalty_redemption_rate
FROM ANALYTICS.CORE.FCT_ROOM_NIGHTS
GROUP BY
  property_id,
  business_date;
