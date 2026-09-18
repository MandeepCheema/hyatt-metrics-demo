-- Generated from Atlan glossary term "Occupancy Rate" (guid 82f7c9a1-1abd-439d-b71e-5186850246d0).
-- Do not hand-edit: change the term in Atlan, approval fires the webhook, this file is regenerated.
-- Last changed by seed at 2026-09-18T00:00:00Z.
CREATE OR REPLACE VIEW ANALYTICS.METRICS.OCCUPANCY_RATE
  COMMENT = 'Rooms sold as a share of available room nights. Reported as a percentage at property-day grain.'
AS
SELECT
  property_id,
  business_date,
  100.0 * SUM(rooms_sold) / NULLIF(SUM(available_room_nights), 0) AS occupancy_rate
FROM ANALYTICS.CORE.FCT_ROOM_NIGHTS
GROUP BY
  property_id,
  business_date;
