/* =========================================================
   RMS • TRIGGERS
   Automatic updates on data change
   Re-run safe — drops old triggers first
========================================================= */

USE rms;
DELIMITER $$


/* -------------------------
   Remove existing triggers
------------------------- */
DROP TRIGGER IF EXISTS trg_set_cancel_time $$


/* =========================================================
   TRIGGER: trg_set_cancel_time
   Ensures cancel_time is set whenever status = CANCELLED
========================================================= */
CREATE TRIGGER trg_set_cancel_time
BEFORE UPDATE ON booking
FOR EACH ROW
BEGIN
  IF NEW.status = 'CANCELLED' AND NEW.cancel_time IS NULL THEN
    SET NEW.cancel_time = NOW();
  END IF;
END $$
/* END TRIGGER: trg_set_cancel_time */


-- =========================================================
-- Add more triggers below
-- =========================================================

DELIMITER ;