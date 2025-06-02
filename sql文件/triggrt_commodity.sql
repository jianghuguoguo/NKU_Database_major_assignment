DROP TRIGGER IF EXISTS trg_commodity_insert;

DELIMITER $$

CREATE TRIGGER trg_commodity_insert
BEFORE INSERT ON commodity
FOR EACH ROW
BEGIN
    -- 检查商品编号唯一性
    IF (SELECT COUNT(*) FROM commodity WHERE commodityID = NEW.commodityID) > 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = '货物编号已存在';
    END IF;
END $$
DELIMITER ;